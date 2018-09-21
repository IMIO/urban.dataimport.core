# -*- coding: utf-8 -*-
import json
from datetime import datetime


def get_licence_dict():
    return {
        'id': '',
        'portalType': '',
        'reference': '',
        'referenceDGATLP': '',
        'subject': '',
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
    }


def get_parcel_dict():
    return {
        'complete_name': '',
        'old_parcel': '',
        'division': '',
        'section': '',
        'radical': '',
        'bis': '',
        'exposant': '',
        'puissance': '',
    }


def get_event_dict():
    return {
        'type': '',
        'eventDate': '',
        'investigationStart': '',
        'investigationEnd': '',
        'investigationReasons': '',
        'decisionDate': '',
        'decision': '',
    }


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)
