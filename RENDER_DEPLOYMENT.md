# Render Deployment Guide

## Problem
When deploying Python applications with Rust dependencies (like `python-jose[cryptography]`) to Render, you may encounter the error:
```
error: failed to create directory `/usr/local/cargo/registry/cache/index.crates.io-1949cf8c6b5b557f`
Caused by: Read-only file system (os error 30)
```

## Solution
This repository includes several files to fix this issue:

### 1. `render.yaml` - Render Configuration
This file configures your Render service with proper environment variables:
- `CARGO_HOME=/tmp/cargo` - Redirects Cargo cache to writable directory
- `CARGO_TARGET_DIR=/tmp/cargo-target` - Redirects build artifacts to writable directory
- Other production environment variables

### 2. `build.sh` - Build Script
A custom build script that:
- Sets up Cargo environment variables
- Creates necessary directories
- Installs dependencies using production requirements

### 3. `requirements-prod.txt` - Production Requirements
Optimized requirements file with:
- Explicit versions for Rust dependencies
- Pre-compiled wheels where possible
- Production-specific packages like `gunicorn`

## Deployment Steps

### Option 1: Using render.yaml (Recommended)
1. Push your code to GitHub/GitLab
2. Connect your repository to Render
3. Render will automatically detect `render.yaml` and use the configuration

### Option 2: Manual Configuration
If you prefer manual setup in Render dashboard:

1. **Environment Variables:**
   ```
   CARGO_HOME=/tmp/cargo
   CARGO_TARGET_DIR=/tmp/cargo-target
   CARGO_BUILD_TARGET_DIR=/tmp/cargo-target
   RUST_BACKTRACE=1
   ```

2. **Build Command:**
   ```bash
   ./build.sh
   ```

3. **Start Command:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

### Option 3: Alternative Build Command
If the build script doesn't work, try this build command directly:
```bash
export CARGO_HOME=/tmp/cargo && export CARGO_TARGET_DIR=/tmp/cargo-target && pip install --upgrade pip && pip install -r requirements-prod.txt
```

## Environment Variables to Set in Render

Make sure to set these environment variables in your Render service:

### Required:
- `SECRET_KEY` - Generate a secure secret key
- `POSTGRES_SERVER` - Your PostgreSQL server URL
- `POSTGRES_USER` - Database username
- `POSTGRES_PASSWORD` - Database password
- `POSTGRES_DB` - Database name
- `BACKEND_CORS_ORIGINS_STR` - Allowed CORS origins (comma-separated)

### Optional:
- `ENVIRONMENT=production`
- `DEBUG=false`

## Troubleshooting

### If build still fails:
1. Check Render logs for specific error messages
2. Try using `requirements.txt` instead of `requirements-prod.txt`
3. Consider using Docker deployment instead
4. Contact Render support with specific error details

### If runtime errors occur:
1. Verify all environment variables are set correctly
2. Check database connectivity
3. Review application logs in Render dashboard

## Additional Notes

- The `CARGO_HOME` and `CARGO_TARGET_DIR` variables redirect Rust compilation to writable directories
- This solution works for most Python packages with Rust dependencies
- Consider using Docker if you continue to have issues with the standard Python environment
