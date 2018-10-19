# -*- coding: utf-8 -*-
import requests


def get_query(url, header):
    return requests.get(url, headers=header)


def post_query(url, header, data):
    return requests.post(url, headers=header, data=data)


def delete_query(url, header):
    return requests.delete(url, headers=header)


def search_query(url, header):
    return requests.get(url, headers=header)
