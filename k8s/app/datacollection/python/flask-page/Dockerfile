FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
COPY app.py app.py
COPY templates/ templates/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]
