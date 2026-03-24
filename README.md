# ChessVision AI

Transform chess videos into interactive game analysis with AI-powered piece detection and Stockfish evaluation.

## Features

- **Video Processing**: Upload videos or provide YouTube URLs
- **AI Piece Detection**: Computer vision pipeline using YOLO
- **Move Extraction**: Automatic board state reconstruction
- **Stockfish Analysis**: Deep position evaluation and blunder detection
- **Interactive Viewer**: Browse moves, evaluation graphs, and insights

## Quick Start

### Using Docker (Recommended)

```bash
# Clone and setup
git clone <repository>
cd chessvision-ai

# Start all services
docker-compose up --build

# Access the app
# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manual Setup

```bash
# 1. Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# 2. Start PostgreSQL and Redis
# (Install via your package manager or use Docker)

# 3. Initialize database
cd backend
python -c "from db.database import init_db; import asyncio; asyncio.run(init_db())"

# 4. Start backend
uvicorn api.main:app --reload

# 5. Start Celery worker (new terminal)
celery -A workers.tasks worker --loglevel=info

# 6. Start frontend (new terminal)
cd ../frontend
npm run dev
```

## Architecture

```
Video Upload/URL → FastAPI → Celery Queue
                        ↓
                  Frame Extraction (OpenCV)
                        ↓
                  Piece Detection (YOLO)
                        ↓
                  Board State Reconstruction
                        ↓
                  Move Detection & Validation
                        ↓
                  Stockfish Analysis
                        ↓
                  PostgreSQL Storage
                        ↓
                  React Frontend
```

## API Endpoints

- `POST /api/jobs/upload` - Upload video file
- `POST /api/jobs/from-url` - Process video from URL
- `GET /api/jobs/{id}` - Get job status
- `GET /api/games/{id}` - Get game with moves
- `GET /api/analysis/game/{id}` - Get analysis insights

## Configuration

Edit `.env` file to configure:
- Database connection
- Redis URL
- Stockfish path and depth
- Frame extraction rate
- Confidence thresholds

## Requirements

- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- Stockfish 16+

## Development

### Backend Structure
```
backend/
├── api/           # FastAPI routes
├── core/          # Business logic
├── db/            # Database models
├── workers/       # Celery tasks
└── schemas/       # Pydantic models
```

### CV Pipeline
```
cv-pipeline/
├── detector/      # Board/piece detection
└── utils/         # Helper functions
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/  # React components
│   ├── pages/       # Page components
│   └── api/         # API client
```

## License

MIT