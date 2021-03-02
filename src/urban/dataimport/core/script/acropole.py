# -*- coding: utf-8 -*-
import re

from progress.bar import FillingSquaresBar
from sqlalchemy import create_engine
from urban.dataimport.core import utils
from urban.dataimport.core.db import LazyDB
from urban.dataimport.core.mapping.acropole_mapping import events_types, portal_type_mapping, \
    state_mapping, title_types, division_mapping, decision_label_mapping

import argparse
import configparser
import json
import time
import unidecode

from urban.dataimport.core.json import DateTimeEncoder, get_applicant_dict, get_event_dict, get_licence_dict, \
    get_parcel_dict, get_work_locations_dict, get_organization_dict
from urban.dataimport.core.mapping.main_mapping import main_licence_deposit_event_id_mapping, \
    main_licence_decision_event_id_mapping
from urban.dataimport.core.utils import parse_cadastral_reference, benchmark_decorator, BaseImport, \
    export_to_customer_json, represent_int, ErrorToCsv, export_error_csv
from urban.dataimport.core.utils import StateManager
from urban.dataimport.core.utils import StateHandler
from urban.dataimport.core.utils import IterationError
from urban.dataimport.core.views.acropole_views import create_views, create_concat_views
from urban.dataimport.core.views.cadastral_views import create_cadastral_views
from urban.dataimport.core.views.bestaddress_views import create_bestaddress_views


class ImportAcropole(BaseImport):

    def __init__(self, config_file, limit=None, range=None, view=None, licence_id=None, ignore_cache=False, benchmarking=False, noop=False, iterate=False):
        print("INITIALIZING")
        self.start_time = time.time()
        self.benchmarking = benchmarking
        self.noop = noop
        self.iterate = iterate
        if self.benchmarking:
            self._benchmark = {}
        config = configparser.ConfigParser()
        config_file = utils.format_path(config_file)
        config.read(config_file)
        self.config = config
        self.limit = limit
        self.range = range
        self.view = view
        self.licence_id = licence_id
        self.search_old_parcels = config['main']['search_old_parcels']
        engine = create_engine('mysql://{user}:{password}@{host}:{port}'.format(**config._sections['database']))
        connection = engine.connect()
        self.db = LazyDB(
            connection,
            config['database']['schema'],
            ignore_cache=ignore_cache,
        )
        engine_cadastral = create_engine('postgresql://{user}:{password}@{host}:{port}'.format(
            **config._sections['cadastral_database']))
        connection_cadastral = engine_cadastral.connect()
        self.cadastral = LazyDB(
            connection_cadastral,
            config['cadastral_database']['schema'],
            ignore_cache=ignore_cache,
        )
        engine_bestaddress = create_engine('postgresql://{user}:{password}@{host}:{port}'.format(
            **config._sections['bestaddress_database']))
        connection_bestaddress = engine_bestaddress.connect()
        self.bestaddress = LazyDB(
            connection_bestaddress,
            config['bestaddress_database']['schema'],
            ignore_cache=ignore_cache,
        )
        create_concat_views(self)
        create_views(self)
        create_cadastral_views(self)
        create_bestaddress_views(self, config['main']['locality'])
        self.street_errors = []
        self.parcel_errors = []
        print("INITIALIZATION COMPLETED")

    def execute(self):
        self.data = []

        error = None
        try:
            self.extract_data()
        except Exception as e:
            error = e

        if self.noop:
            print(json.dumps(self.data, indent=4, sort_keys=True, cls=DateTimeEncoder))
        if not self.noop and error is None:
            with open("{0}.{1}".format(self.config['main']['output_path'], "json"), 'w') as output_file:
                json.dump(self.data, output_file, cls=DateTimeEncoder)
            export_to_customer_json(self)
        print("-- {0} folders extracted --".format(len(self.data)))
        print("--- Total Duration --- %s seconds ---" % (time.time() - self.start_time))
        if self.benchmarking:
            print(json.dumps(self._benchmark, indent=4, sort_keys=True))
        if error:
            raise error

    @StateManager
    def extract_data(self):
        folders = getattr(self.db, self.view)
        if self.range:
            folders = folders[int(self.range.split(':')[0]):int(self.range.split(':')[1])]
        if self.limit:
            folders = folders.head(self.limit)
        if self.licence_id:
            folders = folders[folders.DOSSIER_NUMERO == self.licence_id]

        bar = FillingSquaresBar('Processing licences', max=folders.shape[0])
        for id, licence in folders.iterrows():
            self.get_licence(id, licence)
            bar.next()
        bar.finish()
        export_error_csv([self.parcel_errors, self.street_errors])
        if self.iterate is True:
            try:
                self.validate_data(self.data, 'GenericLicence')
            except Exception:
                raise IterationError('Schema change during iterative process')

    @StateHandler('data', 'acropole_get_licence')
    def get_licence(self, id, licence):
        self.licence_description = []
        licence_dict = get_licence_dict()
        # licence_dict['id'] = str(licence.WRKDOSSIER_ID)
        licence_dict['portalType'] = self.get_portal_type(licence)  # licence type must be the first licence set
        if not licence_dict['portalType']:
            return
        licence_dict["@type"] = licence_dict["portalType"]
        # licence completionState must be the second licence set
        # licence_dict['investigationStart'] = self.get_inquiry_values(licence, 'investigationStart')
        # licence_dict['investigationEnd'] = self.get_inquiry_values(licence, 'investigationEnd')
        # investigation_reasons = self.get_inquiry_values(licence, 'investigationReasons')
        # if investigation_reasons:
        #     licence_dict['investigationReasons'] = [investigation_reasons]
        licence_dict['reference'] = "{}/{}".format(licence.WRKDOSSIER_ID, licence.DOSSIER_NUMERO)
        # licence_dict['referenceDGATLP'] = licence.DOSSIER_REFURB and licence.DOSSIER_REFURB or ''
        licenceSubject = licence.DOSSIER_OBJETFR or licence.DETAILS
        licence_dict['licenceSubject'] = licenceSubject
        if licence.DOSSIER_REFCOM:
            self.licence_description.append({'REFERENCE COM': licence.DOSSIER_REFCOM})
        licence_dict['usage'] = 'not_applicable'
        licence_dict['workLocations'] = self.get_work_locations(licence, licence_dict)
        self.get_organization(licence, licence_dict)
        self.get_applicants(licence, licence_dict['__children__'])
        self.get_parcels(licence, licence_dict['__children__'])
        self.get_events(licence, licence_dict)
        description = str(''.join(str(d) for d in self.licence_description))
        licence_dict['description'] = {
            'data': "{}{} - {}{}".format("<p>", str(licence.DETAILS).replace("\n", ""), description, "</p>"),
            'content-type': 'text/html'
        }  # description must be the last licence set
        self.validate_schema(licence_dict, 'GenericLicence')
        request_dict = licence_dict

        return request_dict

    @benchmark_decorator
    def get_portal_type(self, licence):
        portal_type = portal_type_mapping.get(licence.DOSSIER_TDOSSIERID, None)
        # if portal_type == 'UrbanCertificateOne' and licence.DOSSIER_TYPEIDENT == 'CU2':
        #     portal_type = 'UrbanCertificateTwo'
        return portal_type

    @benchmark_decorator
    def get_inquiry_values(self, licence, field):
        inquiry = self.db.dossier_enquete
        if field == 'investigationReasons':
            inquiry_value = inquiry[
                (inquiry.WRKDOSSIER_ID == licence.WRKDOSSIER_ID) &
                (inquiry.PARAM_IDENT == 'EnqObjet')
            ]
            if inquiry_value.REMARQ_LIB.shape[0] == 1:
                return inquiry_value.iloc[0]['REMARQ_LIB']
        elif field == 'investigationStart':
            inquiry_value = inquiry[
                (inquiry.WRKDOSSIER_ID == licence.WRKDOSSIER_ID) &
                (inquiry.PARAM_IDENT == 'EnqDatDeb')
            ]
            if inquiry_value.PARAM_VALUE.shape[0] == 1:
                return inquiry_value.iloc[0]['PARAM_VALUE']
        elif field == 'investigationEnd':
            inquiry_value = inquiry[
                (inquiry.WRKDOSSIER_ID == licence.WRKDOSSIER_ID) &
                (inquiry.PARAM_IDENT == 'EnqDatFin')
            ]
            if inquiry_value.PARAM_VALUE.shape[0] == 1:
                return inquiry_value.iloc[0]['PARAM_VALUE']

    @benchmark_decorator
    def get_work_locations(self, licence, licence_dict):
        work_locations_list = []
        work_locations_dict = get_work_locations_dict()
        if licence.CONCAT_ADRESSES and licence.CONCAT_ADRESSES.replace("@", "").replace("|", ""):
            for wl in licence.CONCAT_ADRESSES.split("@"):
                split_wl = wl.split("|")
                street = split_wl[0]
                number = split_wl[1]
                zipcode = split_wl[2]
                city = split_wl[3]
                if street:
                    # remove parentheses and its content
                    acropole_street = re.sub(r'\([^)]*\)', '', street).strip()
                    acropole_street = re.sub(r'^allée ', 'Allée ', acropole_street).strip()
                    acropole_street = re.sub(r'^Av[.]', 'Avenue', acropole_street).strip()
                    acropole_street = re.sub(r'^avenue ', 'Avenue ', acropole_street).strip()
                    acropole_street = re.sub(r'^boulevard ', 'Boulevard ', acropole_street).strip()
                    acropole_street = re.sub(r'^chaussée ', 'Chaussée ', acropole_street).strip()
                    acropole_street = re.sub(r'^cour ', 'Cour ', acropole_street).strip()
                    acropole_street = re.sub(r'^esplanade ', 'Esplanade ', acropole_street).strip()
                    acropole_street = re.sub(r'^square ', 'Square ', acropole_street).strip()
                    acropole_street = re.sub(r'^quai ', 'Quai ', acropole_street).strip()
                    acropole_street = re.sub(r'^Pl[.]', 'Place', acropole_street).strip()
                    acropole_street = re.sub(r'^Pl ', 'Place ', acropole_street).strip()
                    acropole_street = re.sub(r'^place ', 'Place ', acropole_street).strip()
                    acropole_street = re.sub(r'^voie ', 'Voie ', acropole_street).strip()
                    acropole_street = re.sub(r'^Voie du Pahis', 'voie du Pahis', acropole_street).strip()  # Exception
                    acropole_street = re.sub(r'^rue ', 'Rue ', acropole_street).strip()
                    acropole_street = re.sub(r'^route ', 'Route ', acropole_street).strip()
                    acropole_street = re.sub(r' St ', ' Saint-', acropole_street).strip()
                    acropole_street = re.sub(r' Ste ', ' Sainte-', acropole_street).strip()

                    acropole_street = re.sub(r'Avenue Delporte', 'Avenue H. Delporte', acropole_street).strip()
                    acropole_street = re.sub(r'Rue de Lexhy', 'Rue Arnold de Lexhy', acropole_street).strip()
                    acropole_street = re.sub(r'Rue Dossogne', 'Rue J. Dossogne', acropole_street).strip()
                    acropole_street = re.sub(r'Rue Depas', 'Rue Jean Depas', acropole_street).strip()
                    acropole_street = re.sub(r'Rue des Champs du Mont', 'Rue Champs du Mont', acropole_street).strip()
                    acropole_street = re.sub(r'Rue Salengro', 'Rue Roger Salengro', acropole_street).strip()
                    acropole_street = re.sub(r'Rue Smeets', 'Rue A. Smeets', acropole_street).strip()
                    acropole_street = re.sub(r'Rue Sualems', 'Rue R. Sualems', acropole_street).strip()
                    acropole_street = re.sub(r'Rue Roosevelt', 'Rue Franklin Roosevelt', acropole_street).strip()
                    acropole_street = re.sub(r'Rue Royer', 'Rue Emile Royer', acropole_street).strip()
                    acropole_street = re.sub(r'Rue Servet', 'Rue Michael Servet', acropole_street).strip()
                    acropole_street = re.sub(r'Rue Sualem', 'Rue R. Sualem', acropole_street).strip()
                    acropole_street = re.sub(r'Rue Wettinck', 'Rue J. Wettinck', acropole_street).strip()
                    acropole_street = re.sub(r'Rue Louis', 'Rue J. Louis', acropole_street).strip()
                    acropole_street = re.sub(r'Rue Marcotty', 'Rue T. Marcotty', acropole_street).strip()
                    acropole_street = re.sub(r'Rue Messager', 'Rue du Messager', acropole_street).strip()
                    acropole_street = re.sub(r'Rue Nicolay', 'Rue Ferdinand Nicolay', acropole_street).strip()
                    acropole_street = re.sub(r'Rue Puit-Marie', 'Rue Puit Marie', acropole_street).strip()
                    acropole_street = re.sub(r'Rue Raick', 'Rue Alexandre Raick', acropole_street).strip()
                    acropole_street = re.sub(r'Rue Renard', 'Rue André Renard', acropole_street).strip()
                    acropole_street = re.sub(r'Quai Destrée', 'Quai Jules Destrée', acropole_street).strip()
                    acropole_street = re.sub(r'Rue Blum', 'Rue Léon Blum', acropole_street).strip()
                    acropole_street = re.sub(r'Rue Bruno', 'Rue Gordano Bruno', acropole_street).strip()
                    acropole_street = re.sub(r'Rue Bois Saint-Jean', 'Rue du Bois Saint-Jean', acropole_street).strip()
                    acropole_street = re.sub(r'Rue Bougnet', 'Rue E. Bougnet', acropole_street).strip()
                    acropole_street = re.sub(r'Rue Baivy', 'Rue Gustave Baivy', acropole_street).strip()
                    acropole_street = re.sub(r'Rue de Stappe', 'Rue des Stappes', acropole_street).strip()
                    acropole_street = re.sub(r'Rue del Rodje Cinse', 'Rue dèl Rodje Cinse', acropole_street).strip()
                    acropole_street = re.sub(r'Rue Delbrouck', 'Rue R. Delbrouck', acropole_street).strip()
                    acropole_street = re.sub(r'Rue Deloye', 'Rue S. Deloye', acropole_street).strip()
                    acropole_street = re.sub(r'Rue Delville', 'Rue Antonin Delville', acropole_street).strip()
                    acropole_street = re.sub(r'Rue des Petits Sarts', 'Rue des Petits-Sarts', acropole_street).strip()
                    acropole_street = re.sub(r'Rue des Bas-Sarts', 'Rue des Bas Sarts', acropole_street).strip()
                    acropole_street = re.sub(r'Rue de Brouckère', 'Rue L. De Brouckère', acropole_street).strip()
                    acropole_street = re.sub(r'Rue Janson', 'Rue Paul Janson', acropole_street).strip()
                    # remove unnecessary characters
                    acropole_street = acropole_street.replace(",", " ").strip().replace("?", " ").strip()
                    bestaddress_streets = self.bestaddress.bestaddress_vue[
                        (self.bestaddress.bestaddress_vue.street == acropole_street)
                    ]
                    if bestaddress_streets.shape[0] == 0:
                        # second chance without street number
                        acropole_street_without_digits = ''.join([letter for letter in acropole_street if not letter.isdigit()]).strip()
                        bestaddress_streets = self.bestaddress.bestaddress_vue[
                            (self.bestaddress.bestaddress_vue.street == acropole_street_without_digits)
                        ]
                        if bestaddress_streets.shape[0] == 0:
                            # last chance : try to remove last char, for example : 1a or 36C
                            acropole_street_without_last_char = acropole_street_without_digits.strip()[:-1]
                            bestaddress_streets = self.bestaddress.bestaddress_vue[
                                (self.bestaddress.bestaddress_vue.street == acropole_street_without_last_char.strip())
                            ]
                            if bestaddress_streets.shape[0] == 0:
                                self.street_errors.append(ErrorToCsv("street_errors",
                                                                     "Pas de résultat pour cette rue",
                                                                     licence_dict['reference'],
                                                                     "rue : {} n°: {} cp: {} localité: {}"
                                                                     .format(street,
                                                                             number,
                                                                             zipcode,
                                                                             city)))
                                self.licence_description.append({'objet': "Pas de résultat pour cette rue",
                                                                 'rue': street,
                                                                 'n°': number,
                                                                 'code postal': zipcode,
                                                                 'localité': city
                                                                 })
                                pass

                    result_count = bestaddress_streets.shape[0]
                    if result_count == 1:
                        work_locations_dict['street'] = bestaddress_streets.iloc[0]['street']
                        work_locations_dict['bestaddress_key'] = str(bestaddress_streets.iloc[0]['key'])  # if str(bestaddress_streets.iloc[0]['key']) not in ('7044037', '7008904') else ""
                        work_locations_dict['number'] = str(unidecode.unidecode(number))
                        work_locations_dict['zipcode'] = bestaddress_streets.iloc[0]['zip']
                        work_locations_dict['locality'] = bestaddress_streets.iloc[0]['entity']
                        # self.licence_description.append({'objet': "Rue trouvée",
                        #                                  'rue': street,
                        #                                  'n°': number,
                        #                                  'code postal': zipcode,
                        #                                  'localité': city
                        #                                  })
                    elif result_count > 1:
                        self.licence_description.append({'objet': "Plus d'un seul résultat pour cette rue",
                                                         'rue': street,
                                                         'n°': number,
                                                         'code postal': zipcode,
                                                         'localité': city
                                                         })
                        self.street_errors.append(ErrorToCsv("street_errors",
                                                             "Plus d'un seul résultat pour cette rue",
                                                             licence_dict['reference'],
                                                             "rue : {} n°: {} cp: {} localité: {}"
                                                             .format(street,
                                                                     number,
                                                                     zipcode,
                                                                     city)))
                if work_locations_dict['street'] or work_locations_dict['number']:
                    work_locations_list.append(work_locations_dict)

        return work_locations_list

    @benchmark_decorator
    def get_applicants(self, licence, licence_children):
        if licence.CONCAT_DEMANDEURS:
            for applicant in licence.CONCAT_DEMANDEURS.split('#'):
                applicant_dict = get_applicant_dict()
                applicant_list = applicant.split('|')
                applicant_dict['name1'] = applicant_list[0]
                applicant_dict['name2'] = applicant_list[1]
                applicant_dict['street'] = applicant_list[2]
                applicant_dict['zipcode'] = applicant_list[3]
                applicant_dict['city'] = applicant_list[4]
                applicant_dict['personTitle'] = title_types.get(applicant_list[5], '')
                applicant_dict['phone'] = applicant_list[6]
                applicant_dict['fax'] = applicant_list[7]
                applicant_dict['gsm'] = applicant_list[8]
                applicant_dict['email'] = applicant_list[9]

                licence_children.append(applicant_dict)

    @benchmark_decorator
    def get_parcels(self, licence, licence_children):
        parcels = licence.CONCAT_PARCELS
        if parcels:
            for parcel in parcels.split("@"):
                parcels_dict = get_parcel_dict()
                parcels_dict['complete_name'] = parcel
                parcels_args = parse_cadastral_reference(parcel)
                division_code = parcels_args[0]
                section = parcels_args[1] if parcels_args[1] else ''
                radical = parcels_args[2] if parcels_args[2] else 0
                bis = parcels_args[3] if parcels_args[3] else 0
                exposant = parcels_args[4] if parcels_args[4] else ''
                puissance = parcels_args[5] if parcels_args[5] else 0
                if division_code and section and radical:
                    if represent_int(puissance) and int(puissance) < 100:
                        if represent_int(radical) and represent_int(bis) and represent_int(puissance):
                            division = division_mapping.get(division_code, None)
                            parcelles_cadastrales = self.cadastral.cadastre_parcelles_vue
                            cadastral_parcels = parcelles_cadastrales[
                                (parcelles_cadastrales.division == int(division)) &
                                (parcelles_cadastrales.section == section) &
                                (parcelles_cadastrales.radical == int(radical)) &
                                ((parcelles_cadastrales.bis.isnull()) if not int(bis)
                                 else parcelles_cadastrales.bis == int(bis)) &
                                ((parcelles_cadastrales.exposant.isnull()) if not exposant
                                 else parcelles_cadastrales.exposant == exposant) &
                                ((parcelles_cadastrales.puissance.isnull()) if not int(puissance)
                                 else parcelles_cadastrales.puissance == str(int(puissance)))
                                ]

                            result_count = cadastral_parcels.shape[0]
                            if result_count == 1:
                                parcels_dict['outdated'] = 'False'
                                parcels_dict['is_official'] = 'True'
                                parcels_dict['division'] = str(cadastral_parcels.iloc[0]['division'])
                                parcels_dict['section'] = cadastral_parcels.iloc[0]['section']
                                parcels_dict['radical'] = str(cadastral_parcels.iloc[0]['radical'])
                                parcels_dict['bis'] = str(cadastral_parcels.iloc[0]['bis']) if cadastral_parcels.iloc[0]['bis'] else ""
                                parcels_dict['exposant'] = cadastral_parcels.iloc[0]['exposant']
                                parcels_dict['puissance'] = str(cadastral_parcels.iloc[0]['puissance']) if cadastral_parcels.iloc[0]['puissance'] else ""
                                self.licence_description.append({'objet': "Parcelle trouvée",
                                                                 'parcelle': parcel,
                                                                 })
                            elif result_count > 1:
                                self.licence_description.append({'objet': "Trop de résultats pour cette parcelle",
                                                                 'parcelle': parcel,
                                                                 })
                            else:
                                parcels_dict['outdated'] = 'False'
                                parcels_dict['is_official'] = 'False'
                                parcels_dict['division'] = str(division)
                                parcels_dict['section'] = section
                                parcels_dict['radical'] = str(int(radical))
                                parcels_dict['bis'] = str(int(bis))
                                parcels_dict['exposant'] = exposant
                                parcels_dict['puissance'] = str(int(puissance))
                                self.licence_description.append({'objet': "Pas de résultat pour cette parcelle",
                                                                 'parcelle': parcels_dict['complete_name'],
                                                                 })
                        else:
                            self.licence_description.append({'objet': "Parcelle incomplète ou non valide",
                                                             'parcelle': parcel,
                                                             })
                    else:
                        self.licence_description.append({'objet': "Parcelle incomplète ou non valide",
                                                         'parcelle': parcels_dict['complete_name'],
                                                         })
                else:
                    self.licence_description.append({'objet': "Parcelle incomplète ou non valide",
                                                     'parcelle': parcels_dict['complete_name'],
                                                     })
                if parcels_dict['division'] and parcels_dict['section']:
                    licence_children.append(parcels_dict)

    @benchmark_decorator
    def get_organization(self, licence, licence_dict):
        organization_dict = get_organization_dict()

        # if hasattr(licence, 'ORG_NOM') and licence.ORG_NOM:
        #     check_org_name = licence.ORG_NOM.replace("/", "").replace("-", "").replace(".", "").replace(" ", "")
        #     if check_org_name:
        #         organization_dict['personTitle'] = title_types.get(licence.ORG_TITLE_ID, "")
        #         organization_dict['name1'] = licence.ORG_NOM
        #         organization_dict['name1'] = organization_dict['name1'].replace("/", "").replace(".", " ")
        #         organization_dict['name2'] = licence.ORG_PRENOM
        #         organization_dict['name2'] = organization_dict['name2'].replace("/", "").replace(".", " ")
        #         organization_dict['number'] = unidecode.unidecode(licence.ORG_NUMERO)
        #         organization_dict['street'] = licence.ORG_RUE
        #         organization_dict['zipcode'] = str(int(licence.ORG_CP))
        #         organization_dict['city'] = licence.ORG_LOCALITE
        #         organization_dict['phone'] = licence.ORG_TEL
        #         organization_dict['gsm'] = licence.ORG_MOBILE
        #         organization_dict['email'] = licence.ORG_MAIL
        #
        #         if licence.ORG_TYPE == 'ARCHITECTE' or \
        #            licence.ORG_TYPE == 'ARCHITECTE|DEMANDEUR_CU' or \
        #            licence.ORG_TYPE == 'DEMANDEUR_CU' or \
        #            licence.ORG_TYPE == 'AUTEUR_ETUDE' or \
        #            licence.ORG_TYPE == 'CONTACT_PEB' or \
        #            licence.ORG_TYPE == 'BUREAU':
        #             organization_dict['@type'] = 'Architect'
        #             licence_dict['architects'].append(organization_dict)
        #         elif licence.ORG_TYPE == 'NOTAIRE':
        #             organization_dict['@type'] = 'Notary'
        #             licence_dict['notaries'].append(organization_dict)
        #         elif licence.ORG_TYPE == 'GEOMETRE':
        #             organization_dict['@type'] = 'Geometrician'
        #             licence_dict['geometricians'].append(organization_dict)

        # Geometrician is mandatory for parceloutlicence type in Urban
        if licence_dict['portalType'] in ('ParcelOutLicence', 'CODT_ParcelOutLicence') and len(licence_dict['geometricians']) == 0:
            organization_dict['@type'] = 'Geometrician'
            organization_dict['name1'] = "Géomètre par défaut"
            organization_dict['name2'] = "Géomètre par défaut"
            organization_dict['zipcode'] = "1000"
            organization_dict['city'] = "Ville"
            licence_dict['geometricians'].append(organization_dict)


    @benchmark_decorator
    def get_events(self, licence, licence_dict):
        for key, values in events_types.items():
            events_param = None
            method = getattr(self, 'get_{0}_event'.format(key))
            method(licence, events_param, licence_dict)

    def get_recepisse_event(self, licence, events_param, licence_dict):
        event_dict = get_event_dict()
        event_dict['title'] = 'Récépissé'
        event_dict['type'] = 'recepisse'
        event_dict['event_id'] = main_licence_deposit_event_id_mapping[licence_dict['portalType']]
        event_dict['eventPortalType'] = 'UrbanEvent'
        if licence.DOSSIER_DATEDEPART:
            event_dict['eventDate'] = str(licence.DOSSIER_DATEDEPART)[0:10]
        elif licence.DOSSIER_DATEDEPOT:
            event_dict['eventDate'] = str(licence.DOSSIER_DATEDEPOT)[0:10]
        else:
            return
        licence_dict['__children__'].append(event_dict)

    def get_completefolder_event(self, licence, events_etape, events_param, licence_children):
        for id, event in events_etape.iterrows():
            event_dict = get_event_dict()
            event_dict['title'] = 'Dossier complet'
            event_dict['type'] = 'completefolder'
            event_dict['event_id'] = 'accuse-de-reception'
            event_dict['eventDate'] = event.ETAPE_DATEDEPART
            licence_children.append(event_dict)

    def get_incompletefolder_event(self, licence, events_etape, events_param, licence_children):
        for id, event in events_etape.iterrows():
            event_dict = get_event_dict()
            event_dict['title'] = 'Dossier incomplet'
            event_dict['type'] = 'incompletefolder'
            event_dict['event_id'] = 'dossier-incomplet'
            event_dict['eventDate'] = event.ETAPE_DATEDEPART
            licence_children.append(event_dict)

    def get_sendtofd_event(self, licence, events_etape, events_param, licence_children):
        for id, event in events_etape.iterrows():
            event_dict = get_event_dict()
            event_dict['title'] = 'Envoyé au FD'
            event_dict['type'] = 'sendtofd'
            event_dict['event_id'] = 'transmis-1er-dossier-rw'
            event_dict['eventDate'] = event.ETAPE_DATEDEPART
            licence_children.append(event_dict)

    def get_sendtoapplicant_event(self, licence, events_etape, events_param, licence_children):
        for id, event in events_etape.iterrows():
            event_dict = get_event_dict()
            event_dict['title'] = 'Envoyé au demandeur'
            event_dict['type'] = 'sendtoapplicant'
            event_dict['eventDate'] = event.ETAPE_DATEDEPART
            licence_children.append(event_dict)

    def get_decision_event(self, licence, events_param, licence_dict):
        event_dict = get_event_dict()
        event_dict['title'] = 'Événement décisionnel'
        event_dict['event_id'] = main_licence_decision_event_id_mapping[licence_dict['portalType']]

        licence_dict['wf_state'] = state_mapping.get(licence.DOSSIER_OCTROI)
        if licence_dict['wf_state']:
            self.licence_description.append({'Précision décision': decision_label_mapping.get(licence_dict['wf_state'])})

        # CODT licences need a transition
        if licence_dict['portalType'].startswith("CODT_") and licence_dict['wf_state']:
                if licence_dict['wf_state'] == 'accept':
                    licence_dict['wf_transition'] = 'accepted'
                elif licence_dict['wf_state'] == 'refuse':
                    licence_dict['wf_transition'] = 'refused'
                elif licence_dict['wf_state'] == 'retire':
                    licence_dict['wf_transition'] = 'retired'
                licence_dict['wf_state'] = ''

        if licence.DOSSIER_DATEDELIV:
            event_dict['eventDate'] = str(licence.DOSSIER_DATEDELIV)[0:10]
            event_dict['decisionDate'] = str(licence.DOSSIER_DATEDELIV)[0:10]
            licence_dict['__children__'].append(event_dict)


def main():
    """ """
    parser = argparse.ArgumentParser(description='Import data from Acropole Database')
    parser.add_argument('config_file', type=str, help='path to the config')
    parser.add_argument('--limit', type=int, help='number of records')
    parser.add_argument('--view', type=str, default='dossiers_vue', help='give licence view to call')
    parser.add_argument('--licence_id', type=str, help='reference of a licence')
    parser.add_argument('--range', type=str, help="input slice, example : '5:10'")
    parser.add_argument('--ignore_cache', type=bool, nargs='?',
                        const=True, default=False, help='ignore local cache')
    parser.add_argument('--benchmarking', type=bool, nargs='?',
                        const=True, default=False, help='add benchmark infos')
    parser.add_argument('--noop', type=bool, nargs='?',
                        const=True, default=False, help='only print result')
    parser.add_argument('--iterate', type=bool, nargs='?',
                        const=True, default=False, help='Use a special cache to iterate')
    args = parser.parse_args()

    ImportAcropole(
        args.config_file,
        view=args.view,
        limit=args.limit,
        range=args.range,
        licence_id=args.licence_id,
        ignore_cache=args.ignore_cache,
        benchmarking=args.benchmarking,
        noop=args.noop,
        iterate=args.iterate
    ).execute()
