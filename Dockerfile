FROM python:3.14-slim-bookworm AS builder
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_CACHE_DIR=1
WORKDIR /build
COPY requirements.txt .
RUN python -m venv /opt/venv && /opt/venv/bin/pip install -r requirements.txt

FROM python:3.14-slim-bookworm AS runtime
ENV PATH="/opt/venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000
RUN groupadd --gid 10001 app && useradd --uid 10001 --gid app --create-home app
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY --chown=10001:10001 manage.py gunicorn.conf.py ./
COPY --chown=10001:10001 api ./api
COPY --chown=10001:10001 demo ./demo
# Ephemeral build-only key; no runtime secret is baked into the image.
RUN DJANGO_SECRET_KEY=build-only-placeholder python manage.py collectstatic --noinput
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3   CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:'+os.getenv('PORT','8000')+'/health/live/',timeout=2)"
CMD ["gunicorn", "demo.wsgi:application", "--config", "gunicorn.conf.py"]
