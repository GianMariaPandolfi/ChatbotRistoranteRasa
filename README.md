# ChatbotRistoranteRasa
To run the bot:

Install Rasa and Rasa X

```
pip install rasa-x --extra-index-url https://pypi.rasa.com/simple
```

install spacy

```
pip install -U spacy
python -m spacy download it
```

install Google Client Library for google calendar api
```
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```
Furthermore you have to enable the api, download the credentials and copy them inside the folder actions.


https://developers.google.com/calendar/quickstart/python

1) Create a file __init__.py inside the folder actions
2) Inside the folder actions launch the action server with

```
rasa run actions
```
3) from the main folder, launch the docker server using:
```
docker-compose up
```
4) train the bot with:
```
rasa train
```

5) now we can lauch rasa on powershell with:
```
rasa shell --endpoints endpoints.yml 
```
or in the interactive mode with:
```
rasa interactive --endpoints endpoints.yml 
```
