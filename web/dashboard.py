"""
Web dashboard for Politics & War Discord Bot
Provides a web interface for bot control and monitoring
"""

from flask import Flask, render_template, request, jsonify
import os
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
                # Start monitoring in background
                import asyncio
                asyncio.create_task(self.espionage_monitor.start_24_7_monitoring())
                return jsonify({"success": True, "message": "Monitoring started"})
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
                result = loop.run_until_complete(self.espionage_monitor.initial_data_collection())
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
