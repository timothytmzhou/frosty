FROM python:3

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r languages/packages/python.txt
