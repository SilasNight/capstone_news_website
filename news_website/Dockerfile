FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --upgrade pip && \
pip install -r requirements.txt

# Copy project
COPY . .

EXPOSE 8000

# Run migrations (optional makemigrations for first-time) and start server
CMD ["sh", "-c", "\
python manage.py makemigrations && \
python manage.py migrate && \
python manage.py runserver 0.0.0.0:8000 \
"]