#!/usr/bin/env python3
"""Mock API server for ChessVision AI demo"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import uuid
import time
from datetime import datetime
import threading

# Store jobs in memory
jobs = {}

class MockJob:
    def __init__(self, url, title):
        self.id = str(uuid.uuid4())
        self.url = url
        self.title = title or "Chess Video Analysis"
        self.status = "pending"
        self.progress = 0
        self.created_at = datetime.now().isoformat()
        self.game_id = None
        
class MockGame:
    def __init__(self, job_id):
        self.id = str(uuid.uuid4())
        self.job_id = job_id
        self.pgn = """[Event "YouTube Chess Analysis"]
[Site "ChessVision AI"]
[Date "2024.03.24"]
[White "Player 1"]
[Black "Player 2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6
8. c3 O-O 9. h3 Nb8 10. d4 Nbd7 11. Nbd2 Bb7 12. Bc2 Re8 13. Nf1 Bf8
14. Ng3 g6 15. Bg5 h6 16. Bd2 Bg7 17. a4 c5 18. d5 c4 19. b4 cxb3
20. Bxb3 Nc5 21. Bc2 Qc7 22. Qe2 Reb8 23. Reb1 Bc8 24. axb5 axb5
25. Rxa8 Rxa8 26. Qd1 Bd7 27. Be3 Qc8 28. Bxc5 Qxc5 29. Rxb5 Qc7
30. Rb1 Rb8 31. Rxb8+ Qxb8 32. Qb1 Qxb1+ 33. Bxb1 Bb5 34. Bc2 Bd7
35. Kf1 Kf8 36. Ke2 Ke7 37. Kd3 Kd8 38. c4 Ne8 39. Ne2 Nc7 40. Nc3
Na6 41. Bd1 Nb4+ 42. Ke2 Bc8 43. Be4 f5 44. exf5 gxf5 45. Bb1 Bf6
46. Na2 Na6 47. Bc2 Nc5 48. Nb4 Bb7 49. Nc6+ Ke8 50. Nfd4 Bxd4
51. Nxd4 e4 52. Bb1 Kd8 53. Bxe4 fxe4 54. Ke3 Bc8 55. Kxe4 Kd7
56. g4 Nb7 57. f4 Nc5+ 58. Kf3 Nb3 59. Nxb3 1-0"""
        self.moves = self.parse_moves()
        self.result = "1-0"
        
    def parse_moves(self):
        # Simplified move parsing for demo
        moves = []
        move_text = self.pgn.split("\n\n")[1] if "\n\n" in self.pgn else self.pgn
        tokens = move_text.split()
        
        move_num = 0
        for token in tokens:
            if "." in token:
                continue
            if token in ["1-0", "0-1", "1/2-1/2", "*"]:
                break
            move_num += 1
            moves.append({
                "move_number": move_num,
                "san": token,
                "uci": "e2e4",  # Simplified
                "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                "evaluation": 0.0 if move_num % 2 == 0 else 0.2,
                "is_blunder": move_num == 25,
                "is_mistake": move_num in [10, 15, 30]
            })
        return moves

def simulate_job_processing(job_id):
    """Simulate job processing in background"""
    time.sleep(2)
    if job_id in jobs:
        jobs[job_id].status = "downloading"
        jobs[job_id].progress = 20
        
    time.sleep(2)
    if job_id in jobs:
        jobs[job_id].status = "processing"
        jobs[job_id].progress = 50
        
    time.sleep(3)
    if job_id in jobs:
        game = MockGame(job_id)
        jobs[job_id].game_id = game.id
        jobs[job_id].status = "completed"
        jobs[job_id].progress = 100
        # Store game
        games[game.id] = game

# Store games
games = {}

class APIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress logs
        pass
        
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if self.path == '/api/':
            response = {
                "message": "ChessVision AI API",
                "version": "1.0.0",
                "status": "online"
            }
        elif self.path == '/api/jobs/':
            response = [{
                "id": job.id,
                "title": job.title,
                "status": job.status,
                "progress": job.progress,
                "source": "youtube",
                "created_at": job.created_at,
                "game_id": job.game_id
            } for job in jobs.values()]
        elif self.path.startswith('/api/jobs/'):
            job_id = self.path.split('/')[-1]
            if job_id in jobs:
                job = jobs[job_id]
                response = {
                    "id": job.id,
                    "title": job.title,
                    "status": job.status,
                    "progress": job.progress,
                    "source": "youtube",
                    "created_at": job.created_at,
                    "game_id": job.game_id
                }
            else:
                response = {"error": "Job not found"}
        elif self.path.startswith('/api/games/'):
            game_id = self.path.split('/')[-1]
            if game_id in games:
                game = games[game_id]
                response = {
                    "id": game.id,
                    "job_id": game.job_id,
                    "pgn": game.pgn,
                    "moves": game.moves,
                    "result": game.result,
                    "total_moves": len(game.moves),
                    "analysis_complete": True
                }
            else:
                response = {"error": "Game not found"}
        else:
            response = {"error": "Not found"}
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode())
        except:
            data = {}
        
        if self.path == '/api/jobs/from-url':
            url = data.get('url', '')
            title = data.get('title', 'YouTube Video')
            
            job = MockJob(url, title)
            jobs[job.id] = job
            
            # Start background processing
            thread = threading.Thread(target=simulate_job_processing, args=(job.id,))
            thread.daemon = True
            thread.start()
            
            response = {
                "id": job.id,
                "title": job.title,
                "status": job.status,
                "progress": job.progress,
                "source": "youtube",
                "created_at": job.created_at
            }
        else:
            response = {"error": "Not found"}
        
        self.wfile.write(json.dumps(response).encode())

if __name__ == '__main__':
    PORT = 8000
    server = HTTPServer(('localhost', PORT), APIHandler)
    print(f"🚀 Mock API Server running at http://localhost:{PORT}")
    print(f"📡 API endpoints:")
    print(f"   GET  http://localhost:{PORT}/api/")
    print(f"   POST http://localhost:{PORT}/api/jobs/from-url")
    print(f"   GET  http://localhost:{PORT}/api/jobs/")
    print(f"   GET  http://localhost:{PORT}/api/jobs/<id>")
    print(f"   GET  http://localhost:{PORT}/api/games/<id>")
    print(f"\nPress Ctrl+C to stop\n")
    server.serve_forever()