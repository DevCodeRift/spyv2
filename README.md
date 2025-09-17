# Politics & War Discord Bot with Espionage Monitoring

A comprehensive Discord bot and web dashboard for the Politics & War game, featuring advanced espionage monitoring and reset time detection.

## 🌟 Features

### Discord Bot Commands
- **Basic Commands**: `!ping`, `!help`, `!gameinfo`, `!nation <name>`
- **Espionage Commands**: `!spy [nation]`, `!spycheck [nation]`, `!wars [nation]`, `!checknation <name>`
- **Monitoring System**: `!monitor`, `!resets [alliance]`, `!startmonitor` (Admin), `!collect` (Admin)

### Web Dashboard
- Real-time spy status checking
- Nation information lookup
- Active wars monitoring
- Monitoring system control panel
- Reset time analytics

### Advanced Espionage Monitoring
- **Automated Tracking**: Monitors all alliance nations every 2 hours
- **Reset Time Detection**: Identifies when nations' daily reset occurs
- **Database Storage**: SQLite database for historical data
- **Intelligent Queuing**: Efficient nation monitoring with queue management
- **Status Change Detection**: Tracks when espionage becomes available/unavailable

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- Discord Bot Token
- Politics & War API Key

### 2. Installation
```bash
git clone <repository>
cd spyv2
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file:
```env
DISCORD_TOKEN=your_discord_bot_token
PNW_API_KEY=your_politics_and_war_api_key
FLASK_SECRET_KEY=your_secret_key_for_web_dashboard
WEB_HOST=0.0.0.0
WEB_PORT=5000
DEBUG=True
```

### 4. Run the Bot
```bash
python main.py
```

The system will start:
- Discord Bot (connects to Discord)
- Web Dashboard (http://localhost:5000)
- Espionage Monitoring System (ready for activation)

## 📊 Monitoring System Workflow

### Initial Setup
1. Use `!collect` command (Admin only) to gather all alliance nations
2. Use `!startmonitor` command (Admin only) to begin automated monitoring
3. The system will check nations every 2 hours and perform full scans every 24 hours

### Reset Time Detection
The system tracks when nations become unavailable for espionage (due to beige/vacation) and then become available again. This transition indicates their daily reset time.

### Data Analysis
- View system status with `!monitor`
- Check reset times with `!resets [alliance_name]`
- Manually check specific nations with `!checknation <nation_name>`

## 🏗️ Architecture

### Components
```
spyv2/
├── api/
│   └── pnw_api.py              # Politics & War GraphQL API wrapper
├── bot/
│   └── discord_bot.py          # Discord bot with commands
├── database/
│   ├── espionage_tracker.py    # SQLite database management
│   └── spy_bot.db              # Database file (auto-created)
├── utils/
│   ├── nation_collector.py     # Data collection utilities
│   └── espionage_monitor.py    # Monitoring system core
├── web/
│   ├── dashboard.py            # Flask web application
│   └── templates/
│       └── dashboard.html      # Web interface
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

### Database Schema
- **nations**: Store nation information and alliance membership
- **espionage_status**: Track espionage availability over time
- **reset_times**: Record detected daily reset times
- **monitoring_queue**: Manage monitoring schedule

## 🔧 Configuration

### Environment Variables
- `DISCORD_TOKEN`: Your Discord bot token
- `PNW_API_KEY`: Your Politics & War API key
- `FLASK_SECRET_KEY`: Secret key for web sessions
- `WEB_HOST`: Web dashboard host (default: 0.0.0.0)
- `WEB_PORT`: Web dashboard port (default: 5000)
- `DEBUG`: Enable debug mode (default: True)

### Discord Bot Permissions
Required Discord permissions:
- Send Messages
- Embed Links
- Read Message History
- Use Slash Commands (optional)

## 📈 Usage Examples

### Check System Status
```
!monitor
```
Shows monitoring system status, tracked nations, and recent activity.

### View Reset Times
```
!resets Rose
```
Shows detected reset times for the "Rose" alliance with hourly distribution.

### Manual Nation Check
```
!checknation ExampleNation
```
Manually checks a specific nation's current espionage status.

### Spy Activity Check
```
!spy ExampleNation
```
Shows recent spy activity and current protection status.

## 🛠️ Development

### API Integration
The bot uses the Politics & War GraphQL API with proper query encoding and error handling. Key features:
- Automatic retry logic
- Query parameter encoding
- Comprehensive error handling
- Rate limiting awareness

### Database Management
SQLite database with automatic schema creation and migration support:
- Efficient indexing for fast queries
- Historical data retention
- Automated cleanup routines

### Monitoring Algorithm
The espionage monitoring system uses intelligent scheduling:
- Priority-based queue management
- Adaptive monitoring intervals
- Automatic error recovery
- Performance optimization

## 🚀 Deployment

### Railway Deployment
The project is configured for Railway deployment:
1. Connect your GitHub repository
2. Set environment variables in Railway dashboard
3. Deploy automatically on push

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## 📝 API Endpoints

### Web Dashboard API
- `GET /api/monitor/status` - Get monitoring system status
- `POST /api/monitor/start` - Start monitoring system
- `POST /api/monitor/collect` - Trigger nation collection
- `GET /api/monitor/resets` - Get reset time report
- `POST /api/monitor/check/<nation_id>` - Manual nation check
- `GET /api/spy/<nation_name>` - Get spy information
- `GET /api/wars` - Get active wars

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This bot is for educational and analytical purposes. Please respect the Politics & War terms of service and API usage guidelines. The espionage monitoring system is designed for intelligence gathering within the game's rules.

## 🆘 Support

For issues, questions, or feature requests:
1. Check the existing issues
2. Create a new issue with detailed information
3. Include relevant error messages and logs

## 🎯 Roadmap

- [ ] Advanced analytics dashboard
- [ ] Multi-server support
- [ ] Custom monitoring intervals
- [ ] Export functionality for data
- [ ] Integration with other game APIs
- [ ] Mobile-responsive web interface
- [ ] Real-time notifications
