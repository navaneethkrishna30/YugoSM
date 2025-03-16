# YugoSM Dashboard

A lightweight service monitoring dashboard that supports both log-based and endpoint-based uptime monitoring. Monitor your services with ease using either log file updates or health check API endpoints.

## Features

- 📊 Real-time 24h, 7d, and 30d uptime statistics
- 🔄 Automatic status updates via WebSocket
- 📝 Live log viewing
- 🔒 Password protection
- 🎯 Dual monitoring modes:
  - Log-based monitoring
  - Health check API monitoring
- 🐳 Easy deployment with Docker
- 💾 Persistent storage for uptime history
- ⚡ Fast and lightweight (consumes 60MB of RAM)

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/navaneethk30/yugosm.git
cd yugosm
```

2. Start the dashboard in API Monitor mode (Please change the values as per our Requirement):
```bash
DASHBOARD_PASSWORD=Password@1234
CHECK_INTERVAL=10
OFFLINE_THRESHOLD=30
LOG_FILE_PATH=/var/log/sample.log
CHECK_TYPE=endpoint
HEALTH_CHECK_URL=http://myservice:6969/health
docker compose up -d
```

4. Access the dashboard at `http://localhost`

## Configuration

| Environment Variable | Description | Default | Required |
|---------------------|-------------|---------|----------|
| DASHBOARD_PASSWORD | Dashboard access password | demo | Yes |
| CHECK_INTERVAL | Service check interval (seconds) | 10 | No |
| OFFLINE_THRESHOLD | Time until service is marked offline (seconds) | 60 | No |
| LOG_FILE_PATH | Path to service log file | /var/log/sample.log | Yes (for log mode) |
| CHECK_TYPE | Monitoring type ('log' or 'endpoint') | log | No |
| HEALTH_CHECK_URL | Health check endpoint URL | - | Yes (for endpoint mode) |

## Monitoring Types

### Log-based Monitoring
Monitors service status by checking log file updates. The service is considered:
- 🟢 Online: If the log file has been updated within the threshold period
- 🔴 Offline: If the log file hasn't been updated within the `OFFLINE_THRESHOLD`


### Endpoint-based Monitoring
Monitors service status by making HTTP HEAD requests to a health check endpoint. The service is considered:
- 🟢 Online: If the endpoint returns a 2xx status code
- 🔴 Offline: If the endpoint returns an error or non-2xx status code

## Data Persistence

Uptime history is stored in a SQLite database located at `/data/uptime.db` inside the container. The data persists across container restarts through a Docker volume.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Author

- Github: (https://github.com/navaneethkrishna30)
- Twitter: (https://twitter.com/navaneethk30)
- LinkedIn: (https://linkedin.com/in/navaneethkrishnamudumba)

## Acknowledgments

- Prototype using [Bolt.new](https://bolt.new/)
- Backend with [FastAPI](https://fastapi.tiangolo.com/)
- Frontend powered by [React](https://reactjs.org/)
- Icons by [Lucide](https://lucide.dev/)
- Cursor [IDE](https://www.cursor.com/)

---
Made with ❤️ by Navaneeth Krishna
