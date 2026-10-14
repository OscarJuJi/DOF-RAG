FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_THREAD_LIMIT=2
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 app \
    && mkdir /archive && chown app:app /archive
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY dof_mcp ./dof_mcp
USER app
EXPOSE 8001
CMD ["python", "-m", "dof_mcp.server", "--transport", "streamable-http"]
