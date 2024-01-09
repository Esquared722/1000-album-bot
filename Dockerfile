FROM python:alpine

# COPY SCRIPT FILES
WORKDIR /code

RUN apk add --no-cache gcc musl-dev linux-headers

# INSTALL DEPENDENCIES

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD python main.py
