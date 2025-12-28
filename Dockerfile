##############################################
# 1) FRONTEND BUILD (Vite / React)
##############################################
FROM node:18 AS frontend
WORKDIR /app/frontend

# Install dependencies first for caching
COPY src/frontend/package*.json ./
RUN npm install

# Copy full project and build
COPY src/frontend/ ./
RUN npm run build


##############################################
# 2) BACKEND API (FastAPI + RAG engine)
##############################################
FROM python:3.11-slim

# Prevent Python from writing .pyc files & buffering stdout
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y build-essential wget && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy backend codebase
COPY . .

# Copy built frontend into FastAPI static directory
RUN mkdir -p src/veridian_atlas/static
COPY --from=frontend /app/frontend/dist ./src/veridian_atlas/static

# Expose backend port
EXPOSE 8000

# Run API server
CMD ["uvicorn", "veridian_atlas.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
