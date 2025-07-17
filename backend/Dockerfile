FROM python:3.12-slim

# System deps
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Source
COPY . .

# Flask env
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Start app
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "app:app"] 