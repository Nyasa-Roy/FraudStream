FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
COPY producer producer
COPY backend backend
COPY stream_processor stream_processor
COPY ml ml
RUN pip install --no-cache-dir .
EXPOSE 8000
CMD ["uvicorn", "fraudstream_backend.app:app", "--host", "0.0.0.0", "--port", "8000"]

