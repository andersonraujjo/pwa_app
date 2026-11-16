# UniApp — imagem enxuta para hospedagem gratuita / VPS
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    SEED_ON_START=true \
    ENV=development
# Em deploy real: ENV=production e SECRET_KEY forte (obrigatório).

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY static ./static
COPY scripts ./scripts

RUN mkdir -p /app/data

# Em produção defina SECRET_KEY e, se quiser, DATABASE_URL via ambiente.
EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers"]
