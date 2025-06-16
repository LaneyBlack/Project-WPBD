FROM bitnami/spark:3.3.0

USER root

# Install pip and dependencies
RUN install_packages python3-pip
COPY ./spark/requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

USER 1001