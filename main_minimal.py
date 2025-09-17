#!/usr/bin/env python3
"""
Minimal main.py for Railway deployment testing
"""

import os
from flask import Flask, jsonify

def create_app():
    app = Flask(__name__)
    
    @app.route('/health')
    def health():
        return jsonify({
            "status": "healthy",
            "service": "Politics & War Discord Bot",
            "mode": "minimal-test"
        }), 200
    
    @app.route('/')
    def root():
        return jsonify({
            "status": "minimal test mode",
            "message": "This is a minimal test to verify Railway deployment"
        })
    
    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    print(f"🏥 Minimal test server starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
