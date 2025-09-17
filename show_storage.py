"""
Demo script showing how the espionage monitoring system stores data
Run this to see exactly what gets stored and how
"""

import sqlite3
import os
from datetime import datetime, timedelta
from database.espionage_tracker import EspionageTracker

def show_storage_demo():
    """Demonstrate how data is stored in the system"""
    print("🗄️ Espionage Monitoring System - Storage Demo")
    print("=" * 60)
    
    # Initialize tracker
    tracker = EspionageTracker()
    
    print("📊 Current Database Contents:")
    print("-" * 40)
    
    # Check if database exists and show basic info
    db_path = tracker.db_path
    if os.path.exists(db_path):
        db_size = os.path.getsize(db_path)
        print(f"Database file: {db_path}")
        print(f"File size: {db_size:,} bytes")
    else:
        print("Database file: Not yet created")
    
    # Show database statistics
    stats = tracker.get_database_stats()
    print(f"\n📈 Current Statistics:")
    print(f"  Total nations: {stats.get('total_nations', 0):,}")
    print(f"  Being monitored: {stats.get('monitoring_count', 0):,}")
    print(f"  Reset times found: {stats.get('reset_times_detected', 0):,}")
    print(f"  Recent checks (24h): {stats.get('recent_checks_24h', 0):,}")
    
    # Show table schemas
    print(f"\n🏗️ Database Schema:")
    print("-" * 40)
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for table_name in tables:
                table = table_name[0]
                print(f"\n📋 Table: {table}")
                
                # Get table info
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                
                for col in columns:
                    col_name = col[1]
                    col_type = col[2]
                    not_null = "NOT NULL" if col[3] else ""
                    print(f"  {col_name:<20} {col_type:<15} {not_null}")
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  → {count:,} rows")
    
    except Exception as e:
        print(f"Error reading database: {e}")
    
    # Show sample data if available
    print(f"\n📝 Sample Data:")
    print("-" * 40)
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Sample nations
            cursor.execute("""
                SELECT id, nation_name, alliance_name, is_active 
                FROM nations 
                ORDER BY last_updated DESC 
                LIMIT 5
            """)
            nations = cursor.fetchall()
            
            if nations:
                print("\n🏛️ Recent Nations:")
                print("ID       | Nation Name           | Alliance    | Active")
                print("-" * 55)
                for nation in nations:
                    print(f"{nation[0]:<8} | {nation[1]:<20} | {nation[2] or 'None':<10} | {nation[3]}")
            
            # Sample monitoring queue
            cursor.execute("""
                SELECT mq.nation_id, n.nation_name, mq.reason, mq.next_check
                FROM monitoring_queue mq
                JOIN nations n ON mq.nation_id = n.id
                ORDER BY mq.next_check
                LIMIT 5
            """)
            queue = cursor.fetchall()
            
            if queue:
                print("\n📋 Monitoring Queue (next to check):")
                print("Nation ID | Nation Name      | Reason              | Next Check")
                print("-" * 70)
                for item in queue:
                    next_check = item[3][:19] if item[3] else "Unknown"
                    print(f"{item[0]:<9} | {item[1]:<15} | {item[2]:<18} | {next_check}")
            
            # Sample reset times
            cursor.execute("""
                SELECT rt.nation_id, n.nation_name, rt.reset_time, rt.detection_method
                FROM reset_times rt
                JOIN nations n ON rt.nation_id = n.id
                ORDER BY rt.created_at DESC
                LIMIT 5
            """)
            resets = cursor.fetchall()
            
            if resets:
                print("\n⏰ Recent Reset Time Detections:")
                print("Nation ID | Nation Name      | Reset Time          | Method")
                print("-" * 70)
                for reset in resets:
                    reset_time = reset[2][:19] if reset[2] else "Unknown"
                    print(f"{reset[0]:<9} | {reset[1]:<15} | {reset_time} | {reset[3]}")
            
            # Sample espionage status
            cursor.execute("""
                SELECT es.nation_id, n.nation_name, es.espionage_available, 
                       es.beige_turns, es.checked_at
                FROM espionage_status es
                JOIN nations n ON es.nation_id = n.id
                ORDER BY es.checked_at DESC
                LIMIT 5
            """)
            statuses = cursor.fetchall()
            
            if statuses:
                print("\n🔍 Recent Espionage Status Checks:")
                print("Nation ID | Nation Name      | Available | Beige | Checked At")
                print("-" * 65)
                for status in statuses:
                    available = "Yes" if status[2] else "No"
                    checked = status[4][:19] if status[4] else "Unknown"
                    print(f"{status[0]:<9} | {status[1]:<15} | {available:<9} | {status[3]:<5} | {checked}")
    
    except Exception as e:
        print(f"Error reading sample data: {e}")
    
    print(f"\n🎯 How Data Flows:")
    print("-" * 40)
    print("1. 🌍 Index all nations → Store in 'nations' table")
    print("2. 📋 Add alliance members → Store in 'monitoring_queue'")
    print("3. 🔍 Check espionage status → Store in 'espionage_status'")
    print("4. ⏰ Detect status change → Store in 'reset_times'")
    print("5. 🧹 Remove from queue → Nation monitoring complete")
    
    print(f"\n💡 Storage Strategy:")
    print("-" * 40)
    print("✅ Keep: Nation info, reset times (forever)")
    print("🔄 Update: Monitoring queue, status checks")
    print("🧹 Clean: Completed monitoring, old statuses")
    print("❌ Skip: Vacation mode, non-alliance nations")

if __name__ == "__main__":
    show_storage_demo()
