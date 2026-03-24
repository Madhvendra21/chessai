#!/usr/bin/env python3
"""Enhanced Mock API server with multiple sample games"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import uuid
import time
import re
import hashlib
from datetime import datetime
import threading

# Store jobs and games
jobs = {}
games = {}

# Multiple sample games
SAMPLE_GAMES = [
    {
        "name": "Famous Immortal Game",
        "white": "Adolf Anderssen",
        "black": "Lionel Kieseritzky",
        "result": "1-0",
        "pgn": """[Event "The Immortal Game"]
[Site "London"]
[Date "1851.06.21"]
[White "Adolf Anderssen"]
[Black "Lionel Kieseritzky"]
[Result "1-0"]

1. e4 e5 2. f4 exf4 3. Bc4 Qh4+ 4. Kf1 b5 5. Bxb5 Nf6 6. Nf3 Qh6 7. d3 Nh5
8. Nh4 Qg5 9. Nf5 c6 10. g4 Nf6 11. Rg1 cxb5 12. h4 Qg6 13. h5 Qg5 14. Qf3
Ng8 15. Bxf4 Qf6 16. Nc3 Bc5 17. Nd5 Qxb2 18. Bd6 Bxg1 19. e5 Qxa1+ 20. Ke2
Na6 21. Nxg7+ Kd8 22. Qf6+ Nxf6 23. Be7# 1-0"""
    },
    {
        "name": "Opera Game",
        "white": "Paul Morphy",
        "black": "Duke Karl / Count Isouard",
        "result": "1-0",
        "pgn": """[Event "Opera Game"]
[Site "Paris"]
[Date "1858"]
[White "Paul Morphy"]
[Black "Duke Karl / Count Isouard"]
[Result "1-0"]

1. e4 e5 2. Nf3 d6 3. d4 Bg4 4. dxe5 Bxf3 5. Qxf3 dxe5 6. Bc4 Nf6 7. Qb3 Qe7
8. Nc3 c6 9. Bg5 b5 10. Nxb5 cxb5 11. Bxb5+ Nbd7 12. O-O-O Rd8 13. Rxd7 Rxd7
14. Rd1 Qe6 15. Bxd7+ Nxd7 16. Qb8+ Nxb8 17. Rd8# 1-0"""
    },
    {
        "name": "World Championship 2023",
        "white": "Ding Liren",
        "black": "Ian Nepomniachtchi",
        "result": "1-0",
        "pgn": """[Event "World Championship 2023"]
[Site "Astana"]
[Date "2023.04.30"]
[White "Ding Liren"]
[Black "Ian Nepomniachtchi"]
[Result "1-0"]

1. d4 Nf6 2. c4 e6 3. Nf3 d5 4. Nc3 Be7 5. Bf4 O-O 6. e3 Nbd7 7. c5 c6
8. Bd3 b6 9. b4 a5 10. a3 Ba6 11. O-O Qc8 12. Qe2 Bxd3 13. Qxd3 Qb7
14. Rab1 axb4 15. axb4 bxc5 16. bxc5 Ra3 17. Rb3 Rfa8 18. Rfb1 Qc8
19. h3 h6 20. Ne5 Nxe5 21. Bxe5 Nd7 22. Bg3 Bd8 23. Kh2 R3a6 24. Qe2 Nf6
25. Qd1 Qa8 26. Qd3 Qa7 27. Rb8 Rxb8 28. Rxb8 Kh7 29. Qb1 Qa2 30. Qb3 Qa7
31. Bd6 Ng8 32. Ne2 Bc7 33. Bxc7 Qxc7 34. Rb7 Qd8 35. Qb4 Nf6 36. Nf4 g5
37. Nd3 Nd7 38. Qb1+ Kg7 39. Qb4 Kg6 40. g4 h5 41. Kg3 hxg4 42. hxg4 Ra7
43. Rxa7 Qxa7 44. Qb8 Qa3 45. Qe8+ Kh6 46. Qxf7 Qc1 47. Nc5 Nxc5 48. dxc5
Qe1+ 49. Kg2 Qxe3 50. Qf6+ Kh7 51. Qf7+ Kh6 52. Qf6+ Kh7 53. Qe7+ Kg6
54. Qe8+ Kg7 55. Qd7+ Kf6 56. Qd8+ Kg6 57. Qg8+ Kh6 58. Qh8+ Kg6
59. Qg8+ Kh6 60. Qh8+ Kg6 61. Qg8+ 1/2-1/2"""
    },
    {
        "name": "Carlsen vs Caruana",
        "white": "Magnus Carlsen",
        "black": "Fabiano Caruana",
        "result": "1-0",
        "pgn": """[Event "World Championship 2018"]
[Site "London"]
[Date "2018.11.28"]
[White "Magnus Carlsen"]
[Black "Fabiano Caruana"]
[Result "1-0"]

1. c4 e6 2. Nf3 d5 3. g3 Nf6 4. Bg2 d4 5. O-O c5 6. e3 Nc6 7. exd4 cxd4
8. d3 Bd6 9. Bg5 O-O 10. Nbd2 h6 11. Bxf6 Qxf6 12. Ne4 Qe7 13. Nxd6 Qxd6
14. a3 b6 15. Rb1 Bb7 16. b4 Rfd8 17. Qe2 Rac8 18. Rfc1 Ne7 19. c5 bxc5
20. bxc5 Rxc5 21. Rxc5 Qxc5 22. Rxb7 Qc1+ 23. Bf1 Nc6 24. Qe4 g6 25. Qe2
Kg7 26. Rb5 e5 27. Re5 Qc3 28. Bg2 Rd5 29. Rxd5 Nb4 30. axb4 Qxa1+
31. Bf1 Qxb4 32. Nxe5 Qb7 33. Qf3 Qe7 34. Nd7 a5 35. Qc6 a4 36. Nc5 a3
37. Nxa4 Qa7 38. Nb6 Qa5 39. Nc4 Qc5 40. Qxc5 1-0"""
    }
]

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

class MockGame:
    def __init__(self, job_id, game_index):
        self.id = str(uuid.uuid4())
        self.job_id = job_id
        
        # Select game based on index
        game_data = SAMPLE_GAMES[game_index % len(SAMPLE_GAMES)]
        
        self.name = game_data["name"]
        self.white = game_data["white"]
        self.black = game_data["black"]
        self.result = game_data["result"]
        self.pgn = game_data["pgn"]
        self.moves = self.parse_moves()
        
    def parse_moves(self):
        """Parse moves from PGN"""
        moves = []
        
        # Extract moves
        moves_text = self.pgn.split("\n\n")[1] if "\n\n" in self.pgn else self.pgn
        moves_text = moves_text.replace("1-0", "").replace("0-1", "").replace("1/2-1/2", "")
        
        tokens = moves_text.split()
        move_list = []
        
        for token in tokens:
            if re.match(r'^\d+\.$', token):
                continue
            if not token or token in ['*', '']:
                continue
            move_list.append(token)
        
        # Generate moves with varying evaluations
        for i, san in enumerate(move_list):
            move_num = i + 1
            
            # Create varied evaluations
            if i < len(move_list) * 0.2:
                eval_val = 0.1 if move_num % 2 == 1 else 0.0
            elif i < len(move_list) * 0.5:
                eval_val = 0.3 if move_num % 2 == 1 else 0.1
            elif i < len(move_list) * 0.8:
                eval_val = 0.8 if move_num % 2 == 1 else 0.4
            else:
                eval_val = 2.5 if move_num % 2 == 1 else 1.5
            
            moves.append({
                "move_number": move_num,
                "san": san,
                "uci": self.san_to_uci(san),
                "fen": self.simulate_fen(move_num),
                "evaluation": eval_val,
                "best_move": None,
                "is_blunder": move_num in [15, 28, 35],
                "is_mistake": move_num in [8, 18, 25, 40],
                "time_in_video": move_num * 4.5
            })
        
        return moves
    
    def san_to_uci(self, san):
        """Convert SAN to simplified UCI"""
        # Simplified mapping for demo
        return "e2e4"
    
    def simulate_fen(self, move_num):
        """Generate different FENs for visual variety"""
        # Return different positions based on move number
        if move_num < 10:
            return "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
        elif move_num < 20:
            return "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4"
        elif move_num < 40:
            return "r1bq1rk1/ppp2ppp/2n2n2/1B1pp3/1b2P3/2NP1N2/PPP2PPP/R1BQ1RK1 w - - 0 8"
        else:
            return "2kr3r/ppp2ppp/2n5/1B1Pp3/1b2P3/2N2N2/PPP2qPP/R2Q1K1R w - - 0 14"

class MockJob:
    def __init__(self, url, title):
        self.id = str(uuid.uuid4())
        self.url = url
        self.title = title or "Chess Video Analysis"
        self.status = "pending"
        self.progress = 0
        self.created_at = datetime.now().isoformat()
        self.game_id = None
        # Use URL hash to determine which game to show
        self.game_index = int(hashlib.md5(url.encode()).hexdigest(), 16) % len(SAMPLE_GAMES)

def simulate_job_processing(job_id):
    """Simulate job processing"""
    time.sleep(3)
    if job_id in jobs:
        jobs[job_id].status = "downloading"
        jobs[job_id].progress = 25
        
    time.sleep(3)
    if job_id in jobs:
        jobs[job_id].status = "processing"
        jobs[job_id].progress = 60
        
    time.sleep(4)
    if job_id in jobs:
        game = MockGame(job_id, jobs[job_id].game_index)
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
                    "white_player": game.white,
                    "black_player": game.black,
                    "total_moves": len(game.moves),
                    "analysis_complete": True
                }
            else:
                response = {"error": "Game not found"}
        elif self.path.startswith('/api/analysis/game/'):
            game_id = self.path.split('/')[-1].replace('/insights', '')
            if game_id in games:
                game = games[game_id]
                insights = []
                
                for move in game.moves:
                    if move["is_blunder"]:
                        insights.append({
                            "move_number": move["move_number"],
                            "type": "blunder",
                            "description": f"{move['san']} was a blunder. Consider alternative moves.",
                        })
                    elif move["is_mistake"]:
                        insights.append({
                            "move_number": move["move_number"],
                            "type": "mistake",
                            "description": f"{move['san']} was inaccurate.",
                        })
                
                insights.insert(0, {
                    "move_number": 1,
                    "type": "opening",
                    "description": f"{game.name} - Famous historical game",
                })
                
                response = {
                    "game_id": game_id,
                    "insights": insights[:8],
                    "accuracy_white": 85 + (hash(game_id) % 10),
                    "accuracy_black": 80 + (hash(game_id) % 12),
                    "key_moments": [
                        {"move_number": i["move_number"], "type": i["type"], "description": i["description"]}
                        for i in insights if i["type"] in ["blunder", "mistake"]
                    ][:5]
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
    print(f"🚀 Mock API Server v3 running at http://localhost:{PORT}")
    print(f"✨ Features:")
    print(f"   - 4 different famous chess games")
    print(f"   - Games selected based on video URL")
    print(f"   - Realistic evaluations and insights")
    print(f"\nPress Ctrl+C to stop\n")
    server.serve_forever()