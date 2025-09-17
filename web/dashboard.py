"""
Web dashboard for Politics & War Discord Bot
Provides a web interface for bot control and monitoring
"""

from flask import Flask, render_template, request, jsonify
import os
import sqlite3
import asyncio
from threading import Thread
from api.pnw_api import PoliticsAndWarAPI
from utils.espionage_monitor import EspionageMonitor
from database.espionage_tracker import EspionageTracker

class WebDashboard:
    """Web dashboard for bot control"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
        
        # Initialize API (defensive initialization)
        api_key = os.getenv('PNW_API_KEY')
        if api_key:
            try:
                self.pnw_api = PoliticsAndWarAPI(api_key)
                # Initialize monitoring system
                self.espionage_tracker = EspionageTracker()
                self.espionage_monitor = EspionageMonitor(api_key)
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize monitoring system: {e}")
                self.pnw_api = None
                self.espionage_tracker = None
                self.espionage_monitor = None
        else:
            print("⚠️ Warning: PNW_API_KEY not set, monitoring features disabled")
            self.pnw_api = None
            self.espionage_tracker = None
            self.espionage_monitor = None
        
        # Set up routes
        self.setup_routes()
    
    def setup_routes(self):
        """Set up web routes"""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard page"""
            return render_template('dashboard.html')
        
        @self.app.route('/health')
        def health():
            """Health check endpoint for Railway deployment"""
            return jsonify({
                "status": "healthy",
                "service": "Politics & War Discord Bot",
                "version": "2.0"
            }), 200
        
        @self.app.route('/api/nation/<nation_name>')
        def api_nation(nation_name):
            """API endpoint to get nation info"""
            if not self.pnw_api:
                return jsonify({"error": "API not initialized - check PNW_API_KEY"}), 503
            try:
                result = self.pnw_api.search_nations(name=nation_name)
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/gameinfo')
        def api_gameinfo():
            """API endpoint to get game info"""
            if not self.pnw_api:
                return jsonify({"error": "API not initialized - check PNW_API_KEY"}), 503
            try:
                result = self.pnw_api.get_game_info()
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/spy/<nation_name>')
        def api_spy_info(nation_name):
            """Get spy information for a nation"""
            if not self.pnw_api:
                return jsonify({"error": "API not initialized - check PNW_API_KEY"}), 503
            try:
                # First find the nation
                search_result = self.pnw_api.search_nations(name=nation_name)
                if 'errors' in search_result or not search_result.get('data', {}).get('nations', {}).get('data', []):
                    return jsonify({'error': f'Nation {nation_name} not found'})
                
                nation_data = search_result['data']['nations']['data'][0]
                nation_id = nation_data['id']
                
                # Get spy activity
                spy_result = self.pnw_api.get_spy_activity(nation_id)
                espionage_result = self.pnw_api.check_espionage_status(nation_id)
                
                return jsonify({
                    'spy_activity': spy_result,
                    'espionage_status': espionage_result
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/spy/me')
        def api_my_spy_info():
            """Get spy information for the API key owner"""
            try:
                spy_result = self.pnw_api.get_spy_activity()
                espionage_result = self.pnw_api.check_espionage_status()
                
                return jsonify({
                    'spy_activity': spy_result,
                    'espionage_status': espionage_result
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/wars')
        def api_wars():
            """Get active wars"""
            if not self.pnw_api:
                return jsonify({"error": "API not initialized - check PNW_API_KEY"}), 503
            try:
                nation_name = request.args.get('nation')
                if nation_name:
                    # Search for specific nation
                    search_result = self.pnw_api.search_nations(name=nation_name)
                    if 'errors' in search_result or not search_result.get('data', {}).get('nations', {}).get('data', []):
                        return jsonify({'error': f'Nation {nation_name} not found'})
                    
                    nation_data = search_result['data']['nations']['data'][0]
                    nation_id = nation_data['id']
                    result = self.pnw_api.get_active_wars(nation_id)
                else:
                    # Get wars for API key owner
                    result = self.pnw_api.get_active_wars()
                
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/monitor/status')
        def api_monitor_status():
            """Get monitoring system status"""
            if not self.espionage_monitor:
                return jsonify({"error": "Monitoring system not initialized - check PNW_API_KEY"}), 503
            try:
                stats = self.espionage_monitor.get_monitoring_stats()
                return jsonify(stats)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/monitor/start', methods=['POST'])
        def api_start_monitoring():
            """Start the espionage monitoring system"""
            if not self.espionage_monitor:
                return jsonify({"error": "Monitoring system not initialized - check PNW_API_KEY"}), 503
            try:
                # Start monitoring in background using a new event loop
                import asyncio
                import threading
                
                def start_monitoring():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.espionage_monitor.start_24_7_monitoring())
                
                # Start in a separate thread
                monitoring_thread = threading.Thread(target=start_monitoring, daemon=True)
                monitoring_thread.start()
                
                return jsonify({"success": True, "message": "Monitoring started in background"})
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/monitor/test-check', methods=['POST'])
        def api_test_check():
            """Test monitoring by checking a few nations"""
            if not self.espionage_monitor:
                return jsonify({"error": "Monitoring system not initialized - check PNW_API_KEY"}), 503
            try:
                # Get a few nations to test
                nations = self.espionage_tracker.get_nations_needing_monitoring()[:5]
                
                if not nations:
                    return jsonify({"message": "No nations need monitoring", "nations_checked": 0})
                
                # Test check a few nations
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                results = []
                for nation in nations:
                    try:
                        result = loop.run_until_complete(
                            self.espionage_monitor.check_nation_espionage_status(nation['id'])
                        )
                        results.append({
                            'nation_id': nation['id'],
                            'nation_name': nation['nation_name'],
                            'result': result
                        })
                    except Exception as e:
                        results.append({
                            'nation_id': nation['id'],
                            'nation_name': nation['nation_name'],
                            'error': str(e)
                        })
                
                loop.close()
                
                return jsonify({
                    "success": True,
                    "message": f"Tested {len(results)} nations",
                    "results": results
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/monitor/collect', methods=['POST'])
        def api_collect_nations():
            """Trigger nation collection"""
            if not self.espionage_monitor:
                return jsonify({"error": "Monitoring system not initialized - check PNW_API_KEY"}), 503
            try:
                # Start collection in background
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.espionage_monitor.index_all_nations())
                loop.close()
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/monitor/resets')
        def api_reset_times():
            """Get reset time report"""
            if not self.espionage_monitor:
                return jsonify({"error": "Monitoring system not initialized - check PNW_API_KEY"}), 503
            try:
                alliance_id = request.args.get('alliance_id')
                if alliance_id:
                    alliance_id = int(alliance_id)
                
                # Get report synchronously
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                report = loop.run_until_complete(self.espionage_monitor.get_reset_time_report(alliance_id))
                loop.close()
                
                return jsonify(report)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/monitor/check/<int:nation_id>', methods=['POST'])
        def api_manual_check(nation_id):
            """Manually check a nation's espionage status"""
            if not self.espionage_monitor:
                return jsonify({"error": "Monitoring system not initialized - check PNW_API_KEY"}), 503
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.espionage_monitor.manual_check_nation(nation_id))
                loop.close()
                
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        # Database viewing endpoints
        @self.app.route('/api/database/nations')
        def api_get_nations():
            """Get all indexed nations"""
            if not self.espionage_tracker:
                return jsonify({"error": "Database not initialized"}), 503
            try:
                limit = request.args.get('limit', 50, type=int)
                offset = request.args.get('offset', 0, type=int)
                alliance_id = request.args.get('alliance_id', type=int)
                
                if alliance_id:
                    nations = self.espionage_tracker.get_alliance_nations(alliance_id)
                else:
                    # Get all nations with pagination
                    with sqlite3.connect(self.espionage_tracker.db_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute('''
                            SELECT id, nation_name, alliance_id, alliance_name, 
                                   last_updated, is_active
                            FROM nations 
                            ORDER BY id DESC 
                            LIMIT ? OFFSET ?
                        ''', (limit, offset))
                        
                        columns = [description[0] for description in cursor.description]
                        nations = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                return jsonify({
                    "nations": nations,
                    "count": len(nations),
                    "limit": limit,
                    "offset": offset
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/database/stats')
        def api_get_database_stats():
            """Get database statistics"""
            if not self.espionage_tracker:
                return jsonify({"error": "Database not initialized"}), 503
            try:
                with sqlite3.connect(self.espionage_tracker.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Total nations
                    cursor.execute('SELECT COUNT(*) FROM nations')
                    total_nations = cursor.fetchone()[0]
                    
                    # Active nations
                    cursor.execute('SELECT COUNT(*) FROM nations WHERE is_active = 1')
                    active_nations = cursor.fetchone()[0]
                    
                    # Nations by alliance
                    cursor.execute('''
                        SELECT alliance_id, alliance_name, COUNT(*) as count 
                        FROM nations 
                        WHERE alliance_id IS NOT NULL AND is_active = 1
                        GROUP BY alliance_id, alliance_name 
                        ORDER BY count DESC 
                        LIMIT 10
                    ''')
                    top_alliances = [dict(zip(['alliance_id', 'alliance_name', 'count'], row)) 
                                   for row in cursor.fetchall()]
                    
                    # Recent espionage checks
                    cursor.execute('SELECT COUNT(*) FROM espionage_status WHERE checked_at > datetime("now", "-24 hours")')
                    recent_checks = cursor.fetchone()[0]
                    
                    # Reset times found
                    cursor.execute('SELECT COUNT(*) FROM reset_times')
                    reset_times_found = cursor.fetchone()[0]
                
                return jsonify({
                    "total_nations": total_nations,
                    "active_nations": active_nations,
                    "top_alliances": top_alliances,
                    "recent_checks_24h": recent_checks,
                    "reset_times_found": reset_times_found
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/database/recent-activity')
        def api_get_recent_activity():
            """Get recent database activity"""
            if not self.espionage_tracker:
                return jsonify({"error": "Database not initialized"}), 503
            try:
                limit = request.args.get('limit', 20, type=int)
                
                with sqlite3.connect(self.espionage_tracker.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Recent espionage checks
                    cursor.execute('''
                        SELECT es.nation_id, n.nation_name, n.alliance_name,
                               es.espionage_available, es.checked_at
                        FROM espionage_status es
                        JOIN nations n ON es.nation_id = n.id
                        ORDER BY es.checked_at DESC
                        LIMIT ?
                    ''', (limit,))
                    
                    columns = [description[0] for description in cursor.description]
                    recent_activity = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                return jsonify({
                    "recent_activity": recent_activity,
                    "count": len(recent_activity)
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    
    def run_flask_app(self):
        """Run the Flask app in a separate thread"""
        host = os.getenv('WEB_HOST', '0.0.0.0')
        # Railway uses PORT environment variable
        port = int(os.getenv('PORT', os.getenv('WEB_PORT', 5000)))
        debug = os.getenv('DEBUG', 'True').lower() == 'true'
        
        self.app.run(host=host, port=port, debug=debug, use_reloader=False)
    
    async def start(self):
        """Start the web dashboard"""
        print("Starting web dashboard...")
        
        # Run Flask in a separate thread
        flask_thread = Thread(target=self.run_flask_app, daemon=True)
        flask_thread.start()
        
        print(f"Web dashboard started on http://{os.getenv('WEB_HOST', '0.0.0.0')}:{int(os.getenv('PORT', os.getenv('WEB_PORT', 5000)))}")
        
        # Keep the async function running
        while True:
            await asyncio.sleep(60)  # Check every minute
