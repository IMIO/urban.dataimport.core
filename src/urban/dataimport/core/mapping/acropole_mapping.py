
events_types = {
        'recepisse': {
            'etape_ids': (-65091, -55774, -48189, -46732, -42670, -33521),
            'param_ids': (),
        },
        # 'completefolder': {
        #     'etape_ids': (-42831, -63928, -66924, -33526),
        #     'param_ids': (),
        # },
        # 'incompletefolder': {
        #     'etape_ids': (-33547, -42845),
        #     'param_ids': (),
        # },
        # 'sendtofd': {
        #     'etape_ids': (-43482, -63977, -33553),
        #     'param_ids': (),
        # },
        # 'sendtoapplicant': {
        #     'etape_ids': (-63981, -33551, -43468),
        #     'param_ids': (),
        # },
        'decision': {
            'etape_ids': (-43439,
                          -33545,
                          -63967,  # Permis urbanisation délivrance permis: date de décision
                          -55736,
                          -38452,
                          -49801,  # Article127 délivrance permis: date de décision
                          -15243,  # Déclaration rapport du collège: date de décision
                          -35865,  # Annexe49 pour les NL/CU: date de décision
                          -14296   # Division rapport du service: date de décision
                          ),
            'param_ids': (-35039, -79378, -78845, -78319, -49413, -62984),
        },
}

main_state_id_mapping = [0, 1]

portal_type_mapping = {
    'Article 127': 'Article127',
    'Déclaration': 'Declaration',
    'Déclaration environnementale': 'EnvClassThree',
    "Demande d'avis préalable": 'PreliminaryNotice',
    'Demandes diverses': 'MiscDemand',
    'Division': 'Division',
    'Lettre de notaire': 'NotaryLetter',
    "Permis d'environnement classe 1": 'EnvClassOne',
    "Permis d'environnement classe 2": 'EnvClassTwo',
    "Permis d'environnement limitrophes": 'EnvClassBordering',
    "Permis d'urbanisation": 'ParcelOutLicence',
    "Permis d'urbanisme": 'BuildLicence',
    "Permis unique": 'UniqueLicence',
}

# urbmessagestatus table
state_mapping = {
    'Annulé / Abandonné': 'retire',   # abandonné
    'En cours': '',         # en cours
    'Refusé': 'refuse',    # refusé
    'Accepté' : 'accept',    # octroyé
}

accepted_main_label_mapping = {
    'BuildLicence': 'Permis octroyé',
    'Article127': 'Permis octroyé',
    'ParcelOutLicence': 'Permis octroyé',
    'UniqueLicence': 'Permis octroyé',
    'Declaration': 'Permis octroyé',
    'Division': 'Division traitée',
    'UrbanCertificateOne': 'Certificat octroyé',
    'UrbanCertificateTwo': 'Certificat octroyé',
    'EnvClassOne': 'Permis octroyé',
    'EnvClassTwo': 'Permis octroyé',
    'EnvClassThree': 'Déclaration recevable',
    'MiscDemand': 'Demande traitée',
}

refused_main_label_mapping = {
    'BuildLicence': 'Permis refusé',
    'Article127': 'Permis refusé',
    'ParcelOutLicence': 'Permis refusé',
    'UniqueLicence': 'Permis refusé',
    'Declaration': 'Permis refusé',
    'Division': 'Division refusée',
    'UrbanCertificateOne': 'Certificat refusé',
    'UrbanCertificateTwo': 'Certificat refusé',
    'EnvClassOne': 'Permis refusé',
    'EnvClassTwo': 'Permis refusé',
    'EnvClassThree': 'Déclaration irrecevable',
    'MiscDemand': 'Refusé',
}


decision_vocabulary_mapping = {
    'accept': 'favorable',
    'refuse': 'defavorable',
    'retire': '',
}

custom_state_label_mapping = {
    '-2': 'Annulé / Abandonné',
    '-3': 'Dossier en cours (étape non clôturée)',
    '-4': 'Permis suspendu',
    '-5': 'Refusé sur recours',
    '-6': 'Octroyé sur recours',
    '-7': 'Déclaration recevable',
    '-8': 'Déclaration irrecevable',
    '-9': 'Etat particulier',
    '-10': 'Annulation par GW',
    '-11': 'Permis retiré par le Collège',
    '-12': 'Permis délivré',
    '-13': 'Dossier suspendu par régularisation',
    '-14': 'Octroi partiel du permis',
    '-15': 'Permis octroyé par le FT',
    '-16': 'Octroi partiel du permis par le FT',
    '-17': 'Permis refusé par le FT',
    '-18': 'Permis refusé par le Collège',
    '-19': 'Permis périmé',
    '-20': 'Recours en cours',
    '-21': 'Pas décision recours - Octroyé',
    '-22': 'Pas décision recours - Refusé',
    '-23': 'Permis octroyé par le FT/FD',
    '-24': 'Octroi partiel du permis par le FT/FD',
    '-25': 'Permis refusé par le FT/FD',
    '-26': 'Octroi conditionnel du permis',
    '-27': 'Déc. recevable avec cond. compl.',
    '-28': 'Introduction d\'un recours',
    '-29': 'Recours',
    '-30': 'Déc. recevable sans cond. compl.',
    '-31': 'Déc. recevable par défaut',
    '-32': 'RS vaut octroi',
    '-33': 'Dossier clôturé',
    '-34': 'RS vaut refus',
    '-35': 'Révision octroyée par le collège',
    '-36': 'Révision octroyée par le FT',
    '-37': 'Révision refusée par le collège',
    '-38': 'Révision refusée par le FT',
    '-39': 'Demande rejetée',
    '-40': 'Permis octroyé suite décision confirmée',
    '-41': 'Modif. octroyée suite décision confirmée',
    '-42': 'Octroi cond. suite décision confirmée',
    '-43': 'Permis refusé suite décision confirmée',
    '-44': 'Modif. refusée suite décision confirmée',
    '-45': 'Annulation du permis suite décision du Gvt',
    '-46': 'Annulation du permis',
    '-47': 'Permis octroyé suite levée suspension',
    '-48': 'Permis refusé suite levée suspension',
    '-49': 'Permis octroyé',
    '-50': 'Permis refusé',
    '-52': 'Recours contre le projet',
    '-53': 'Projet approuvé',
    '-54': 'Projet refusé',
    '-55': 'Approuvé sur recours',
    '-56': 'Refusé sur recours',
    '-57': 'Refus tacite',
    '-58': 'Demande irrecevable',
    '-59': 'Décision dont recours confirmé par défaut',
    '-60': 'Dossier refusé suite saisine',
    '-61': 'Dossier octroyé suite saisine',
    '-62': 'Refusé par recours suite saisine',
    '-63': 'Octroyé par recours suite saisine',
    '-64': 'Permis de location délivré',
    '-65': 'Arrêté d\'inhabitabilité et de surpeuplement',
    '-66': 'Arrêté d\'inhabitabilité',
    '-67': 'Attestation de surpeuplement',
    '-68': 'Permis de location refusé',
    '-69': 'Permis de location retiré',
    '-70': 'Permis de location supprimé',
    '-71': 'Recours introduit',
    '-72': 'Permis de location octroyé sur recours',
    '-73': 'Permis de location refusé sur recours',
    '-74': 'Arrêté d\'inhabitabilité confirmé sur recours',
    '-75': 'Arrêté d\'inhabitabilité annulé sur recours',
    '-76': 'Plans modifiés introduits',
    '-77': 'Recours irrecevable',
    '-78': 'Dossier en infraction',
    '-79': 'Dossier régularisé',
    '-80': 'Attestation de conformité délivrée',
    '-81': 'Retour situation unifamiliale',
    '-82': 'Octroi partiel',
    '-83': 'Autorisation octroyée',
    '-84': 'Autorisation refusée',
    '-85': 'Autorisation octroyée sur recours',
    '-86': 'Autorisation refusée sur recours',
    '-87': 'Plans modifiés en cours',
    '-88': 'Voirie refusée',
    '-89': 'Voirie autorisée',
    '-90': 'Voirie réputée refusée',
    '-91': 'Recours voirie en cours',
    '-92': 'Voirie refusée sur recours',
    '-93': 'Voirie autorisée sur recours',
    '-94': 'Pas décision recours - voirie refusée',
    '-95': 'Pas décision recours - voirie autorisée',
    '-96': 'Permis octroyé par FIC/FT',
    '-97': 'Permis refusé par FIC/FT',
    '-98': 'Permis octroyé par FIC/FT/FD',
    '-99': 'Permis refusé par FIC/FT/FD',
    '-100': 'Permis octroyé par FIC/FD',
    '-101': 'Permis refusé par FIC/FD',
    '-102': 'Permis octroyé par le FIC',
    '-103': 'Permis refusé par le FIC',
    '-104': 'Octroi partiel sur recours',
}


title_types = {
    -1000: 'mister',
    21607: 'misters',
    -1001: 'madam',
    171280: 'ladies',
    -1002: 'miss',
    -1003: 'madam_and_mister',
    676263: 'madam_and_mister',
    850199: 'madam_and_mister',
    89801: 'master',
}

# custom to the locality
division_mapping = {
    '01': '62096',
    '02': '62352',
    '03': '62353',
    '04': '62354',
    '05': '62355',
    '06': '62356',
    '07': '62357',
    '08': '62358',
    '09': '62058',
    '10': '62342',
    '11': '62343',
    '12': '62019',
}

decision_label_mapping = {
    '': '',
}
