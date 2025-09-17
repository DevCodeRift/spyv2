"""
Environment Variable Checker for Politics & War 24/7 Espionage Monitoring
Run this script to verify your environment setup before starting the bot
"""

import os
from dotenv import load_dotenv

def check_environment():
    """Check if all required environment variables are properly set"""
    print("🔍 Environment Variable Setup Check")
    print("=" * 50)
    
    # Load .env file if it exists
    env_file_exists = os.path.exists('.env')
    if env_file_exists:
        load_dotenv()
        print("✅ .env file found and loaded")
    else:
        print("⚠️  .env file not found (using system environment variables)")
    
    print()
    
    # Required variables
    required_vars = {
        'DISCORD_TOKEN': 'Discord Bot Token (required for bot to connect)',
        'PNW_API_KEY': 'Politics & War API Key (required for game data)'
    }
    
    # Optional variables with defaults
    optional_vars = {
        'FLASK_SECRET_KEY': ('Web dashboard session security', 'dev-secret-key'),
        'WEB_HOST': ('Web dashboard host address', '0.0.0.0'),
        'WEB_PORT': ('Web dashboard port number', '5000'),
        'DEBUG': ('Debug mode for development', 'True')
    }
    
    print("🚨 REQUIRED Variables:")
    print("-" * 30)
    
    all_required_set = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Don't show full token for security
            display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            print(f"✅ {var:<15} : {display_value} ({description})")
        else:
            print(f"❌ {var:<15} : MISSING - {description}")
            all_required_set = False
    
    print("\nℹ️  OPTIONAL Variables:")
    print("-" * 30)
    
    for var, (description, default) in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var:<15} : {value} ({description})")
        else:
            print(f"⚪ {var:<15} : Using default '{default}' ({description})")
    
    print("\n" + "=" * 50)
    
    if all_required_set:
        print("🎉 ALL REQUIRED VARIABLES SET!")
        print("✅ Ready to start the 24/7 monitoring system")
        print("\nNext steps:")
        print("1. Run: python main.py")
        print("2. Bot will auto-connect to Discord")
        print("3. 24/7 monitoring will auto-start")
        print("4. Web dashboard: http://localhost:5000")
    else:
        print("❌ MISSING REQUIRED VARIABLES!")
        print("\nTo fix this:")
        print("1. Copy .env.example to .env")
        print("2. Edit .env and fill in your tokens:")
        print("   - DISCORD_TOKEN: Get from https://discord.com/developers/applications")
        print("   - PNW_API_KEY: Get from Politics & War account settings")
        print("3. Run this script again to verify")
    
    print("\n💡 Need help getting tokens? See ENVIRONMENT_SETUP.md")
    
    return all_required_set

def test_api_connection():
    """Test if the API key works"""
    api_key = os.getenv('PNW_API_KEY')
    if not api_key:
        print("⚠️  Cannot test API - PNW_API_KEY not set")
        return False
    
    print("\n🔌 Testing Politics & War API Connection...")
    
    try:
        from api.pnw_api import PoliticsAndWarAPI
        api = PoliticsAndWarAPI(api_key)
        
        # Simple test query
        result = api.get_game_info()
        
        if 'data' in result and 'game_info' in result['data']:
            print("✅ API connection successful!")
            game_date = result['data']['game_info'].get('game_date', 'Unknown')
            print(f"   Game date: {game_date}")
            return True
        else:
            print("❌ API connection failed - Invalid response")
            if 'errors' in result:
                print(f"   Error: {result['errors'][0]['message']}")
            return False
            
    except Exception as e:
        print(f"❌ API connection failed - {e}")
        return False

if __name__ == "__main__":
    # Check environment variables
    env_ok = check_environment()
    
    # Test API if environment is OK
    if env_ok:
        api_ok = test_api_connection()
        
        if api_ok:
            print("\n🚀 SYSTEM READY!")
            print("Everything is configured correctly.")
            print("Run 'python main.py' to start the 24/7 monitoring system.")
        else:
            print("\n⚠️  Environment OK but API test failed.")
            print("Check your PNW_API_KEY and try again.")
    else:
        print("\n🔧 Please fix the environment variables and try again.")
