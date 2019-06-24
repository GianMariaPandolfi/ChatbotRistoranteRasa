from __future__ import print_function
from typing import Any, Text, Dict, List
from rasa_core_sdk import Action, Tracker
from rasa_core_sdk.executor import CollectingDispatcher
from rasa_core_sdk.events import SlotSet, UserUtteranceReverted, ConversationPaused
from rasa_core_sdk.forms import FormAction
from datetime import datetime, timedelta
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.events']

number_of_seats = 80


class ActionControlloRichiesta(Action):
    """Check the parameters found with the intent richiesta_di_prenotazione"""

    def name(self) -> Text:
         return "action_controllo_richiesta"

    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        date = None
        saved_time = None
        num_persone = None

        if any(tracker.get_latest_entity_values("num_persone")):
            num = next(tracker.get_latest_entity_values("num_persone"))
            if int(num) > 0:
                num_persone = num

        if any(tracker.get_latest_entity_values("time")):  # check if Duckling got a time entity
             date = next(tracker.get_latest_entity_values('time'), None)
             time = next(tracker.get_latest_entity_values('time'), None)
             time = time.split("T")[1].split(":")
             time_to_evaluate = int(time[0])
             num_persone_fix = 0  # used to handle the case where duckling extract num_persone as time
             if num_persone is not None:
                 num_persone_fix = int(num_persone)

             if time_to_evaluate != 0 and time_to_evaluate != num_persone_fix:  # handle case with no time entered and case
                                                                                # where duckling extract num_persone as time
                 if time_to_evaluate < 11:
                     time_to_evaluate += 12  # from 02:00 to 14:00
                 if (11 <= time_to_evaluate < 15) or (18 <= time_to_evaluate < 23):
                     saved_time = str(time_to_evaluate) + ":" + time[1] + ":" + time[2] + ":" + time[3]
                     # from 2019-06-18T12:00:00.000+02:00 to 12:00:00.000+02:00
                 else:
                     dispatcher.utter_template("utter_orario_chiuso", tracker)

             if datetime.strptime(date[:19], '%Y-%m-%dT%H:%M:%S').weekday() == 0:  # check if it's monday (close day)
                 dispatcher.utter_template('utter_lunedi_chiuso', tracker)
             else:
                 date = date.split("T")[0]

         #save in the slot the information that we got

        return [
             SlotSet('data', date),
             SlotSet('orario', saved_time),
             SlotSet('num_persone', num_persone)
        ]


class PrenotazioneForm(FormAction):
    '''Collects prenotation info'''

    def name(self):
        return "prenotazione_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return [
            "data",
            "orario",
            "num_persone"
        ]

    def slot_mappings(self):
        return {"data": [
                    self.from_entity(entity="time"),
                ],
                "orario": [
                    self.from_entity(entity="time"),
                    self.from_entity(entity="number"),
                ],
                "num_persone": [self.from_entity(entity="num_persone"),
                                self.from_entity(entity="number"),],
                }

    def validate_data(self, value, dispatcher, tracker, domain):

        if any(tracker.get_latest_entity_values("time")):
            date = value
            try:
                if datetime.strptime(date[:19], '%Y-%m-%dT%H:%M:%S').weekday() == 0:  # check if it's monday (close day)
                    dispatcher.utter_template('utter_lunedi_chiuso', tracker)
                    return {"data": None}
                else:
                    date = date.split("T")[0]
                    return {"data": date}
            except ValueError:
                return {"data": date}
        else:
            return {"data": None}

    def validate_orario(self, value, dispatcher, tracker, domain):

        if any(tracker.get_latest_entity_values("time")):
            try:  #for values validated by action_controllo_richiesta
                time = value
                time = time.split("T")[1].split(":")
                time_to_evaluate = int(time[0])
                if time_to_evaluate != 0:
                    if time_to_evaluate < 11:
                        time_to_evaluate += 12  # from 02:00 to 14:00
                    if (11 <= time_to_evaluate < 15) or (18 <= time_to_evaluate < 23):
                        saved_time = str(time_to_evaluate) + ":" + time[1] + ":" + time[2] + ":" + time[3]
                        # from 2019-06-18T12:00:00.000+02:00 to 12:00:00.000+02:00
                        return {"orario": saved_time}
                    else:
                        dispatcher.utter_template("utter_orario_chiuso", tracker)
                        return {"orario": None}
            except IndexError:
                return {"orario": value}

        elif any(tracker.get_latest_entity_values("number")):
            try:
                time_to_evaluate = int(value)
                if time_to_evaluate != 0:
                    if time_to_evaluate < 11:
                        time_to_evaluate += 12  # from 02:00 to 14:00
                    if (11 <= time_to_evaluate < 15) or (18 <= time_to_evaluate < 23):
                        saved_time = str(time_to_evaluate) + ":00:00.000+02:00"  # from 2019-06-18T12:00:00.000+02:00
                                                                                 # to 12:00:00.000+02:00
                                                                                 # TODO for other timezone
                        return {"orario": saved_time}
                    else:
                        dispatcher.utter_template("utter_orario_chiuso", tracker)
                        return {"orario": None}
            except ValueError:
                return {"orario": value}
        else:
            return {"orario": None}

    def validate_num_persone(self, value, dispatcher, tracker, domain):

        if any(tracker.get_latest_entity_values("num_persone")) or any(tracker.get_latest_entity_values("number")):
            if int(value) > 0:
                return {"num_persone": value}
            else:
                return {"num_persone": None}
        else:
            return {"num_persone": None}

    def submit(self,
               dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any]) -> List[Dict]:
        return []


class ActionDefaultFallback(Action):
    # if the chatbot doesn't understand for 2 consecutive times handoff the conversation to a human

    def name(self) -> Text:
        return "action_default_fallback"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List["Event"]:

        last_utter = get_last_utter_action(tracker, dispatcher)
        if "action_default_fallback" == last_utter:
            dispatcher.utter_message("handoff to human: implementazione notifica")  # TODO implement handoff
            return [ConversationPaused()]

        # first time
        else:
            dispatcher.utter_template("utter_default", tracker)
            return [UserUtteranceReverted()]


def get_last_utter_action(tracker, dispatcher):
    ##goes back through the list of events and finds
    ##the last utter_action
    for event in reversed(tracker.events):
        try:
            if event.get('name') not in ['action_listen', None, 'utter_default', 'prenotazione_form']:
                last_utter_action = event.get('name')
                # dispatcher.utter_message(last_utter_action)
                return last_utter_action
            else:
                pass
        except:
            pass
            return 'error! no last action found'


class ActionCheckCalendar(Action):
    """Check the parameters found with the intent richiesta_di_prenotazione"""

    def name(self) -> Text:
         return "action_check_calendar"

    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

         #save in the slot the information that we got
         number_of_people = int(tracker.get_slot("num_persone"))
         orario = tracker.get_slot("orario")
         data = tracker.get_slot("data")
         prenotation_time = data + "T" + orario
         global number_of_seats
         service = authentication()
         if ":" == prenotation_time[-3:-2]:
             prenotation_time = prenotation_time[:-3] + prenotation_time[
                                                        -2:]  # formattazione orario per chiamate successive
         prenotation_time_start = datetime.strptime(prenotation_time, '%Y-%m-%dT%H:%M:%S.%f%z')
         prenotation_time_end = prenotation_time_start + timedelta(hours=2)  # si assume che una prenotazione duri 2 ore

         events_result = service.events().list(calendarId='chatbotrasasintra@gmail.com',
                                               timeMin=prenotation_time_start.isoformat(),
                                               timeMax=prenotation_time_end.isoformat()
                                               ).execute()
         events = events_result.get('items', [])
         if check_available_seats(events, number_of_people):  # si controlla che ci siano posti disponibili
             dispatcher.utter_template("utter_confirmation", tracker)
             return [SlotSet('available_seats', True)]
         else:
             dispatcher.utter_message("Mi dispiace ma siamo al completo.")
             return [SlotSet('available_seats', False)]


class ActionInsertCalendar(Action):
    """Check the parameters found with the intent richiesta_di_prenotazione"""

    def name(self) -> Text:
         return "action_insert_calendar"

    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         # save in the slot the information that we got

         intent = tracker.latest_message['intent'].get('name')
         if(intent == "afferma"):
             number_of_people = int(tracker.get_slot("num_persone"))
             orario = tracker.get_slot("orario")
             data = tracker.get_slot("data")
             prenotation_time = data + "T" + orario
             global number_of_seats
             service = authentication()
             if ":" == prenotation_time[-3:-2]:
                 prenotation_time = prenotation_time[:-3] + prenotation_time[-2:]
             prenotation_time_start = datetime.strptime(prenotation_time, '%Y-%m-%dT%H:%M:%S.%f%z')
             prenotation_time_end = prenotation_time_start + timedelta(hours=2)  # we assume that a reservation last 2 hours

             events_result = service.events().list(calendarId='chatbotrasasintra@gmail.com',
                                                   timeMin=prenotation_time_start.isoformat(),
                                                   timeMax=prenotation_time_end.isoformat()
                                                   ).execute()
             events = events_result.get('items', [])
             if check_available_seats(events, number_of_people):  # double check
                 insert_event(service, prenotation_time_start, prenotation_time_end, number_of_people, dispatcher)
                 dispatcher.utter_template("utter_confirmed", tracker)
                 return [SlotSet('conferma_prenotazione', True)]

             else:
                 dispatcher.utter_message("Mi dispiace ma siamo pieni.")
                 return [SlotSet('conferma_prenotazione', False),
                         SlotSet('available_seats', False)]
         elif intent == "nega":
            dispatcher.utter_template('utter_not_confirmed', tracker)
            return [SlotSet('conferma_prenotazione', False)]


def authentication():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('calendar', 'v3', credentials=creds)
    return service


def insert_event(service, prenotation_time_start, prenotation_time_end, number_of_people, dispatcher):
    event = {
        'summary': 'Prenotazione',
        'description': 'Prenotazione di {nome cliente} per' + str(number_of_people),  # get nome cliente from facebook

        'extendedProperties': {
            'private': {
                'number_of_people': str(number_of_people)
            }
        },
        'start': {
            'dateTime': prenotation_time_start.strftime('%Y-%m-%dT%H:%M:%S%z'),
            'timeZone': 'Europe/Berlin'
        },
        'end': {
            'dateTime': prenotation_time_end.strftime('%Y-%m-%dT%H:%M:%S%z'),
            'timeZone': 'Europe/Berlin'
        },
    }

    event = service.events().insert(calendarId='chatbotrasasintra@gmail.com', body=event).execute()
    # dispatcher.utter_message('Event created: %s' % (event.get('htmlLink')))



def check_available_seats(events, number_of_people):
    total_number_of_people = number_of_people
    for event in events:
        total_number_of_people += int(event.get('extendedProperties').get('private').get('number_of_people'))
    if total_number_of_people > number_of_seats:
        return False
    else:
        return True


