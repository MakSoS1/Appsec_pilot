FROM python:3.12-slim
WORKDIR /app
COPY agent /app/agent
COPY backend /app/backend
RUN pip install --no-cache-dir -e /app/agent -e /app/backend
WORKDIR /app/backend
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
