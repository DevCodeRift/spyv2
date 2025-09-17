"""
Main entry point for the Politics & War Discord Bot
Runs both the Discord bot and web dashboard with espionage monitoring
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def start_health_only_server():
    """Start minimal health server when main application can't start"""
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    
    @app.route('/health')
    def health():
        return jsonify({
            "status": "healthy",
            "service": "Politics & War Discord Bot",
            "mode": "health-only"
        }), 200
    
    @app.route('/')
    def root():
        return jsonify({
            "status": "health-only mode",
            "message": "Set DISCORD_TOKEN and PNW_API_KEY environment variables to enable full functionality"
        })
    
    port = int(os.getenv('PORT', 5000))
    print(f"🏥 Health-only server starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

# Check for required environment variables FIRST
required_vars = ['DISCORD_TOKEN', 'PNW_API_KEY']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
    print("🏥 Starting health-only server for Railway deployment...")
    start_health_only_server()
    sys.exit(0)

# Only import heavy modules if we have the required environment variables
try:
    import asyncio
    from bot.discord_bot import DiscordBot
    from web.dashboard import WebDashboard
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🏥 Starting health-only server due to import error")
    start_health_only_server()
    sys.exit(0)

async def main():
    """Main application entry point"""
    print("🚀 Starting Politics & War Discord Bot with Espionage Monitoring...")
    print("✅ Environment variables configured")
    print("📊 Web dashboard will be available at http://localhost:5000")
    print("🤖 Discord bot will connect to Discord")
    print("🔍 24/7 Espionage monitoring system (auto-starts)")
    print("\nNew 24/7 System Features:")
    print("  • Auto-indexes ALL nations in the game")
    print("  • Skips vacation mode nations")
    print("  • Only monitors alliance members")
    print("  • Stops monitoring once reset time found")
    print("  • Auto-adds new nations every hour")
    print("\nAvailable Discord Commands:")
    print("  !help - Show all commands")
    print("  !monitor - Check 24/7 monitoring status")
    print("  !resets [alliance] - Show detected reset times")
    print("  !spy [nation] - Check spy activity")
    print("  !spycheck [nation] - Detailed spy status")
    print("\nAdmin Commands:")
    print("  !startmonitor - Manual start (auto-starts anyway)")
    print("  !stopmonitor - Stop monitoring")
    print("  !collect - Force full nation indexing")
    print("\nStarting services...")
    
    # Initialize bot
    bot = DiscordBot()
    
    # Initialize web dashboard
    dashboard = WebDashboard()
    
    try:
        # Start both services
        await asyncio.gather(
            bot.start(),
            dashboard.start()
        )
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ Error starting services: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Fatal error in main application: {e}")
        print("🏥 Starting emergency health-only server...")
        start_health_only_server()
