## saluto_iniziale
* saluto_iniziale
  - utter_saluto_iniziale

## informazioni_apertura
* saluto_iniziale
    - utter_saluto_iniziale
* informazioni_apertura
    - utter_informazioni_apertura
* saluto_finale
    - utter_saluto_finale


## Generated Story 4485582073990765020
* richiesta_di_prenotazione{"time": "2019-06-21T00:00:00.000+02:00"}
    - action_controllo_richiesta
    - slot{"data": "2019-06-21"}
    - slot{"orario": null}
    - slot{"num_persone": null}
    - prenotazione_form
    - form{"name": "prenotazione_form"}
    - slot{"data": "2019-06-21"}
    - slot{"requested_slot": "orario"}
* form: informa{"number": 9}
    - form: prenotazione_form
    - slot{"orario": "21:00:00.000+02:00"}
    - slot{"requested_slot": "num_persone"}
* form: informa{"number": 3}
    - form: prenotazione_form
    - slot{"num_persone": 3}
    - form{"name": null}
    - slot{"requested_slot": null}
    - action_check_calendar
    - slot{"available_seats": true}
* afferma
    - action_insert_calendar
    - slot{"conferma_prenotazione": true}
* saluto_finale
    - utter_saluto_finale

## Generated Story -989188352814597707
* richiesta_di_prenotazione{"time": "2019-06-21T00:00:00.000+02:00"}
    - action_controllo_richiesta
    - slot{"data": "2019-06-21"}
    - slot{"orario": null}
    - slot{"num_persone": null}
    - prenotazione_form
    - form{"name": "prenotazione_form"}
    - slot{"data": "2019-06-21"}
    - slot{"requested_slot": "orario"}
* form: informa{"number": 9}
    - form: prenotazione_form
    - slot{"orario": "21:00:00.000+02:00"}
    - slot{"requested_slot": "num_persone"}
* form: informa{"number": 3}
    - form: prenotazione_form
    - slot{"num_persone": 3}
    - form{"name": null}
    - slot{"requested_slot": null}
    - action_check_calendar
    - slot{"available_seats": true}
* nega
    - action_insert_calendar
    - slot{"conferma_prenotazione": false}

## Generated Story -6559317164413973936
* saluto_iniziale
    - utter_saluto_iniziale
* informazioni_apertura
    - utter_informazioni_apertura
* richiesta_di_prenotazione
    - action_controllo_richiesta
    - slot{"data": null}
    - slot{"orario": null}
    - slot{"num_persone": null}
    - prenotazione_form
    - form{"name": "prenotazione_form"}
    - slot{"requested_slot": "data"}
* form: informa{"time": "2019-06-25T00:00:00.000+02:00"}
    - form: prenotazione_form
    - slot{"data": "2019-06-25"}
    - slot{"requested_slot": "orario"}
* form: informa{"time": "2019-06-24T13:00:00.000+02:00"}
    - form: prenotazione_form
    - slot{"orario": "13:00:00.000+02:00"}
    - slot{"requested_slot": "num_persone"}
* form: informa{"number": 3}
    - form: prenotazione_form
    - slot{"num_persone": 3}
    - form{"name": null}
    - slot{"requested_slot": null}
    - action_check_calendar
    - slot{"available_seats": true}
* afferma
    - action_insert_calendar
    - slot{"conferma_prenotazione": true}
* saluto_finale
    - utter_saluto_finale
