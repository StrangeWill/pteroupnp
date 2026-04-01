FROM python:3.13-slim

# miniupnpc is a C extension and needs gcc to build from source
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# gcc is only needed to build miniupnpc, remove it after to keep the image lean
RUN apt-get purge -y gcc && apt-get autoremove -y

COPY main.py .

CMD ["python", "main.py"]