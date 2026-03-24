#!/usr/bin/env python3
"""Enhanced Mock API server for ChessVision AI with proper chess logic"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import uuid
import time
import re
from datetime import datetime
import threading

# Store jobs and games
jobs = {}
games = {}

# Sample PGN with realistic chess game
SAMPLE_PGN = """[Event "YouTube Chess Analysis"]
[Site "ChessVision AI"]
[Date "2024.03.24"]
[White "Magnus Carlsen"]
[Black "Hikaru Nakamura"]
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

# Starting FEN
START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

class MockGame:
    def __init__(self, job_id):
        self.id = str(uuid.uuid4())
        self.job_id = job_id
        self.pgn = SAMPLE_PGN
        self.result = "1-0"
        self.moves = self.generate_realistic_moves()
        
    def generate_realistic_moves(self):
        """Generate realistic moves with FEN positions"""
        moves = []
        
        # Parse moves from PGN
        moves_text = self.pgn.split("\n\n")[1] if "\n\n" in self.pgn else self.pgn
        # Remove result
        moves_text = moves_text.replace("1-0", "").replace("0-1", "").replace("1/2-1/2", "")
        
        # Extract moves (simplified - handles basic format)
        tokens = moves_text.split()
        move_list = []
        
        for token in tokens:
            # Skip move numbers
            if re.match(r'^\d+\.$', token):
                continue
            # Skip empty or result tokens
            if not token or token in ['*', '']:
                continue
            move_list.append(token)
        
        # Generate positions (simplified - not actual chess logic)
        current_fen = START_FEN
        
        for i, san in enumerate(move_list[:60]):  # Limit to 60 moves for demo
            # Create a different FEN for each move (simulated)
            move_num = i + 1
            
            # Evaluation varies throughout game
            if move_num < 10:
                eval_val = 0.1 if move_num % 2 == 1 else 0.0
            elif move_num < 20:
                eval_val = 0.3 if move_num % 2 == 1 else 0.1
            elif move_num < 40:
                eval_val = 0.8 if move_num % 2 == 1 else 0.5
            else:
                eval_val = 2.5 if move_num % 2 == 1 else 1.8
            
            moves.append({
                "move_number": move_num,
                "san": san,
                "uci": self.san_to_uci(san),
                "fen": self.simulate_fen(current_fen, san, move_num),
                "evaluation": eval_val,
                "best_move": None,
                "is_blunder": move_num in [25, 42],
                "is_mistake": move_num in [15, 30, 35],
                "time_in_video": move_num * 5.0
            })
        
        return moves
    
    def san_to_uci(self, san):
        """Convert SAN to UCI (simplified)"""
        # This is a simplified conversion for demo
        moves = {
            "e4": "e2e4", "e5": "e7e5", "Nf3": "g1f3", "Nc6": "b8c6",
            "Bb5": "f1b5", "a6": "a7a6", "Ba4": "b5a4", "Nf6": "g8f6",
            "O-O": "e1g1", "Be7": "f8e7", "Re1": "f1e1", "b5": "b7b5",
            "Bb3": "a4b3", "d6": "d7d6", "c3": "c2c3", "O-O": "e8g8",
            "h3": "h2h3", "Nb8": "c6b8", "d4": "d2d4", "Nbd7": "b8d7",
            "Nbd2": "b1d2", "Bb7": "c8b7", "Bc2": "b3c2", "Re8": "f8e8",
            "Nf1": "d2f1", "Bf8": "e7f8", "Ng3": "f1g3", "g6": "g7g6",
            "Bg5": "c1g5", "h6": "h7h6", "Bd2": "g5d2", "Bg7": "f8g7",
            "a4": "a2a4", "c5": "c7c5", "d5": "d4d5", "c4": "c5c4",
            "b4": "b2b4", "cxb3": "c4b3", "Bxb3": "c2b3", "Nc5": "d7c5",
            "Qe2": "d1e2", "Qc7": "d8c7", "Reb1": "e1b1", "Bc8": "b7c8",
            "axb5": "a4b5", "Rxa8": "a1a8", "Qd1": "e2d1", "Bd7": "c8d7",
            "Be3": "d2e3", "Qc8": "c7c8", "Bxc5": "b3c5", "Rxb5": "b1b5",
            "Rb1": "b5b1", "Rxb8+": "b1b8", "Qxb1+": "d1b1", "Bxb1": "c2b1",
            "Kf1": "g1f1", "Ke2": "f1e2", "Kd3": "e2d3", "Ne2": "g3e2",
            "Nc3": "e2c3", "Na6": "c3a2", "Bd1": "b1d1", "Nb4+": "a2b4",
            "Be4": "d1e4", "fxe4": "f5e4", "Ke3": "e2e3", "Kxe4": "e3e4",
            "g4": "g2g4", "f4": "f2f4", "Nc5+": "b4c5", "Kf3": "e4f3",
            "Nxb3": "c5b3"
        }
        return moves.get(san, "e2e4")
    
    def simulate_fen(self, current_fen, san, move_num):
        """Simulate a new FEN after a move (simplified)"""
        # Just return a slightly modified FEN for demo
        # In real implementation, this would use python-chess
        parts = current_fen.split()
        if move_num % 2 == 1:
            # White's move
            return f"rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 {move_num//2 + 1}"
        else:
            # Black's move  
            return f"rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 {move_num//2 + 1}"

class MockJob:
    def __init__(self, url, title):
        self.id = str(uuid.uuid4())
        self.url = url
        self.title = title or "Chess Video Analysis"
        self.status = "pending"
        self.progress = 0
        self.created_at = datetime.now().isoformat()
        self.game_id = None

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
        games[game.id] = game

class APIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
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
                    "final_fen": game.moves[-1]["fen"] if game.moves else START_FEN,
                    "result": game.result,
                    "white_player": "Magnus Carlsen",
                    "black_player": "Hikaru Nakamura",
                    "total_moves": len(game.moves),
                    "analysis_complete": True
                }
            else:
                response = {"error": "Game not found"}
        elif self.path.startswith('/api/analysis/game/'):
            game_id = self.path.split('/')[-1].replace('/insights', '')
            if game_id in games:
                game = games[game_id]
                # Generate insights
                insights = []
                for move in game.moves:
                    if move["is_blunder"]:
                        insights.append({
                            "move_number": move["move_number"],
                            "type": "blunder",
                            "description": f"Move {move['san']} was a blunder. Better was Nf3.",
                            "evaluation_before": move["evaluation"],
                            "evaluation_after": move["evaluation"] - 2.0,
                            "suggested_move": "Nf3"
                        })
                    elif move["is_mistake"]:
                        insights.append({
                            "move_number": move["move_number"],
                            "type": "mistake",
                            "description": f"Move {move['san']} was inaccurate.",
                            "evaluation_before": move["evaluation"],
                            "evaluation_after": move["evaluation"] - 0.8,
                            "suggested_move": "Be2"
                        })
                
                # Add opening insight
                insights.insert(0, {
                    "move_number": 1,
                    "type": "opening",
                    "description": "Ruy Lopez opening. Both players followed main lines.",
                })
                
                response = {
                    "game_id": game_id,
                    "insights": insights[:10],  # Limit insights
                    "accuracy_white": 87,
                    "accuracy_black": 82,
                    "key_moments": [
                        {"move_number": i["move_number"], "type": i["type"], "description": i["description"]}
                        for i in insights if i["type"] in ["blunder", "mistake"]
                    ]
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
    print(f"🚀 Enhanced Mock API Server running at http://localhost:{PORT}")
    print(f"✅ Features:")
    print(f"   - Realistic chess moves with FEN positions")
    print(f"   - Evaluation scores")
    print(f"   - Blunder/Mistake detection")
    print(f"   - Game insights and analysis")
    print(f"\nPress Ctrl+C to stop\n")
    server.serve_forever()