# Render Deployment Fix - Alternative Solutions

## Problem
Render is not using the `render.yaml` file and is encountering Rust compilation errors when building `pydantic-core` from source.

## Immediate Solutions

### Solution 1: Manual Build Command (Recommended)
In your Render service settings, set the **Build Command** to:

```bash
export CARGO_HOME=/tmp/cargo && export CARGO_TARGET_DIR=/tmp/cargo-target && pip install --upgrade pip && pip install --only-binary=all --prefer-binary -r requirements.txt
```

### Solution 2: Use the Build Script
Set the **Build Command** to:
```bash
./render-build.sh
```

### Solution 3: Environment Variables
Add these environment variables in your Render service:

- `CARGO_HOME` = `/tmp/cargo`
- `CARGO_TARGET_DIR` = `/tmp/cargo-target`
- `CARGO_BUILD_TARGET_DIR` = `/tmp/cargo-target`
- `RUST_BACKTRACE` = `1`

Then use this build command:
```bash
pip install --upgrade pip && pip install --only-binary=all --prefer-binary -r requirements.txt
```

## Why This Works

1. **Cargo Environment Variables**: Redirect Rust compilation to writable directories (`/tmp/cargo`)
2. **Pre-compiled Wheels**: The `--only-binary=all --prefer-binary` flags force pip to use pre-compiled wheels instead of building from source
3. **Specific Versions**: Updated `requirements.txt` uses specific versions with known pre-compiled wheels

## Updated Files

- `requirements.txt` - Updated with Render-compatible versions
- `render-build.sh` - Simple build script for Render
- `render.yaml` - Still available if Render starts using it

## Start Command
Use this **Start Command** in Render:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Environment Variables to Set
Make sure to set these in your Render service:

### Required:
- `SECRET_KEY` - Generate a secure secret key
- `POSTGRES_SERVER` - Your PostgreSQL server URL
- `POSTGRES_USER` - Database username  
- `POSTGRES_PASSWORD` - Database password
- `POSTGRES_DB` - Database name
- `BACKEND_CORS_ORIGINS_STR` - Allowed CORS origins

### Optional:
- `ENVIRONMENT` = `production`
- `DEBUG` = `false`

## Testing Locally
To test the build process locally:

```bash
# Set environment variables
export CARGO_HOME=/tmp/cargo
export CARGO_TARGET_DIR=/tmp/cargo-target

# Run the build
pip install --upgrade pip
pip install --only-binary=all --prefer-binary -r requirements.txt
```

## If Still Having Issues

1. **Try Docker**: Consider using Docker deployment instead
2. **Contact Render Support**: They may have specific solutions for your account
3. **Use Different Python Version**: Try Python 3.11 instead of 3.13
4. **Alternative Dependencies**: Consider replacing `python-jose[cryptography]` with `PyJWT` if possible

## Alternative Dependencies
If Rust compilation continues to be problematic, consider these alternatives:

```txt
# Instead of python-jose[cryptography]
PyJWT==2.8.0

# Instead of passlib[bcrypt]  
argon2-cffi==23.1.0
```

These alternatives don't require Rust compilation and should work reliably on Render.
