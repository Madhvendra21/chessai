# Deploy to Vercel - Quick Steps

## The Problem
Your current deployment shows a blank page because it's trying to build the React app.

## Solution - Deploy Static HTML

### Step 1: Delete Current Deployment
1. Go to https://vercel.com/dashboard
2. Find "frontend-red-one-42" project
3. Click **Settings** → **General**
4. Scroll down → Click **Delete Project**
5. Type project name to confirm

### Step 2: Create New Deployment
1. Go to https://vercel.com/new
2. Import GitHub repo: `Madhvendra21/chessai`
3. **IMPORTANT** - Configure correctly:
   - **Project Name**: chessvision-ai
   - **Framework Preset**: `Other`
   - **Root Directory**: `./` (root, not frontend/)
   - **Build Command**: Leave blank
   - **Output Directory**: Leave blank
4. Click **Deploy**

### Step 3: Verify
After deployment, visit:
- `https://your-project.vercel.app` - Should show homepage
- `https://your-project.vercel.app/jobs.html` - Should show jobs page
- `https://your-project.vercel.app/game.html?id=test` - Should show game page

## Files That Must Deploy
- index.html (homepage)
- jobs.html (jobs list)
- game.html (game viewer)
- test.html (test page)
- vercel.json (routing config)

## What's Working Locally
Visit http://localhost:8080 - this is what should appear on Vercel.

## Common Mistakes
❌ Setting "Framework Preset" to "Create React App"  
❌ Setting "Root Directory" to "frontend/"  
❌ Adding build commands  

✅ Set "Framework Preset" to "Other"  
✅ Leave all build fields blank  
✅ Deploy from root folder  

## Alternative
If still not working, I can deploy to Netlify instead - it handles static sites better.

Current GitHub: https://github.com/Madhvendra21/chessai