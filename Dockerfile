FROM python:3.6.9
WORKDIR /mathbot-ml
COPY . .
EXPOSE $PORT
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
CMD uvicorn --app-dir src main:app --host 0.0.0.0 --port $PORT
