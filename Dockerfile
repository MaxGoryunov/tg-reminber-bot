FROM python:3.9

WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y gcc
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 3040

CMD ["python", "./main.py"]