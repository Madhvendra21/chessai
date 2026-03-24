# Deployment Guide

## GitHub Repository Setup

The repository has been created at `https://github.com/Chauhan27Mahi/chessai.git`

To push your code:

```bash
cd /Users/madhvendra.singh/mahichess/chessvision-ai

# Configure git (if not done)
git config user.email "your@email.com"
git config user.name "Your Name"

# The repository is already initialized and committed
# Just push to GitHub:
git push -u origin main
```

**Note**: If the repository doesn't exist on GitHub yet, you need to:
1. Create it at https://github.com/new
2. Name it "chessai"
3. Make it public or private as preferred
4. Then run the push command above

## Vercel Deployment

### Frontend (React)

1. Go to https://vercel.com and sign in with GitHub
2. Click "Add New Project"
3. Import the `chessai` repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add Environment Variables:
   ```
   VITE_API_URL=https://your-backend-url.vercel.app/api
   ```
6. Deploy!

### Backend (FastAPI)

**Important**: Vercel has limitations for Python backends:
- No long-running processes (Celery won't work)
- No persistent filesystem
- 10s timeout on API routes
- Stockfish must be installed in build

For production, consider these alternatives:

#### Option 1: Railway/Render (Recommended)
```bash
# Deploy to Railway
npm install -g @railway/cli
railway login
railway init
cd backend
railway up
```

#### Option 2: AWS/GCP (Full Control)
Use Docker Compose with:
- ECS (AWS) or Cloud Run (GCP) for backend
- RDS (AWS) or Cloud SQL (GCP) for PostgreSQL
- ElastiCache (AWS) or Memorystore (GCP) for Redis

#### Option 3: VPS (DigitalOcean/Linode)
```bash
# SSH into server
git clone https://github.com/Chauhan27Mahi/chessai.git
cd chessvision-ai
docker-compose up -d
```

### Database Setup

For Vercel deployment, use managed databases:

**Neon (PostgreSQL)**:
1. Sign up at https://neon.tech
2. Create database
3. Copy connection string to Vercel env vars

**Upstash (Redis)**:
1. Sign up at https://upstash.com
2. Create Redis database
3. Copy connection string to Vercel env vars

### Environment Variables for Vercel

```
# Backend
DATABASE_URL=postgresql://...
REDIS_URL=rediss://...
STOCKFISH_PATH=/usr/local/bin/stockfish

# Frontend
VITE_API_URL=https://your-backend.vercel.app/api
```

## Local Development

```bash
# Start all services
docker-compose up

# Or manually:
# Terminal 1: PostgreSQL + Redis
docker-compose up postgres redis

# Terminal 2: Backend
cd backend
python -m uvicorn api.main:app --reload

# Terminal 3: Worker
cd backend
celery -A workers.tasks worker --loglevel=info

# Terminal 4: Frontend
cd frontend
npm run dev
```

## Architecture for Production

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Vercel    │────▶│  Railway/    │────▶│   Neon      │
│  (Frontend) │     │   Render     │     │(PostgreSQL) │
└─────────────┘     │  (Backend)   │     └─────────────┘
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │   Upstash    │
                    │    (Redis)   │
                    └──────────────┘
```

## Testing the Deployment

1. Upload a video via the frontend
2. Check job status in the jobs list
3. View the analyzed game with:
   - Interactive board
   - Move list
   - Evaluation graph
   - Insights panel

## Troubleshooting

**CORS errors**: Ensure backend has proper CORS settings
**Stockfish not found**: Install in Dockerfile or use managed service
**Database connection failed**: Check connection string format
**Worker not processing**: Verify Redis connection and Celery setup