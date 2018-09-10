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
        'workLocations': [],
        'applicants': [],
        'parcels': [],
        'events': [],
    }


def get_work_locations_dict():
    return {
        'number': '',
        'address': '',
        'postalcode': '',
        'locality': ''
    }


def get_applicant_dict():
    return {
        'lastname': '',
        'firstname': ''
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
