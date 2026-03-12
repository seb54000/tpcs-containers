# bgd-lite Dockerfile
FROM python:3.12-slim

# Sécurité: user non-root
RUN useradd -r -u 10001 -g nogroup appuser

WORKDIR /app
COPY app.py /app/app.py

ENV PORT=8080
EXPOSE 8080

USER 10001
CMD ["python", "/app/app.py"]
