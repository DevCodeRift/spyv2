"""
Data collection system for fetching and storing all alliance nations
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from api.pnw_api import PoliticsAndWarAPI
from database.espionage_tracker import EspionageTracker

class NationCollector:
    """Collects and stores nation data from the Politics & War API"""
    
    def __init__(self, api_key: str):
        self.api = PoliticsAndWarAPI(api_key)
        self.tracker = EspionageTracker()
        self.request_delay = 1.0  # Delay between API requests to avoid rate limiting
    
    async def collect_all_alliance_nations(self) -> Dict[str, Any]:
        """Collect all nations that are in alliances"""
        print("🔍 Starting collection of all alliance nations...")
        
        collected_nations = 0
        total_pages = 0
        errors = 0
        
        try:
            page = 1
            while True:
                print(f"📖 Processing page {page}...")
                
                # Fetch nations with alliance filter (alliance_id > 0 means they're in an alliance)
                query = f'''{{
                    nations(
                        first: 500,
                        page: {page}
                    ) {{
                        paginatorInfo {{
                            currentPage
                            lastPage
                            hasMorePages
                        }}
                        data {{
                            id
                            nation_name
                            leader_name
                            alliance_id
                            alliance {{
                                name
                            }}
                            score
                            num_cities
                            espionage_available
                            beige_turns
                            vacation_mode_turns
                            last_active
                        }}
                    }}
                }}'''
                
                result = self.api.query(query)
                
                if 'errors' in result:
                    print(f"❌ Error on page {page}: {result['errors'][0]['message']}")
                    errors += 1
                    break
                
                data = result.get('data', {}).get('nations', {})
                paginator_info = data.get('paginatorInfo', {})
                nations = data.get('data', [])
                
                # Filter for alliance nations only
                alliance_nations = [n for n in nations if n.get('alliance_id', 0) > 0]
                
                print(f"📊 Found {len(alliance_nations)}/{len(nations)} alliance nations on page {page}")
                
                # Store nations and their espionage status
                for nation in alliance_nations:
                    # Add nation to database
                    success = self.tracker.add_nation(nation)
                    
                    if success:
                        # Update espionage status
                        status_data = {
                            'espionage_available': nation.get('espionage_available', True),
                            'beige_turns': nation.get('beige_turns', 0),
                            'vacation_mode_turns': nation.get('vacation_mode_turns', 0),
                            'last_active': nation.get('last_active')
                        }
                        
                        self.tracker.update_espionage_status(nation['id'], status_data)
                        
                        # If espionage is not available, add to monitoring queue
                        if not nation.get('espionage_available', True):
                            reason = "initially_protected"
                            if nation.get('beige_turns', 0) > 0:
                                reason = "beige_protection"
                            elif nation.get('vacation_mode_turns', 0) > 0:
                                reason = "vacation_mode"
                            
                            self.tracker.add_to_monitoring_queue(nation['id'], reason)
                        
                        collected_nations += 1
                
                total_pages = page
                
                # Check if there are more pages
                if not paginator_info.get('hasMorePages', False):
                    break
                
                page += 1
                
                # Rate limiting delay
                await asyncio.sleep(self.request_delay)
                
                # Progress update every 10 pages
                if page % 10 == 0:
                    print(f"🔄 Progress: {page} pages processed, {collected_nations} nations collected")
        
        except Exception as e:
            print(f"💥 Critical error during collection: {e}")
            errors += 1
        
        stats = self.tracker.get_stats()
        
        result = {
            'success': errors == 0,
            'collected_nations': collected_nations,
            'total_pages': total_pages,
            'errors': errors,
            'database_stats': stats,
            'completion_time': datetime.utcnow().isoformat()
        }
        
        print(f"✅ Collection complete!")
        print(f"📈 Nations collected: {collected_nations}")
        print(f"📄 Pages processed: {total_pages}")
        print(f"🔍 Nations being monitored: {stats.get('monitoring_count', 0)}")
        print(f"❌ Errors: {errors}")
        
        return result
    
    async def update_specific_nations(self, nation_ids: List[int]) -> Dict[str, Any]:
        """Update specific nations' espionage status"""
        print(f"🔄 Updating {len(nation_ids)} specific nations...")
        
        updated = 0
        errors = 0
        
        # Process in batches to avoid API limits
        batch_size = 50
        
        for i in range(0, len(nation_ids), batch_size):
            batch = nation_ids[i:i + batch_size]
            
            print(f"📦 Processing batch {i//batch_size + 1}: nations {i+1}-{min(i+batch_size, len(nation_ids))}")
            
            try:
                # Query this batch of nations
                id_list = ','.join(map(str, batch))
                query = f'''{{
                    nations(id: [{id_list}]) {{
                        data {{
                            id
                            nation_name
                            espionage_available
                            beige_turns
                            vacation_mode_turns
                            last_active
                        }}
                    }}
                }}'''
                
                result = self.api.query(query)
                
                if 'errors' in result:
                    print(f"❌ Error in batch: {result['errors'][0]['message']}")
                    errors += 1
                    continue
                
                nations = result.get('data', {}).get('nations', {}).get('data', [])
                
                for nation in nations:
                    # Update espionage status
                    status_data = {
                        'espionage_available': nation.get('espionage_available', True),
                        'beige_turns': nation.get('beige_turns', 0),
                        'vacation_mode_turns': nation.get('vacation_mode_turns', 0),
                        'last_active': nation.get('last_active')
                    }
                    
                    success = self.tracker.update_espionage_status(nation['id'], status_data)
                    
                    if success:
                        updated += 1
                        
                        # Check if espionage became available (potential reset time detection)
                        if nation.get('espionage_available', True):
                            # This might be a reset time - record it
                            reset_time = datetime.utcnow()
                            self.tracker.record_reset_time(
                                nation['id'], 
                                reset_time, 
                                "monitoring_check"
                            )
                            print(f"🎯 Detected potential reset time for {nation.get('nation_name', 'Unknown')}: {reset_time}")
                
                # Rate limiting
                await asyncio.sleep(self.request_delay)
                
            except Exception as e:
                print(f"💥 Error processing batch: {e}")
                errors += 1
        
        return {
            'success': errors == 0,
            'updated_nations': updated,
            'errors': errors,
            'completion_time': datetime.utcnow().isoformat()
        }
    
    async def run_monitoring_cycle(self) -> Dict[str, Any]:
        """Run a monitoring cycle to check nations that need updates"""
        print("🔍 Starting monitoring cycle...")
        
        # Get nations that need to be checked
        nations_to_check = self.tracker.get_nations_to_monitor()
        
        if not nations_to_check:
            print("✅ No nations need monitoring at this time")
            return {'success': True, 'checked_nations': 0, 'message': 'No nations to check'}
        
        print(f"📋 Found {len(nations_to_check)} nations to check")
        
        # Extract nation IDs
        nation_ids = [nation['nation_id'] for nation in nations_to_check]
        
        # Update their status
        result = await self.update_specific_nations(nation_ids)
        
        # Update next check times for nations still protected
        for nation in nations_to_check:
            # Schedule next check in 2 hours
            next_check = datetime.utcnow() + timedelta(hours=2)
            # This would be handled by the update process
        
        print(f"✅ Monitoring cycle complete: {result}")
        return result
