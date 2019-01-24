# -*- coding: utf-8 -*-
import json
from datetime import datetime


def get_licence_dict():
    return {
        'id': '',
        'portalType': '',
        'reference': '',
        'referenceDGATLP': '',
        'licenceSubject': '',
        'completionState': '',
        'description': '',
        'workLocations': [],
        'applicants': [],
        'parcels': [],
        'events': [],
    }


def get_work_locations_dict():
    return {
        'number': '',
        'street': '',
    }


def get_applicant_dict():
    return {
        '@type': 'Applicant',
        'personTitle': '',
        'name1': '',
        'name2': '',
        'email': '',
        'phone': '',
        'gsm': '',
        'fax': '',
        'street': '',
        'zipcode': '',
        'city': '',
        'country': '',
    }


def get_parcel_dict():
    return {
        '@type': 'PortionOut',
        'complete_name': '',
        'outdated': '',
        'division': '',
        'section': '',
        'radical': '',
        'bis': '',
        'exposant': '',
        'puissance': '',
    }


def get_event_dict():
    return {
        '@type': 'UrbanEvent',
        'urbaneventtypes': '',
        'type': '',
        'eventDate': '',
        'decisionDate': '',
        'decision': '',
    }


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)
