FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
COPY producer producer
COPY backend backend
COPY stream_processor stream_processor
COPY ml ml
RUN pip install --no-cache-dir .
CMD ["python", "-m", "fraudstream_processor.main"]

