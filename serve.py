#!/usr/bin/env python3
"""Simple HTTP server for ChessVision AI"""
import http.server
import socketserver
import webbrowser
import os

PORT = 8080

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

os.chdir('/Users/madhvendra.singh/mahichess/chessvision-ai')

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print(f"\n🚀 ChessVision AI is running!")
    print(f"📍 Local URL: http://localhost:{PORT}")
    print(f"🌐 Open this URL in your browser")
    print(f"\nPress Ctrl+C to stop the server\n")
    
    # Try to open browser automatically
    try:
        webbrowser.open(f'http://localhost:{PORT}')
        print("✅ Browser opened automatically!")
    except:
        print("⚠️  Please open http://localhost:8080 manually in your browser")
    
    httpd.serve_forever()