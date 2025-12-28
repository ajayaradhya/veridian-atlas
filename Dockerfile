##############################################
# 1) FRONTEND BUILD (Vite / React)
##############################################
FROM node:18 AS frontend
WORKDIR /app/frontend

# Install dependencies first (cache optimization)
COPY src/frontend/package*.json ./
RUN npm install

# Copy full frontend and build
COPY src/frontend/ ./
RUN npm run build


##############################################
# 2) BACKEND API (FastAPI + RAG Engine)
##############################################
FROM python:3.11-slim AS backend

# Prevent Python cache/buffering
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure Python can import from /app/src
ENV PYTHONPATH="/app/src"

# Set working directory
WORKDIR /app

# Install system build dependencies
RUN apt-get update && \
    apt-get install -y build-essential wget && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend project
COPY . .

# Copy frontend build to the directory server.py serves from
# Matches: PROJECT_ROOT/frontend/dist
COPY --from=frontend /app/frontend/dist ./src/frontend/dist

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI using the correct module path
CMD ["uvicorn", "veridian_atlas.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
