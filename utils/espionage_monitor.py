"""
24/7 Espionage monitoring system for tracking espionage availability changes
Optimized to skip vacation mode nations and focus on alliance members only
"""

import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
import os
from utils.nation_collector import NationCollector
from database.espionage_tracker import EspionageTracker
from api.pnw_api import PoliticsAndWarAPI

class EspionageMonitor:
    """Monitors espionage availability changes and detects reset times"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api = PoliticsAndWarAPI(api_key)
        self.collector = NationCollector(api_key)
        self.tracker = EspionageTracker()
        self.is_running = False
        self.last_full_scan = None
        self.monitoring_active = False
    
    async def start_24_7_monitoring(self):
        """Start the 24/7 monitoring system with optimized workflow"""
        print("🚀 Starting 24/7 Espionage Monitoring System...")
        self.is_running = True
        
        # Phase 1: Index all nations in the game first
        print("📊 Phase 1: Indexing all nations in the game...")
        await self.index_all_nations()
        
        # Phase 2: Start monitoring espionage activity
        print("🔍 Phase 2: Starting espionage monitoring...")
        await self.start_espionage_monitoring()
        
        # Schedule regular tasks
        schedule.every(1).hours.do(self._schedule_new_nation_check)
        schedule.every(2).hours.do(self._schedule_monitoring_cycle)  # Every 2 hours for turn changes
        schedule.every(24).hours.do(self._schedule_cleanup)
        
        print("⏰ Scheduled tasks:")
        print("   • New nation check: Every 1 hour")
        print("   • Monitoring cycle: Every 2 hours (turn changes)")
        print("   • Database cleanup: Every 24 hours")
        
        # Main 24/7 monitoring loop
        while self.is_running:
            schedule.run_pending()
            await asyncio.sleep(60)  # Check every minute for scheduled tasks
    
    async def index_all_nations(self) -> Dict[str, Any]:
        """Index all nations in the game, filtering for alliance members only"""
        print("🗂️ Indexing all nations in the game...")
        
        # First, test if API is working with a simple query
        print("🔍 Testing API connection...")
        test_query = """
        {
          nations(first: 1) {
            data {
              id
              nation_name
            }
          }
        }
        """
        
        test_result = self.api.query(test_query)
        print(f"📊 Test API result: {test_result}")
        if test_result is None or 'errors' in test_result:
            print(f"❌ API test failed: {test_result}")
            return {'success': False, 'error': f'API connection test failed: {test_result}'}
        
        print("✅ API connection test passed")
        
        try:
            page = 1
            total_nations = 0
            alliance_nations = 0
            
            while True:
                print(f"  � Processing page {page}...")
                
                # Get nations with alliance info (simplified query)
                query = f"""
                {{
                  nations(first: 100, page: {page}) {{
                    paginatorInfo {{
                      hasMorePages
                      currentPage
                    }}
                    data {{
                      id
                      nation_name
                      alliance_id
                      vacation_mode_turns
                    }}
                  }}
                }}
                """
                
                print(f"📊 Executing query for page {page}...")
                result = self.api.query(query)
                print(f"📊 Raw result type: {type(result)}")
                print(f"📊 Raw result: {str(result)[:200]}...")
                
                # Better error handling for API response
                if result is None:
                    print(f"❌ API returned None on page {page} - possible rate limit or network issue")
                    break
                
                if 'errors' in result:
                    print(f"❌ Error on page {page}: {result['errors']}")
                    break
                
                # Check if we have valid data structure
                if 'data' not in result:
                    print(f"❌ No 'data' key in result on page {page}: {result}")
                    break
                
                nations_data = result.get('data', {}).get('nations', {})
                if not nations_data:
                    print(f"❌ No nations data on page {page}")
                    break
                
                nations = nations_data.get('data', [])
                
                if not nations:
                    break
                
                # Process each nation
                for nation in nations:
                    total_nations += 1
                    
                    # Skip nations not in alliance
                    if not nation.get('alliance_id'):
                        continue
                    
                    # Skip vacation mode nations (they don't need monitoring)
                    if nation.get('vacation_mode_turns', 0) > 0:
                        continue
                    
                    # Add to database (simplified data)
                    self.tracker.add_or_update_nation(
                        nation_id=nation['id'],
                        nation_name=nation['nation_name'],
                        alliance_id=nation['alliance_id'],
                        alliance_name='',  # Not fetching alliance name for now
                        last_active='',    # Not fetching last_active for now
                        should_monitor=True  # Start monitoring immediately
                    )
                    
                    alliance_nations += 1
                
                # Check if more pages
                paginator = nations_data.get('paginatorInfo', {})
                if not paginator.get('hasMorePages', False):
                    break
                
                page += 1
                await asyncio.sleep(1)  # Rate limiting
            
            print(f"✅ Indexing complete!")
            print(f"   • Total nations processed: {total_nations:,}")
            print(f"   • Alliance nations indexed: {alliance_nations:,}")
            
            return {
                'success': True,
                'total_nations': total_nations,
                'alliance_nations': alliance_nations
            }
            
        except Exception as e:
            print(f"❌ Error during indexing: {e}")
            return {'success': False, 'error': str(e)}
    
    async def start_espionage_monitoring(self):
        """Start monitoring espionage status for indexed nations"""
        print("🔍 Starting espionage monitoring for alliance nations...")
        self.monitoring_active = True
        
        # Get nations that need monitoring (no reset time found yet)
        nations_to_monitor = self.tracker.get_nations_needing_monitoring()
        print(f"📊 Found {len(nations_to_monitor)} nations needing monitoring")
        
        # Start monitoring cycle
        await self.monitoring_cycle()
    
    async def monitoring_cycle(self) -> Dict[str, Any]:
        """Run a monitoring cycle to check nations that need monitoring"""
        if not self.monitoring_active:
            return {'success': False, 'message': 'Monitoring not active'}
        
        print(f"🔍 [{datetime.utcnow()}] Running monitoring cycle...")
        
        try:
            # Get nations that need monitoring
            nations_to_check = self.tracker.get_nations_needing_monitoring()
            
            if not nations_to_check:
                print("✅ No nations need monitoring (all reset times found)")
                return {'success': True, 'checked_nations': 0, 'message': 'All reset times found'}
            
            checked_nations = 0
            reset_times_found = 0
            
            for nation in nations_to_check:
                nation_id = nation['nation_id']
                
                # Check current espionage status
                current_status = await self.check_nation_espionage_status(nation_id)
                
                if current_status:
                    # Check if this is a status change (protection -> available = reset time!)
                    reset_detected = self.tracker.record_espionage_status(
                        nation_id=nation_id,
                        espionage_available=current_status['espionage_available'],
                        beige_turns=current_status.get('beige_turns', 0),
                        vacation_mode_turns=current_status.get('vacation_mode_turns', 0)
                    )
                    
                    if reset_detected:
                        print(f"🎯 Reset time detected for {nation['nation_name']}!")
                        reset_times_found += 1
                        
                        # Stop monitoring this nation (reset time found)
                        self.tracker.stop_monitoring_nation(nation_id)
                
                checked_nations += 1
                
                # Rate limiting
                await asyncio.sleep(0.5)
            
            print(f"✅ Monitoring cycle completed")
            print(f"   • Nations checked: {checked_nations}")
            print(f"   • Reset times found: {reset_times_found}")
            
            return {
                'success': True,
                'checked_nations': checked_nations,
                'reset_times_found': reset_times_found
            }
            
        except Exception as e:
            print(f"💥 Error during monitoring cycle: {e}")
            return {'success': False, 'error': str(e)}
    
    async def check_new_nations(self) -> Dict[str, Any]:
        """Check for new nations and add them to monitoring"""
        print("🆕 Checking for new nations...")
        
        try:
            # Get the latest nation ID in our database
            latest_id = self.tracker.get_latest_nation_id()
            
            # Query for nations with ID greater than our latest
            query = f"""
            {{
              nations(id_gt: {latest_id}, first: 100) {{
                data {{
                  id
                  nation_name
                  alliance_id
                  alliance {{
                    id
                    name
                  }}
                  vacation_mode_turns
                  beige_turns
                  last_active
                  espionage_available
                }}
              }}
            }}
            """
            
            result = self.api.query(query)
            
            if 'errors' in result:
                print(f"❌ Error checking new nations: {result['errors']}")
                return {'success': False, 'error': str(result['errors'])}
            
            nations = result.get('data', {}).get('nations', {}).get('data', [])
            new_nations_added = 0
            
            for nation in nations:
                # Skip non-alliance nations
                if not nation.get('alliance_id'):
                    continue
                
                # Skip vacation mode nations
                if nation.get('vacation_mode_turns', 0) > 0:
                    continue
                
                # Add to monitoring
                self.tracker.add_or_update_nation(
                    nation_id=nation['id'],
                    nation_name=nation['nation_name'],
                    alliance_id=nation['alliance_id'],
                    alliance_name=nation.get('alliance', {}).get('name', ''),
                    last_active=nation.get('last_active', ''),
                    should_monitor=True
                )
                
                new_nations_added += 1
            
            if new_nations_added > 0:
                print(f"✅ Added {new_nations_added} new nations to monitoring")
            
            return {
                'success': True,
                'new_nations_added': new_nations_added
            }
            
        except Exception as e:
            print(f"❌ Error checking new nations: {e}")
            return {'success': False, 'error': str(e)}
    
    async def check_nation_espionage_status(self, nation_id: int) -> Dict[str, Any]:
        """Check a specific nation's espionage status"""
        try:
            query = f"""
            {{
              nations(id: [{nation_id}]) {{
                data {{
                  id
                  espionage_available
                  beige_turns
                  vacation_mode_turns
                }}
              }}
            }}
            """
            
            result = self.api.query(query)
            
            if 'errors' in result:
                return None
            
            nations = result.get('data', {}).get('nations', {}).get('data', [])
            return nations[0] if nations else None
            
        except Exception as e:
            print(f"❌ Error checking nation {nation_id}: {e}")
            return None
    
    async def cleanup_completed_nations(self):
        """Clean up nations that no longer need monitoring"""
        print("🧹 Running cleanup...")
        
        # Remove nations from monitoring queue if:
        # 1. Reset time already found
        # 2. Nation went into vacation mode
        # 3. Nation left alliance
        
        cleanup_count = self.tracker.cleanup_monitoring_queue()
        print(f"✅ Cleanup completed: {cleanup_count} nations removed from monitoring")
    
    def _schedule_new_nation_check(self):
        """Schedule new nation check (called by scheduler)"""
        asyncio.create_task(self.check_new_nations())
    
    def _schedule_monitoring_cycle(self):
        """Schedule monitoring cycle (called by scheduler)"""
        asyncio.create_task(self.monitoring_cycle())
    
    def _schedule_cleanup(self):
        """Schedule cleanup (called by scheduler)"""
        asyncio.create_task(self.cleanup_completed_nations())
    
    def stop_monitoring(self):
        """Stop the monitoring system"""
        print("🛑 Stopping Espionage Monitoring System...")
        self.is_running = False
        self.monitoring_active = False
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring system statistics"""
        stats = self.tracker.get_database_stats()
        
        return {
            'is_running': self.is_running,
            'monitoring_active': self.monitoring_active,
            'total_nations': stats.get('total_nations', 0),
            'monitoring_count': stats.get('monitoring_count', 0),
            'reset_times_detected': stats.get('reset_times_detected', 0),
            'recent_checks_24h': stats.get('recent_checks_24h', 0),
            'last_full_scan': self.last_full_scan.isoformat() if self.last_full_scan else None
        }
    
    async def manual_check_nation(self, nation_id: int) -> Dict[str, Any]:
        """Manually check a specific nation's espionage status"""
        print(f"🔍 Manual check for nation ID: {nation_id}")
        
        try:
            result = await self.collector.update_specific_nations([nation_id])
            return result
        except Exception as e:
            print(f"💥 Error during manual check: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get current monitoring statistics"""
        stats = self.tracker.get_stats()
        
        # Add monitoring-specific stats
        stats.update({
            'is_running': self.is_running,
            'last_full_scan': self.last_full_scan.isoformat() if self.last_full_scan else None,
            'next_monitoring_cycle': self._get_next_scheduled_time('monitoring'),
            'next_full_rescan': self._get_next_scheduled_time('rescan')
        })
        
        return stats
    
    def _get_next_scheduled_time(self, task_type: str) -> str:
        """Get the next scheduled time for a task"""
        try:
            # This is a simplified version - in a real implementation,
            # you'd want to track this more precisely
            if task_type == 'monitoring':
                return (datetime.utcnow() + timedelta(hours=2)).isoformat()
            elif task_type == 'rescan':
                return (datetime.utcnow() + timedelta(hours=24)).isoformat()
        except:
            return "Unknown"
    
    async def get_reset_time_report(self, alliance_id: int = None) -> Dict[str, Any]:
        """Generate a report of detected reset times"""
        print("📊 Generating reset time report...")
        
        try:
            reset_times = self.tracker.get_nation_reset_times()
            
            # Group by alliance if specified
            if alliance_id:
                alliance_nations = self.tracker.get_alliance_nations(alliance_id)
                alliance_nation_ids = {n['id'] for n in alliance_nations}
                reset_times = [rt for rt in reset_times if rt['nation_id'] in alliance_nation_ids]
            
            # Sort by reset time
            reset_times.sort(key=lambda x: x['reset_time'])
            
            # Generate statistics
            total_detected = len(reset_times)
            unique_nations = len(set(rt['nation_id'] for rt in reset_times))
            
            # Group by hour of day
            hourly_distribution = {}
            for rt in reset_times:
                try:
                    hour = datetime.fromisoformat(rt['reset_time'].replace('Z', '+00:00')).hour
                    hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
                except:
                    continue
            
            return {
                'total_reset_times_detected': total_detected,
                'unique_nations_with_resets': unique_nations,
                'hourly_distribution': hourly_distribution,
                'recent_detections': reset_times[-10:],  # Last 10 detections
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"💥 Error generating reset time report: {e}")
            return {'success': False, 'error': str(e)}
