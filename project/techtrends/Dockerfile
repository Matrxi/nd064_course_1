FROM python:2.7
LABEL maintainer="matrxi"

COPY . /app
WORKDIR /app

RUN python init_db.py

RUN pip install -r requirements.txt

EXPOSE 3111

CMD ["python","app.py"]
