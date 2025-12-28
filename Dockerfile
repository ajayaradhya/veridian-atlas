##############################################
# 1) FRONTEND BUILD (Vite / React)
##############################################
FROM node:18 AS frontend
WORKDIR /app/frontend

# Install dependencies first (build cache benefit)
COPY src/frontend/package*.json ./
RUN npm install

# Copy frontend source and build
COPY src/frontend/ ./
RUN npm run build


##############################################
# 2) BACKEND API (FastAPI + RAG Engine)
##############################################
FROM python:3.11-slim AS backend

# Prevent Python cache & buffering
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

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

# Place frontend build where server.py expects it
# NOTE: this matches PROJECT_ROOT/frontend/dist inside container
COPY --from=frontend /app/frontend/dist ./src/frontend/dist

# Expose FastAPI port
EXPOSE 8000

# Default command (runs API)
CMD ["uvicorn", "veridian_atlas.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
