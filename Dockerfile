from google/cloud-sdk

RUN pip3 install pygcloud

RUN mkdir -p /app
COPY requirements.txt /app
COPY config.yaml /app
COPY src/*.py /app
RUN pip3 install -r app/requirements.txt

WORKDIR /app

CMD ["python3", "gcp_inventory.py", "inventory"]
