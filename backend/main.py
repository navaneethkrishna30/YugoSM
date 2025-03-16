from fastapi import FastAPI, WebSocket, HTTPException, Depends, WebSocketDisconnect
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os
import secrets
import aiofiles
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict
from pydantic import BaseModel
import logging
from collections import deque
import json
import sqlite3
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI and security
app = FastAPI()
security = HTTPBasic()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH")
SERVICE_CHECK_INTERVAL = int(os.getenv("SERVICE_CHECK_INTERVAL", "10"))
OFFLINE_THRESHOLD = int(os.getenv("OFFLINE_THRESHOLD", "30"))
DB_PATH = os.getenv("DB_PATH", "uptime.db")

# In-memory storage
uptime_history = deque(maxlen=168)
connected_clients: List[WebSocket] = []
last_log_modification = datetime.now()
last_log_position = 0

# Pydantic models
class UptimeRecord(BaseModel):
    timestamp: datetime
    status: bool
    response_time: Optional[float] = None
    error_message: Optional[str] = None

class UptimeStorage(BaseModel):
    records: List[Dict]
    last_cleanup: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UptimeMetrics(BaseModel):
    status: bool
    uptime_24h: float
    uptime_7d: float
    uptime_30d: float
    last_updated: str

STORAGE_FILE = "uptime_history.json"
MAX_HISTORY_DAYS = 30

class LogEntry(BaseModel):
    message: str
    timestamp: Optional[str] = None

class IntervalUpdate(BaseModel):
    check_interval: int

# Database setup

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS uptime_records (
                timestamp TEXT NOT NULL,
                status BOOLEAN NOT NULL,
                response_time REAL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        
        # Insert default config if not exists
        conn.execute("""
            INSERT OR IGNORE INTO config (key, value)
            VALUES ('check_interval', '10')
        """)
        conn.commit()

@asynccontextmanager
async def get_db():
    db = sqlite3.connect(DB_PATH)
    try:
        yield db
    finally:
        db.close()

async def get_check_interval() -> int:
    async with get_db() as db:
        result = db.execute("SELECT value FROM config WHERE key = 'check_interval'").fetchone()
        return int(result[0]) if result else 10

async def set_check_interval(interval: int):
    async with get_db() as db:
        db.execute("UPDATE config SET value = ? WHERE key = 'check_interval'", (str(interval),))
        db.commit()

async def save_uptime_record(record: Dict):
    async with get_db() as db:
        db.execute(
            "INSERT INTO uptime_records (timestamp, status, response_time) VALUES (?, ?, ?)",
            (record['timestamp'].isoformat(), record['status'], record.get('response_time'))
        )
        db.commit()

async def get_uptime_records(hours: int = 720) -> List[Dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    async with get_db() as db:
        records = db.execute(
            "SELECT timestamp, status, response_time FROM uptime_records WHERE timestamp > ?",
            (cutoff.isoformat(),)
        ).fetchall()
        return [
            {
                'timestamp': datetime.fromisoformat(r[0]),
                'status': bool(r[1]),
                'response_time': r[2]
            }
            for r in records
        ]

# Utility functions
async def check_log_activity() -> bool:
    """Check if the log file has been modified recently."""
    global last_log_modification, last_log_position
    
    try:
        if not os.path.exists(LOG_FILE_PATH):
            logger.error(f"Log file not found: {LOG_FILE_PATH}")
            return False

        stat = os.stat(LOG_FILE_PATH)
        current_size = stat.st_size
        current_time = datetime.now()
        
        if current_size > last_log_position:
            last_log_modification = current_time
            last_log_position = current_size
            return True
        
        if (current_time - last_log_modification).total_seconds() > OFFLINE_THRESHOLD:
            return False
            
        return True
    except Exception as e:
        logger.error(f"Error checking log activity: {e}")
        return False

def calculate_uptime(hours: int) -> float:
    """Calculate uptime percentage for the specified number of hours."""
    if not uptime_history:
        return 100.0
    
    relevant_records = list(uptime_history)[-hours:]
    if not relevant_records:
        return 100.0
    
    uptime_count = sum(1 for record in relevant_records if record.status)
    return (uptime_count / len(relevant_records)) * 100

async def read_last_logs(limit: int = 100) -> List[LogEntry]:
    """Read the last N lines from the log file."""
    try:
        if not os.path.exists(LOG_FILE_PATH):
            return []
            
        async with aiofiles.open(LOG_FILE_PATH, mode='r') as file:
            lines = []
            async for line in file:
                lines.append(line.strip())
                if len(lines) > limit:
                    lines.pop(0)
                    
            return [
                LogEntry(
                    message=line
                )
                for line in lines
            ]
    except Exception as e:
        logger.error(f"Error reading logs: {e}")
        return []

def format_timedelta(td: timedelta) -> str:
    """Convert timedelta to human readable string."""
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
    
    return " ".join(parts)

async def broadcast_status(status: bool, logs: List[LogEntry]):
    """Broadcast status and logs to all connected clients."""
    storage = await load_uptime_history()
    metrics = await calculate_uptime_metrics(storage.records)
    
    for client in connected_clients[:]:
        try:
            await client.send_json({
                "status": metrics.dict(),
                "logs": [log.dict() for log in logs]
            })
        except Exception as e:
            logger.error(f"Error broadcasting to client: {e}")
            if client in connected_clients:
                connected_clients.remove(client)

async def load_uptime_history() -> UptimeStorage:
    """Load uptime history from JSON file."""
    try:
        if os.path.exists(STORAGE_FILE):
            async with aiofiles.open(STORAGE_FILE, mode='r') as f:
                data = json.loads(await f.read())
                return UptimeStorage(
                    records=[{**r, 'timestamp': datetime.fromisoformat(r['timestamp'])} 
                            for r in data['records']],
                    last_cleanup=datetime.fromisoformat(data['last_cleanup'])
                )
    except Exception as e:
        logger.error(f"Error loading uptime history: {e}")
    
    return UptimeStorage(records=[], last_cleanup=datetime.now(timezone.utc))

async def save_uptime_history(storage: UptimeStorage):
    """Save uptime history to JSON file."""
    try:
        async with aiofiles.open(STORAGE_FILE, mode='w') as f:
            await f.write(storage.json())
    except Exception as e:
        logger.error(f"Error saving uptime history: {e}")

async def cleanup_old_records(storage: UptimeStorage):
    """Remove records older than MAX_HISTORY_DAYS."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_HISTORY_DAYS)
    storage.records = [r for r in storage.records if r['timestamp'] > cutoff]
    storage.last_cleanup = datetime.now(timezone.utc)

async def calculate_uptime_metrics(records: List[Dict]) -> UptimeMetrics:
    """Calculate uptime percentages for different time periods."""
    now = datetime.now(timezone.utc)
    
    def calculate_period_uptime(hours: int) -> float:
        cutoff = now - timedelta(hours=hours)
        relevant_records = [r for r in records if r['timestamp'] > cutoff]
        if not relevant_records:
            return 100.0
        uptime_count = sum(1 for r in relevant_records if r['status'])
        return (uptime_count / len(relevant_records)) * 100

    return UptimeMetrics(
        status=records[-1]['status'] if records else True,
        uptime_24h=calculate_period_uptime(24),
        uptime_7d=calculate_period_uptime(24 * 7),
        uptime_30d=calculate_period_uptime(24 * 30),
        last_updated=now.isoformat()
    )

async def check_service_status() -> UptimeRecord:
    """Enhanced service status check."""
    start_time = datetime.now(timezone.utc)
    try:
        is_active = await check_log_activity()
        end_time = datetime.now(timezone.utc)
        response_time = (end_time - start_time).total_seconds()
        
        return UptimeRecord(
            timestamp=start_time,
            status=is_active,
            response_time=response_time if is_active else None,
            error_message=None if is_active else "Log file not updated"
        )
    except Exception as e:
        return UptimeRecord(
            timestamp=start_time,
            status=False,
            response_time=None,
            error_message=str(e)
        )

async def update_status():
    """Enhanced periodic task to check service status and broadcast updates."""
    storage = await load_uptime_history()
    
    while True:
        try:
            # Check service status
            status_record = await check_service_status()
            record_dict = status_record.dict()
            storage.records.append(record_dict)
            
            # Cleanup old records periodically (once per day)
            if datetime.now(timezone.utc) - storage.last_cleanup > timedelta(days=1):
                await cleanup_old_records(storage)
            
            # Save updated history
            await save_uptime_history(storage)
            
            # Calculate metrics and broadcast
            metrics = await calculate_uptime_metrics(storage.records)
            logs = await read_last_logs(100)
            
            # Broadcast enhanced status
            await broadcast_status(status_record.status, logs)
                    
        except Exception as e:
            logger.error(f"Error updating status: {e}")
            
        await asyncio.sleep(SERVICE_CHECK_INTERVAL)

# Authentication
def verify_password(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify the dashboard password."""
    if not secrets.compare_digest(credentials.password, DASHBOARD_PASSWORD):
        raise HTTPException(
            status_code=401,
            detail="Invalid password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True

# FastAPI endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize database and start background tasks."""
    init_db()
    asyncio.create_task(update_status())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        if websocket in connected_clients:
            connected_clients.remove(websocket)

@app.get("/download-logs")
async def download_logs(credentials: HTTPBasicCredentials = Depends(security)):
    """Endpoint to download the complete log file."""
    verify_password(credentials)
    
    try:
        async with aiofiles.open(LOG_FILE_PATH, mode='r') as file:
            content = await file.read()
            return content
    except Exception as e:
        logger.error(f"Error downloading logs: {e}")
        raise HTTPException(status_code=500, detail="Error downloading logs")

@app.get("/api/auth")
async def auth(credentials: HTTPBasicCredentials = Depends(security)):
    """Endpoint for frontend authentication."""
    verify_password(credentials)
    return {"status": "ok"}