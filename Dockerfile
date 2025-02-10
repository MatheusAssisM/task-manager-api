FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY .env .

COPY . .

EXPOSE 8000

CMD ["python", "-m", "src.app"]