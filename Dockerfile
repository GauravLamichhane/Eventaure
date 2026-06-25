# Base image
FROM python:3.12-slim

# Prevent Python from creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

#show logs immediately
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

#Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

#Copy project files
COPY . .

#Expose Django port
EXPOSE 8000

#Run Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]