
events_types = {
        'recepisse': {
            'etape_ids': (-65091, -55774, -48189, -46732, -42670, -33521),
            'param_ids': (),
        },
        'completefolder': {
            'etape_ids': (-42831, -63928, -66924, -33526),
            'param_ids': (),
        },
        'incompletefolder': {
            'etape_ids': (-33547, -42845),
            'param_ids': (),
        },
        'sendtofd': {
            'etape_ids': (-43482, -63977, -33553),
            'param_ids': (),
        },
        'sendtoapplicant': {
            'etape_ids': (-63981, -33551, -43468),
            'param_ids': (),
        },
        'decision': {
            'etape_ids': (-43439, -33545, -63967, -55736, -38452, -49801),
            'param_ids': (-35039, -79378, -78845, -78319, -49413, -62984),
        },
}

portal_type_mapping = {
    -67348: 'EnvClassTwo',
    -62737: 'ParcelOutLicence',
    -53925: 'UniqueLicence',
    -49306: 'Article127',
    -46623: 'EnvClassThree',
    -42575: 'BuildLicence',
    -37624: 'EnvClassTwo',
    -36624: '',  # infractions, not yet implemented
    -34766: 'NotaryLetter',
    -32669: 'BuildLicence',  # ?
    -15200: 'Declaration',
    -14179: 'Division',
}

state_mapping = {
    -58: 'refuse',  # irrecevable (validé par chatelet)
    -49: 'accept',  # -49 = octroyé
    -46: 'refuse',  # -46 = annulé par le FD
    -30: 'accept',  # recevable (validé par chatelet)
    -27: 'accept',  # recevable avec condition (validé par chatelet)
    -26: 'accept',  # -26 = octroyé
    -20: 'refuse',  # refus, ministre sur recours (validé par chatelet)
    -19: 'retire',  # -19 = périmé
    -17: 'refuse',  # refus (FT) (validé par chatelet)
    -15: 'accept',  # accepté (FT) (validé par chatelet)
    -14: 'accept',  # -14 = octroyé
    -12: 'accept',  # -12 = octroyé (validé par Fl)
    -11: 'retire',  # -11 = retiré
    -10: 'retire',  # -10 = retiré (validé par Fl)
    -8: 'refuse',  # irrecevable (validé par chatelet)
    -7: 'accept',  # recevable (validé par chatelet)
    -6: 'accept',  # -6 = octroyé (validé par Fl)
    -5: 'refuse',  # -5 = refusé
    -4: 'retire',  # -4 = suspendu
    -3: 'accept',  # -3 = octroyé
    -2: 'retire',  # -2 = abandonné
    -1: '',  # -1 = en cours
    0: 'refuse',  # -1 = refusé
    1: 'accept',  # 1 = octroyé
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
    '01': '52022',
    '02': '52023',
    '03': '52038',
}
