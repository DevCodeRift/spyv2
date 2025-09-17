#!/usr/bin/env python3
"""
Minimal health server for Railway - no dependencies on main application
"""

import os
import sys

# Check if we need to run health-only mode
if len(sys.argv) > 1 and sys.argv[1] == '--health-only':
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    
    @app.route('/health')
    def health():
        return jsonify({
            "status": "healthy",
            "service": "Politics & War Discord Bot",
            "mode": "health-only"
        }), 200
    
    @app.route('/')
    def root():
        return jsonify({
            "status": "health-only mode",
            "message": "Add environment variables to enable full functionality"
        })
    
    port = int(os.getenv('PORT', 5000))
    print(f"🏥 Health-only server starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
    sys.exit(0)

# Otherwise, try to run the full application
try:
    # Import main application
    from main import main
    import asyncio
    
    # Run the main application
    asyncio.run(main())
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🏥 Falling back to health-only mode")
    
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    
    @app.route('/health')
    def health():
        return jsonify({
            "status": "healthy",
            "service": "Politics & War Discord Bot",
            "mode": "health-fallback",
            "error": str(e)
        }), 200
    
    @app.route('/')
    def root():
        return jsonify({
            "status": "health-fallback mode",
            "message": "Import error occurred, running minimal health server",
            "error": str(e)
        })
    
    port = int(os.getenv('PORT', 5000))
    print(f"🏥 Health fallback server starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

except Exception as e:
    print(f"❌ Application error: {e}")
    print("🏥 Falling back to health-only mode")
    
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    
    @app.route('/health')
    def health():
        return jsonify({
            "status": "healthy",
            "service": "Politics & War Discord Bot",
            "mode": "health-emergency",
            "error": str(e)
        }), 200
    
    @app.route('/')
    def root():
        return jsonify({
            "status": "health-emergency mode",
            "message": "Application error occurred, running minimal health server",
            "error": str(e)
        })
    
    port = int(os.getenv('PORT', 5000))
    print(f"🏥 Health emergency server starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
