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
from urban.dataimport.core.views.urbaweb_views import create_views


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
        # create_concat_views(self)
        create_views(self)
        create_cadastral_views(self)
        create_bestaddress_views(self, config['main']['locality'])
        self.parcel_errors = []
        self.street_errors = []
        self.verify_date_pattern = re.compile("^\d{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])$")
        # Avoid references duplicates
        self.duplicates_list = ['1945-015', '1946-052', '1946-064', '1947-203', '1948-209', '1948-246', '1949-000', '1949-340', '1949-367', '1950-415', '1950-437', '1950-474', '1950-511', '1950-512', '1950-515', '1950-548', '1951-000', '1951-567', '1951-619', '1952-728', '1952-731', '1953-860', '1953-912', '1953-938', '1953-980', '1954-1008', '1954-1079', '1954-1082', '1954-1144', '1954-988', '1954-999', '1955-1220', '1955-1265', '1955-1311', '1955-1336', '1955-1356', '1956-1472', '1956-1507', '1957-1588', '1957-1716', '1958-1816', '1958-1856', '1959-1929', '1959-1940', '1959-1943', '1959-2029', '1959-2051', '1960-2176', '1960-2260', '1961-2287', '1961-2395', '1961-2432', '1961-2468', '1962-2593', '1963-052', '1963-064', '1963-2687', '1963-2725', '1963-2752', '1964-054HH', '1964-161', '1964-166', '1964-216', '1964-228', '1965-240', '1965-294', '1965-323', '1965-335', '1965-361', '1967-572', '1967-635', '1967-643', '1967-659', '1968-368HL', '1968-722', '1968-786', '1968-793b', '1968-796', '1969-396HL', '1969-861', '1969-866', '1970-932', '1970-999', '1971-001', '1971-002', '1971-003', '1971-005', '1971-006', '1971-007', '1971-008', '1971-009', '1971-010', '1971-011', '1971-012', '1971-016', '1971-018', '1971-019', '1971-020', '1971-021', '1971-022', '1971-023', '1971-024', '1971-025', '1971-026', '1971-027', '1971-028', '1971-029', '1971-030', '1971-031', '1971-032', '1971-033', '1971-034', '1971-035', '1971-036', '1971-037', '1971-038', '1971-039', '1971-040', '1971-041', '1971-042', '1971-043', '1971-044', '1971-045', '1971-046', '1971-047', '1971-048', '1971-049', '1971-050', '1971-051', '1971-052', '1971-053', '1971-054', '1971-057', '1971-058', '1971-061', '1971-063', '1971-064', '1971-065', '1971-066', '1971-067', '1971-069', '1971-071', '1971-075', '1971-076', '1971-077', '1971-080', '1971-083', '1971-084', '1971-085', '1971-086', '1971-087', '1971-089', '1971-090', '1971-091', '1971-092', '1971-094', '1972-095', '1972-097', '1972-098', '1972-099', '1972-100', '1972-101', '1972-102', '1972-104', '1972-105', '1972-106', '1972-107', '1972-108', '1972-109', '1972-111', '1972-112', '1972-113', '1972-114', '1972-115', '1972-116', '1972-119', '1972-120', '1972-121', '1972-123', '1972-124', '1972-125', '1972-126', '1972-127', '1972-128', '1972-129', '1972-130', '1972-131', '1972-132', '1972-133', '1972-134', '1972-135', '1972-136', '1972-137', '1972-138', '1972-139', '1972-140', '1972-141', '1972-142', '1972-144', '1972-145', '1972-146', '1972-147', '1972-148', '1972-149', '1972-150', '1972-151', '1972-152', '1972-153', '1972-154', '1972-155', '1972-157', '1972-158', '1972-159', '1972-160', '1972-161', '1972-162', '1972-163', '1972-165', '1972-166', '1972-167', '1972-168', '1972-170', '1972-171', '1972-172', '1972-173', '1972-174', '1972-175', '1972-176', '1972-177', '1972-178', '1972-179', '1972-180', '1972-181', '1972-182', '1972-183', '1972-184', '1972-185', '1972-186', '1972-187', '1972-189', '1972-190', '1972-191', '1972-192', '1972-196', '1972-197', '1972-198', '1972-199', '1972-200', '1972-201', '1972-202', '1972-203', '1972-204', '1972-205', '1972-206', '1972-207', '1972-208', '1972-209', '1972-210', '1972-211', '1972-212', '1972-214', '1972-215', '1972-217', '1972-219', '1972-221', '1972-222', '1972-223', '1972-224', '1973-226', '1973-227', '1973-228', '1973-229', '1973-230', '1973-231', '1973-232', '1973-233', '1973-234', '1973-235', '1973-236', '1973-237', '1973-238', '1973-239', '1973-240', '1973-241', '1973-242', '1973-243', '1973-244', '1973-245', '1973-246', '1973-247', '1973-248', '1973-249', '1973-250', '1973-252', '1973-253', '1973-254', '1973-255', '1973-256', '1973-257', '1973-258', '1973-259', '1973-260', '1973-261', '1973-263', '1973-264', '1973-265', '1973-267', '1973-268', '1973-269', '1973-270', '1973-271', '1973-272', '1973-273', '1973-275', '1973-276', '1973-277', '1973-278', '1973-279', '1973-281', '1973-282', '1973-283', '1973-284', '1973-285', '1973-286', '1973-287', '1973-288', '1973-288b', '1973-289', '1973-290', '1973-291', '1973-292', '1973-295', '1973-296', '1973-297', '1973-298', '1973-299', '1973-300', '1973-301', '1973-302', '1973-303', '1973-304', '1973-305', '1973-306', '1973-307', '1973-308', '1973-309', '1973-310', '1973-311', '1973-312', '1973-313', '1973-314', '1973-315', '1973-316', '1973-317', '1973-318', '1973-319', '1973-320', '1973-321', '1973-322', '1973-323', '1973-324', '1973-325', '1973-326', '1973-327', '1973-328', '1973-330', '1973-331', '1973-332', '1973-333', '1973-335', '1973-342', '1973-343', '1973-345', '1973-346', '1973-347', '1973-348', '1973-349', '1973-357', '1973-358', '1975-573', '1976-765', '1977-104', '1978-373', '1978-398', '1979-463', '1979-466', '1979-485', '1980-587', '1980-594', '1980-611', '1980-664', '1980-744', '1980-766', '1982-016', '1982-081', '1983-024', '1983-089', '1983-105', '1983-106', '1985-037', '1985-084', '1986-009', '1987-073', '1988-101', '1989-105', '1991-084', '1991-091', '1991-132', '1992-030', '1993-032', '1993-041', '1994-015', '1994-151', '1994-152', '1995-071a', '1995-071b', '1996-012', '1996-096', '1996-099a', '1996-158', '1996-167a', '1997-013', '1997-032', '1997-058', '1997-099', '1997-153', '1998-016', '1998-019', '1998-047', '1998-090', '1998-103', '1998-139a', '1998-166', '2000-030', '2000-050a', '2000-071', '2000-100', '2000-118', '2000-132', '2001-032', '2001-032a', '2001-047', '2001-064', '2003-060', '2003-102', '2004-042', '2004-113A', '2005-021', '2005-022', '2005-115i-D', '2007-033A', '2007-366 U', '2008-081', '2012-008', '2014-136', '2015-084A', '2015-095', '2016-074', '2016-083', '2016-086', '2016-086A', '2016-132', '2017-015A', '2017-025C', '2017-041', '2017-058', '2018-031', '2018-080', '2020-028U', '2021-050C', "2016-144"]
        self.duplicates_count = dict(zip(self.duplicates_list, [0] * len(self.duplicates_list)))
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
                folders = folders[folders.NUM_PERMIS == self.licence_id]
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
        # if not licence_dict['portalType']:
        #     return
        licence_dict["@type"] = licence_dict["portalType"]
        # if licence.REFERENCE_TECH == 0 and licence.REFERENCE:
        #     ref = licence.REFERENCE
        # elif licence.REFERENCE_TECH and licence.REFERENCE_TECH != 0:
        #     ref = licence.REFERENCE_TECH
        # else:
        #     ref = 'inconnue'

        licence_dict['reference'] = licence.NUM_PERMIS or licence.N1
        # licence_dict['Title'] = "{} {}".format(licence_dict['reference'], licence.NATURE_TITRE)
        licence_dict['licenceSubject'] = licence.TRAVAUX
        licence_dict['usage'] = 'not_applicable'
        self.get_parcels(licence, licence_dict['__children__'])
        licence_dict['workLocations'] = self.get_work_locations(licence, licence_dict)
        self.get_organization(licence, licence_dict)
        self.get_applicants(licence, licence_dict['__children__'], licence_dict)
        self.get_events(licence, licence_dict)

        if licence_dict['reference'] in self.duplicates_list:
            self.duplicates_count[licence_dict['reference']] = self.duplicates_count[licence_dict['reference']] + 1
            print("Duplicate reference: {} / Duplicate iteration : {}".format(licence_dict['reference'],
                                                                              self.duplicates_count[
                                                                                  licence_dict['reference']]))
            licence_dict['reference'] = "{}_{}".format(licence_dict['reference'], self.duplicates_count[licence_dict['reference']])

        # self.get_rubrics(licence, licence_dict)
        # self.get_parcellings(licence)
        # if hasattr(licence, "PHC") and licence.PHC:
        #     self.licence_description.append({'Parcelle(s) hors commune': licence.PHC})
        # if hasattr(licence, "DEBUT_TRAVAUX") and licence.DEBUT_TRAVAUX and len(licence.DEBUT_TRAVAUX) == 10:
        #     work_begin_date = datetime.strptime(licence.DEBUT_TRAVAUX, '%Y-%m-%d').strftime('%d/%m/%Y')
        #     self.licence_description.append({'Début des travaux': work_begin_date})
        # if hasattr(licence, "FIN_TRAVAUX") and licence.FIN_TRAVAUX and len(licence.FIN_TRAVAUX) == 10:
        #     work_end_date = datetime.strptime(licence.FIN_TRAVAUX, '%Y-%m-%d').strftime('%d/%m/%Y')
        #     self.licence_description.append({'Fin des travaux': work_end_date})

        # if self.config['main']['with_attachments'] and self.config['main']['with_attachments'] == 'True':
        #     if hasattr(licence, "INFOS_DOCUMENTS") and licence.INFOS_DOCUMENTS:
        #         self.get_documents(licence, licence_dict['__children__'])
        description = str(''.join(str(d) for d in self.licence_description))
        description_data = "{} - {}".format(description, str(licence.NATURE).replace("\n", " "))
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
        portal_type = portal_type_mapping.get(licence.TYPE, 'BuildLicence')
        if portal_type in ['BuildLicence', 'Article127', 'UniqueLicence', 'IntegratedLicence']:
            if licence.AUTORISATION and int(licence.AUTORISATION[6:8]) > 16 and int(licence.AUTORISATION[6:8]) < 23 and int(licence.AUTORISATION[3:5]) > 5:
                print("CODT: {}".format(licence.AUTORISATION))
                portal_type = "{}{}".format("CODT_", portal_type)
            elif licence.REFUS and int(licence.REFUS[6:8]) > 16 and int(licence.REFUS[6:8]) < 23 and int(licence.REFUS[3:5]) > 5:
                print("CODT: {}".format(licence.REFUS))
                portal_type = "{}{}".format("CODT_", portal_type)
        return portal_type

    @benchmark_decorator
    def get_work_locations(self, licence, licence_dict):
        work_locations_list = []
        work_locations_dict = get_work_locations_dict()
        if licence.SITUATION_BIEN:
            # remove parentheses and its content
            licence.SITUATION_BIEN = re.sub(r'\([^)]*\)', '', licence.SITUATION_BIEN).strip()
            urbaweb_street = re.sub(r'\d.*', '', licence.SITUATION_BIEN).strip()
            urbaweb_number = re.sub(r'^\D*', '', licence.SITUATION_BIEN).strip()

            urbaweb_street = re.sub(r'^Av[.]', 'Avenue', urbaweb_street).strip()
            urbaweb_street = re.sub(r'^Av ', 'Avenue ', urbaweb_street).strip()
            urbaweb_street = re.sub(r'^Pl[.]', 'Place', urbaweb_street).strip()
            urbaweb_street = re.sub(r'^Pl ', 'Place ', urbaweb_street).strip()
            urbaweb_street = re.sub(r'^rue ', 'Rue ', urbaweb_street).strip()
            urbaweb_street = re.sub(r' St ', ' Saint-', urbaweb_street).strip()
            urbaweb_street = re.sub(r' Ste ', ' Sainte-', urbaweb_street).strip()

            # # TODO custom GH
            urbaweb_street = re.sub(r"Acacias", "Avenue des Acacias", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Aérport", "Rue de l'Aéroport", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Aéropostale", "Rue de l'Aéropostale", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Agneau", "Rue de l'Agneau", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Aîte", "Rue de l'Aîte", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Alliés", "Rue des Alliés", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Aqueduc", "Rue de l'Aqueduc", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Arbre à la Croix", "Rue de l'Arbre à la Croix", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Avenir", "Rue de l'Avenir", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Barrière", "Rue de la Barrière", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Bihet", "Rue du Bihet", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Bois de Malette", "Rue Bois Malette", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Body", "Rue Michel Body", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Chapuis", "Rue Grégoire Chapuis", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Champs", "Rue des Champs", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Churchill", "Rue Winston Churchill", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Defrêcheux", "Rue Nicolas Defrêcheux", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Defuisseaux", "Rue Alfred Defuisseaux", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Degive", "Rue Antoine Degive", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Dejardin", "Rue Joseph Dejardin", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Denis", "Rue Hector Denis", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Destrée", "Rue Jules Destrée", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Doyenné", "Place du Doyenné", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Dunant", "Rue Henri Dunant", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Edison", "Rue Thomas Edison", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^En Bois", "Rue en Bois", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^En bois", "Rue en Bois", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Ferrer", "Rue Francisco Ferrer", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Fleming", "Rue du Docteur Fleming", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Gare", "Avenue de la Gare", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Goffin", "Rue Hubert Goffin", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Gramme", "Rue Zénobe Gramme", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Gruslin", "Rue J. Gruslin", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Hannut", "Chaussée de Hannut", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Haute-Claire", "Rue Haute Claire", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Hayîre", "Thier de la Hayire", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Herman", "Impasse Herman", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Heusdens", "Rue Joseph Heusdens", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Hugo", "Rue Victor Hugo", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Jace", "Thier de Jace", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Janson", "Rue Paul Janson", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Jaurès", "Rue Jean Jaurès", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Jossens", "Rue Edouard Jossens", urbaweb_street).strip()
            urbaweb_street = re.sub(r"King", "Rue Martin Luther King", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Lakaye", "Rue Pierre Lakaye", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Lexhy", "Rue Mathieu de Lexhy", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Lincoln", "Rue Abraham Lincoln", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Malvoz", "Rue Ernest Malvoz", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Malette", "Rue Bois Malette", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Massillon", "Impasse Massillon", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Materne", "Rue Adrien Materne", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Mattéoti", "Rue Giacomo Mattéoti", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Maquet", "Impasse Maquet", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Matteoti", "Rue Giacomo Mattéoti", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Mâvis", "Rue Mavis", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Merlot", "Rue Jean Joseph Merlot", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Neuve voie", "Rue Neuve Voie", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Onze novembre", "Rue du Onze Novembre", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Pasteur", "Rue Louis Pasteur", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Paque", "Rue Simon Paque", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Pas St-Martin", "Rue Pas Saint-Martin", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Remouchamps", "Rue Edouard Remouchamps", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Renan", "Rue Ernest Renan", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Rond Point de Blanckart Surlet", "Rond-Point de Blanckart-Surlet", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^rouvroi", "Rue Rouvroi", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Rouvroi", "Rue Rouvroi", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Rouyer", "Rue Joseph Rouyer", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Sainte Anne", "Rue Sainte-Anne", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^St-Anne", "Rue Sainte-Anne", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Saint-Exupéry", "Rue Saint-Exupéry", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Saint-Léonard", "Thier Saint-Léonard", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Samson", "Rue Arthur Samson", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Sart Thiri", "Rue du Sart-Thiri", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Schweitzer", "Rue Docteur Schweitzer", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Selys Longchamps", "Rue Jean de Sélys Longchamps", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Solvay", "Rue Ernest Solvay", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Sous-le-Château", "Rue Sous le Château", urbaweb_street).strip()
            urbaweb_street = re.sub(r"St-Léonard", "Thier Saint-Léonard", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Ste-Anne", "Rue Sainte-Anne", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Technologies", "Rue des Nouvelles Technologies", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Terwagne", "Rue Freddy Terwagne", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Thier St-Léonard", "Thier Saint-Léonard", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Thiri", "Rue du Sart-Thiri", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Tombeur", "Rue Lambert Tombeur", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Vandervelde", "Avenue Emile Vandervelde", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Verhaeren", "Rue Emile Verhaeren", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Verte", "Chaussée Verte", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Volders", "Rue Jean Volders", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Vrindts", "Rue Joseph Vrindts", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Wasseiges", "Rue de Wasseige", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Wathour", "Rue Victor Wathour", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Wauters", "Avenue Joseph Wauters", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^Wauthier", "Impasse Wauthier", urbaweb_street).strip()
            urbaweb_street = re.sub(r"Zola", "Rue Emile Zola", urbaweb_street).strip()
            urbaweb_street = re.sub(r"^XVIII Bonniers", "Rue des Dix-Huit Bonniers", urbaweb_street).strip()
            #
            # # End custom code
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
                    # third chance : add "Rue" before street name
                    urbaweb_street_with_rue = "{} {}".format("Rue", urbaweb_street_without_digits.strip())
                    bestaddress_streets = df_ba_vue[
                        (df_ba_vue.street == urbaweb_street_with_rue.strip())
                    ]
                    if bestaddress_streets.shape[0] == 0:
                        # fourth chance : add "Rue de " before street name
                        urbaweb_street_with_rue_de = "{} {}".format("Rue de", urbaweb_street_without_digits.strip())
                        bestaddress_streets = df_ba_vue[
                            (df_ba_vue.street == urbaweb_street_with_rue_de.strip())
                        ]
                        if bestaddress_streets.shape[0] == 0:
                            # fifth chance : add "Rue du " before street name
                            urbaweb_street_with_rue_du = "{} {}".format("Rue du", urbaweb_street_without_digits.strip())
                            bestaddress_streets = df_ba_vue[
                                (df_ba_vue.street == urbaweb_street_with_rue_du.strip())
                            ]
                            if bestaddress_streets.shape[0] == 0:
                                # sixth chance : add "Rue de l'" before street name
                                urbaweb_street_with_rue_del = "{}{}".format("Rue de l'",
                                                                            urbaweb_street_without_digits.strip())
                                bestaddress_streets = df_ba_vue[
                                    (df_ba_vue.street == urbaweb_street_with_rue_del.strip())
                                ]
                                if bestaddress_streets.shape[0] == 0:
                                    # seventh chance : add "Rue de la" before street name
                                    urbaweb_street_with_rue_del = "{} {}".format("Rue de la",
                                                                                urbaweb_street_without_digits.strip())
                                    bestaddress_streets = df_ba_vue[
                                        (df_ba_vue.street == urbaweb_street_with_rue_del.strip())
                                    ]
                                    if bestaddress_streets.shape[0] == 0:
                                        # eighth chance : add "Rue des" before street name
                                        urbaweb_street_with_rue_des = "{} {}".format("Rue des",
                                                                                     urbaweb_street_without_digits.strip())
                                        bestaddress_streets = df_ba_vue[
                                            (df_ba_vue.street == urbaweb_street_with_rue_des.strip())
                                        ]
            if bestaddress_streets.shape[0] == 0:
                self.street_errors.append(ErrorToCsv("street_errors",
                                                     "Pas de résultat pour cette rue",
                                                     licence.NUM_PERMIS,
                                                     "rue : {}"
                                                     .format(licence.SITUATION_BIEN)))
                self.licence_description.append({'objet': "Pas de résultat pour cette rue",
                                                 'rue': licence.SITUATION_BIEN
                                                 })
                pass

            result_count = bestaddress_streets.shape[0]
            if result_count == 1:
                work_locations_dict['street'] = bestaddress_streets.iloc[0]['street']
                work_locations_dict['bestaddress_key'] = str(bestaddress_streets.iloc[0]['key']) if str(bestaddress_streets.iloc[0]['key']) not in ('7044037', '7008904', '7017260', '7011944') else ""
                work_locations_dict['number'] = str(unidecode.unidecode(urbaweb_number))
                work_locations_dict['zipcode'] = bestaddress_streets.iloc[0]['zip']
                work_locations_dict['locality'] = bestaddress_streets.iloc[0]['entity']
            elif result_count > 1:
                # if all the streets keys are the same
                if (bestaddress_streets == bestaddress_streets.iloc[0]['key']).all(axis=0)['key']:
                    work_locations_dict['street'] = bestaddress_streets.iloc[0]['street']
                    work_locations_dict['bestaddress_key'] = str(bestaddress_streets.iloc[0]['key'])
                    work_locations_dict['number'] = str(unidecode.unidecode(urbaweb_number))
                    work_locations_dict['zipcode'] = bestaddress_streets.iloc[0]['zip']
                    work_locations_dict['locality'] = bestaddress_streets.iloc[0]['entity']
                elif urbaweb_street == "Diérain Patar":
                    # Mons lez Liege
                    if "62453" in [parcel['division'] for parcel in licence_dict['__children__'] if parcel['@type'] == 'Parcel']:
                        work_locations_dict['street'] = "Rue Diérain Patar"
                        work_locations_dict['bestaddress_key'] = "7068803"
                        work_locations_dict['number'] = str(unidecode.unidecode(urbaweb_number))
                        work_locations_dict['zipcode'] = "4460"
                        work_locations_dict['locality'] = "Mons-lez-Liège"
                    else:
                        work_locations_dict['street'] = "Rue Diérain Patar"
                        work_locations_dict['bestaddress_key'] = "7024045"
                        work_locations_dict['number'] = str(unidecode.unidecode(urbaweb_number))
                        work_locations_dict['zipcode'] = "4460"
                        work_locations_dict['locality'] = "Grâce-Hollogne"
                elif urbaweb_street == "Chaussée de Liège":
                    # Bierset
                    if "62016" in [parcel['division'] for parcel in licence_dict['__children__'] if parcel['@type'] == 'Parcel']:
                        work_locations_dict['street'] = "Chaussée de Liège"
                        work_locations_dict['bestaddress_key'] = "7024005"
                        work_locations_dict['number'] = str(unidecode.unidecode(urbaweb_number))
                        work_locations_dict['zipcode'] = "4460"
                        work_locations_dict['locality'] = "Bierset"
                    elif "62054" in [parcel['division'] for parcel in licence_dict['__children__'] if parcel['@type'] == 'Parcel']:
                        # Hollogne aux Pierres
                        work_locations_dict['street'] = "Chaussée de Liège"
                        work_locations_dict['bestaddress_key'] = "7051904"
                        work_locations_dict['number'] = str(unidecode.unidecode(urbaweb_number))
                        work_locations_dict['zipcode'] = "4460"
                        work_locations_dict['locality'] = "Hollogne aux Pierres"
                    else:
                        self.street_errors.append(ErrorToCsv("street_errors",
                                                             "Plus d'un seul résultat pour cette rue",
                                                             licence.NUM_PERMIS,
                                                             "rue : {}"
                                                             .format(licence.SITUATION_BIEN)))
                        self.licence_description.append({'objet': "Plus d'un seul résultat pour cette rue",
                                                         'rue': licence.SITUATION_BIEN
                                                         })
                elif urbaweb_street == "Chaussée de Hannut" or urbaweb_street == "Chaussée  de Hannut":
                    # Bierset
                    if "62016" in [parcel['division'] for parcel in licence_dict['__children__'] if
                                   parcel['@type'] == 'Parcel']:
                        work_locations_dict['street'] = "Chaussée de Hannut"
                        work_locations_dict['bestaddress_key'] = "7014756"
                        work_locations_dict['number'] = str(unidecode.unidecode(urbaweb_number))
                        work_locations_dict['zipcode'] = "4460"
                        work_locations_dict['locality'] = "Bierset"
                    else:
                        # GH par défaut
                        work_locations_dict['street'] = "Chaussée de Hannut"
                        work_locations_dict['bestaddress_key'] = "7024004"
                        work_locations_dict['number'] = str(unidecode.unidecode(urbaweb_number))
                        work_locations_dict['zipcode'] = "4460"
                        work_locations_dict['locality'] = "Grâce-Hollogne"
                else:
                    self.street_errors.append(ErrorToCsv("street_errors",
                                                         "Plus d'un seul résultat pour cette rue",
                                                         licence.NUM_PERMIS,
                                                         "rue : {}"
                                                         .format(licence.SITUATION_BIEN)))
                    self.licence_description.append({'objet': "Plus d'un seul résultat pour cette rue",
                                                     'rue': licence.SITUATION_BIEN
                                                     })
        if work_locations_dict['street'] or work_locations_dict['number']:
            work_locations_list.append(work_locations_dict)

        return work_locations_list

    @benchmark_decorator
    def get_applicants(self, licence, licence_children, licence_dict):

        applicant_dict = get_applicant_dict()
        applicant_dict['name1'] = licence.NOM
        applicant_dict['name2'] = licence.PRENOM
        applicant_dict['street'] = licence.ADRESSE
        applicant_dict['zipcode'] = licence.CODE
        applicant_dict['city'] = licence.COMMUNE
        if licence_dict["@type"] in ['Division', 'UrbanCertificateOne', 'UrbanCertificateTwo', 'NotaryLetter']:
            applicant_dict['@type'] = 'Proprietary'
        licence_children.append(applicant_dict)


    @benchmark_decorator
    def get_parcels(self, licence, licence_children):
        if not licence.RADICAUX:
            return
        radicaux = licence.RADICAUX.split(",")
        division_code = licence.DIV
        if len(division_code) == 1:
            division_code = '0{}'.format(division_code)
        division = division_mapping.get(division_code, None)
        section = licence.SECT.upper()
        if division and section and radicaux:
            try:
                for radical_group in radicaux:
                    parcels_dict = get_parcel_dict()
                    parcels_dict['complete_name'] = "{} {} {}".format(division, section, licence.RADICAUX)
                    bis = '0'
                    if '/' in radical_group:
                        bis_regex = r"\/(\d+)"
                        search_bis = re.search(bis_regex, radical_group)
                        if search_bis:
                            bis = re.search(bis_regex, radical_group).group(1)
                        radical_group = re.sub(bis_regex, "", radical_group)
                    regex = r"^(\d+)(\w{1})?(\d+)?$"
                    result = re.search(regex, radical_group)
                    if not result:
                        self.parcel_errors.append(ErrorToCsv("parcels_errors",
                                                             "Parcelle incomplète ou non valide",
                                                             licence.NUM_PERMIS,
                                                             parcels_dict['complete_name']))
                        continue
                    if result.group(1):
                        radical = result.group(1)
                    else:
                        radical = ''
                    if result.group(2):
                        exposant = result.group(2).upper()
                    else:
                        exposant = ' '
                    if result.group(3):
                        puissance = result.group(3)
                    else:
                        puissance = '0'

                    if division and section and radical:
                        capakey = '{0:05d}{1}{2:04d}/{3:02d}{4}{5:03d}'.format(
                            int(division),
                            section,
                            int(radical),
                            int(bis),
                            exposant,
                            int(puissance),
                        )
                        if capakey and len(capakey) != 17:
                            # print("capakey ko: {}".format(capakey))
                            self.parcel_errors.append(ErrorToCsv("parcels_errors",
                                                                 "Parcelle incomplète ou non valide",
                                                                 licence.NUM_PERMIS,
                                                                 parcels_dict['complete_name']))
                            self.licence_description.append({'objet': "Parcelle incomplète ou non valide",
                                                             'parcelle': parcels_dict['complete_name'],
                                                             })
                            continue
                        parcelles_cadastrales = self.cadastral.cadastre_parcelles_vue
                        cadastral_parcels = parcelles_cadastrales[
                            (parcelles_cadastrales.capakey == capakey)
                        ]
                        result_count = cadastral_parcels.shape[0]
                        if result_count >= 1:
                            parcels_dict['outdated'] = 'False'
                            parcels_dict['is_official'] = 'True'
                            parcels_dict['division'] = str(cadastral_parcels.iloc[0]['division'])
                            parcels_dict['section'] = cadastral_parcels.iloc[0]['section']
                            parcels_dict['radical'] = str(cadastral_parcels.iloc[0]['radical'])
                            parcels_dict['bis'] = str(cadastral_parcels.iloc[0]['bis']) if cadastral_parcels.iloc[0][
                                'bis'] else ""
                            parcels_dict['exposant'] = cadastral_parcels.iloc[0]['exposant']
                            parcels_dict['puissance'] = str(cadastral_parcels.iloc[0]['puissance']) if cadastral_parcels.iloc[0]['puissance'] else ""
                        elif result_count == 0:
                            try:
                                parcelles_old_cadastrales = self.cadastral.cadastre_parcelles_old_vue
                                cadastral_parcels_old = parcelles_old_cadastrales[
                                    (parcelles_old_cadastrales.capakey == capakey)
                                ]
                            except Exception as e:
                                print(e)

                            result_count_old = cadastral_parcels_old.shape[0]
                            # Looking for old parcels
                            if result_count_old >= 1:
                                parcels_dict['outdated'] = 'True'
                                parcels_dict['is_official'] = 'True'
                                parcels_dict['division'] = str(cadastral_parcels_old.iloc[0]['division'])
                                parcels_dict['section'] = cadastral_parcels_old.iloc[0]['section']
                                parcels_dict['radical'] = str(int(cadastral_parcels_old.iloc[0]['radical']))
                                parcels_dict['bis'] = str(cadastral_parcels_old.iloc[0]['bis']) if \
                                    cadastral_parcels_old.iloc[0]['bis'] else ""
                                parcels_dict['exposant'] = cadastral_parcels_old.iloc[0]['exposant']
                                parcels_dict['puissance'] = str(cadastral_parcels_old.iloc[0]['puissance']) if \
                                    cadastral_parcels_old.iloc[0]['puissance'] else ""
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
                    if parcels_dict['division'] and parcels_dict['section']:
                        licence_children.append(parcels_dict)
            except Exception as e:
                print(e)

    @benchmark_decorator
    def get_organization(self, licence, licence_dict):
        organization_dict = get_organization_dict()

        if licence.ARCHITECTE:
            organization_dict['@type'] = 'Architect'
            organization_dict['name1'] = licence.ARCHITECTE
            # fix link to an existing architect restapi side
            if organization_dict['name1'] == u"ENTR'AXES ARCHITECTES":
                organization_dict['name1'] = u"ENTRAXES ARCHITECTES"
            if organization_dict['name1'] == '---' or organization_dict['name1'] == '/':
                organization_dict['name1'] = "inconnu"
            organization_dict['number'] = re.sub(r'^\D*', '', licence.ADR_ARCHI).strip()
            organization_dict['street'] = re.sub(r'\d.*', '', licence.ADR_ARCHI).replace(",","").strip()
            organization_dict['zipcode'] = licence.CODE_ARCHI
            organization_dict['city'] = licence.COMMUNE_ARCHI
            licence_dict['architects'].append(organization_dict)

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

        if licence.AUTORISATION:
            if int(licence.AUTORISATION[6:8]) > 23:
                year = "19"
            else:
                year = "20"
            date_autorisation = "{}{}-{}-{}".format(year, licence.AUTORISATION[6:8], licence.AUTORISATION[3:5], licence.AUTORISATION[0:2])
        if licence.REFUS:
            if int(licence.REFUS[6:8]) > 23:
                year = "19"
            else:
                year = "20"
            date_refus = "{}{}-{}-{}".format(year, licence.REFUS[6:8], licence.REFUS[3:5], licence.REFUS[0:2])

        if licence.AUTORISATION and not licence.REFUS:
            event_dict['eventDate'] = date_autorisation
            licence_dict['wf_state'] = 'accept'
        elif not licence.AUTORISATION and licence.REFUS:
            event_dict['eventDate'] = date_refus
            licence_dict['wf_state'] = 'refuse'
        elif licence.AUTORISATION and licence.REFUS:
            if date_autorisation > date_refus:
                licence_dict['wf_state'] = 'accept'
            elif date_autorisation < date_refus:
                licence_dict['wf_state'] = 'refuse'
            else:
                licence_dict['wf_state'] = ''
                self.licence_description.append({'objet': "Autorisation et Refus à la même date : {}".format(licence.SITUATION_BIEN)})
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
