# -*- coding: utf-8 -*-

import re
from datetime import datetime

from progress.bar import FillingSquaresBar
from urban.dataimport.core import utils
from sqlalchemy import create_engine

import argparse
import configparser
import json
import time
import unidecode

from urban.dataimport.core.db import LazyDB
from urban.dataimport.core.json import get_licence_dict, get_work_locations_dict, DateTimeEncoder, get_applicant_dict, \
    get_organization_dict, get_parcel_dict, get_event_dict, get_attachment_dict
from urban.dataimport.core.mapping.main_mapping import main_licence_decision_event_id_mapping, \
    main_licence_deposit_event_id_mapping, main_licence_not_receivable_event_id_mapping
from urban.dataimport.core.mapping.urbaweb_mapping import division_mapping, events_types, \
    title_types
from urban.dataimport.core.mapping.urbaweb_mapping import portal_type_mapping
from urban.dataimport.core.utils import BaseImport, StateManager, StateHandler, benchmark_decorator, \
    export_to_customer_json, represent_int, IterationError, ErrorToCsv, export_error_csv, \
    get_file_data_from_suffix_path, get_filename_from_suffix_path, html_escape
from urban.dataimport.core.views.bestaddress_views import create_bestaddress_views
from urban.dataimport.core.views.cadastral_views import create_cadastral_views
from urban.dataimport.core.views.urbaweb_views import create_views, create_concat_views


class ImportUrbaweb(BaseImport):

    def __init__(self, config_file, view, views, limit=None, range=None, licence_id=None, id=None, ignore_cache=False, pg_ignore_cache=False, benchmarking=False, noop=False, iterate=False):
        print("INITIALIZING")
        self.view = view
        self.views = views
        self.limit = limit
        self.range = range
        self.licence_id = licence_id
        self.id = id
        self.start_time = time.time()
        self.benchmarking = benchmarking
        self.noop = noop
        self.iterate = iterate
        config = configparser.ConfigParser()
        config_file = utils.format_path(config_file)
        config.read(config_file)
        self.config = config
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
            ignore_cache=pg_ignore_cache,
        )
        engine_bestaddress = create_engine('postgresql://{user}:{password}@{host}:{port}'.format(
            **config._sections['bestaddress_database']))
        connection_bestaddress = engine_bestaddress.connect()
        self.bestaddress = LazyDB(
            connection_bestaddress,
            config['bestaddress_database']['schema'],
            ignore_cache=pg_ignore_cache,
        )
        create_concat_views(self)
        create_views(self)
        create_cadastral_views(self)
        create_bestaddress_views(self, config['main']['locality'])
        self.parcel_errors = []
        self.street_errors = []
        self.verify_date_pattern = re.compile("^\d{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])$")
        print("INITIALIZATION COMPLETED")

    def execute(self):
        self.data = []
        error = None
        try:
            self.extract_data()
        except Exception as e:
            error = e
        if error:
            raise error

        if not self.noop and error is None:
            with open("{0}.{1}".format(self.config['main']['output_path'], "json"), 'w') as output_file:
                json.dump(self.data, output_file, cls=DateTimeEncoder)
            if not(self.config['main']['with_attachments']) or (self.config['main']['with_attachments'] and self.config['main']['with_attachments'] != 'True'):
                export_to_customer_json(self)
        print("-- {0} folders extracted --".format(len(self.data)))
        print("--- Total Duration --- %s seconds ---" % (time.time() - self.start_time))

    @StateManager
    def extract_data(self):
        if not self.views:
            extract_data_views = [self.view]
        else:
            extract_data_views = self.views
        for extract_data_view in extract_data_views:
            folders = getattr(self.db, extract_data_view)
            if self.range:
                folders = folders[int(self.range.split(':')[0]):int(self.range.split(':')[1])]
            if self.limit:
                folders = folders.head(self.limit)
            if self.licence_id:
                folders = folders[folders.REFERENCE == self.licence_id]
            if self.id:
                folders = folders[folders.id == int(self.id)]
            bar = FillingSquaresBar('Processing licences for {}'.format(str(extract_data_view)), max=folders.shape[0])
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

    @StateHandler('data', 'urbaweb_get_licence')
    def get_licence(self, id, licence):
        self.licence_description = []
        licence_dict = get_licence_dict()
        licence_dict['portalType'] = self.get_portal_type(licence)  # licence type must be the first licence set
        if not licence_dict['portalType']:
            return
        licence_dict["@type"] = licence_dict["portalType"]
        if licence.REFERENCE_TECH == 0 and licence.REFERENCE:
            ref = licence.REFERENCE
        elif licence.REFERENCE_TECH and licence.REFERENCE_TECH != 0:
            ref = licence.REFERENCE_TECH
        else:
            ref = 'inconnue'

        licence_dict['reference'] = "{}/{}".format(licence.id, ref)
        # licence_dict['Title'] = "{} {}".format(licence_dict['reference'], licence.NATURE_TITRE)
        licence_dict['licenceSubject'] = licence.NATURE_TITRE
        licence_dict['usage'] = 'not_applicable'
        licence_dict['workLocations'] = self.get_work_locations(licence)
        self.get_organization(licence, licence_dict)
        self.get_applicants(licence, licence_dict['__children__'], licence_dict)
        self.get_parcels(licence, licence_dict['__children__'])
        self.get_events(licence, licence_dict)
        self.get_rubrics(licence, licence_dict)
        self.get_parcellings(licence)
        if hasattr(licence, "PHC") and licence.PHC:
            self.licence_description.append({'Parcelle(s) hors commune': licence.PHC})
        if hasattr(licence, "DEBUT_TRAVAUX") and licence.DEBUT_TRAVAUX and len(licence.DEBUT_TRAVAUX) == 10:
            work_begin_date = datetime.strptime(licence.DEBUT_TRAVAUX, '%Y-%m-%d').strftime('%d/%m/%Y')
            self.licence_description.append({'Début des travaux': work_begin_date})
        if hasattr(licence, "FIN_TRAVAUX") and licence.FIN_TRAVAUX and len(licence.FIN_TRAVAUX) == 10:
            work_end_date = datetime.strptime(licence.FIN_TRAVAUX, '%Y-%m-%d').strftime('%d/%m/%Y')
            self.licence_description.append({'Fin des travaux': work_end_date})

        if self.config['main']['with_attachments'] and self.config['main']['with_attachments'] == 'True':
            if hasattr(licence, "INFOS_DOCUMENTS") and licence.INFOS_DOCUMENTS:
                self.get_documents(licence, licence_dict['__children__'])
        description = str(''.join(str(d) for d in self.licence_description))
        description_data = "{} - {} {} {}".format(description, str(licence.NATURE_TITRE).replace("\n", " "), str(licence.NATURE_DETAILS).replace("\n", " "), html_escape(str(licence.REMARQUES).replace("\n", " ").replace("\t", " ").replace("\r", " ").replace("?", " ")))
        description_data = description_data[:7899]  # upper length is refused TextField/Mimetype text/html.
        licence_dict['description'] = {
            'data': "<p>{}</p>".format(description_data),
            'content-type': 'text/html'
        }  # description must be the last licence set
        # self.validate_schema(licence_dict, 'GenericLicence')
        request_dict = licence_dict

        return request_dict

    @benchmark_decorator
    def get_portal_type(self, licence):
        portal_type = portal_type_mapping.get(licence.type_permis_fk, None)
        if portal_type == 'BuildLicence' and licence.DIRECTIVE_AUTORITE_COMPETENTE in ('1', '2'):
            portal_type = 'Article127'
        if portal_type == 'EnvClassOne' and licence.CLASSE == 2:
            portal_type = 'EnvClassTwo'
        if portal_type == 'NotaryLetter' and licence.TYPE_DOSSIER == '1':
            portal_type = 'Division'
        if portal_type == 'MiscDemand':
            # CUSTOM Soignies
            if licence.id in (23264, 23347, 23425, 23426, 23525, 24307):
                portal_type = 'IntegratedLicence'
            # END CUSTOM
            elif licence.type_permis_fk == 11:
                self.licence_description.append({'Demandes Diverses': "Autre Dossier"})
            elif licence.type_permis_fk == 7:
                self.licence_description.append({'Demandes Diverses': "Déclaration Impétrants"})
            elif licence.type_permis_fk == 18:
                self.licence_description.append({'Demandes Diverses': "Infraction urbanistique"})
            elif licence.type_permis_fk == 21:
                self.licence_description.append({'Demandes Diverses': "Insalubrité Logement"})
            elif licence.type_permis_fk == 19:
                self.licence_description.append({'Demandes Diverses': "Permis Location"})

        return portal_type

    @benchmark_decorator
    def get_work_locations(self, licence):
        work_locations_list = []
        work_locations_dict = get_work_locations_dict()
        if licence.LOCALITE_RUE:
            # remove parentheses and its content
            urbaweb_street = re.sub(r'\([^)]*\)', '', licence.LOCALITE_RUE).strip()
            urbaweb_street = re.sub(r'^Av[.]', 'Avenue', urbaweb_street).strip()
            urbaweb_street = re.sub(r'^Av ', 'Avenue ', urbaweb_street).strip()
            urbaweb_street = re.sub(r'^Pl[.]', 'Place', urbaweb_street).strip()
            urbaweb_street = re.sub(r'^Pl ', 'Place ', urbaweb_street).strip()
            urbaweb_street = re.sub(r'^rue ', 'Rue ', urbaweb_street).strip()
            urbaweb_street = re.sub(r' St ', ' Saint-', urbaweb_street).strip()
            urbaweb_street = re.sub(r' Ste ', ' Sainte-', urbaweb_street).strip()

            # TODO custom SOIG : to remove
            urbaweb_street = re.sub(r'Chemin Biamont', 'Chemin de Biamont', urbaweb_street).strip()
            if licence.LOCALITE_LABEL in 'Neufvilles':
                urbaweb_street = re.sub(r'Rue Reine De Hongrie', 'Rue Reine de Hongrie', urbaweb_street).strip()
            elif licence.LOCALITE_LABEL in 'Casteau(Soignies)':
                urbaweb_street = re.sub(r'Rue Reine De Hongrie', 'Rue Reine  de Hongrie', urbaweb_street).strip()
            elif licence.LOCALITE_LABEL in 'Thieusies':
                urbaweb_street = re.sub(r'Rue Reine De Hongrie', 'Rue  Reine de Hongrie', urbaweb_street).strip()
            urbaweb_street = re.sub(r"Place d' Horrues", "Place d'Horrues", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Square de Savoye", "Square Eugène de Savoye", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Rue de l' Agace", "Rue de l'Agace", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Rue Mouligneau", "Rue du Mouligneau", urbaweb_street).strip()
            urbaweb_street = re.sub(r"boul. John Fitzgerald Kennedy", "Boulevard J.F.Kennedy", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Chemin de Williaupont", "Chemin de Willaupont", urbaweb_street).strip()

            # End custom code

            df_ba_vue = self.bestaddress.bestaddress_vue
            bestaddress_streets = df_ba_vue[
                (df_ba_vue.street == urbaweb_street)
            ]
            if bestaddress_streets.shape[0] == 0:
                # second chance without street number
                urbaweb_street_without_digits = ''.join([letter for letter in urbaweb_street if not letter.isdigit()]).strip()
                bestaddress_streets = df_ba_vue[
                    (df_ba_vue.street == urbaweb_street_without_digits)
                ]
                if bestaddress_streets.shape[0] == 0:
                    # last chance : try to remove last char, for example : 1a or 36C
                    urbaweb_street_without_last_char = urbaweb_street_without_digits.strip()[:-1]
                    bestaddress_streets = df_ba_vue[
                        (df_ba_vue.street == urbaweb_street_without_last_char.strip())
                    ]
                    if bestaddress_streets.shape[0] == 0:
                        self.street_errors.append(ErrorToCsv("street_errors",
                                                             "Pas de résultat pour cette rue",
                                                             licence.REFERENCE,
                                                             "rue : {} n°: {} cp: {} localité: {}"
                                                             .format(licence.LOCALITE_RUE,
                                                                     licence.LOCALITE_NUM,
                                                                     licence.LOCALITE_CP,
                                                                     licence.LOCALITE_LABEL)))
                        self.licence_description.append({'objet': "Pas de résultat pour cette rue",
                                                         'rue': licence.LOCALITE_RUE,
                                                         'n°': licence.LOCALITE_NUM,
                                                         'code postal': licence.LOCALITE_CP,
                                                         'localité': licence.LOCALITE_LABEL
                                                         })
                        pass

            result_count = bestaddress_streets.shape[0]
            if result_count == 1:
                work_locations_dict['street'] = bestaddress_streets.iloc[0]['street']
                work_locations_dict['bestaddress_key'] = str(bestaddress_streets.iloc[0]['key']) if str(bestaddress_streets.iloc[0]['key']) not in ('7044037', '7008904', '7017260', '7011944') else ""
                work_locations_dict['number'] = str(unidecode.unidecode(licence.LOCALITE_NUM))
                work_locations_dict['zipcode'] = bestaddress_streets.iloc[0]['zip']

                work_locations_dict['locality'] = bestaddress_streets.iloc[0]['entity']
            elif result_count > 1:
                self.street_errors.append(ErrorToCsv("street_errors",
                                                     "Plus d'un seul résultat pour cette rue",
                                                     licence.REFERENCE,
                                                     "rue : {} n°: {} cp: {} localité: {}"
                                                     .format(licence.LOCALITE_RUE,
                                                             licence.LOCALITE_NUM,
                                                             licence.LOCALITE_CP,
                                                             licence.LOCALITE_LABEL)))
                self.licence_description.append({'objet': "Plus d'un seul résultat pour cette rue",
                                                 'rue': licence.LOCALITE_RUE,
                                                 'n°': licence.LOCALITE_NUM,
                                                 'code postal': licence.LOCALITE_CP,
                                                 'localité': licence.LOCALITE_LABEL
                                                 })
        if work_locations_dict['street'] or work_locations_dict['number']:
            work_locations_list.append(work_locations_dict)

        return work_locations_list

    @benchmark_decorator
    def get_applicants(self, licence, licence_children, licence_dict):
        applicants = list(dict.fromkeys(licence.INFOS_DEMANDEURS.split("#")))
        try:
            for applicant_infos in applicants:
                applicant = applicant_infos.split("|")
                applicant_dict = get_applicant_dict()
                applicant_dict['personTitle'] = title_types.get(applicant[0], "")
                applicant_dict['name1'] = applicant[1]
                applicant_dict['name2'] = applicant[2]
                applicant_dict['number'] = applicant[3]
                applicant_dict['street'] = applicant[4]
                applicant_dict['zipcode'] = applicant[9]
                applicant_dict['city'] = applicant[5]
                applicant_dict['phone'] = applicant[6]
                applicant_dict['gsm'] = applicant[7]
                applicant_dict['email'] = applicant[8]
                if licence_dict["@type"] in ['Division', 'UrbanCertificateOne', 'UrbanCertificateTwo', 'NotaryLetter']:
                    applicant_dict['@type'] = 'Proprietary'
                licence_children.append(applicant_dict)
        except Exception:
            print("debug applicant")

    @benchmark_decorator
    def get_parcels(self, licence, licence_children):
        parcels = licence.INFOS_PARCELLES
        if parcels:
            try:
                for parcel in parcels.split("@"):
                    parcels_dict = get_parcel_dict()
                    parcels_dict['complete_name'] = parcel
                    parcels_args = parcel.split("|")
                    division_num = parcels_args[0]
                    section = parcels_args[1]
                    radical_bis_exp_puissance = parcels_args[2]
                    section = section.upper()
                    exposant = exposant.upper()
                    # re.match('^[A-Z]?$' single uppercase standard character
                    if division_num and section and radical_bis_exp_puissance and re.match('^[A-Z]?$', section.upper().replace(' ', '')):
                        # capakey without division and section is 11 character long.
                        section = section.upper()
                        if len(radical_bis_exp_puissance) == 11:
                            radical = radical_bis_exp_puissance[0:4]
                            bis = radical_bis_exp_puissance[5:7]
                            exposant = radical_bis_exp_puissance[7:8]
                            exposant = '' if exposant == '#' else exposant
                            puissance = radical_bis_exp_puissance[8:11]
                            if represent_int(puissance) and int(puissance) < 100:
                                if represent_int(radical) and represent_int(bis) and represent_int(puissance):
                                    try:
                                        division = division_mapping.get('{0:02d}'.format(int(division_num)), None)
                                        parcelles_cadastrales = self.cadastral.cadastre_parcelles_vue
                                        cadastral_parcels = parcelles_cadastrales[
                                            (parcelles_cadastrales.division == int(division)) &
                                            (parcelles_cadastrales.section == section) &
                                            (parcelles_cadastrales.radical == int(radical)) &
                                            ((parcelles_cadastrales.bis.isnull()) if not int(bis)
                                             else parcelles_cadastrales.bis == str(int(bis))) &
                                            ((parcelles_cadastrales.exposant.isnull()) if not exposant
                                             else parcelles_cadastrales.exposant == exposant) &
                                            ((parcelles_cadastrales.puissance.isnull()) if not int(puissance)
                                             else parcelles_cadastrales.puissance == puissance)
                                            ]
                                    except Exception as e:
                                        print(e)

                                    result_count = cadastral_parcels.drop_duplicates().shape[0]
                                    if result_count == 1:
                                        parcels_dict['outdated'] = 'False'
                                        parcels_dict['is_official'] = 'True'
                                        parcels_dict['division'] = str(cadastral_parcels.iloc[0]['division'])
                                        parcels_dict['section'] = cadastral_parcels.iloc[0]['section']
                                        parcels_dict['radical'] = str(int(cadastral_parcels.iloc[0]['radical']))
                                        parcels_dict['bis'] = str(cadastral_parcels.iloc[0]['bis']) if cadastral_parcels.iloc[0]['bis'] else ""
                                        parcels_dict['exposant'] = cadastral_parcels.iloc[0]['exposant']
                                        parcels_dict['puissance'] = str(cadastral_parcels.iloc[0]['puissance']) if cadastral_parcels.iloc[0]['puissance'] else ""
                                    elif result_count > 1:
                                        self.parcel_errors.append(ErrorToCsv("parcels_errors",
                                                                             "Trop de résultats pour cette parcelle",
                                                                             licence.REFERENCE,
                                                                             parcels_dict['complete_name']))
                                        self.licence_description.append({'objet': "Trop de résultats pour cette parcelle",
                                                                         'parcelle': parcels_dict['complete_name'],
                                                                         })
                                    elif result_count == 0:
                                        try:
                                            parcelles_old_cadastrales = self.cadastral.cadastre_parcelles_old_vue
                                            cadastral_parcels_old = parcelles_old_cadastrales[
                                                (parcelles_old_cadastrales.division == int(division)) &
                                                (parcelles_old_cadastrales.section == section) &
                                                (parcelles_old_cadastrales.radical == int(radical)) &
                                                ((parcelles_old_cadastrales.bis.isnull()) if not int(bis)
                                                 else parcelles_old_cadastrales.bis == str(int(bis))) &
                                                ((parcelles_old_cadastrales.exposant.isnull()) if not exposant
                                                 else parcelles_old_cadastrales.exposant == exposant) &
                                                ((parcelles_old_cadastrales.puissance.isnull()) if not int(puissance)
                                                 else parcelles_old_cadastrales.puissance == puissance)
                                                ]
                                        except Exception as e:
                                            print(e)

                                        result_count_old = cadastral_parcels_old.drop_duplicates().shape[0]
                                        # Looking for old parcels
                                        if result_count_old == 1:
                                            parcels_dict['outdated'] = 'True'
                                            parcels_dict['is_official'] = 'True'
                                            parcels_dict['division'] = str(cadastral_parcels_old.iloc[0]['division'])
                                            parcels_dict['section'] = cadastral_parcels_old.iloc[0]['section']
                                            parcels_dict['radical'] = str(int(cadastral_parcels_old.iloc[0]['radical']))
                                            parcels_dict['bis'] = str(cadastral_parcels_old.iloc[0]['bis']) if cadastral_parcels_old.iloc[0]['bis'] else ""
                                            parcels_dict['exposant'] = cadastral_parcels_old.iloc[0]['exposant']
                                            parcels_dict['puissance'] = str(cadastral_parcels_old.iloc[0]['puissance']) if cadastral_parcels_old.iloc[0]['puissance'] else ""
                                        elif result_count_old > 1:
                                            self.parcel_errors.append(ErrorToCsv("parcels_errors",
                                                                                 "Trop de résultats pour cette ancienne parcelle",
                                                                                 licence.REFERENCE,
                                                                                 parcels_dict['complete_name']))
                                            self.licence_description.append(
                                                {'objet': "Trop de résultats pour cette ancienne parcelle",
                                                 'parcelle': parcels_dict['complete_name'],
                                                 })
                                        if result_count_old == 0:
                                            self.licence_description.append(
                                                {'objet': "Pas de résultat pour cette parcelle",
                                                 'parcelle': parcels_dict['complete_name'],
                                                 })
                                    else:
                                        self.licence_description.append({'objet': "Pas de résultat pour cette parcelle",
                                                                         'parcelle': parcels_dict['complete_name'],
                                                                         })
                                else:
                                    self.parcel_errors.append(ErrorToCsv("parcels_errors",
                                                                         "Parcelle incomplète ou non valide",
                                                                         licence.REFERENCE,
                                                                         parcels_dict['complete_name']))
                                    self.licence_description.append({'objet': "Parcelle incomplète ou non valide",
                                                                     'parcelle': parcels_dict['complete_name'],
                                                                     })
                            else:
                                self.parcel_errors.append(ErrorToCsv("parcels_errors",
                                                                     "Parcelle incomplète ou non valide",
                                                                     licence.REFERENCE,
                                                                     parcels_dict['complete_name']))
                                self.licence_description.append({'objet': "Parcelle incomplète ou non valide",
                                                                 'parcelle': parcels_dict['complete_name'],
                                                                 })
                        else:
                            self.parcel_errors.append(ErrorToCsv("parcels_errors",
                                                                 "Parcelle incomplète ou non valide",
                                                                 licence.REFERENCE,
                                                                 parcels_dict['complete_name']))
                            self.licence_description.append({'objet': "Parcelle incomplète ou non valide",
                                                             'parcelle': parcels_dict['complete_name'],
                                                             })
                    else:
                        self.parcel_errors.append(ErrorToCsv("parcels_errors",
                                                             "Parcelle incomplète ou non valide",
                                                             licence.REFERENCE,
                                                             parcels_dict['complete_name']))
                        self.licence_description.append({'objet': "Parcelle incomplète ou non valide",
                                                         'parcelle': parcels_dict['complete_name'],
                                                         })
                    if parcels_dict['division'] and parcels_dict['section']:
                        licence_children.append(parcels_dict)
            except Exception as e:
                print(e)

    @benchmark_decorator
    def get_organization(self, licence, licence_dict):
        organization_dict = get_organization_dict()

        if hasattr(licence, 'ORG_NOM') and licence.ORG_NOM:
            check_org_name = licence.ORG_NOM.replace("/", "").replace("-", "").replace(".", "").replace(" ", "")
            if check_org_name:
                organization_dict['personTitle'] = title_types.get(licence.ORG_TITLE_ID, "")
                organization_dict['name1'] = licence.ORG_NOM
                organization_dict['name1'] = organization_dict['name1'].replace("/", "").replace(".", " ")
                organization_dict['name2'] = licence.ORG_PRENOM
                organization_dict['name2'] = organization_dict['name2'].replace("/", "").replace(".", " ")
                organization_dict['number'] = unidecode.unidecode(licence.ORG_NUMERO)
                organization_dict['street'] = licence.ORG_RUE
                organization_dict['zipcode'] = str(int(licence.ORG_CP))
                organization_dict['city'] = licence.ORG_LOCALITE
                organization_dict['phone'] = licence.ORG_TEL
                organization_dict['gsm'] = licence.ORG_MOBILE
                organization_dict['email'] = licence.ORG_MAIL

                if licence.ORG_TYPE == 'ARCHITECTE' or \
                   licence.ORG_TYPE == 'ARCHITECTE|DEMANDEUR_CU' or \
                   licence.ORG_TYPE == 'DEMANDEUR_CU' or \
                   licence.ORG_TYPE == 'AUTEUR_ETUDE' or \
                   licence.ORG_TYPE == 'CONTACT_PEB' or \
                   licence.ORG_TYPE == 'BUREAU':
                    organization_dict['@type'] = 'Architect'
                    licence_dict['architects'].append(organization_dict)
                elif licence.ORG_TYPE == 'NOTAIRE':
                    organization_dict['@type'] = 'Notary'
                    licence_dict['notaries'].append(organization_dict)
                elif licence.ORG_TYPE == 'GEOMETRE':
                    organization_dict['@type'] = 'Geometrician'
                    licence_dict['geometricians'].append(organization_dict)

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
        if licence_dict['portalType'] == "Division":
            event_dict['eventDate'] = licence.DATE_DEMANDE
        else:
            event_dict['eventDate'] = licence.DATE_RECEPISSE
        if self.verify_date_pattern.match(event_dict['eventDate']):
            licence_dict['__children__'].append(event_dict)

    def get_not_receivable_event(self, licence, events_param, licence_dict):
        if licence.STATUT == 2:
            event_dict = get_event_dict()
            event_dict['title'] = 'Non recevable'
            event_dict['type'] = 'not_receivable'
            event_dict['event_id'] = main_licence_not_receivable_event_id_mapping[licence_dict['portalType']]
            # event_dict['eventDate'] = licence.DATE_STATUT
            licence_dict['__children__'].append(event_dict)

    def get_decision_event(self, licence, events_param, licence_dict):
        event_dict = get_event_dict()
        event_dict['title'] = 'Événement décisionnel'
        event_dict['type'] = 'decision'
        event_dict['event_id'] = main_licence_decision_event_id_mapping[licence_dict['portalType']]

        if licence.STATUT == 1:
            # event_dict['decision'] = main_licence_decision_mapping['OctroiCollege']
            licence_dict['wf_state'] = 'accept'
            self.licence_description.append({'Précision décision': "Octroi Collège"})
        elif licence.STATUT == 2:
            # event_dict['decision'] = main_licence_decision_mapping['RefusCollege']
            licence_dict['wf_state'] = 'refuse'
            self.licence_description.append({'Précision décision': "Refus Collège"})
        elif licence.STATUT == 3:
            # event_dict['decision'] = main_licence_decision_mapping['RefusTutelle']
            licence_dict['wf_state'] = 'refuse'
            self.licence_description.append({'Précision décision': "Refus Tutelle"})
        elif licence.STATUT == 4:
            # event_dict['decision'] = main_licence_decision_mapping['OctroiTutelle']
            licence_dict['wf_state'] = 'accept'
            self.licence_description.append({'Précision décision': "Octroi Tutelle"})
        elif licence.STATUT == 5:
            # event_dict['decision'] = main_licence_decision_mapping['RefusFD']
            licence_dict['wf_state'] = 'refuse'
            self.licence_description.append({'Précision décision': "Refus par le FD"})
        elif licence.STATUT == 6:
            # event_dict['decision'] = main_licence_decision_mapping['RefusCollege']
            licence_dict['wf_state'] = 'refuse'
            self.licence_description.append({'Précision décision': "Refus Collège (2)"})
        elif licence.STATUT == 7:
            # event_dict['decision'] = main_licence_decision_mapping['OctroiCollege']
            licence_dict['wf_state'] = 'accept'
            self.licence_description.append({'Précision décision': "Autorisation Collège, retrait puis nouvelle autorisation"})
        elif licence.STATUT == 8:
            # event_dict['decision'] = main_licence_decision_mapping['Irrecevable_2xI']
            licence_dict['wf_state'] = 'refuse'
            self.licence_description.append({'Précision décision': "Irrecevable car deux fois incomplet"})
        elif licence.STATUT == 9:
            # pas de date de décision
            licence_dict['wf_state'] = 'refuse'
            self.licence_description.append({'Précision décision': "Refus tacite du Fonctionnaire"})
        elif licence.STATUT == 10:
            # event_dict['decision'] = main_licence_decision_mapping['AbandonDemandeur']
            licence_dict['wf_state'] = 'retire'
            self.licence_description.append({'Précision décision': "Abandonné par le demandeur"})
        elif licence.STATUT == 14:
            # event_dict['decision'] = main_licence_decision_mapping['OctroiFD']
            licence_dict['wf_state'] = 'accept'
            self.licence_description.append({'Précision décision': "Octroi par le FD"})
        elif licence.STATUT == 17:
            # event_dict['decision'] = main_licence_decision_mapping['OctroiFD']
            licence_dict['wf_state'] = 'accept'
            self.licence_description.append({'Précision décision': "Octroi par le FD"})
        elif licence.STATUT == 18:
            # event_dict['decision'] = main_licence_decision_mapping['RefusFD']
            licence_dict['wf_state'] = 'refuse'
            self.licence_description.append({'Précision décision': "Refus par le FD"})
        elif licence.STATUT == 28:
            # event_dict['decision'] = main_licence_decision_mapping['OctroiFD']
            licence_dict['wf_state'] = 'accept'
            self.licence_description.append({'Précision décision': "Octroi partiel du FD"})
        elif licence.STATUT == 34:
            # event_dict['decision'] = main_licence_decision_mapping['Abandon']
            licence_dict['wf_state'] = 'retire'
            self.licence_description.append({'Précision décision': "Abandon"})
        elif licence.STATUT == 35:
            # event_dict['decision'] = main_licence_decision_mapping['Recevable']
            licence_dict['wf_state'] = 'accept'
            self.licence_description.append({'Précision décision': "Recevable avec condition"})
        elif licence.STATUT == 36:
            # Twice incomplete : Refused
            # event_dict['decision'] = main_licence_decision_mapping['Irrecevable']
            licence_dict['wf_state'] = 'refuse'
            self.licence_description.append({'Précision décision': "Irrecevable car deux fois incomplet"})
        elif licence.STATUT == 0 or licence.STATUT == 30 or licence.STATUT == 31 or licence.STATUT == '' or licence.STATUT == 15 or licence.STATUT == 27:
            """
                En cours ou non déterminé
            """
        else:
            import ipdb; ipdb.set_trace() # TODO REMOVE BREAKPOINT
            print("unknown status")

        # CUSTOM encoding error for example drt, dat, drc, dac
        # custom SOIG
        # if licence_dict['portalType'] == "Declaration":
        #     if licence.REFERENCE in ("2014/DU001", "2014/DU002", "2015/DU013"):
        #         event_dict['decision'] = main_licence_decision_mapping['OctroiFD']
        #         licence_dict['wf_state'] = 'accept'
        #         self.licence_description.append({'Précision décision': "Erreur encodage : Octroi par le FD"})
        # END CUSTOM

        #  get decision date with four dates licencetype system (college/tutelle)
        if licence_dict['portalType'] in (
                'BuildLicence',
                'ParcelOutLicence',
                'UniqueLicence',
                'EnvClassOne',
                'EnvClassTwo',
                'EnvClassThree',
                'Article127',
                'IntegratedLicence',
                'MiscDemand'
        ):
            drt = licence.AUTORISATION_DATE_REFUS_TUTELLE
            dat = licence.AUTORISATION_DATE_AUTORISATION_TUTELLE
            drc = licence.AUTORISATION_DATE_REFUS_COLLEGE
            dac = licence.AUTORISATION_DATE_AUTORISATION_COLLEGE
            if hasattr(licence, "DATE_DECISION_TUTELLE") and licence.DATE_DECISION_TUTELLE:
                event_dict['eventDate'] = licence.DATE_DECISION_TUTELLE

            elif drt or dat:
                if drt and dat:
                    event_dict['eventDate'] = drt if drt > dat else dat
                elif drt:
                    event_dict['eventDate'] = drt
                else:
                    event_dict['eventDate'] = dat
            elif drc or dac:
                if drc and dac:
                    event_dict['eventDate'] = drc if drc > dac else dac
                elif drc:
                    event_dict['eventDate'] = drc
                else:
                    event_dict['eventDate'] = dac
        elif licence_dict['portalType'] in ('Division', 'NotaryLetter', 'UrbanCertificateOne', 'UrbanCertificateTwo'):
            # get decision date with 2 'colleges' dates licencetype
            drc = licence.AUTORISATION_DATE_REFUS_COLLEGE
            dac = licence.AUTORISATION_DATE_AUTORISATION_COLLEGE
            if drc and dac:
                event_dict['eventDate'] = drc if drc > dac else dac
            elif drc:
                event_dict['eventDate'] = drc
            else:
                event_dict['eventDate'] = dac

        if event_dict['eventDate']:
            event_dict['decisionDate'] = event_dict['eventDate']

        # CODT licences need a transition
        if licence_dict['portalType'].startswith("CODT_") and licence_dict['wf_state']:
            if licence_dict['wf_state'] == 'accept':
                licence_dict['wf_transition'] = 'accepted'
            elif licence_dict['wf_state'] == 'refuse':
                licence_dict['wf_transition'] = 'refused'
            elif licence_dict['wf_state'] == 'retire':
                licence_dict['wf_transition'] = 'retired'
            licence_dict['wf_state'] = ''

        # Divison has a specific WF and hasn't 'refuse' transition
        if licence_dict['portalType'] == 'Division' and (licence_dict['wf_state'] == 'refuse' or licence_dict['wf_state'] == 'retire'):
            licence_dict['wf_state'] = 'nonapplicable'

        if event_dict['eventDate'] and event_dict['decisionDate']:
            if self.verify_date_pattern.match(event_dict['eventDate']) and self.verify_date_pattern.match(event_dict['decisionDate']):
                licence_dict['__children__'].append(event_dict)

    def get_rubrics(self, licence, licence_dict):
        if hasattr(licence, "INFOS_RUBRIQUES") and licence.INFOS_RUBRIQUES:
            self.licence_description.append({'Rubriques': licence.INFOS_RUBRIQUES})
            rubrics_list = []
            for rubric in licence.INFOS_RUBRIQUES.split("@"):
                rubrics_list.append(rubric)
            if rubrics_list:
                licence_dict['rubrics'] = rubrics_list

    def get_parcellings(self, licence):
        if hasattr(licence, "NOM_LOT") and licence.NOM_LOT:
            self.licence_description.append({'Nom lotissement': licence.NOM_LOT})
        if hasattr(licence, "NB_LOT") and licence.NB_LOT:
            self.licence_description.append({'Nombre de lots': licence.NB_LOT})

    def get_documents(self, licence, licence_children):
        # remove duplicates file (same title/description/path) from dirty input DB
        infos_documents = list(dict.fromkeys(licence.INFOS_DOCUMENTS.split("@")))
        title_check = []
        for document in infos_documents:
            try:
                document_dict = get_attachment_dict()
                document_split = document.split("|")
                if document_split[2]:
                    if document_split[0] in title_check:
                        continue
                    else:
                        title_check.append(document_split[0])
                        document_dict["title"] = document_split[0]
                        document_dict["description"] = document_split[1]
                        document_dict["file"]["filename"] = get_filename_from_suffix_path(
                            self.config['main']['documents_path'],
                            document_split[2]
                        )
                        document_dict["file"]["data"] = get_file_data_from_suffix_path(
                            self.config['main']['documents_path'],
                            document_split[2]
                        )
                        if document_dict["file"]["filename"] and document_dict["file"]["filename"] != "":
                            licence_children.append(document_dict)
                        else:
                            self.licence_description.append({'Document non retrouvé': document})
            except Exception as e:
                print(e)


def main():
    """ """
    parser = argparse.ArgumentParser(description='Import data from Urbaweb CSV Files')
    parser.add_argument('config_file', type=str, help='path to the config')
    parser.add_argument('--limit', type=int, help='number of records')
    parser.add_argument('--view', type=str, default='permis_urbanisme_vue', help='give licence view to call')
    parser.add_argument('--views', nargs='+', default=[], help='give licence views list to call')
    parser.add_argument('--licence_id', type=str, help='reference of a licence')
    parser.add_argument('--id', type=str, help='db id of a licence')
    parser.add_argument('--range', type=str, help="input slice, example : '5:10'")
    parser.add_argument('--ignore_cache', type=bool, nargs='?',
                        const=True, default=False, help='ignore mysql db local cache')
    parser.add_argument('--pg_ignore_cache', type=bool, nargs='?',
                        const=True, default=False, help='ignore postgres db local cache')
    parser.add_argument('--benchmarking', type=bool, nargs='?',
                        const=True, default=False, help='add benchmark infos')
    parser.add_argument('--noop', type=bool, nargs='?',
                        const=True, default=False, help='only print result')
    parser.add_argument('--iterate', type=bool, nargs='?',
                        const=True, default=False, help='Use a special cache to iterate')
    args = parser.parse_args()

    ImportUrbaweb(
        args.config_file,
        view=args.view,
        views=args.views,
        limit=args.limit,
        range=args.range,
        licence_id=args.licence_id,
        id=args.id,
        ignore_cache=args.ignore_cache,
        pg_ignore_cache=args.pg_ignore_cache,
        benchmarking=args.benchmarking,
        noop=args.noop,
        iterate=args.iterate
    ).execute()
