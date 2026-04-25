FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_PREFER_BINARY=1 \
    FRUIT_MODEL_PATH=/app/runs/train/fruit_quality_check/weights/best.pt \
    FRUIT_MODEL_STORE_DIR=/app/backend/models \
    FRUIT_QUALITY_RULES_PATH=/app/backend/runtime/quality_rules.json

WORKDIR /app

ARG DEBIAN_MIRROR=https://mirrors.tuna.tsinghua.edu.cn

RUN sed -i "s|http://deb.debian.org/debian|${DEBIAN_MIRROR}/debian|g; s|http://deb.debian.org/debian-security|${DEBIAN_MIRROR}/debian-security|g" /etc/apt/sources.list.d/debian.sources \
    && apt-get -o Acquire::ForceIPv4=true update \
    && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --index-url https://download.pytorch.org/whl/cpu \
    torch==2.5.1+cpu \
    torchvision==0.20.1+cpu

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \
    fastapi>=0.115 \
    numpy>=1.24 \
    onnx>=1.17 \
    onnxruntime>=1.19 \
    openpyxl>=3.1 \
    python-multipart>=0.0.9 \
    pillow>=10.0 \
    pydantic>=2.0 \
    pyyaml>=6.0 \
    opencv-python>=4.8 \
    uvicorn[standard]>=0.30 \
    requests>=2.23.0 \
    scipy>=1.4.1 \
    matplotlib>=3.3.0 \
    psutil>=5.8.0 \
    polars>=0.20.0 \
    ultralytics-thop>=2.0.18

RUN pip install --no-deps -i https://pypi.tuna.tsinghua.edu.cn/simple ultralytics==8.4.37

COPY backend backend
COPY frontend frontend
COPY cli.py cli.py
COPY data.yaml data.yaml
COPY runs/train/fruit_quality_check/results.csv runs/train/fruit_quality_check/results.csv
COPY runs/train/fruit_quality_check/weights runs/train/fruit_quality_check/weights
COPY README.md README.md

RUN mkdir -p /app/backend/artifacts /app/backend/models /app/backend/runtime

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=25s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/system/health', timeout=3)"

CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
