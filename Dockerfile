FROM python:3.12-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install wheel
COPY dlib-19.24.99-cp312-cp312-win_amd64.whl .
RUN pip install ./dlib-19.24.99-cp312-cp312-win_amd64.whl

# Copy other files
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy rest of the code
COPY . .

# Expose your app on port 8000 (FastAPI)
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
