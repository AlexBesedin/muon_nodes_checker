FROM python:3.9

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y sqlite3

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main/main.py"]
