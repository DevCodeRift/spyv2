#!/usr/bin/env python3
"""
Simple health server for Railway deployment
Only runs Flask for health checks without requiring environment variables
"""

from flask import Flask, jsonify
import os

def create_health_app():
    """Create a minimal Flask app with just health endpoint"""
    app = Flask(__name__)
    
    @app.route('/health')
    def health():
        """Health check endpoint for Railway deployment"""
        return jsonify({
            "status": "healthy",
            "service": "Politics & War Discord Bot",
            "version": "2.0",
            "mode": "health-only"
        }), 200
    
    @app.route('/')
    def index():
        """Root endpoint"""
        return jsonify({
            "service": "Politics & War Discord Bot",
            "status": "health-only mode",
            "message": "Set DISCORD_TOKEN and PNW_API_KEY to enable full functionality"
        })
    
    return app

def main():
    """Run the health server"""
    app = create_health_app()
    
    # Railway uses PORT environment variable
    port = int(os.getenv('PORT', 5000))
    host = '0.0.0.0'
    
    print(f"🏥 Health server starting on {host}:{port}")
    print("🔗 Health check available at /health")
    
    app.run(host=host, port=port, debug=False)

if __name__ == "__main__":
    main()
