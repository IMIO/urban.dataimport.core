
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
    -106391: 'CODT_ParcelOutLicence',
    -100942: 'CODT_UrbanCertificateTwo',
    -100648: 'CODT_UrbanCertificateOne',
    -96223: 'CODT_BuildLicence',
    -92968: 'CODT_CommercialLicence',
    -92498: 'CODT_CommercialLicence',
    -88291: 'CODT_CommercialLicence',
    -80932: 'CODT_CommercialLicence',
    -77233: 'MiscDemand',
    -67348: 'EnvClassOne',
    -62737: 'ParcelOutLicence',
    -58199: '',  # to complete or ignore
    -57728: 'EnvClassTwo',
    -53925: 'UniqueLicence',
    -52990: '',  # to complete or ignore
    -49306: 'Article127',
    -46623: 'EnvClassThree',
    -42575: 'BuildLicence',
    -40086: 'ParcelOutLicence',
    -37624: 'EnvClassOne',
    # -36624: 'MiscDemand',  # infractions
    -34766: 'UrbanCertificateOne',
    -32669: 'BuildLicence',  # ?
    -28278: '',  # to complete or ignore
    -26124: 'ParcelOutLicence',
    -25638: 'MiscDemand',
    -21454: 'MiscDemand',
    -20646: 'Article127',
    -19184: 'EnvClassTwo',
    -17277: 'BuildLicence',
    -15200: 'Declaration',
    -14333: 'MiscDemand',  # reclamations
    -14179: 'Division',
    # -13467: '',  # infractions remove id in view
    -11889: '',  # to complete or ignore
    -10362: 'MiscDemand',  # demande de principe
    -10200: '',  # to complete or ignore
    -7812: '',  # to complete or ignore
    -6523: '',  # to complete or ignore
    -5976: 'EnvClassThree',
    -5753: 'UrbanCertificateOne',
    -4775: '',  # to complete or ignore
    -3575: '',  # to complete or ignore
    -2982: 'UrbanCertificateOne',  # or UrbanCertificateTwo see TYPEIDENT
    -1972: '',  # to complete or ignore
    -1014: '',  # to complete or ignore
    900510: 'ParcelOutLicence',
    900538: 'BuildLicence',
    1049197: 'EnvClassTwo',
    1120089: 'EnvClassOne',
    1120967: 'EnvClassThree',
}

# urbmessagestatus table
state_mapping = {
    -58: 'refuse',  # demande irrecevable
    -50: 'refuse',  # refusé
    -49: 'accept',  # octroyé
    -48: 'refuse',  # Permis refusé suite levée suspension
    -47: 'accept',  # Permis octroyé suite levée suspension
    -46: 'retire',  # annulation du permis
    -45: 'retire',  # Annulation du permis suite décision du Gvt
    -44: 'refuse',  # Modif. refusée suite décision confirmée
    -43: 'refuse',  # Permis refusé suite décision confirmée
    -42: 'accept',  # Octroi cond. suite décision confirmée
    -41: 'accept',  # Modif. octroyée suite décision confirmée
    -40: 'accept',  # Permis octroyé suite décision confirmée
    -39: 'refuse',  # Demande rejetée
    -38: 'refuse',  # Révision refusée par FT
    -37: 'refuse',  # Révision refusée par le collège
    -36: 'accept',  # Révision octroyée par FT
    -35: 'accept',  # Révision octroyée par le collège
    -34: 'refuse',  # RS vaut refus : refusé ?
    -33: 'retire',  # clôturé donc annulé ? pas de statut
    -32: 'accept',  # RS vaut octroi : octroyé ?
    -31: 'accept',  # déclaration recevable par défaut
    -30: 'accept',  # déclaration recevable sans condition complémentaire
    -29: '',        # recours, état en cours ?
    -28: '',        # introduction d'un recours, état en cours ?
    -27: 'accept',  # recevable avec condition complémentaire
    -26: 'accept',  # octroi conditionnel
    -25: 'refuse',  # Permis refusé par le FT/FD
    -24: 'accept',  # Octroi partiel du permis par le FT/FD
    -23: 'accept',  # octroyé par le FT
    -22: 'refuse',  # Pas décision recours - Refusé
    -21: 'accept',  # Pas décision recours - Octroyé
    -20: '',        # recours en cours
    -19: 'retire',  # périmé
    -18: 'refuse',  # refusé par le collège
    -17: 'refuse',  # refus par le FT
    -16: 'accept',  # octroyé partiellement par le FT
    -15: 'accept',  # octroyé par le FT
    -14: 'accept',  # octroi partiel
    -13: 'retire',  # suspendu
    -12: 'accept',  # délivré
    -11: 'retire',  # retiré
    -10: 'retire',  # annulé
    -9: '',         # état inconnu
    -8: 'refuse',   # irrecevable
    -7: 'accept',   # recevable
    -6: 'accept',   # octroyé sur recours
    -5: 'refuse',   # refusé
    -4: 'retire',   # suspendu
    -3: '',         # en cours
    -2: 'retire',   # abandonné
    -1: '',         # en cours
    0: 'refuse',    # refusé
    1: 'accept',    # octroyé
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
    '01': '25091',
    '02': '25033',
    '03': '25092',
}

decision_label_mapping = {
    '': '',
}
