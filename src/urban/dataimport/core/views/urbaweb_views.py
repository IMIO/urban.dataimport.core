# -*- coding: utf-8 -*-
def create_views(import_urbaweb):
    import_urbaweb.db.create_view("permis_urbanisme_vue",
                                  """
                                    SELECT PERMIS.id,
                                           PERMIS.type_permis_fk,
                                           PERMIS.numero_permis AS REFERENCE_TECH,
                                           PERMIS.numero_permis_delivre AS REFERENCE,
                                           PERMIS.reference_urbanisme AS REFERENCE_URB,
                                           PERMIS.statut_permis AS STATUT,
                                           PERMIS.parcelle_hors_commune AS PHC,
                                           PERMIS.info_rue_f AS LOCALITE_RUE,
                                           PERMIS.numero AS LOCALITE_NUM,
                                           LOCALITE.code_postal AS LOCALITE_CP,
                                           LOCALITE.libelle_f AS LOCALITE_LABEL,
                                           PERMIS.date_demande AS DATE_DEMANDE,
                                           PERMIS.date_recepisse AS DATE_RECEPISSE,
                                           PERMIS.date_depot AS DATE_DEPOT,
                                           NATURE.libelle_f AS NATURE_TITRE,
                                           PERMIS.libnat AS NATURE_DETAILS,
                                           PERMIS.remarque_resume AS REMARQUES,
                                           DEMANDEURS.CONCAT_DEMANDEUR  AS INFOS_DEMANDEURS,
                                           IF(PARCELS.CONCAT_PARCELS = '1|.|0000/00#000', '', PARCELS.CONCAT_PARCELS) AS INFOS_PARCELLES,
                                           AUTORISATION.date_autorisation_college AS AUTORISATION_DATE_AUTORISATION_COLLEGE,
                                           AUTORISATION.date_refus_college AS AUTORISATION_DATE_REFUS_COLLEGE,                                           
                                           AUTORISATION.date_autorisation_tutelle AS AUTORISATION_DATE_AUTORISATION_TUTELLE,
                                           AUTORISATION.date_refus_tutelle AS AUTORISATION_DATE_REFUS_TUTELLE,
                                           AVIS_COLLEGE.libelle_f AS AVIS_COLLEGE_LABEL,
                                           AVIS_RECOUR.libelle_f AS RECOUR_AVIS_LABEL,
                                           RECOUR.remarque  AS RECOUR_REMARQUE,
                                           RECOUR.reference_rw AS RECOUR_REFERENCE,
                                           TRAVAUX.date_debut AS DEBUT_TRAVAUX,
                                           TRAVAUX.date_fin AS FIN_TRAVAUX,
                                           PERMIS_DOCUMENTS.DOCUMENTS AS INFOS_DOCUMENTS,
                                           ORG.civilite_fk AS ORG_TITLE_ID,
                                           ORG.nom AS ORG_NOM,
                                           ORG.prenom AS ORG_PRENOM,
                                           ORG.rue AS ORG_RUE,
                                           ORG.numero AS ORG_NUMERO,
                                           ORG.code_postal AS ORG_CP,
                                           ORG.localite AS ORG_LOCALITE,
                                           ORG.telephone AS ORG_TEL,
                                           ORG.gsm AS ORG_MOBILE,
                                           ORG.mail AS ORG_MAIL,
                                           ORG.type_list AS ORG_TYPE
                                    FROM p_permis AS PERMIS
                                    LEFT JOIN get_demandeurs AS DEMANDEURS ON DEMANDEURS.ID_PERMIS = PERMIS.id
                                    LEFT JOIN get_parcelles AS PARCELS ON PARCELS.ID_PERMIS = PERMIS.id
                                    LEFT JOIN c_localite AS LOCALITE ON PERMIS.localite_fk = LOCALITE.id
                                    LEFT JOIN c_nature AS NATURE ON PERMIS.nature_fk = NATURE.id
                                    LEFT JOIN p_permis_urbanisme AS PU ON PU.id = PERMIS.id
                                    LEFT JOIN c_organisme AS ORG ON PU.organisme_fk = ORG.id
                                    LEFT JOIN p_autorisation AS AUTORISATION ON PU.autorisation_fk = AUTORISATION.id
                                    LEFT JOIN c_avis_college AS AVIS_COLLEGE ON AVIS_COLLEGE.id = AUTORISATION.avis_college_fk
                                    LEFT JOIN p_recour AS RECOUR ON PU.recour_fk = RECOUR.id
                                    LEFT JOIN c_avis_college AS AVIS_RECOUR ON AVIS_RECOUR.id = RECOUR.avis_fk
                                    LEFT JOIN get_document_infos AS PERMIS_DOCUMENTS ON PERMIS_DOCUMENTS.ID_PERMIS = PERMIS.id
                                    LEFT JOIN p_travaux AS TRAVAUX ON TRAVAUX.id = PU.travaux_fk
                                    WHERE PERMIS.type_permis_fk = 1 AND PERMIS.numero_permis NOT IN ('2017/Purb/001', '2017/Purb/002');
                                  """
                                  )

    # import_urbaweb.db.create_view("permis_article127_vue",
    #                               """
    #                                 SELECT PERMIS.id,
    #                                        PERMIS.type_permis_fk,
    #                                        PERMIS.numero_permis AS REFERENCE_TECH,
    #                                        PERMIS.numero_permis_delivre AS REFERENCE,
    #                                        PERMIS.reference_urbanisme AS REFERENCE_URB,
    #                                        PERMIS.statut_permis AS STATUT,
    #                                        PERMIS.parcelle_hors_commune AS PHC,
    #                                        PERMIS.info_rue_f AS LOCALITE_RUE,
    #                                        PERMIS.numero AS LOCALITE_NUM,
    #                                        LOCALITE.code_postal AS LOCALITE_CP,
    #                                        LOCALITE.libelle_f AS LOCALITE_LABEL,
    #                                        PERMIS.date_demande AS DATE_DEMANDE,
    #                                        PERMIS.date_recepisse AS DATE_RECEPISSE,
    #                                        PERMIS.date_depot AS DATE_DEPOT,
    #                                        NATURE.libelle_f AS NATURE_TITRE,
    #                                        PERMIS.libnat AS NATURE_DETAILS,
    #                                        PERMIS.remarque_resume AS REMARQUES,
    #                                        DEMANDEURS.CONCAT_DEMANDEUR  AS INFOS_DEMANDEURS,
    #                                        IF(PARCELS.CONCAT_PARCELS = '1|.|0000/00#000', '', PARCELS.CONCAT_PARCELS) AS INFOS_PARCELLES,
    #                                        AUTORISATION.date_autorisation_college AS AUTORISATION_DATE_AUTORISATION_COLLEGE,
    #                                        AUTORISATION.date_refus_college AS AUTORISATION_DATE_REFUS_COLLEGE,
    #                                        AUTORISATION.date_autorisation_tutelle AS AUTORISATION_DATE_AUTORISATION_TUTELLE,
    #                                        AUTORISATION.date_refus_tutelle AS AUTORISATION_DATE_REFUS_TUTELLE,
    #                                        AVIS_COLLEGE.libelle_f AS AVIS_COLLEGE_LABEL,
    #                                        AVIS_RECOUR.libelle_f AS RECOUR_AVIS_LABEL,
    #                                        RECOUR.date_decision_tutelle DATE_DECISION_TUTELLE,
    #                                        RECOUR.decision_tutelle AS DECISION_TUTELLE,
    #                                        RECOUR.remarque  AS RECOUR_REMARQUE,
    #                                        RECOUR.reference_rw AS RECOUR_REFERENCE,
    #                                        TRAVAUX.date_debut AS DEBUT_TRAVAUX,
    #                                        TRAVAUX.date_fin AS FIN_TRAVAUX,
    #                                        PERMIS_DOCUMENTS.DOCUMENTS AS INFOS_DOCUMENTS,
    #                                        ORG.civilite_fk AS ORG_TITLE_ID,
    #                                        ORG.nom AS ORG_NOM,
    #                                        ORG.prenom AS ORG_PRENOM,
    #                                        ORG.rue AS ORG_RUE,
    #                                        ORG.numero AS ORG_NUMERO,
    #                                        ORG.code_postal AS ORG_CP,
    #                                        ORG.localite AS ORG_LOCALITE,
    #                                        ORG.telephone AS ORG_TEL,
    #                                        ORG.gsm AS ORG_MOBILE,
    #                                        ORG.mail AS ORG_MAIL,
    #                                        ORG.type_list AS ORG_TYPE,
    #                                        DIRECTIVE.fonctionnaire_delegue AS DIRECTIVE_FD,
    #                                        DIRECTIVE.autorite_competente AS DIRECTIVE_AUTORITE_COMPETENTE
    #                                 FROM p_permis AS PERMIS
    #                                 LEFT JOIN get_demandeurs AS DEMANDEURS ON DEMANDEURS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN get_parcelles AS PARCELS ON PARCELS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN c_localite AS LOCALITE ON PERMIS.localite_fk = LOCALITE.id
    #                                 LEFT JOIN c_nature AS NATURE ON PERMIS.nature_fk = NATURE.id
    #                                 LEFT JOIN p_permis_urbanisme AS PU ON PU.id = PERMIS.id
    #                                 LEFT JOIN c_organisme AS ORG ON PU.organisme_fk = ORG.id
    #                                 LEFT JOIN p_autorisation AS AUTORISATION ON PU.autorisation_fk = AUTORISATION.id
    #                                 LEFT JOIN c_avis_college AS AVIS_COLLEGE ON AVIS_COLLEGE.id = AUTORISATION.avis_college_fk
    #                                 LEFT JOIN p_recour AS RECOUR ON PU.recour_fk = RECOUR.id
    #                                 LEFT JOIN c_avis_college AS AVIS_RECOUR ON AVIS_RECOUR.id = RECOUR.avis_fk
    #                                 LEFT JOIN get_document_infos AS PERMIS_DOCUMENTS ON PERMIS_DOCUMENTS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN p_directive AS DIRECTIVE ON PERMIS.directive_fk = DIRECTIVE.id
    #                                 LEFT JOIN p_travaux AS TRAVAUX ON TRAVAUX.id = PU.travaux_fk
    #                                 WHERE PERMIS.type_permis_fk = 1 AND DIRECTIVE.autorite_competente IN ('1', '2');
    #                               """
    #                               )

    import_urbaweb.db.create_view("permis_urbanisation_vue",
                                  """
                                           SELECT PERMIS.id,
                                           PERMIS.type_permis_fk,
                                           PERMIS.numero_permis AS REFERENCE_TECH,
                                           PERMIS.numero_permis_delivre AS REFERENCE,
                                           PERMIS.reference_urbanisme AS REFERENCE_URB,
                                           PERMIS.statut_permis AS STATUT,
                                           PERMIS.parcelle_hors_commune AS PHC,
                                           PERMIS.info_rue_f AS LOCALITE_RUE,
                                           PERMIS.numero AS LOCALITE_NUM,
                                           LOCALITE.code_postal AS LOCALITE_CP,
                                           LOCALITE.libelle_f AS LOCALITE_LABEL,
                                           PERMIS.date_demande AS DATE_DEMANDE,
                                           PERMIS.date_recepisse AS DATE_RECEPISSE,
                                           PERMIS.date_depot AS DATE_DEPOT,
                                           NATURE.libelle_f AS NATURE_TITRE,
                                           PERMIS.libnat AS NATURE_DETAILS,
                                           PERMIS.remarque_resume AS REMARQUES,
                                           DEMANDEURS.CONCAT_DEMANDEUR  AS INFOS_DEMANDEURS,
                                           IF(PARCELS.CONCAT_PARCELS = '1|.|0000/00#000', '', PARCELS.CONCAT_PARCELS) AS INFOS_PARCELLES,
                                           AUTORISATION.date_autorisation_college AS AUTORISATION_DATE_AUTORISATION_COLLEGE,
                                           AUTORISATION.date_refus_college AS AUTORISATION_DATE_REFUS_COLLEGE,                                           
                                           AUTORISATION.date_autorisation_tutelle AS AUTORISATION_DATE_AUTORISATION_TUTELLE,
                                           AUTORISATION.date_refus_tutelle AS AUTORISATION_DATE_REFUS_TUTELLE,
                                           AVIS_COLLEGE.libelle_f AS AVIS_COLLEGE_LABEL,
                                           AVIS_RECOUR.libelle_f AS RECOUR_AVIS_LABEL,
                                           RECOUR.remarque  AS RECOUR_REMARQUE,
                                           RECOUR.reference_rw AS RECOUR_REFERENCE,
                                           TRAVAUX.date_debut AS DEBUT_TRAVAUX,
                                           TRAVAUX.date_fin AS FIN_TRAVAUX,
                                           PERMIS_DOCUMENTS.DOCUMENTS AS INFOS_DOCUMENTS,
                                           ORG.civilite_fk AS ORG_TITLE_ID,
                                           ORG.nom AS ORG_NOM,
                                           ORG.prenom AS ORG_PRENOM,
                                           ORG.rue AS ORG_RUE,
                                           ORG.numero AS ORG_NUMERO,
                                           ORG.code_postal AS ORG_CP,
                                           ORG.localite AS ORG_LOCALITE,
                                           ORG.telephone AS ORG_TEL,
                                           ORG.gsm AS ORG_MOBILE,
                                           ORG.mail AS ORG_MAIL,
                                           ORG.type_list AS ORG_TYPE,
                                           PURB.nom_lotissement AS NOM_LOT,
                                           PURB.nombre_de_lots AS NB_LOT
                                    FROM p_permis AS PERMIS
                                    LEFT JOIN get_demandeurs AS DEMANDEURS ON DEMANDEURS.ID_PERMIS = PERMIS.id
                                    LEFT JOIN get_parcelles AS PARCELS ON PARCELS.ID_PERMIS = PERMIS.id
                                    LEFT JOIN c_localite AS LOCALITE ON PERMIS.localite_fk = LOCALITE.id
                                    LEFT JOIN c_nature AS NATURE ON PERMIS.nature_fk = NATURE.id
                                    LEFT JOIN p_permis_lotir AS PURB ON PURB.id = PERMIS.id
                                    LEFT JOIN c_organisme AS ORG ON PURB.organisme_fk = ORG.id
                                    LEFT JOIN p_autorisation AS AUTORISATION ON PURB.autorisation_fk = AUTORISATION.id
                                    LEFT JOIN c_avis_college AS AVIS_COLLEGE ON AVIS_COLLEGE.id = AUTORISATION.avis_college_fk
                                    LEFT JOIN p_recour AS RECOUR ON PURB.recour_fk = RECOUR.id
                                    LEFT JOIN c_avis_college AS AVIS_RECOUR ON AVIS_RECOUR.id = RECOUR.avis_fk
                                    LEFT JOIN get_document_infos AS PERMIS_DOCUMENTS ON PERMIS_DOCUMENTS.ID_PERMIS = PERMIS.id
                                    LEFT JOIN p_travaux AS TRAVAUX ON TRAVAUX.id = PURB.travaux_fk
                                    WHERE PERMIS.type_permis_fk = 2 OR PERMIS.type_permis_fk = 16;
                                  """
                                  )

    import_urbaweb.db.create_view("permis_env_classe3_vue",
                                  """
                                    SELECT PERMIS.id,
                                    PERMIS.type_permis_fk,
                                    PERMIS.numero_permis AS REFERENCE_TECH,
                                    PERMIS.numero_permis_delivre AS REFERENCE,
                                    PERMIS.reference_urbanisme  AS REFERENCE_URB,
                                    PERMIS.statut_permis AS STATUT,
                                    PERMIS.parcelle_hors_commune AS PHC,
                                    PERMIS.info_rue_f AS LOCALITE_RUE,
                                    PERMIS.numero  AS LOCALITE_NUM,
                                    LOCALITE.code_postal AS LOCALITE_CP,
                                    LOCALITE.libelle_f AS LOCALITE_LABEL,
                                    PERMIS.date_demande AS DATE_DEMANDE,
                                    PERMIS.date_recepisse AS DATE_RECEPISSE,
                                    PERMIS.date_depot AS DATE_DEPOT,
                                    NATURE.libelle_f AS NATURE_TITRE,
                                    PERMIS.libnat AS NATURE_DETAILS,
                                    IFNULL(PERMIS.remarque_resume, '') AS REMARQUES,
                                    DEMANDEURS.CONCAT_DEMANDEUR AS INFOS_DEMANDEURS,
                                    IF(PARCELS.CONCAT_PARCELS = '1|.|0000/00#000', '', PARCELS.CONCAT_PARCELS) AS INFOS_PARCELLES,
                                    PE3_DECISION.date_autorisation_college AS AUTORISATION_DATE_AUTORISATION_COLLEGE,
                                    PE3_DECISION.date_refus_college AS AUTORISATION_DATE_REFUS_COLLEGE,                                           
                                    PE3_DECISION.date_autorisation_tutelle AS AUTORISATION_DATE_AUTORISATION_TUTELLE,
                                    PE3_DECISION.date_refus_tutelle AS AUTORISATION_DATE_REFUS_TUTELLE,
                                    RUBRICS.CONCAT_RUBRICS_CODE AS INFOS_RUBRIQUES,
                                    PERMIS_DOCUMENTS.DOCUMENTS AS INFOS_DOCUMENTS
                                    FROM p_permis AS PERMIS
                                    LEFT JOIN get_demandeurs AS DEMANDEURS ON DEMANDEURS.ID_PERMIS = PERMIS.id
                                    LEFT JOIN get_parcelles AS PARCELS ON PARCELS.ID_PERMIS = PERMIS.id
                                    LEFT JOIN c_localite AS LOCALITE ON PERMIS.localite_fk = LOCALITE.id
                                    LEFT JOIN c_nature AS NATURE ON PERMIS.nature_fk = NATURE.id
                                    LEFT JOIN p_permis_environnement_classe3 AS PE3 ON PE3.id = PERMIS.id
                                    LEFT JOIN p_decision_environnement_classe3 AS PE3_DECISION ON PE3.decision_environnement_fk = PE3_DECISION.id
                                    LEFT JOIN get_rubrics_cl3 AS RUBRICS ON RUBRICS.ID_PERMIS = PERMIS.id
                                    LEFT JOIN get_document_infos AS PERMIS_DOCUMENTS ON PERMIS_DOCUMENTS.ID_PERMIS = PERMIS.id
                                    WHERE PERMIS.type_permis_fk = 17 AND PERMIS.numero_permis NOT IN ('2017/classe3/03', '2017/classe3/04', '2017/classe3/06');
                                  """
                                  )

    import_urbaweb.db.create_view("permis_unique_vue",
                                  """
                                    SELECT PERMIS.id,
                                    PERMIS.type_permis_fk,
                                    PERMIS.numero_permis AS REFERENCE_TECH,
                                    PERMIS.numero_permis_delivre AS REFERENCE,
                                    PERMIS.reference_urbanisme  AS REFERENCE_URB,
                                    PERMIS.statut_permis AS STATUT,
                                    PERMIS.parcelle_hors_commune AS PHC,
                                    PERMIS.info_rue_f AS LOCALITE_RUE,
                                    PERMIS.numero  AS LOCALITE_NUM,
                                    LOCALITE.code_postal AS LOCALITE_CP,
                                    LOCALITE.libelle_f AS LOCALITE_LABEL,
                                    PERMIS.date_demande AS DATE_DEMANDE,
                                    PERMIS.date_recepisse AS DATE_RECEPISSE,
                                    PERMIS.date_depot AS DATE_DEPOT,
                                    NATURE.libelle_f AS NATURE_TITRE,
                                    PERMIS.libnat AS NATURE_DETAILS,
                                    IFNULL(PERMIS.remarque_resume, '') AS REMARQUES,
                                    DEMANDEURS.CONCAT_DEMANDEUR AS INFOS_DEMANDEURS,
                                    IF(PARCELS.CONCAT_PARCELS = '1|.|0000/00#000', '', PARCELS.CONCAT_PARCELS) AS INFOS_PARCELLES,
                                    PUN_DECISION.date_autorisation_college AS AUTORISATION_DATE_AUTORISATION_COLLEGE,
                                    PUN_DECISION.date_autorisation_tutelle AS AUTORISATION_DATE_AUTORISATION_TUTELLE,
                                    PUN_DECISION.date_refus_college AS AUTORISATION_DATE_REFUS_COLLEGE,
                                    PUN_DECISION.date_refus_tutelle AS AUTORISATION_DATE_REFUS_TUTELLE,
                                    TRAVAUX.date_debut AS DEBUT_TRAVAUX,
                                    TRAVAUX.date_fin AS FIN_TRAVAUX,
                                    RUBRICS.CONCAT_RUBRICS_CODE AS INFOS_RUBRIQUES,
                                    PERMIS_DOCUMENTS.DOCUMENTS AS INFOS_DOCUMENTS,
                                    ORG.civilite_fk AS ORG_TITLE_ID,
                                    ORG.nom AS ORG_NOM,
                                    ORG.prenom AS ORG_PRENOM,
                                    ORG.rue AS ORG_RUE,
                                    ORG.numero AS ORG_NUMERO,
                                    ORG.code_postal AS ORG_CP,
                                    ORG.localite AS ORG_LOCALITE,
                                    ORG.telephone AS ORG_TEL,
                                    ORG.gsm AS ORG_MOBILE,
                                    ORG.mail AS ORG_MAIL,
                                    ORG.type_list AS ORG_TYPE
                                    FROM p_permis AS PERMIS
                                    LEFT JOIN get_demandeurs AS DEMANDEURS ON DEMANDEURS.ID_PERMIS = PERMIS.id
                                    LEFT JOIN get_parcelles AS PARCELS ON PARCELS.ID_PERMIS = PERMIS.id
                                    LEFT JOIN c_localite AS LOCALITE ON PERMIS.localite_fk = LOCALITE.id
                                    LEFT JOIN c_nature AS NATURE ON PERMIS.nature_fk = NATURE.id
                                    LEFT JOIN p_permis_unique AS PUN ON PUN.id = PERMIS.id
                                    LEFT JOIN p_decision_unique AS PUN_DECISION ON PUN.decision_unique_fk = PUN_DECISION.id
                                    LEFT JOIN c_organisme AS ORG ON PUN.organisme_fk = ORG.id
                                    LEFT JOIN get_rubrics_unique AS RUBRICS ON RUBRICS.ID_PERMIS = PERMIS.id
                                    LEFT JOIN get_document_infos AS PERMIS_DOCUMENTS ON PERMIS_DOCUMENTS.ID_PERMIS = PERMIS.id
                                    LEFT JOIN p_travaux AS TRAVAUX ON TRAVAUX.id = PUN.travaux_fk
                                    WHERE PERMIS.type_permis_fk = 10;
                                  """
                                  )
    # Type 11 : Autres dossiers
    # Type 7 : Déclaration Impétrants
    # Type 18 : Infraction Urbanistique
    # Type 19 : Permis Location
    # Type 21 : Insalubrité logement

    # import_urbaweb.db.create_view("permis_autre_dossier_vue",
    #                               """
    #                                 SELECT PERMIS.id,
    #                                        PERMIS.type_permis_fk,
    #                                        PERMIS.numero_permis AS REFERENCE_TECH,
    #                                        PERMIS.numero_permis_delivre AS REFERENCE,
    #                                        PERMIS.reference_urbanisme AS REFERENCE_URB,
    #                                        PERMIS.statut_permis AS STATUT,
    #                                        PERMIS.parcelle_hors_commune AS PHC,
    #                                        PERMIS.info_rue_f AS LOCALITE_RUE,
    #                                        PERMIS.numero AS LOCALITE_NUM,
    #                                        LOCALITE.code_postal AS LOCALITE_CP,
    #                                        LOCALITE.libelle_f AS LOCALITE_LABEL,
    #                                        PERMIS.date_demande AS DATE_DEMANDE,
    #                                        PERMIS.date_recepisse AS DATE_RECEPISSE,
    #                                        PERMIS.date_depot AS DATE_DEPOT,
    #                                        NATURE.libelle_f AS NATURE_TITRE,
    #                                        PERMIS.libnat AS NATURE_DETAILS,
    #                                        PERMIS.remarque_resume AS REMARQUES,
    #                                        DEMANDEURS.CONCAT_DEMANDEUR  AS INFOS_DEMANDEURS,
    #                                        IF(PARCELS.CONCAT_PARCELS = '1|.|0000/00#000', '', PARCELS.CONCAT_PARCELS) AS INFOS_PARCELLES,
    #                                        AUTORISATION.date_autorisation_college AS AUTORISATION_DATE_AUTORISATION_COLLEGE,
    #                                        AUTORISATION.date_refus_college AS AUTORISATION_DATE_REFUS_COLLEGE,
    #                                        AUTORISATION.date_autorisation_tutelle AS AUTORISATION_DATE_AUTORISATION_TUTELLE,
    #                                        AUTORISATION.date_refus_tutelle AS AUTORISATION_DATE_REFUS_TUTELLE,
    #                                        PERMIS_DOCUMENTS.DOCUMENTS AS INFOS_DOCUMENTS,
    #                                        ORG.civilite_fk AS ORG_TITLE_ID,
    #                                        ORG.nom AS ORG_NOM,
    #                                        ORG.prenom AS ORG_PRENOM,
    #                                        ORG.rue AS ORG_RUE,
    #                                        ORG.numero AS ORG_NUMERO,
    #                                        ORG.code_postal AS ORG_CP,
    #                                        ORG.localite AS ORG_LOCALITE,
    #                                        ORG.telephone AS ORG_TEL,
    #                                        ORG.gsm AS ORG_MOBILE,
    #                                        ORG.mail AS ORG_MAIL,
    #                                        ORG.type_list AS ORG_TYPE
    #                                 FROM p_permis AS PERMIS
    #                                 LEFT JOIN get_demandeurs AS DEMANDEURS ON DEMANDEURS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN get_parcelles AS PARCELS ON PARCELS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN c_localite AS LOCALITE ON PERMIS.localite_fk = LOCALITE.id
    #                                 LEFT JOIN c_nature AS NATURE ON PERMIS.nature_fk = NATURE.id
    #                                 LEFT JOIN p_permis_autre_dossier AS PAD ON PAD.id = PERMIS.id
    #                                 LEFT JOIN p_autorisation AS AUTORISATION ON PAD.autorisation_fk = AUTORISATION.id
    #                                 LEFT JOIN c_organisme AS ORG ON PAD.organisme_fk = ORG.id
    #                                 LEFT JOIN get_document_infos AS PERMIS_DOCUMENTS ON PERMIS_DOCUMENTS.ID_PERMIS = PERMIS.id
    #                                 WHERE PERMIS.type_permis_fk = 11 OR PERMIS.type_permis_fk = 7 OR PERMIS.type_permis_fk = 18 OR PERMIS.type_permis_fk = 19 OR PERMIS.type_permis_fk = 21;
    #                               """
    #                               )

    import_urbaweb.db.create_view("permis_env1_vue",
                                  """
                                    SELECT PERMIS.id,
                                    PERMIS.type_permis_fk,
                                    PERMIS.numero_permis AS REFERENCE_TECH,
                                    PERMIS.numero_permis_delivre AS REFERENCE,
                                    PERMIS.reference_urbanisme  AS REFERENCE_URB,
                                    PERMIS.statut_permis AS STATUT,
                                    PERMIS.parcelle_hors_commune AS PHC,
                                    1 AS CLASSE,
                                    PERMIS.info_rue_f AS LOCALITE_RUE,
                                    PERMIS.numero  AS LOCALITE_NUM,
                                    LOCALITE.code_postal AS LOCALITE_CP,
                                    LOCALITE.libelle_f AS LOCALITE_LABEL,
                                    PERMIS.date_demande AS DATE_DEMANDE,
                                    PERMIS.date_recepisse AS DATE_RECEPISSE,
                                    PERMIS.date_depot AS DATE_DEPOT,
                                    NATURE.libelle_f AS NATURE_TITRE,
                                    PERMIS.libnat AS NATURE_DETAILS,
                                    IFNULL(PERMIS.remarque_resume, '') AS REMARQUES,
                                    DEMANDEURS.CONCAT_DEMANDEUR AS INFOS_DEMANDEURS,
                                    IF(PARCELS.CONCAT_PARCELS = '1|.|0000/00#000', '', PARCELS.CONCAT_PARCELS) AS INFOS_PARCELLES,
                                    PE_DECISION.date_autorisation_college AS AUTORISATION_DATE_AUTORISATION_COLLEGE,
                                    PE_DECISION.date_autorisation_tutelle AS AUTORISATION_DATE_AUTORISATION_TUTELLE,
                                    PE_DECISION.date_refus_college AS AUTORISATION_DATE_REFUS_COLLEGE,
                                    PE_DECISION.date_refus_tutelle AS AUTORISATION_DATE_REFUS_TUTELLE,
                                    RUBRICS.CONCAT_RUBRICS_CODE AS INFOS_RUBRIQUES,
                                    PERMIS_DOCUMENTS.DOCUMENTS AS INFOS_DOCUMENTS
                                    FROM p_permis AS PERMIS
                                    LEFT JOIN get_demandeurs AS DEMANDEURS ON DEMANDEURS.ID_PERMIS = PERMIS.id
                                    LEFT JOIN get_parcelles AS PARCELS ON PARCELS.ID_PERMIS = PERMIS.id
                                    LEFT JOIN c_localite AS LOCALITE ON PERMIS.localite_fk = LOCALITE.id
                                    LEFT JOIN c_nature AS NATURE ON PERMIS.nature_fk = NATURE.id
                                    LEFT JOIN p_permis_environnement AS PE ON PE.id = PERMIS.id
                                    LEFT JOIN p_decision_environnement AS PE_DECISION ON PE.decision_environnement_fk = PE_DECISION.id
                                    LEFT JOIN get_rubrics AS RUBRICS ON RUBRICS.ID_PERMIS = PERMIS.id
                                    LEFT JOIN get_document_infos AS PERMIS_DOCUMENTS ON PERMIS_DOCUMENTS.ID_PERMIS = PERMIS.id
                                    WHERE PERMIS.type_permis_fk = 6 AND (environnement_classe_fk = 1 OR environnement_classe_fk = 2 OR environnement_classe_fk = 5);
                                  """
                                  )
    import_urbaweb.db.create_view("permis_env2_vue",
                                  """
                                    SELECT PERMIS.id,
                                    PERMIS.type_permis_fk,
                                    PERMIS.numero_permis AS REFERENCE_TECH,
                                    PERMIS.numero_permis_delivre AS REFERENCE,
                                    PERMIS.reference_urbanisme  AS REFERENCE_URB,
                                    PERMIS.statut_permis AS STATUT,
                                    PERMIS.parcelle_hors_commune AS PHC,
                                    2 AS CLASSE,
                                    PERMIS.info_rue_f AS LOCALITE_RUE,
                                    PERMIS.numero  AS LOCALITE_NUM,
                                    LOCALITE.code_postal AS LOCALITE_CP,
                                    LOCALITE.libelle_f AS LOCALITE_LABEL,
                                    PERMIS.date_demande AS DATE_DEMANDE,
                                    PERMIS.date_recepisse AS DATE_RECEPISSE,
                                    PERMIS.date_depot AS DATE_DEPOT,
                                    NATURE.libelle_f AS NATURE_TITRE,
                                    PERMIS.libnat AS NATURE_DETAILS,
                                    IFNULL(PERMIS.remarque_resume, '') AS REMARQUES,
                                    DEMANDEURS.CONCAT_DEMANDEUR AS INFOS_DEMANDEURS,
                                    IF(PARCELS.CONCAT_PARCELS = '1|.|0000/00#000', '', PARCELS.CONCAT_PARCELS) AS INFOS_PARCELLES,
                                    PE_DECISION.date_autorisation_college AS AUTORISATION_DATE_AUTORISATION_COLLEGE,
                                    PE_DECISION.date_autorisation_tutelle AS AUTORISATION_DATE_AUTORISATION_TUTELLE,
                                    PE_DECISION.date_refus_college AS AUTORISATION_DATE_REFUS_COLLEGE,
                                    PE_DECISION.date_refus_tutelle AS AUTORISATION_DATE_REFUS_TUTELLE,
                                    RUBRICS.CONCAT_RUBRICS_CODE AS INFOS_RUBRIQUES,
                                    PERMIS_DOCUMENTS.DOCUMENTS AS INFOS_DOCUMENTS
                                    FROM p_permis AS PERMIS
                                    LEFT JOIN get_demandeurs AS DEMANDEURS ON DEMANDEURS.ID_PERMIS = PERMIS.id
                                    LEFT JOIN get_parcelles AS PARCELS ON PARCELS.ID_PERMIS = PERMIS.id
                                    LEFT JOIN c_localite AS LOCALITE ON PERMIS.localite_fk = LOCALITE.id
                                    LEFT JOIN c_nature AS NATURE ON PERMIS.nature_fk = NATURE.id
                                    LEFT JOIN p_permis_environnement AS PE ON PE.id = PERMIS.id
                                    LEFT JOIN p_decision_environnement AS PE_DECISION ON PE.decision_environnement_fk = PE_DECISION.id
                                    LEFT JOIN get_rubrics AS RUBRICS ON RUBRICS.ID_PERMIS = PERMIS.id
                                    LEFT JOIN get_document_infos AS PERMIS_DOCUMENTS ON PERMIS_DOCUMENTS.ID_PERMIS = PERMIS.id
                                    WHERE PERMIS.type_permis_fk = 6 AND (environnement_classe_fk = 3 OR environnement_classe_fk = 6);
                                  """
                                  )
    # import_urbaweb.db.create_view("lettre_notariale_vue",
    #                               """
    #                                 SELECT PERMIS.id,
    #                                        PERMIS.type_permis_fk,
    #                                        PERMIS.numero_permis AS REFERENCE_TECH,
    #                                        PERMIS.numero_permis_delivre AS REFERENCE,
    #                                        PERMIS.reference_urbanisme AS REFERENCE_URB,
    #                                        PERMIS.statut_permis AS STATUT,
    #                                        PERMIS.parcelle_hors_commune AS PHC,
    #                                        LN.notaire_type_dossier_fk AS TYPE_DOSSIER,
    #                                        PERMIS.info_rue_f AS LOCALITE_RUE,
    #                                        PERMIS.numero AS LOCALITE_NUM,
    #                                        LOCALITE.code_postal AS LOCALITE_CP,
    #                                        LOCALITE.libelle_f AS LOCALITE_LABEL,
    #                                        PERMIS.date_demande AS DATE_DEMANDE,
    #                                        PERMIS.date_recepisse AS DATE_RECEPISSE,
    #                                        PERMIS.date_depot AS DATE_DEPOT,
    #                                        NATURE.libelle_f AS NATURE_TITRE,
    #                                        PERMIS.libnat AS NATURE_DETAILS,
    #                                        PERMIS.remarque_resume AS REMARQUES,
    #                                        DEMANDEURS.CONCAT_DEMANDEUR  AS INFOS_DEMANDEURS,
    #                                        IF(PARCELS.CONCAT_PARCELS = '1|.|0000/00#000', '', PARCELS.CONCAT_PARCELS) AS INFOS_PARCELLES,
    #                                        AUTORISATION.date_autorisation_college AS AUTORISATION_DATE_AUTORISATION_COLLEGE,
    #                                        AUTORISATION.date_refus_college AS AUTORISATION_DATE_REFUS_COLLEGE,
    #                                        PERMIS_DOCUMENTS.DOCUMENTS AS INFOS_DOCUMENTS,
    #                                        ORG.civilite_fk AS ORG_TITLE_ID,
    #                                        ORG.nom AS ORG_NOM,
    #                                        ORG.prenom AS ORG_PRENOM,
    #                                        ORG.rue AS ORG_RUE,
    #                                        ORG.numero AS ORG_NUMERO,
    #                                        ORG.code_postal AS ORG_CP,
    #                                        ORG.localite AS ORG_LOCALITE,
    #                                        ORG.telephone AS ORG_TEL,
    #                                        ORG.gsm AS ORG_MOBILE,
    #                                        ORG.mail AS ORG_MAIL,
    #                                        ORG.type_list AS ORG_TYPE,
    #                                        DIRECTIVE.fonctionnaire_delegue AS DIRECTIVE_FD,
    #                                        DIRECTIVE.autorite_competente AS DIRECTIVE_AUTORITE_COMPETENTE
    #                                 FROM p_permis AS PERMIS
    #                                 LEFT JOIN get_demandeurs AS DEMANDEURS ON DEMANDEURS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN get_parcelles AS PARCELS ON PARCELS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN c_localite AS LOCALITE ON PERMIS.localite_fk = LOCALITE.id
    #                                 LEFT JOIN c_nature AS NATURE ON PERMIS.nature_fk = NATURE.id
    #                                 LEFT JOIN p_permis_demande_notaire AS LN ON LN.id = PERMIS.id
    #                                 LEFT JOIN c_organisme AS ORG ON LN.organisme_fk = ORG.id
    #                                 LEFT JOIN p_autorisation_notaire AS AUTORISATION ON LN.autorisation_notaire_fk = AUTORISATION.id
    #                                 LEFT JOIN get_document_infos AS PERMIS_DOCUMENTS ON PERMIS_DOCUMENTS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN p_directive AS DIRECTIVE ON PERMIS.directive_fk = DIRECTIVE.id
    #                                 WHERE PERMIS.type_permis_fk = 8 AND (LN.notaire_type_dossier_fk != 1 OR LN.notaire_type_dossier_fk IS NULL);
    #                               """
    #                               )

    # import_urbaweb.db.create_view("division_vue",
    #                               """
    #                                 SELECT PERMIS.id,
    #                                        PERMIS.type_permis_fk,
    #                                        PERMIS.numero_permis AS REFERENCE_TECH,
    #                                        PERMIS.numero_permis_delivre AS REFERENCE,
    #                                        PERMIS.reference_urbanisme AS REFERENCE_URB,
    #                                        PERMIS.statut_permis AS STATUT,
    #
    #                                        PERMIS.parcelle_hors_commune AS PHC,
    #                                        LN.notaire_type_dossier_fk AS TYPE_DOSSIER,
    #                                        PERMIS.info_rue_f AS LOCALITE_RUE,
    #                                        PERMIS.numero AS LOCALITE_NUM,
    #                                        LOCALITE.code_postal AS LOCALITE_CP,
    #                                        LOCALITE.libelle_f AS LOCALITE_LABEL,
    #                                        PERMIS.date_demande AS DATE_DEMANDE,
    #                                        PERMIS.date_recepisse AS DATE_RECEPISSE,
    #                                        PERMIS.date_depot AS DATE_DEPOT,
    #                                        NATURE.libelle_f AS NATURE_TITRE,
    #                                        PERMIS.libnat AS NATURE_DETAILS,
    #                                        PERMIS.remarque_resume AS REMARQUES,
    #                                        DEMANDEURS.CONCAT_DEMANDEUR  AS INFOS_DEMANDEURS,
    #                                        IF(PARCELS.CONCAT_PARCELS = '1|.|0000/00#000', '', PARCELS.CONCAT_PARCELS) AS INFOS_PARCELLES,
    #                                        AUTORISATION.date_autorisation_college AS AUTORISATION_DATE_AUTORISATION_COLLEGE,
    #                                        AUTORISATION.date_refus_college AS AUTORISATION_DATE_REFUS_COLLEGE,
    #                                        PERMIS_DOCUMENTS.DOCUMENTS AS INFOS_DOCUMENTS,
    #                                        ORG.civilite_fk AS ORG_TITLE_ID,
    #                                        ORG.nom AS ORG_NOM,
    #                                        ORG.prenom AS ORG_PRENOM,
    #                                        ORG.rue AS ORG_RUE,
    #                                        ORG.numero AS ORG_NUMERO,
    #                                        ORG.code_postal AS ORG_CP,
    #                                        ORG.localite AS ORG_LOCALITE,
    #                                        ORG.telephone AS ORG_TEL,
    #                                        ORG.gsm AS ORG_MOBILE,
    #                                        ORG.mail AS ORG_MAIL,
    #                                        ORG.type_list AS ORG_TYPE
    #                                 FROM p_permis AS PERMIS
    #                                 LEFT JOIN get_demandeurs AS DEMANDEURS ON DEMANDEURS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN get_parcelles AS PARCELS ON PARCELS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN c_localite AS LOCALITE ON PERMIS.localite_fk = LOCALITE.id
    #                                 LEFT JOIN c_nature AS NATURE ON PERMIS.nature_fk = NATURE.id
    #                                 LEFT JOIN p_permis_demande_notaire AS LN ON LN.id = PERMIS.id
    #                                 LEFT JOIN c_organisme AS ORG ON LN.organisme_fk = ORG.id
    #                                 LEFT JOIN p_autorisation_notaire AS AUTORISATION ON LN.autorisation_notaire_fk = AUTORISATION.id
    #                                 LEFT JOIN get_document_infos AS PERMIS_DOCUMENTS ON PERMIS_DOCUMENTS.ID_PERMIS = PERMIS.id
    #                                 WHERE PERMIS.type_permis_fk = 8 AND LN.notaire_type_dossier_fk = 1;
    #                               """
    #                               )

    import_urbaweb.db.create_view("declaration_vue",
                                  """
                                    SELECT PERMIS.id,
                                           PERMIS.type_permis_fk,
                                           PERMIS.numero_permis AS REFERENCE_TECH,
                                           PERMIS.numero_permis_delivre AS REFERENCE,
                                           PERMIS.reference_urbanisme AS REFERENCE_URB,
                                           PERMIS.statut_permis AS STATUT,
                                           PERMIS.parcelle_hors_commune AS PHC,
                                           PERMIS.info_rue_f AS LOCALITE_RUE,
                                           PERMIS.numero AS LOCALITE_NUM,
                                           LOCALITE.code_postal AS LOCALITE_CP,
                                           LOCALITE.libelle_f AS LOCALITE_LABEL,
                                           PERMIS.date_demande AS DATE_DEMANDE,
                                           PERMIS.date_recepisse AS DATE_RECEPISSE,
                                           PERMIS.date_depot AS DATE_DEPOT,
                                           RECEVABILITE.date_autorisation_college AS RECEVABILITE_DATE_AUTORISATION_COLLEGE,
                                           RECEVABILITE.date_irrecevable AS RECEVABILITE_DATE_IRRECEVABLE,
                                           TRAVAUX.date_debut AS DEBUT_TRAVAUX,
                                           TRAVAUX.date_fin AS FIN_TRAVAUX,
                                           NATURE.libelle_f AS NATURE_TITRE,
                                           PERMIS.libnat AS NATURE_DETAILS,
                                           PERMIS.remarque_resume AS REMARQUES,
                                           DEMANDEURS.CONCAT_DEMANDEUR  AS INFOS_DEMANDEURS,
                                           IF(PARCELS.CONCAT_PARCELS = '1|.|0000/00#000', '', PARCELS.CONCAT_PARCELS) AS INFOS_PARCELLES,                                         
                                           PERMIS_DOCUMENTS.DOCUMENTS AS INFOS_DOCUMENTS
                                    FROM p_permis AS PERMIS
                                    LEFT JOIN get_demandeurs AS DEMANDEURS ON DEMANDEURS.ID_PERMIS = PERMIS.id
                                    LEFT JOIN get_parcelles AS PARCELS ON PARCELS.ID_PERMIS = PERMIS.id
                                    LEFT JOIN c_localite AS LOCALITE ON PERMIS.localite_fk = LOCALITE.id
                                    LEFT JOIN c_nature AS NATURE ON PERMIS.nature_fk = NATURE.id
                                    LEFT JOIN p_permis_declaration_urbanistique AS DECL ON DECL.id = PERMIS.id
                                    LEFT JOIN p_recevabilite AS RECEVABILITE ON DECL.recevabilite_fk = RECEVABILITE.id
                                    LEFT JOIN get_document_infos AS PERMIS_DOCUMENTS ON PERMIS_DOCUMENTS.ID_PERMIS = PERMIS.id
                                    LEFT JOIN p_travaux AS TRAVAUX ON TRAVAUX.id = DECL.travaux_fk
                                    WHERE PERMIS.type_permis_fk = 9;
                                  """
                                  )

    # import_urbaweb.db.create_view("avis_prealable_vue",
    #                               """
    #                                 SELECT PERMIS.id,
    #                                        PERMIS.type_permis_fk,
    #                                        PERMIS.numero_permis AS REFERENCE_TECH,
    #                                        PERMIS.numero_permis_delivre AS REFERENCE,
    #                                        PERMIS.reference_urbanisme AS REFERENCE_URB,
    #                                        PERMIS.statut_permis AS STATUT,
    #
    #                                        PERMIS.parcelle_hors_commune AS PHC,
    #                                        PERMIS.info_rue_f AS LOCALITE_RUE,
    #                                        PERMIS.numero AS LOCALITE_NUM,
    #                                        LOCALITE.code_postal AS LOCALITE_CP,
    #                                        LOCALITE.libelle_f AS LOCALITE_LABEL,
    #                                        PERMIS.date_demande AS DATE_DEMANDE,
    #                                        PERMIS.date_recepisse AS DATE_RECEPISSE,
    #                                        PERMIS.date_depot AS DATE_DEPOT,
    #                                        NATURE.libelle_f AS NATURE_TITRE,
    #                                        PERMIS.libnat AS NATURE_DETAILS,
    #                                        PERMIS.remarque_resume AS REMARQUES,
    #                                        DEMANDEURS.CONCAT_DEMANDEUR  AS INFOS_DEMANDEURS,
    #                                        IF(PARCELS.CONCAT_PARCELS = '1|.|0000/00#000', '', PARCELS.CONCAT_PARCELS) AS INFOS_PARCELLES,
    #                                        PERMIS_DOCUMENTS.DOCUMENTS AS INFOS_DOCUMENTS,
    #                                        ORG.civilite_fk AS ORG_TITLE_ID,
    #                                        ORG.nom AS ORG_NOM,
    #                                        ORG.prenom AS ORG_PRENOM,
    #                                        ORG.rue AS ORG_RUE,
    #                                        ORG.numero AS ORG_NUMERO,
    #                                        ORG.code_postal AS ORG_CP,
    #                                        ORG.localite AS ORG_LOCALITE,
    #                                        ORG.telephone AS ORG_TEL,
    #                                        ORG.gsm AS ORG_MOBILE,
    #                                        ORG.mail AS ORG_MAIL,
    #                                        ORG.type_list AS ORG_TYPE
    #                                 FROM p_permis AS PERMIS
    #                                 LEFT JOIN get_demandeurs AS DEMANDEURS ON DEMANDEURS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN get_parcelles AS PARCELS ON PARCELS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN c_localite AS LOCALITE ON PERMIS.localite_fk = LOCALITE.id
    #                                 LEFT JOIN c_nature AS NATURE ON PERMIS.nature_fk = NATURE.id
    #                                 LEFT JOIN p_permis_avis_prealable AS AVIS ON AVIS.id = PERMIS.id
    #                                 LEFT JOIN c_organisme AS ORG ON AVIS.organisme_fk = ORG.id
    #                                 LEFT JOIN get_document_infos AS PERMIS_DOCUMENTS ON PERMIS_DOCUMENTS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN p_directive AS DIRECTIVE ON PERMIS.directive_fk = DIRECTIVE.id
    #                                 WHERE PERMIS.type_permis_fk = 5;
    #                               """
    #                               )
    # import_urbaweb.db.create_view("certificat_urbanisme1_vue",
    #                               """
    #                                 SELECT PERMIS.id,
    #                                        PERMIS.type_permis_fk,
    #                                        PERMIS.numero_permis AS REFERENCE_TECH,
    #                                        PERMIS.numero_permis_delivre AS REFERENCE,
    #                                        PERMIS.reference_urbanisme AS REFERENCE_URB,
    #                                        PERMIS.statut_permis AS STATUT,
    #                                        PERMIS.parcelle_hors_commune AS PHC,
    #                                        PERMIS.info_rue_f AS LOCALITE_RUE,
    #                                        PERMIS.numero AS LOCALITE_NUM,
    #                                        LOCALITE.code_postal AS LOCALITE_CP,
    #                                        LOCALITE.libelle_f AS LOCALITE_LABEL,
    #                                        PERMIS.date_demande AS DATE_DEMANDE,
    #                                        PERMIS.date_recepisse AS DATE_RECEPISSE,
    #                                        PERMIS.date_depot AS DATE_DEPOT,
    #                                        NATURE.libelle_f AS NATURE_TITRE,
    #                                        PERMIS.libnat AS NATURE_DETAILS,
    #                                        PERMIS.remarque_resume AS REMARQUES,
    #                                        DEMANDEURS.CONCAT_DEMANDEUR  AS INFOS_DEMANDEURS,
    #                                        IF(PARCELS.CONCAT_PARCELS = '1|.|0000/00#000', '', PARCELS.CONCAT_PARCELS) AS INFOS_PARCELLES,
    #                                        AUTORISATION_CU.date_autorisation_college AS AUTORISATION_DATE_AUTORISATION_COLLEGE,
    #                                        AUTORISATION_CU.date_refus_college AS AUTORISATION_DATE_REFUS_COLLEGE,
    #                                        PERMIS_DOCUMENTS.DOCUMENTS AS INFOS_DOCUMENTS,
    #                                        ORG.civilite_fk AS ORG_TITLE_ID,
    #                                        ORG.nom AS ORG_NOM,
    #                                        ORG.prenom AS ORG_PRENOM,
    #                                        ORG.rue AS ORG_RUE,
    #                                        ORG.numero AS ORG_NUMERO,
    #                                        ORG.code_postal AS ORG_CP,
    #                                        ORG.localite AS ORG_LOCALITE,
    #                                        ORG.telephone AS ORG_TEL,
    #                                        ORG.gsm AS ORG_MOBILE,
    #                                        ORG.mail AS ORG_MAIL,
    #                                        ORG.type_list AS ORG_TYPE
    #                                 FROM p_permis AS PERMIS
    #                                 LEFT JOIN get_demandeurs AS DEMANDEURS ON DEMANDEURS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN get_parcelles AS PARCELS ON PARCELS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN c_localite AS LOCALITE ON PERMIS.localite_fk = LOCALITE.id
    #                                 LEFT JOIN c_nature AS NATURE ON PERMIS.nature_fk = NATURE.id
    #                                 LEFT JOIN p_permis_certificat_urbanisme1 AS CU1 ON CU1.id = PERMIS.id
    #                                 LEFT JOIN p_autorisation_cu AS AUTORISATION_CU ON AUTORISATION_CU.id = CU1.autorisation_cu_fk
    #                                 LEFT JOIN c_organisme AS ORG ON CU1.organisme_fk = ORG.id
    #                                 LEFT JOIN get_document_infos AS PERMIS_DOCUMENTS ON PERMIS_DOCUMENTS.ID_PERMIS = PERMIS.id
    #                                 WHERE PERMIS.type_permis_fk = 3;
    #                               """
    #                               )
    # import_urbaweb.db.create_view("certificat_urbanisme2_vue",
    #                               """
    #                                 SELECT PERMIS.id,
    #                                        PERMIS.type_permis_fk,
    #                                        PERMIS.numero_permis AS REFERENCE_TECH,
    #                                        PERMIS.numero_permis_delivre AS REFERENCE,
    #                                        PERMIS.reference_urbanisme AS REFERENCE_URB,
    #                                        PERMIS.statut_permis AS STATUT,
    #                                        PERMIS.parcelle_hors_commune AS PHC,
    #                                        PERMIS.info_rue_f AS LOCALITE_RUE,
    #                                        PERMIS.numero AS LOCALITE_NUM,
    #                                        LOCALITE.code_postal AS LOCALITE_CP,
    #                                        LOCALITE.libelle_f AS LOCALITE_LABEL,
    #                                        PERMIS.date_demande AS DATE_DEMANDE,
    #                                        PERMIS.date_recepisse AS DATE_RECEPISSE,
    #                                        PERMIS.date_depot AS DATE_DEPOT,
    #                                        NATURE.libelle_f AS NATURE_TITRE,
    #                                        PERMIS.libnat AS NATURE_DETAILS,
    #                                        PERMIS.remarque_resume AS REMARQUES,
    #                                        DEMANDEURS.CONCAT_DEMANDEUR  AS INFOS_DEMANDEURS,
    #                                        IF(PARCELS.CONCAT_PARCELS = '1|.|0000/00#000', '', PARCELS.CONCAT_PARCELS) AS INFOS_PARCELLES,
    #                                        AUTORISATION_CU.date_autorisation_college AS AUTORISATION_DATE_AUTORISATION_COLLEGE,
    #                                        AUTORISATION_CU.date_refus_college AS AUTORISATION_DATE_REFUS_COLLEGE,
    #                                        PERMIS_DOCUMENTS.DOCUMENTS AS INFOS_DOCUMENTS,
    #                                        ORG.civilite_fk AS ORG_TITLE_ID,
    #                                        ORG.nom AS ORG_NOM,
    #                                        ORG.prenom AS ORG_PRENOM,
    #                                        ORG.rue AS ORG_RUE,
    #                                        ORG.numero AS ORG_NUMERO,
    #                                        ORG.code_postal AS ORG_CP,
    #                                        ORG.localite AS ORG_LOCALITE,
    #                                        ORG.telephone AS ORG_TEL,
    #                                        ORG.gsm AS ORG_MOBILE,
    #                                        ORG.mail AS ORG_MAIL,
    #                                        ORG.type_list AS ORG_TYPE
    #                                 FROM p_permis AS PERMIS
    #                                 LEFT JOIN get_demandeurs AS DEMANDEURS ON DEMANDEURS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN get_parcelles AS PARCELS ON PARCELS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN c_localite AS LOCALITE ON PERMIS.localite_fk = LOCALITE.id
    #                                 LEFT JOIN c_nature AS NATURE ON PERMIS.nature_fk = NATURE.id
    #                                 LEFT JOIN p_permis_certificat_urbanisme2 AS CU2 ON CU2.id = PERMIS.id
    #                                 LEFT JOIN p_autorisation_cu AS AUTORISATION_CU ON AUTORISATION_CU.id = CU2.autorisation_cu_fk
    #                                 LEFT JOIN c_organisme AS ORG ON CU2.organisme_fk = ORG.id
    #                                 LEFT JOIN get_document_infos AS PERMIS_DOCUMENTS ON PERMIS_DOCUMENTS.ID_PERMIS = PERMIS.id
    #                                 WHERE PERMIS.type_permis_fk = 4;
    #                               """
    #                               )

    # import_urbaweb.db.create_view("pic_vue",
    #                               """
    #                                 SELECT PERMIS.id,
    #                                        PERMIS.type_permis_fk,
    #                                        PERMIS.numero_permis AS REFERENCE_TECH,
    #                                        PERMIS.numero_permis_delivre AS REFERENCE,
    #                                        PERMIS.reference_urbanisme AS REFERENCE_URB,
    #                                        PERMIS.statut_permis AS STATUT,
    #
    #                                        PERMIS.parcelle_hors_commune AS PHC,
    #                                        PERMIS.info_rue_f AS LOCALITE_RUE,
    #                                        PERMIS.numero AS LOCALITE_NUM,
    #                                        LOCALITE.code_postal AS LOCALITE_CP,
    #                                        LOCALITE.libelle_f AS LOCALITE_LABEL,
    #                                        PERMIS.date_demande AS DATE_DEMANDE,
    #                                        PERMIS.date_recepisse AS DATE_RECEPISSE,
    #                                        PERMIS.date_depot AS DATE_DEPOT,
    #                                        NATURE.libelle_f AS NATURE_TITRE,
    #                                        PERMIS.libnat AS NATURE_DETAILS,
    #                                        PERMIS.remarque_resume AS REMARQUES,
    #                                        DEMANDEURS.CONCAT_DEMANDEUR  AS INFOS_DEMANDEURS,
    #                                        IF(PARCELS.CONCAT_PARCELS = '1|.|0000/00#000', '', PARCELS.CONCAT_PARCELS) AS INFOS_PARCELLES,
    #                                        PERMIS_DOCUMENTS.DOCUMENTS AS INFOS_DOCUMENTS,
    #                                        ORG.civilite_fk AS ORG_TITLE_ID,
    #                                        ORG.nom AS ORG_NOM,
    #                                        ORG.prenom AS ORG_PRENOM,
    #                                        ORG.rue AS ORG_RUE,
    #                                        ORG.numero AS ORG_NUMERO,
    #                                        ORG.code_postal AS ORG_CP,
    #                                        ORG.localite AS ORG_LOCALITE,
    #                                        ORG.telephone AS ORG_TEL,
    #                                        ORG.gsm AS ORG_MOBILE,
    #                                        ORG.mail AS ORG_MAIL,
    #                                        ORG.type_list AS ORG_TYPE
    #                                 FROM p_permis AS PERMIS
    #                                 LEFT JOIN get_demandeurs AS DEMANDEURS ON DEMANDEURS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN get_parcelles AS PARCELS ON PARCELS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN c_localite AS LOCALITE ON PERMIS.localite_fk = LOCALITE.id
    #                                 LEFT JOIN c_nature AS NATURE ON PERMIS.nature_fk = NATURE.id
    #                                 LEFT JOIN p_permis_implantation_commerciale AS PIC ON PIC.id = PERMIS.id
    #                                 LEFT JOIN c_organisme AS ORG ON PIC.organisme_fk = ORG.id
    #                                 LEFT JOIN get_document_infos AS PERMIS_DOCUMENTS ON PERMIS_DOCUMENTS.ID_PERMIS = PERMIS.id
    #                                 WHERE PERMIS.type_permis_fk = 21;
    #                               """
    #                               )

    # import_urbaweb.db.create_view("permis_urbanisme_codt_vue",
    #                               """
    #                                 SELECT PERMIS.id,
    #                                        PERMIS.type_permis_fk,
    #                                        PERMIS.numero_permis AS REFERENCE_TECH,
    #                                        PERMIS.numero_permis_delivre AS REFERENCE,
    #                                        PERMIS.reference_urbanisme AS REFERENCE_URB,
    #                                        PERMIS.statut_permis AS STATUT,
    #                                        PERMIS.parcelle_hors_commune AS PHC,
    #                                        PERMIS.info_rue_f AS LOCALITE_RUE,
    #                                        PERMIS.numero AS LOCALITE_NUM,
    #                                        LOCALITE.code_postal AS LOCALITE_CP,
    #                                        LOCALITE.libelle_f AS LOCALITE_LABEL,
    #                                        PERMIS.date_demande AS DATE_DEMANDE,
    #                                        PERMIS.date_recepisse AS DATE_RECEPISSE,
    #                                        PERMIS.date_depot AS DATE_DEPOT,
    #                                        NATURE.libelle_f AS NATURE_TITRE,
    #                                        PERMIS.libnat AS NATURE_DETAILS,
    #                                        PERMIS.remarque_resume AS REMARQUES,
    #                                        DEMANDEURS.CONCAT_DEMANDEUR  AS INFOS_DEMANDEURS,
    #                                        IF(PARCELS.CONCAT_PARCELS = '1|.|0000/00#000', '', PARCELS.CONCAT_PARCELS) AS INFOS_PARCELLES,
    #                                        PERMIS.date_permis_annule_abandon AS DATE_PERMIS_ABANDON,
    #                                        AUTORISATION.date_decision_college AS DATE_DECISION_COLLEGE,
    #                                        AUTORISATION.decision_college_ AS DECISION_COLLEGE,
    #                                        PERMIS_DOCUMENTS.DOCUMENTS AS INFOS_DOCUMENTS,
    #                                        ORG.civilite_fk AS ORG_TITLE_ID,
    #                                        ORG.nom AS ORG_NOM,
    #                                        ORG.prenom AS ORG_PRENOM,
    #                                        ORG.rue AS ORG_RUE,
    #                                        ORG.numero AS ORG_NUMERO,
    #                                        ORG.code_postal AS ORG_CP,
    #                                        ORG.localite AS ORG_LOCALITE,
    #                                        ORG.telephone AS ORG_TEL,
    #                                        ORG.gsm AS ORG_MOBILE,
    #                                        ORG.mail AS ORG_MAIL,
    #                                        ORG.type_list AS ORG_TYPE,
    #                                        DIRECTIVE.fonctionnaire_delegue AS DIRECTIVE_FD,
    #                                        DIRECTIVE.autorite_competente AS DIRECTIVE_AUTORITE_COMPETENTE
    #                                 FROM p_permis AS PERMIS
    #                                 LEFT JOIN get_demandeurs AS DEMANDEURS ON DEMANDEURS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN get_parcelles AS PARCELS ON PARCELS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN c_localite AS LOCALITE ON PERMIS.localite_fk = LOCALITE.id
    #                                 LEFT JOIN c_nature AS NATURE ON PERMIS.nature_fk = NATURE.id
    #                                 LEFT JOIN p_permis_urbanisme_codt AS PUCODT ON PUCODT.id = PERMIS.id
    #                                 LEFT JOIN c_organisme AS ORG ON PUCODT.organisme_fk = ORG.id
    #                                 LEFT JOIN p_autorisation_codt AS AUTORISATION ON PUCODT.autorisation_codt_fk = AUTORISATION.id
    #                                 LEFT JOIN get_document_infos AS PERMIS_DOCUMENTS ON PERMIS_DOCUMENTS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN p_directive AS DIRECTIVE ON PERMIS.directive_fk = DIRECTIVE.id
    #                                 WHERE PERMIS.type_permis_fk = 23 AND DIRECTIVE.autorite_competente NOT IN ('1', '2');
    #                               """
    #                               )
    # import_urbaweb.db.create_view("permis_urbanisation_codt_vue",
    #                               """
    #                                        SELECT PERMIS.id,
    #                                        PERMIS.type_permis_fk,
    #                                        PERMIS.numero_permis AS REFERENCE_TECH,
    #                                        PERMIS.numero_permis_delivre AS REFERENCE,
    #                                        PERMIS.reference_urbanisme AS REFERENCE_URB,
    #                                        PERMIS.statut_permis AS STATUT,
    #
    #                                        PERMIS.parcelle_hors_commune AS PHC,
    #                                        PERMIS.info_rue_f AS LOCALITE_RUE,
    #                                        PERMIS.numero AS LOCALITE_NUM,
    #                                        LOCALITE.code_postal AS LOCALITE_CP,
    #                                        LOCALITE.libelle_f AS LOCALITE_LABEL,
    #                                        PERMIS.date_demande AS DATE_DEMANDE,
    #                                        PERMIS.date_recepisse AS DATE_RECEPISSE,
    #                                        PERMIS.date_depot AS DATE_DEPOT,
    #                                        NATURE.libelle_f AS NATURE_TITRE,
    #                                        PERMIS.libnat AS NATURE_DETAILS,
    #                                        PERMIS.remarque_resume AS REMARQUES,
    #                                        DEMANDEURS.CONCAT_DEMANDEUR  AS INFOS_DEMANDEURS,
    # #                                        IF(PARCELS.CONCAT_PARCELS = '1|.|0000/00#000', '', PARCELS.CONCAT_PARCELS) AS INFOS_PARCELLES,
    #                                         TRAVAUX.date_debut AS DEBUT_TRAVAUX,
    #                                         TRAVAUX.date_fin AS FIN_TRAVAUX,
    #                                        PERMIS_DOCUMENTS.DOCUMENTS AS INFOS_DOCUMENTS,
    #                                        ORG.civilite_fk AS ORG_TITLE_ID,
    #                                        ORG.nom AS ORG_NOM,
    #                                        ORG.prenom AS ORG_PRENOM,
    #                                        ORG.rue AS ORG_RUE,
    #                                        ORG.numero AS ORG_NUMERO,
    #                                        ORG.code_postal AS ORG_CP,
    #                                        ORG.localite AS ORG_LOCALITE,
    #                                        ORG.telephone AS ORG_TEL,
    #                                        ORG.gsm AS ORG_MOBILE,
    #                                        ORG.mail AS ORG_MAIL,
    #                                        ORG.type_list AS ORG_TYPE,
    #                                        PURBCODT.nom_lotissement AS NOM_LOT,
    #                                        PURBCODT.nombre_de_lots AS NB_LOT
    #                                 FROM p_permis AS PERMIS
    #                                 LEFT JOIN get_demandeurs AS DEMANDEURS ON DEMANDEURS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN get_parcelles AS PARCELS ON PARCELS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN c_localite AS LOCALITE ON PERMIS.localite_fk = LOCALITE.id
    #                                 LEFT JOIN c_nature AS NATURE ON PERMIS.nature_fk = NATURE.id
    #                                 LEFT JOIN p_permis_urbanisation_codt AS PURBCODT ON PURBCODT.id = PERMIS.id
    #                                 LEFT JOIN c_organisme AS ORG ON PURBCODT.organisme_fk = ORG.id
    #                                 LEFT JOIN get_document_infos AS PERMIS_DOCUMENTS ON PERMIS_DOCUMENTS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN p_travaux AS TRAVAUX ON TRAVAUX.id = PURBCODT.travaux_fk
    #                                 WHERE PERMIS.type_permis_fk = 25;
    #                               """
    #                               )

    # import_urbaweb.db.create_view("certificat_urbanisme2_codt_vue",
    #                               """
    #                                 SELECT PERMIS.id,
    #                                        PERMIS.type_permis_fk,
    #                                        PERMIS.numero_permis AS REFERENCE_TECH,
    #                                        PERMIS.numero_permis_delivre AS REFERENCE,
    #                                        PERMIS.reference_urbanisme AS REFERENCE_URB,
    #                                        PERMIS.statut_permis AS STATUT,
    #                                        PERMIS.date_statut AS DATE_STATUT,
    #                                        PERMIS.parcelle_hors_commune AS PHC,
    #                                        PERMIS.info_rue_f AS LOCALITE_RUE,
    #                                        PERMIS.numero AS LOCALITE_NUM,
    #                                        LOCALITE.code_postal AS LOCALITE_CP,
    #                                        LOCALITE.libelle_f AS LOCALITE_LABEL,
    #                                        PERMIS.date_demande AS DATE_DEMANDE,
    #                                        PERMIS.date_recepisse AS DATE_RECEPISSE,
    #                                        PERMIS.date_depot AS DATE_DEPOT,
    #                                        NATURE.libelle_f AS NATURE_TITRE,
    #                                        PERMIS.libnat AS NATURE_DETAILS,
    #                                        PERMIS.remarque_resume AS REMARQUES,
    #                                        DEMANDEURS.CONCAT_DEMANDEUR  AS INFOS_DEMANDEURS,
    #                                        IF(PARCELS.CONCAT_PARCELS = '1|.|0000/00#000', '', PARCELS.CONCAT_PARCELS) AS INFOS_PARCELLES,
    #                                          TRAVAUX.date_debut AS DEBUT_TRAVAUX,
    #                                          TRAVAUX.date_fin AS FIN_TRAVAUX,
    #                                        PERMIS_DOCUMENTS.DOCUMENTS AS INFOS_DOCUMENTS,
    #                                        ORG.civilite_fk AS ORG_TITLE_ID,
    #                                        ORG.nom AS ORG_NOM,
    #                                        ORG.prenom AS ORG_PRENOM,
    #                                        ORG.rue AS ORG_RUE,
    #                                        ORG.numero AS ORG_NUMERO,
    #                                        ORG.code_postal AS ORG_CP,
    #                                        ORG.localite AS ORG_LOCALITE,
    #                                        ORG.telephone AS ORG_TEL,
    #                                        ORG.gsm AS ORG_MOBILE,
    #                                        ORG.mail AS ORG_MAIL,
    #                                        ORG.type_list AS ORG_TYPE
    #                                 FROM p_permis AS PERMIS
    #                                 LEFT JOIN get_demandeurs AS DEMANDEURS ON DEMANDEURS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN get_parcelles AS PARCELS ON PARCELS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN c_localite AS LOCALITE ON PERMIS.localite_fk = LOCALITE.id
    #                                 LEFT JOIN c_nature AS NATURE ON PERMIS.nature_fk = NATURE.id
    #                                 LEFT JOIN p_permis_certificat_urbanisme2_codt AS CU2CODT ON CU2CODT.id = PERMIS.id
    #                                 LEFT JOIN c_organisme AS ORG ON CU2CODT.organisme_fk = ORG.id
    #                                 LEFT JOIN get_document_infos AS PERMIS_DOCUMENTS ON PERMIS_DOCUMENTS.ID_PERMIS = PERMIS.id
    #                                 LEFT JOIN p_travaux AS TRAVAUX ON TRAVAUX.id = CU2CODT.travaux_fk
    #                                 WHERE PERMIS.type_permis_fk = 24;
    #                               """
    #                               )


def create_concat_views(import_urbaweb):

    import_urbaweb.db.create_view("get_demandeurs",
                                  """
                                      SELECT
                                        `permis`.
                                        `id`
                                        AS
                                        `ID_PERMIS`,
                                        GROUP_CONCAT(REPLACE(CONCAT(
                                            `demandeur`.
                                        `civilite_fk`,
                                        '|',
                                        `demandeur`.
                                        `prenom`,
                                        '|',
                                        `demandeur`.
                                        `nom`,
                                        '|',
                                        `demandeur`.
                                        `numero`,
                                        '|',
                                        `demandeur`.
                                        `rue`,
                                        '|',
                                        `demandeur`.
                                        `localite`,
                                        '|',
                                        `demandeur`.
                                        `telephone`,
                                        '|',
                                        `demandeur`.
                                        `gsm`,
                                        '|',
                                        `demandeur`.
                                        `mail`,
                                        '|',
                                        `demandeur`.
                                        `code_postal`), '#', '')
                                        SEPARATOR
                                        '#') AS
                                        `CONCAT_DEMANDEUR`
                                    FROM
                                    (`p_permis` `permis`
                                    LEFT JOIN `p_demandeur` `demandeur` ON ((`demandeur`.`permis_fk` = `permis`.`id`)))
                                    GROUP
                                    BY
                                    `ID_PERMIS`;
                                  """
                                  )
    import_urbaweb.db.create_view("get_parcelles",
                                  """
                                    SELECT
                                        `permis`.`id` AS `ID_PERMIS`,
                                        GROUP_CONCAT( `parcels`.`division_fk`, '|', `parcels`.`section_cadastrale`, '|', `parcels`.`cadastre`
                                            SEPARATOR '@') AS `CONCAT_PARCELS`
                                    FROM
                                        (`p_permis` `permis`
                                        LEFT JOIN `p_parcelle` `parcels` ON ((`parcels`.`permis_fk` = `permis`.`id`)))
                                    GROUP BY `ID_PERMIS`;
                                  """
                                  )

    import_urbaweb.db.create_view("get_document_infos",
                                  """
                                    SELECT
                                        `permis`.`id` AS `ID_PERMIS`,
                                        GROUP_CONCAT( `infos`.`id_document`,'|', `infos`.`libelle`
                                            SEPARATOR '@') AS `DOCUMENTS`
                                    FROM
                                        (`p_permis` `permis`
                                        LEFT JOIN `p_document_info_permis` `infos` ON ((`infos`.`permis_fk` = `permis`.`id`)))
                                    GROUP BY `ID_PERMIS`;
                                  """
                                  )

    import_urbaweb.db.create_view("get_rubrics_unique",
                                  """
                                    SELECT
                                        `permis`.`id` AS `ID_PERMIS`,
                                        GROUP_CONCAT( `LABEL_RUBRIC`.`code`
                                            SEPARATOR '@') AS `CONCAT_RUBRICS_CODE`
                                    FROM
                                        (`p_permis` `permis`
                                        LEFT JOIN `j_permis_unique_environnement_arrete_rubrique` `JOIN_PUN_RUBRIC` ON ((`JOIN_PUN_RUBRIC`.`permis_id` = `permis`.`id`))
                                        LEFT JOIN `c_environnement_arrete_rubrique` `LABEL_RUBRIC` ON ((`JOIN_PUN_RUBRIC`.`environnement_arrete_rubrique_id` = `LABEL_RUBRIC`.`id`)))
                                    GROUP BY `ID_PERMIS`;
                                  """
                                  )

    import_urbaweb.db.create_view("get_rubrics_cl3",
                                  """
                                    SELECT
                                        `permis`.`id` AS `ID_PERMIS`,
                                        GROUP_CONCAT( `LABEL_RUBRIC`.`code`
                                            SEPARATOR '@') AS `CONCAT_RUBRICS_CODE`
                                    FROM
                                        (`p_permis` `permis`
                                        LEFT JOIN `j_permis_environnement_classe3_environnement_arrete_rubrique` `JOIN_PE3_RUBRIC` ON ((`JOIN_PE3_RUBRIC`.`permis_id` = `permis`.`id`))
                                        LEFT JOIN `c_environnement_arrete_rubrique` `LABEL_RUBRIC` ON ((`JOIN_PE3_RUBRIC`.`environnement_arrete_rubrique_id` = `LABEL_RUBRIC`.`id`)))
                                    GROUP BY `ID_PERMIS`;
                                  """
                                  )

    import_urbaweb.db.create_view("get_rubrics",
                                  """
                                    SELECT
                                        `permis`.`id` AS `ID_PERMIS`,
                                        GROUP_CONCAT( `LABEL_RUBRIC`.`code`
                                            SEPARATOR '@') AS `CONCAT_RUBRICS_CODE`
                                    FROM
                                        (`p_permis` `permis`
                                        LEFT JOIN `j_permis_environnement_environnement_arrete_rubrique` `JOIN_PE_RUBRIC` ON ((`JOIN_PE_RUBRIC`.`permis_id` = `permis`.`id`))
                                        LEFT JOIN `c_environnement_arrete_rubrique` `LABEL_RUBRIC` ON ((`JOIN_PE_RUBRIC`.`environnement_arrete_rubrique_id` = `LABEL_RUBRIC`.`id`)))
                                    GROUP BY `ID_PERMIS`;
                                  """
                                  )
