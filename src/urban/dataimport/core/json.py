# -*- coding: utf-8 -*-
import json
from datetime import datetime


def get_request_dict():
    return {
        "client_id": "LIEGE",
        "application_id": "URBAN",
        "request_type": "POST",
        "path": "/@buildlicence",
        "parameters": ""
    }


def get_licence_dict():
    return {
        # 'id': '',
        'portalType': '',
        'reference': '',
        'Title': '',
        'referenceDGATLP': '',
        'licenceSubject': '',
        'review_state': '',
        'wf_transition': '',
        'wf_state': '',
        'description': '',
        'workLocations': [],
        'architects': [],
        'notaries': [],
        'geometricians': [],
        'rubrics': [],
        '__children__': [],
    }


def get_work_locations_dict():
    return {
        'number': '',
        'street': '',
        'locality': '',
        'bestaddress_key': '',
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


def get_organization_dict():
    return {
        '@type': '',
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
        'force_create': 'True',
    }


def get_parcel_dict():
    return {
        '@type': 'Parcel',
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
        'event_id': '',
        'type': '',
        'eventPortalType': '',
        'eventDate': '',
        'decisionDate': '',
        'decision': '',
    }


def get_attachment_dict():
    return {
        "@type": "File",
        "title": '',
        "description": "",
        "file": {
            "data": "",
            "encoding": "base64",
            "filename": "",
            "content-type": ""
        }
    }


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        try:
            if isinstance(o, datetime):
                return o.isoformat()

            return json.JSONEncoder.default(self, o)
        except Exception as e:
            print("debug")
