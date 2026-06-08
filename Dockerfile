FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

COPY backend/ backend/
COPY frontend/dist/ frontend/dist/

ENV PYTHONPATH=/app
ENV NEO4J_URI=bolt://neo4j:7687
ENV NEO4J_PASSWORD=songci2026

EXPOSE 8083

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8083"]
