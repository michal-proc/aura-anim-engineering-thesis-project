FROM nvidia/cuda:12.6.0-cudnn-devel-ubuntu22.04 AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3-pip \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Make python3.11 the default python
RUN ln -s /usr/bin/python3.11 /usr/bin/python

ENV PYTHONUNBUFFERED=1
WORKDIR /backend

RUN python -m venv /backend/.venv
ENV PATH="/backend/.venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM nvidia/cuda:12.6.0-cudnn-runtime-ubuntu22.04 AS runtime

# Install Python and runtime dependencies including CUDA libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-venv \
    python3-pip \
    curl \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    # Added these to try to fix runtime errors due to missing libraries
    libcusparselt0 \
    cuda-cupti-12-6 \
    && rm -rf /var/lib/apt/lists/*

# Make python3.11 the default python
RUN ln -s /usr/bin/python3.11 /usr/bin/python

ENV PYTHONUNBUFFERED=1
ENV RAY_memory_monitor_refresh_ms=0
ENV PYTHONPATH="/backend"
ENV PATH="/backend/.venv/bin:$PATH"

WORKDIR /backend
RUN mkdir -p outputs weights logs temp

# Copy virtual environment from builder
COPY --from=builder /backend/.venv /backend/.venv

# Install git as a separate step as it is required by the application to download the deep
# learning dependencies not distributed as wheels
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

EXPOSE 8000 8265

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

WORKDIR /

CMD ["python", "-m", "backend.serve_app"]
