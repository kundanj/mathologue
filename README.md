# Mathologue: Python ML Models for a maths chatbot
Maths chatbot for answering maths questions:
This project is based on a dual step chat processing where each question is passed through
1) a neural-keras based multi label text classifier that identifies the type of question asked
2) a  rules based pipeline of further dissection of questions using either regex or NLP (Spacy dependency parsing or Spacy rules based matching).

## Install
`pip install --upgrade pip`

`pip3 install -r requirements.txt`

## Create and activate virtual env
`python -m venv math-env` 

`source ./math-env/bin/activate`

## Train the Model
`python src/ml/train.py`

## PreBuild/test command line
`python src/test_predict.py`
refer sample questions in test_predict.py to determine what questions are answerable by the bot

## Build
on local:
`uvicorn --app-dir src main:app --reload`
or
`python3 -m uvicorn --app-dir src main:app --reload`

## Deployment
To deploy on heroku/AWS follow Docker build and deploy:

## Test API
Local:
`curl -X POST -H "Content-Type: application/json" -d '{"chatID" : "XXXAA1", "message": "what is 50% of 3450"}'   http://127.0.0.1:8000/chat/`

## Issues:
On python 3.8+ requirements.txt will need to drop data_classes etc packages for build


## License:
This code is released under GPL license - feel free to contribute to this and add new maths categories and question formats.
