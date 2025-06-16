FROM bitnami/spark:3.3.0

USER root
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./spark /app/spark

USER 1001  # Bitnami images often use this non-root user