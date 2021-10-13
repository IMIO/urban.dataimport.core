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
    'Déclaration': 'Declaration',
    'DECLARATION URBANISTIQUE': 'Declaration',
    'DECLARATION': 'Declaration',
    'déclaration': 'Declaration',
    'déclaratiion': 'Declaration',
    'Déclarataion': 'Declaration',
    'Unique': 'UniqueLicence',
    'UNIQUE': 'UniqueLicence',
    'Un ique': 'UniqueLicence',
    'Saisine': 'Article127',
    'SAISINE': 'Article127',
    'Saisine FD': 'Article127',
    'Recours': 'Article127',
    'D.VI.22': 'Article127',
    'D.IV.22': 'Article127',
    'D.IV,22': 'Article127',
    '127': 'Article127',
    'Article 127': 'Article127',
    'Art. 127': 'Article127',
    'Art.127': 'Article127',
    # 'PP': 'BuidLicence',  # Petit permis
    # 'Petit perrmis': 'BuidLicence',  # Petit permis
    # 'petit permis': 'BuidLicence',  # Petit permis
    # 'Petit Permis': 'BuidLicence',  # Petit permis
    # 'PETIT PERMIS': 'BuidLicence',  # Petit permis
    # 'Petit permis': 'BuidLicence',  # Petit permis
    # 'Octroi FD': 'BuidLicence',  # Petit permis
    'Intégré': 'IntegratedLicence',
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
    '01': 62046,
    '02': 62054,
    '03': 62453,
    '04': 62454,
    '05': 62105,
    '06': 62016,
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
