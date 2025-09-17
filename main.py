"""
Main entry point for the Politics & War Discord Bot
Runs both the Discord bot and web dashboard with espionage monitoring
"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import bot and web components
from bot.discord_bot import DiscordBot
from web.dashboard import WebDashboard

async def main():
    """Main application entry point"""
    print("🚀 Starting Politics & War Discord Bot with Espionage Monitoring...")
    
    # Check for required environment variables
    required_vars = ['DISCORD_TOKEN', 'PNW_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("\n🔧 Quick Fix:")
        print("1. Copy .env.example to .env")
        print("2. Edit .env and fill in your tokens:")
        for var in missing_vars:
            if var == 'DISCORD_TOKEN':
                print("   - DISCORD_TOKEN: Get from https://discord.com/developers/applications")
            elif var == 'PNW_API_KEY':
                print("   - PNW_API_KEY: Get from Politics & War account settings")
        print("3. Run: python check_env.py (to verify)")
        print("4. Run: python main.py (to start the bot)")
        print("\n📖 For detailed setup guide, see: ENVIRONMENT_SETUP.md")
        
        # Start health-only server for Railway deployment
        print("\n🏥 Starting health-only server for deployment...")
        from health_server import main as health_main
        health_main()
        return
    
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
    asyncio.run(main())
