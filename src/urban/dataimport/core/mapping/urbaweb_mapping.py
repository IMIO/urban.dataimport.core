events_types = {
        # 'recepisse': {
        # },
        # 'completefolder': {
        # },
        # 'incompletefolder': {
        # },
        # 'not_receivable': {
        # },
        # 'sendtofd': {
        # },
        'decision': {
        },
}

portal_type_mapping = {
    1: 'BuildLicence',
    2: 'ParcelOutLicence',
    3: 'UrbanCertificateOne',
    4: 'UrbanCertificateTwo',
    5: 'PreliminaryNotice',
    6: 'EnvClassOne',
    7: 'MiscDemand',  # DeclarationImpetrant
    8: 'NotaryLetter',
    9: 'Declaration',
    10: 'UniqueLicence',
    11: 'MiscDemand',
    16: 'ParcelOutLicence',
    17: 'EnvClassThree',
    18: 'MiscDemand',  # Infraction
    19: 'MiscDemand',  # Permis Location
    21: 'MiscDemand',  # Insalubrités logement
    22: 'CODT_CommercialLicence',
    23: 'CODT_BuildLicence',
    24: 'CODT_UrbanCertificateTwo',
    25: 'CODT_ParcelOutLicence',
    26: 'Infraction CODT',   # ?
    27: 'ProjectMeeting',
}

decision_code_mapping = {
    '0': 'Favorable',
    '1': 'Favorable conditionné',
    '2': 'Défavorable',
    '3': 'Réputé Favorable',
    '4': '',
    '': '',
}

view_endpoint_mapping = {
    'permis_env_vue': '@envclasstwo'
}

# division code, to update for specific locality, by default b.l'a
# division_mapping = {
#     '01': 25014,
#     '02': 25742,
#     '03': 25743,
#     '04': 25744,
#     '05': 25054,
#     '06': 25078
# }
division_mapping = {
    '01': 55008,
    '02': 55009,
    '03': 55024
}

# title ids, to update for specific locality, by default b.l'a
title_types = {
    8: 'mister',
    49: 'mister',
    54: 'mister',
    7: 'misters',
    45: 'misters',
    46: 'misters',
    1: 'madam',
    30: 'madam',
    5: 'ladies',
    41: 'ladies',
    44: 'ladies',
    38: 'madam',
    9: 'madam_and_mister',
    27: 'madam_and_mister',
    50: 'madam_and_mister',
    3: 'master',
    39: 'master',
    52: 'master',
    40: 'masters',
    4: 'masters',
}

licence_status_mapping = {
    '0': '',
    '1': 'Octroi',
    '2': 'Irrecevable',
    '3': 'Refusé Tutelle',
    '4': 'Octroi Tutelle',
}
