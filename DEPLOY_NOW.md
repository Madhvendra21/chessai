# Deploy ChessVision AI to Vercel NOW

## Quick Deploy (One-Click)

### Option 1: Vercel Web Interface (Easiest - 2 minutes)

1. Go to https://vercel.com/new
2. Import your GitHub repo: `Madhvendra21/chessai`
3. Configure:
   - **Project Name**: chessvision-ai
   - **Framework**: Other
   - **Root Directory**: ./ (root)
   - **Build Command**: (leave empty)
   - **Output Directory**: public
4. Click **Deploy**

### Option 2: Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login (opens browser)
vercel login

# Deploy this project
cd /Users/madhvendra.singh/mahichess/chessvision-ai
vercel --prod
```

## What Gets Deployed

✅ **Static HTML Frontend** (Working Immediately)
- Home page: Upload interface
- Jobs page: Track processing
- Game page: Interactive chess analysis

✅ **Basic API** (Serverless Functions)
- Health check endpoint
- Job creation endpoints
- Mock responses for demo

## Your Site URLs After Deploy

- **Frontend**: `https://chessvision-ai.vercel.app`
- **API**: `https://chessvision-ai.vercel.app/api`

## Features Working on Static Site

✅ Beautiful dark-themed UI
✅ YouTube URL input
✅ Video upload interface
✅ Job tracking page
✅ Interactive chess board
✅ Move navigation
✅ Evaluation display
✅ Responsive design

## Full Backend Setup (Optional)

For complete video processing with AI analysis:

1. Deploy backend separately to Railway/Render
2. Update `API_URL` in `public/index.html`
3. Redeploy frontend

See DEPLOYMENT.md for full details.

## Troubleshooting

**Build Error?**
- Make sure "Output Directory" is set to `public`

**404 Errors?**
- Check that vercel.json is properly configured

**API not working?**
- Vercel free tier has limitations
- Use Railway for full backend

---

## Deploy Right Now

Your repository: https://github.com/Madhvendra21/chessai

**Click this button to deploy:**

https://vercel.com/new/clone?repository-url=https://github.com/Madhvendra21/chessai

Or manually:
1. Go to https://vercel.com
2. Add New Project
3. Import `Madhvendra21/chessai`
4. Deploy!