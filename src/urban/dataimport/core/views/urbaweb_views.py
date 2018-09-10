def create_views(import_urbaweb):
    import_urbaweb.db.create_view("permis_urbanisation_vue",
                                   """
                                    SELECT 'ID', 'TYPE', 'PERMIS_NUM', 'REFERENCE', 'REFERENCE_DGO3', 'RUE', 'NUMERO', 'CP', 'LOCALITE', 'DATE_DEMANDE', 'DATE_RECEPISSE', 'DATE_DEPOT', 'NAT', 'LIBNAT', 'PERMIS_REMARQUE', 'DEMANDEURS', 'PARCELLES', 'DATE ANNULATION', 'DATE_AUTORISATION', 'DOCUMENTS', 'ORGANISME_NOM', 'ORGANISME_PRENOM', 'ORGANISME_RUE', 'ORGANISME_NUMERO', 'ORGANISME_CP', 'ORGANISME_LOCALITE', 'ORGANISME_TEL', 'ORGANISME_GSM', 'ORGANISME_TYPE'
                                    UNION ALL
                                    SELECT PERMIS.id, PERMIS.type_permis_fk, PERMIS.numero_permis, CONCAT(PERMIS.annee_recepisse, '/', PERMIS.numero_permis) AS REFERENCE, PERMIS.reference_urbanisme, PERMIS.info_rue_d, PERMIS.numero, LOCALITE.code_postal, LOCALITE.libelle_f, PERMIS.date_demande, PERMIS.date_recepisse, PERMIS.date_depot, NATURE.libelle_f, PERMIS.libnat, REPLACE( IFNULL(PERMIS.remarque_resume, ''), '\"' , "\\" ), DEMANDEURS.CONCAT_DEMANDEUR, PARCELS.CONCAT_PARCELS, PERMIS.date_permis_annule, PURB.date_autorisation, PERMIS_DOCUMENTS.DOCUMENTS, ORG.nom, ORG.prenom, ORG.rue, ORG.numero, ORG.code_postal, ORG.localite, ORG.telephone, ORG.gsm, ORG.type_list FROM soignies_urbacsv_20171114.p_permis AS PERMIS
                                    LEFT JOIN get_demandeurs AS DEMANDEURS ON DEMANDEURS.ID_PERMIS = PERMIS.id
                                    LEFT JOIN get_parcelles AS PARCELS ON PARCELS.ID_PERMIS = PERMIS.id
                                    LEFT JOIN c_localite AS LOCALITE ON PERMIS.localite_fk = LOCALITE.id
                                    LEFT JOIN c_nature AS NATURE ON PERMIS.nature_fk = NATURE.id
                                    LEFT JOIN p_permis_lotir AS PU ON PURB.id = PERMIS.id
                                    LEFT JOIN c_organisme AS ORG ON PURB.organisme_fk = ORG.id
                                    LEFT JOIN get_document_infos AS PERMIS_DOCUMENTS ON PERMIS_DOCUMENTS.ID_PERMIS = PERMIS.id
                                    WHERE PERMIS.type_permis_fk = 2
                                    INTO OUTFILE '/tmp/PURB_1.csv'
                                    -- INTO OUTFILE '/var/lib/mysql-files/xxx.csv' -- set user rights on this folder, remove file csv output file between general query execution
                                    CHARACTER SET 'utf8'
                                    FIELDS TERMINATED BY ';'
                                    ENCLOSED BY '"'
                                    LINES TERMINATED BY '\n';
                                   """
                                  )
