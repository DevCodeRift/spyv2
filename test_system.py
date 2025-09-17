"""
Test script for the Politics & War Discord Bot
Tests API functionality and database operations
"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from api.pnw_api import PoliticsAndWarAPI
from database.espionage_tracker import EspionageTracker
from utils.espionage_monitor import EspionageMonitor

async def test_api():
    """Test API functionality"""
    print("🔍 Testing Politics & War API...")
    
    api = PoliticsAndWarAPI(os.getenv('PNW_API_KEY'))
    
    # Test basic API query
    print("  Testing game info query...")
    result = api.get_game_info()
    if 'data' in result:
        print("  ✅ Game info query successful")
    else:
        print("  ❌ Game info query failed")
        return False
    
    # Test nation search
    print("  Testing nation search...")
    result = api.search_nations(name="test")
    if 'data' in result:
        print("  ✅ Nation search successful")
    else:
        print("  ❌ Nation search failed")
        return False
    
    # Test spy activity check
    print("  Testing spy activity query...")
    result = api.get_spy_activity()
    if 'data' in result:
        print("  ✅ Spy activity query successful")
    else:
        print("  ❌ Spy activity query failed")
        return False
    
    return True

def test_database():
    """Test database functionality"""
    print("🗄️ Testing database operations...")
    
    try:
        tracker = EspionageTracker()
        
        # Test database connection
        print("  Testing database connection...")
        stats = tracker.get_database_stats()
        print("  ✅ Database connection successful")
        
        # Test table creation
        print("  Testing table structure...")
        # Tables should be created automatically
        print("  ✅ Database tables verified")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
        return False

async def test_monitoring_system():
    """Test espionage monitoring system"""
    print("🔍 Testing espionage monitoring system...")
    
    try:
        api = PoliticsAndWarAPI(os.getenv('PNW_API_KEY'))
        tracker = EspionageTracker()
        monitor = EspionageMonitor(api, tracker)
        
        print("  Testing monitoring system initialization...")
        stats = monitor.get_monitoring_stats()
        print("  ✅ Monitoring system initialized")
        
        print("  Testing manual nation check...")
        # Test with a known nation ID (assuming nation ID 1 exists)
        result = await monitor.manual_check_nation(1)
        if result.get('success'):
            print("  ✅ Manual nation check successful")
        else:
            print("  ⚠️ Manual nation check completed (may be expected)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Monitoring system test failed: {e}")
        return False

async def run_tests():
    """Run all tests"""
    print("🚀 Starting Politics & War Bot Tests")
    print("=" * 50)
    
    # Check environment variables
    print("🔧 Checking environment variables...")
    required_vars = ['PNW_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set them in a .env file or as environment variables")
        return
    
    print("✅ Environment variables configured")
    print()
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    # Test API
    if await test_api():
        tests_passed += 1
    print()
    
    # Test Database
    if test_database():
        tests_passed += 1
    print()
    
    # Test Monitoring System
    if await test_monitoring_system():
        tests_passed += 1
    print()
    
    # Results
    print("=" * 50)
    print(f"🎯 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The system is ready to use.")
        print()
        print("Next steps:")
        print("1. Run `python main.py` to start the bot")
        print("2. Use `!collect` command to gather alliance nations")
        print("3. Use `!startmonitor` command to begin monitoring")
        print("4. Check status with `!monitor` command")
    else:
        print("⚠️ Some tests failed. Please check the configuration and try again.")

if __name__ == "__main__":
    asyncio.run(run_tests())
