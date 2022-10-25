FROM library/python:3.7-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app/

RUN python manage.py collectstatic --noinput
EXPOSE 8000

CMD ["gunicorn", "cms.wsgi", "--log-file", "-", "-b", "0.0.0.0" ]