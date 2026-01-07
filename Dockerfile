# --- STAGE 1: Frontend Build (Tailwind) ---
FROM node:18-alpine AS frontend-builder
WORKDIR /app

# Copy package files first to leverage Docker's layer caching
COPY package*.json ./
RUN npm install

# Copy all project files
COPY . .

# IMPORTANT: We run the CLI directly without --watch so the build can complete.
# This creates the features.css file inside app/static/dist/
RUN npx @tailwindcss/cli -i app/static/src/features_src.css -o app/static/dist/features.css --content 'app/templates/**/*.html'

# --- STAGE 2: Backend (Flask + Postgres) ---
FROM python:3.11-slim

# Prevent Python from writing .pyc files and ensure output is logged immediately
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app

# Install system dependencies required for psycopg2 (Postgres) and Bcrypt
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Copy ONLY the compiled CSS from the frontend-builder stage
# This ensures app/static/dist exists even if it's ignored locally
COPY --from=frontend-builder /app/app/static/dist /app/app/static/dist

# Expose the port Flask/Gunicorn will run on
EXPOSE 5000

# Run the app using Gunicorn (pointing to your run.py)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]