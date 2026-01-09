# --- STAGE 1: Frontend Build (Tailwind) ---
FROM node:18-alpine AS frontend-builder
WORKDIR /app

# Copy package files first to leverage Docker's layer caching
COPY package*.json ./
RUN npm install

# Copy all project files
COPY . .

# Ensure the output directory exists before Tailwind tries to write to it
RUN mkdir -p app/static/dist

# IMPORTANT: We run the CLI directly without --watch so the build can complete.
# This creates the features.css file inside app/static/dist/
# Compiles the CSS once and moves to the next step
# Use npx to find concurrently in the local node_modules
RUN npx concurrently \
  "npx @tailwindcss/cli -i app/static/src/features_src.css -o app/static/dist/features.css --content 'app/templates/**/*.html'" \
  "npx @tailwindcss/cli -i app/static/src/input.css -o app/static/dist/main.css --content 'app/templates/**/*.html'"


# --- STAGE 2: Backend (Flask + Postgres) ---
# --- STAGE 2: Backend (Flask + Postgres) ---
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 1. Copy the entire project first
COPY . .

# 2. Inject the compiled CSS from Stage 1 (Overwrites any local dist folder)
COPY --from=frontend-builder /app/app/static/dist/ /app/app/static/dist/

# 3. Setup the entrypoint script
RUN chmod +x entrypoint.sh

# 4. Final settings
EXPOSE 5000

# IMPORTANT: Only ONE CMD allowed. 
# We use the entrypoint script so migrations run before the server starts.
CMD ["./entrypoint.sh"]