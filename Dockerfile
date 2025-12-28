# ------------------------------------------------------------
# 1) Base image with Python
# ------------------------------------------------------------
FROM python:3.11-slim

# Prevent Python from writing .pyc files & buffering stdout
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# ------------------------------------------------------------
# 2) Set work directory in container
# ------------------------------------------------------------
WORKDIR /app

# ------------------------------------------------------------
# 3) Install system deps (ChromaDB, PyTorch CPU, etc.)
# ------------------------------------------------------------
RUN apt-get update && \
    apt-get install -y build-essential wget && \
    rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# 4) Copy project metadata + install dependencies
# ------------------------------------------------------------
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ------------------------------------------------------------
# 5) Copy codebase
# ------------------------------------------------------------
COPY . .

# ------------------------------------------------------------
# 6) Expose FastAPI port
# ------------------------------------------------------------
EXPOSE 8000

# ------------------------------------------------------------
# 7) Start the API
# ------------------------------------------------------------
CMD ["uvicorn", "veridian_atlas.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
