# Author: niranjanxprt (https://github.com/niranjanxprt)
# Build React frontend
FROM node:20-alpine AS frontend
WORKDIR /app/frontend-react
COPY frontend-react/package*.json ./
RUN npm ci
COPY frontend-react/ ./
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL:-http://localhost:8000}
RUN npm run build:docker

# Python backend + serve React static
FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY frontend/ ./frontend/
COPY --from=frontend /app/frontend-react/dist ./static
COPY start.sh ./
RUN chmod +x start.sh

ENV PYTHONUNBUFFERED=1
EXPOSE 8000
