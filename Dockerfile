FROM public.ecr.aws/docker/library/python:latest

# COPY SCRIPT FILES
COPY . .

# INSTALL DEPENDENCIES

RUN python -m pip install -r requirements.txt --no-cache-dir

CMD python main.py
