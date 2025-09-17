#!/usr/bin/env python3
"""
Quick database debug script to check what's in the database
"""

import sqlite3
import os

# Find the database
db_paths = [
    'database/espionage.db',
    'espionage.db',
    'bot/database/espionage.db'
]

for db_path in db_paths:
    if os.path.exists(db_path):
        print(f"Found database at: {db_path}")
        
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Check tables exist
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                print(f"Tables: {[table[0] for table in tables]}")
                
                # Check nations table
                if ('nations',) in tables:
                    cursor.execute('SELECT COUNT(*) FROM nations')
                    total_nations = cursor.fetchone()[0]
                    print(f"Total nations: {total_nations}")
                    
                    cursor.execute('SELECT COUNT(*) FROM nations WHERE is_active = 1')
                    active_nations = cursor.fetchone()[0]
                    print(f"Active nations: {active_nations}")
                    
                    cursor.execute('SELECT COUNT(*) FROM nations WHERE alliance_id IS NOT NULL')
                    alliance_nations = cursor.fetchone()[0]
                    print(f"Alliance nations: {alliance_nations}")
                    
                    # Sample data
                    cursor.execute('SELECT id, nation_name, alliance_id FROM nations LIMIT 5')
                    sample = cursor.fetchall()
                    print(f"Sample nations: {sample}")
                else:
                    print("Nations table not found!")
                
                # Check monitoring queue
                if ('monitoring_queue',) in tables:
                    cursor.execute('SELECT COUNT(*) FROM monitoring_queue')
                    queue_count = cursor.fetchone()[0]
                    print(f"Monitoring queue: {queue_count}")
                else:
                    print("Monitoring queue table not found!")
                
                # Check reset times
                if ('reset_times',) in tables:
                    cursor.execute('SELECT COUNT(*) FROM reset_times')
                    reset_count = cursor.fetchone()[0]
                    print(f"Reset times: {reset_count}")
                else:
                    print("Reset times table not found!")
                
        except Exception as e:
            print(f"Error accessing database: {e}")
        
        break
else:
    print("No database found!")
    print("Checked paths:", db_paths)
