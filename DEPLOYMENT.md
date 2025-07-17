# Deployment Guide - Privacy-Preserving Query Interface

## Quick Deploy Options

### Option 1: Railway (Recommended - Easiest)

1. **Sign up** at [railway.app](https://railway.app)
2. **Connect your GitHub** repository
3. **Deploy** - Railway will automatically detect the Dockerfile and deploy

### Option 2: Render

1. **Sign up** at [render.com](https://render.com)
2. **Create a new Web Service**
3. **Connect your GitHub** repository
4. **Set build command**: `docker build -f Dockerfile.backend .`
5. **Set start command**: `python -m flask run --host=0.0.0.0 --port=$PORT`

### Option 3: Local Docker

```bash
# Build and run locally
docker-compose up --build

# Access at http://localhost
```

## What You Get

- ✅ HTTPS automatically enabled
- ✅ Automatic deployments from GitHub
- ✅ No server management
- ✅ Free tier available
- ✅ Custom domain support

## For 3 Users

This setup is perfect for a prototype with 3 users:
- No complex infrastructure
- No security overhead
- Easy to share with colleagues
- Can be upgraded later if needed

## Next Steps

1. Choose a deployment platform
2. Push your code to GitHub
3. Connect to the platform
4. Share the URL with your colleagues

That's it! No complex setup needed for a prototype. 