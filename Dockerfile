FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DATA_DIR=/app/data \
    PORT=8000

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN sed -i 's/\r$//' entrypoint.sh \
    && mkdir -p /app/data /app/staticfiles \
    && DJANGO_SECRET_KEY=build-only-key python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["sh", "entrypoint.sh"]
