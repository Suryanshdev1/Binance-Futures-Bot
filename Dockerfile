# Dockerfile for Railway / Render deployment
# Place this in the ROOT of your project

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
COPY web_demo/requirements.txt ./web_demo/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -r web_demo/requirements.txt

# Copy entire project
COPY . .

# Expose port (Render/Railway sets PORT env var)
ENV PORT=8501
EXPOSE $PORT

# Start Streamlit app
# For FastAPI, change to: CMD ["uvicorn", "web_demo.api:app", "--host", "0.0.0.0", "--port", "8501"]
CMD ["streamlit", "run", "web_demo/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
