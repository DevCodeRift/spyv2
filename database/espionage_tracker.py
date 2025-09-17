"""
Database models for tracking nation espionage availability and reset times
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os

class EspionageTracker:
    """Database manager for tracking nation espionage availability"""
    
    def __init__(self, db_path: str = "database/espionage_tracker.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Nations table - stores basic nation information
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS nations (
                    id INTEGER PRIMARY KEY,
                    nation_name TEXT NOT NULL,
                    leader_name TEXT,
                    alliance_id INTEGER,
                    alliance_name TEXT,
                    score REAL,
                    cities INTEGER,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Espionage status table - tracks current and historical espionage availability
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS espionage_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nation_id INTEGER,
                    espionage_available BOOLEAN,
                    beige_turns INTEGER DEFAULT 0,
                    vacation_mode_turns INTEGER DEFAULT 0,
                    last_active TIMESTAMP,
                    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (nation_id) REFERENCES nations (id)
                )
            ''')
            
            # Reset times table - stores detected daily reset times
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reset_times (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nation_id INTEGER,
                    reset_time TIMESTAMP,
                    confidence_level REAL DEFAULT 1.0,
                    detection_method TEXT,
                    verified BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (nation_id) REFERENCES nations (id)
                )
            ''')
            
            # Monitoring queue - nations that need to be checked every 2 hours
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monitoring_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nation_id INTEGER,
                    reason TEXT,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    next_check TIMESTAMP,
                    priority INTEGER DEFAULT 1,
                    FOREIGN KEY (nation_id) REFERENCES nations (id)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_nation_alliance ON nations (alliance_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_espionage_nation ON espionage_status (nation_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_espionage_checked ON espionage_status (checked_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reset_nation ON reset_times (nation_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_monitoring_next_check ON monitoring_queue (next_check)')
            
            conn.commit()
    
    def add_nation(self, nation_data: Dict[str, Any]) -> bool:
        """Add or update a nation in the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO nations 
                    (id, nation_name, leader_name, alliance_id, alliance_name, score, cities, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    nation_data.get('id'),
                    nation_data.get('nation_name'),
                    nation_data.get('leader_name'),
                    nation_data.get('alliance_id'),
                    nation_data.get('alliance', {}).get('name') if nation_data.get('alliance') else None,
                    nation_data.get('score'),
                    nation_data.get('num_cities')
                ))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding nation {nation_data.get('nation_name', 'Unknown')}: {e}")
            return False
    
    def update_espionage_status(self, nation_id: int, status_data: Dict[str, Any]) -> bool:
        """Update espionage status for a nation"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO espionage_status 
                    (nation_id, espionage_available, beige_turns, vacation_mode_turns, last_active, checked_at)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    nation_id,
                    status_data.get('espionage_available', True),
                    status_data.get('beige_turns', 0),
                    status_data.get('vacation_mode_turns', 0),
                    status_data.get('last_active')
                ))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating espionage status for nation {nation_id}: {e}")
            return False
    
    def add_to_monitoring_queue(self, nation_id: int, reason: str = "espionage_unavailable") -> bool:
        """Add a nation to the monitoring queue"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Calculate next check time (2 hours from now)
                next_check = datetime.utcnow() + timedelta(hours=2)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO monitoring_queue 
                    (nation_id, reason, next_check, added_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (nation_id, reason, next_check))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding nation {nation_id} to monitoring queue: {e}")
            return False
    
    def record_reset_time(self, nation_id: int, reset_time: datetime, detection_method: str = "espionage_availability") -> bool:
        """Record a detected reset time for a nation"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO reset_times 
                    (nation_id, reset_time, detection_method, created_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (nation_id, reset_time, detection_method))
                
                # Remove from monitoring queue since we found the reset time
                cursor.execute('DELETE FROM monitoring_queue WHERE nation_id = ?', (nation_id,))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error recording reset time for nation {nation_id}: {e}")
            return False
    
    def get_nations_to_monitor(self) -> List[Dict[str, Any]]:
        """Get nations that need to be checked (next_check time has passed)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT mq.nation_id, n.nation_name, mq.reason, mq.next_check
                    FROM monitoring_queue mq
                    JOIN nations n ON mq.nation_id = n.id
                    WHERE mq.next_check <= CURRENT_TIMESTAMP
                    ORDER BY mq.priority DESC, mq.next_check ASC
                    LIMIT 50
                ''')
                
                return [
                    {
                        'nation_id': row[0],
                        'nation_name': row[1],
                        'reason': row[2],
                        'next_check': row[3]
                    }
                    for row in cursor.fetchall()
                ]
        except Exception as e:
            print(f"Error getting nations to monitor: {e}")
            return []
    
    def get_nation_reset_times(self, nation_id: int = None) -> List[Dict[str, Any]]:
        """Get reset times for a nation or all nations"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if nation_id:
                    cursor.execute('''
                        SELECT rt.nation_id, n.nation_name, rt.reset_time, rt.confidence_level, 
                               rt.detection_method, rt.verified, rt.created_at
                        FROM reset_times rt
                        JOIN nations n ON rt.nation_id = n.id
                        WHERE rt.nation_id = ?
                        ORDER BY rt.created_at DESC
                    ''', (nation_id,))
                else:
                    cursor.execute('''
                        SELECT rt.nation_id, n.nation_name, rt.reset_time, rt.confidence_level,
                               rt.detection_method, rt.verified, rt.created_at
                        FROM reset_times rt
                        JOIN nations n ON rt.nation_id = n.id
                        ORDER BY rt.created_at DESC
                        LIMIT 100
                    ''')
                
                return [
                    {
                        'nation_id': row[0],
                        'nation_name': row[1],
                        'reset_time': row[2],
                        'confidence_level': row[3],
                        'detection_method': row[4],
                        'verified': row[5],
                        'created_at': row[6]
                    }
                    for row in cursor.fetchall()
                ]
        except Exception as e:
            print(f"Error getting reset times: {e}")
            return []
    
    def get_alliance_nations(self, alliance_id: int = None) -> List[Dict[str, Any]]:
        """Get all nations in alliances (or specific alliance)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if alliance_id:
                    cursor.execute('''
                        SELECT id, nation_name, leader_name, alliance_id, alliance_name, score, cities
                        FROM nations 
                        WHERE alliance_id = ? AND alliance_id > 0 AND is_active = 1
                        ORDER BY score DESC
                    ''', (alliance_id,))
                else:
                    cursor.execute('''
                        SELECT id, nation_name, leader_name, alliance_id, alliance_name, score, cities
                        FROM nations 
                        WHERE alliance_id > 0 AND is_active = 1
                        ORDER BY alliance_id, score DESC
                    ''')
                
                return [
                    {
                        'id': row[0],
                        'nation_name': row[1],
                        'leader_name': row[2],
                        'alliance_id': row[3],
                        'alliance_name': row[4],
                        'score': row[5],
                        'cities': row[6]
                    }
                    for row in cursor.fetchall()
                ]
        except Exception as e:
            print(f"Error getting alliance nations: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total nations
                cursor.execute('SELECT COUNT(*) FROM nations WHERE alliance_id > 0 AND is_active = 1')
                total_nations = cursor.fetchone()[0]
                
                # Nations being monitored
                cursor.execute('SELECT COUNT(*) FROM monitoring_queue')
                monitoring_count = cursor.fetchone()[0]
                
                # Reset times detected
                cursor.execute('SELECT COUNT(*) FROM reset_times')
                reset_times_count = cursor.fetchone()[0]
                
                # Recent status checks
                cursor.execute('SELECT COUNT(*) FROM espionage_status WHERE checked_at > datetime("now", "-24 hours")')
                recent_checks = cursor.fetchone()[0]
                
                return {
                    'total_nations': total_nations,
                    'monitoring_count': monitoring_count,
                    'reset_times_detected': reset_times_count,
                    'recent_checks_24h': recent_checks
                }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}
    
    def add_or_update_nation(self, nation_id: int, nation_name: str, alliance_id: int, 
                           alliance_name: str, last_active: str, should_monitor: bool = True) -> bool:
        """Add or update a nation and optionally add to monitoring"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Add/update nation
                cursor.execute('''
                    INSERT OR REPLACE INTO nations 
                    (id, nation_name, alliance_id, alliance_name, last_updated, is_active)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, 1)
                ''', (nation_id, nation_name, alliance_id, alliance_name))
                
                # Add to monitoring if requested and not already found reset time
                if should_monitor:
                    # Check if we already have reset time for this nation
                    cursor.execute('SELECT COUNT(*) FROM reset_times WHERE nation_id = ?', (nation_id,))
                    has_reset_time = cursor.fetchone()[0] > 0
                    
                    if not has_reset_time:
                        # Add to monitoring queue
                        next_check = datetime.utcnow() + timedelta(hours=1)  # Check in 1 hour
                        cursor.execute('''
                            INSERT OR REPLACE INTO monitoring_queue 
                            (nation_id, reason, next_check, added_at)
                            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                        ''', (nation_id, "new_nation_monitoring", next_check))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding/updating nation {nation_name}: {e}")
            return False
    
    def get_nations_needing_monitoring(self) -> List[Dict[str, Any]]:
        """Get nations that need espionage monitoring (no reset time found yet)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT mq.nation_id, n.nation_name, n.alliance_name, mq.next_check
                    FROM monitoring_queue mq
                    JOIN nations n ON mq.nation_id = n.id
                    WHERE mq.next_check <= CURRENT_TIMESTAMP
                    AND n.is_active = 1
                    ORDER BY mq.priority DESC, mq.next_check ASC
                    LIMIT 100
                ''')
                
                return [
                    {
                        'nation_id': row[0],
                        'nation_name': row[1],
                        'alliance_name': row[2],
                        'next_check': row[3]
                    }
                    for row in cursor.fetchall()
                ]
        except Exception as e:
            print(f"Error getting nations needing monitoring: {e}")
            return []
    
    def record_espionage_status(self, nation_id: int, espionage_available: bool, 
                              beige_turns: int, vacation_mode_turns: int) -> bool:
        """Record espionage status and detect reset time if status changed"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get last status for this nation
                cursor.execute('''
                    SELECT espionage_available, checked_at 
                    FROM espionage_status 
                    WHERE nation_id = ? 
                    ORDER BY checked_at DESC 
                    LIMIT 1
                ''', (nation_id,))
                
                last_status = cursor.fetchone()
                reset_detected = False
                
                # Check for reset time detection (protection -> available)
                if last_status:
                    last_available = bool(last_status[0])
                    
                    # If last check was unavailable and now available = reset time!
                    if not last_available and espionage_available:
                        # Record reset time
                        now = datetime.utcnow()
                        cursor.execute('''
                            INSERT INTO reset_times 
                            (nation_id, reset_time, detection_method, created_at)
                            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                        ''', (nation_id, now, "protection_to_available"))
                        
                        reset_detected = True
                
                # Record current status
                cursor.execute('''
                    INSERT INTO espionage_status 
                    (nation_id, espionage_available, beige_turns, vacation_mode_turns, checked_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (nation_id, espionage_available, beige_turns, vacation_mode_turns))
                
                # Update next check time if still monitoring
                if not reset_detected:
                    next_check = datetime.utcnow() + timedelta(hours=6)  # Check again in 6 hours
                    cursor.execute('''
                        UPDATE monitoring_queue 
                        SET next_check = ? 
                        WHERE nation_id = ?
                    ''', (next_check, nation_id))
                
                conn.commit()
                return reset_detected
                
        except Exception as e:
            print(f"Error recording espionage status for nation {nation_id}: {e}")
            return False
    
    def stop_monitoring_nation(self, nation_id: int) -> bool:
        """Remove a nation from monitoring (reset time found)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM monitoring_queue WHERE nation_id = ?', (nation_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error stopping monitoring for nation {nation_id}: {e}")
            return False
    
    def get_latest_nation_id(self) -> int:
        """Get the highest nation ID in our database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COALESCE(MAX(id), 0) FROM nations')
                return cursor.fetchone()[0]
        except Exception as e:
            print(f"Error getting latest nation ID: {e}")
            return 0
    
    def cleanup_monitoring_queue(self) -> int:
        """Clean up monitoring queue (remove vacation/non-alliance nations)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Remove nations that are no longer active or went into vacation
                cursor.execute('''
                    DELETE FROM monitoring_queue 
                    WHERE nation_id IN (
                        SELECT n.id FROM nations n
                        WHERE n.alliance_id IS NULL 
                        OR n.is_active = 0
                    )
                ''')
                
                # Remove nations that already have reset times
                cursor.execute('''
                    DELETE FROM monitoring_queue 
                    WHERE nation_id IN (
                        SELECT nation_id FROM reset_times
                    )
                ''')
                
                cleanup_count = cursor.rowcount
                conn.commit()
                return cleanup_count
                
        except Exception as e:
            print(f"Error during cleanup: {e}")
            return 0
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total nations
                cursor.execute('SELECT COUNT(*) FROM nations WHERE alliance_id IS NOT NULL AND is_active = 1')
                total_nations = cursor.fetchone()[0]
                
                # Nations being monitored
                cursor.execute('SELECT COUNT(*) FROM monitoring_queue')
                monitoring_count = cursor.fetchone()[0]
                
                # Reset times detected
                cursor.execute('SELECT COUNT(*) FROM reset_times')
                reset_times_count = cursor.fetchone()[0]
                
                # Recent status checks
                cursor.execute('SELECT COUNT(*) FROM espionage_status WHERE checked_at > datetime("now", "-24 hours")')
                recent_checks = cursor.fetchone()[0]
                
                # Unique nations with reset times
                cursor.execute('SELECT COUNT(DISTINCT nation_id) FROM reset_times')
                unique_nations_with_resets = cursor.fetchone()[0]
                
                return {
                    'total_nations': total_nations,
                    'monitoring_count': monitoring_count,
                    'reset_times_detected': reset_times_count,
                    'recent_checks_24h': recent_checks,
                    'unique_nations_with_resets': unique_nations_with_resets
                }
        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {}
