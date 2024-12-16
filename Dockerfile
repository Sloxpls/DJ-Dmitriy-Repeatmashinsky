FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "src/app.py"]
