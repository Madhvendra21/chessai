# Quick Start - Deploy to Vercel

## Step 1: Setup GitHub Repository

Repository is already created at: **https://github.com/Madhvendra21/chessai.git**

Code has been pushed ✓

## Step 2: Deploy Frontend to Vercel

1. Go to https://vercel.com
2. Click "Add New Project"
3. Import `chessai` from GitHub
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add Environment Variable:
   ```
   VITE_API_URL=https://your-backend-url.vercel.app/api
   ```
6. Click Deploy

## Step 3: Deploy Backend to Vercel

**Note**: The backend needs a database. For MVP, you can use:
- **SQLite** (for testing only)
- **Supabase** (recommended free PostgreSQL)
- **Railway/Render** (better for full backend)

### Option A: Deploy to Vercel (Limited)

1. Create new project in Vercel
2. Import same repo
3. Configure:
   - **Root Directory**: `backend`
   - **Framework Preset**: Other
   - **Build Command**: None
   - **Output Directory**: .
4. Add Environment Variables:
   ```
   DATABASE_URL=sqlite:///tmp/chessvision.db
   REDIS_URL=memory://
   STOCKFISH_PATH=stockfish
   ```

### Option B: Deploy to Railway (Recommended)

1. Go to https://railway.app
2. Click "New Project"
3. Deploy from GitHub repo
4. Add PostgreSQL plugin
5. Add Redis plugin
6. Deploy!

### Option C: Deploy to Render

1. Go to https://render.com
2. Create "Web Service"
3. Connect GitHub repo
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
5. Add PostgreSQL database
6. Deploy!

## Step 4: Update Frontend API URL

After backend is deployed, update the frontend environment variable:

```
VITE_API_URL=https://your-backend-domain.com/api
```

Redeploy frontend.

## Step 5: Test the App

1. Visit your frontend URL
2. Upload a chess video or enter YouTube URL
3. Wait for processing
4. View the analyzed game!

## Free Tier Limits

**Vercel**:
- 100GB bandwidth/month
- 1000 build minutes/month
- Serverless functions timeout: 10s

**Railway**:
- $5 free credit/month
- Good for small projects

**Render**:
- Web services: Free (sleeps after 15min)
- PostgreSQL: Free tier available

## Troubleshooting

**CORS Errors**: Add your frontend domain to backend CORS settings
**Database Errors**: Check DATABASE_URL format
**Upload Fails**: Increase body size limit in backend
**Stockfish Missing**: Install via apt-get in build command

## Next Steps

For production with video processing:
- Use Railway/Render for backend (better than Vercel for Python)
- Use Supabase for database
- Use Cloudinary for video storage
- Use Upstash for Redis