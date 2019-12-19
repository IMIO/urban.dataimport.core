events_types = {
        'recepisse': {
        },
        # 'completefolder': {
        # },
        # 'incompletefolder': {
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
    7: 'DeclarationImpetrant',  # ?
    8: 'NotaryLetter',
    9: 'Declaration',
    10: 'UniqueLicence',
    11: 'MiscDemand',
    16: 'ParcelOutLicence',
    17: 'EnvClassThree',
    18: 'Infraction',  # ?
    19: 'PermisLocation',  # ?
    21: 'CODT_CommercialLicence',  # ?
    22: 'RoadDecree',
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

division_mapping = {
    '01': 25014,
    '02': 25742,
    '03': 25743,
    '04': 25744,
    '05': 25054,
    '06': 25078
}
