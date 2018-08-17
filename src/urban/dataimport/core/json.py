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
        'workLocations': '',
        'applicants': [],
        'parcels': []
    }


def get_applicant_dict():
    return {
        'lastname': '',
        'firstname': ''
    }


def get_parcel_dict():
    return {
        'complete_name': '',
        'division': '',
        'section': '',
        'radical': '',
        'bis': '',
        'exposant': '',
        'puissance': ''
    }


def get_event_dict():
    return {
        'type': '',
        'date': '',
        'investigationStart': '',
        'investigationEnd': '',
        'investigationReasons': '',
        'decision': '',
    }


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)
