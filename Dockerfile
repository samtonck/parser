FROM python:3.8
RUN pip3 install fastapi uvicorn bs4 requests transliterate pymysql
COPY ./app /app
CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "15400"]
