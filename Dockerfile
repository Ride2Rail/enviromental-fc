FROM python:3.8

ENV APP_NAME=environmental.py
COPY /code/"$APP_NAME" /code/"$APP_NAME"
COPY /code/environmental.conf /code/environmental.conf
COPY /code/utils_environmental.py /code/utils_environmental.py

WORKDIR /code


ENV FLASK_APP="$APP_NAME"
ENV FLASK_RUN_HOST=0.0.0.0

RUN pip3 install --no-cache-dir --upgrade pip

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 5008

CMD ["flask", "run"]
