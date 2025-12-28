FROM python:3.9-slim

# Install ffmpeg for audio conversion
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Set up app
WORKDIR /app
COPY . .

# Install python libraries
RUN pip install --no-cache-dir -r requirements.txt

# Start the server
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000", "--timeout", "120"]
