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

To run Rasa x you will also need SQLite to store data:
https://sqlite.org/download.html

1) Inside the folder actions create a file
```
__init__.py
```
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

6) We can also launch our bot on Rasa x (UI) using:
```
rasa x --endpoints endpoints.yml 
```



The bot is not ready to understand everything,
but it should be ready to understand a typical conversation like this:

```
- Ciao

                Ciao, vuoi sapere gli orari di apertura o vuoi effettuare una prenotazione?
                
- vorrei sapere gli orari di apertura
              
              siamo aperti dal martedi alla domenica, per pranzo dalle 11:00 alle 15:00, per cena dalle 18:00 alle 23:00.
              
- vorrei effettuare una prenotazione
                
               Per quale giorno voleva prenotare?

- per martedi
               A che ora?
                
- alle 9 di sera          

               Quante persone sarete?
                
- saremo 3
               Ecco la sua prenotazione:
                - giorno: 2019-06-25
                - orario: 21:00:00.000+02:00
                - numero persone: 3
                Desidera confermarla?

- si
                 La sua prenotazione è confermata.
 
- grazie, a presto

                  Ciao, a presto.
 
```                

