FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

# MySQL (mysqlclient) system requirements
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8007

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8007"]
