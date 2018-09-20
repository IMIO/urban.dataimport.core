def create_views(import_acropole):
    import_acropole.db.create_view("dossier_enquete",
                                   """
                                    SELECT DOSSIER.WRKDOSSIER_ID,
                                           DOSSIER.DOSSIER_NUMERO,
                                           PARAM.PARAM_IDENT,
                                           PARAM.PARAM_VALUE,
                                            PARAM.PARAM_NOMFUSION,
                                           REMARQUE.REMARQ_LIB
                                    FROM
                                        wrkdossier AS DOSSIER
                                    INNER JOIN k2 AS MAIN_JOIN
                                    ON MAIN_JOIN.K_ID1 = DOSSIER.WRKDOSSIER_ID
                                    INNER JOIN wrkparam AS PARAM
                                    ON MAIN_JOIN.K_ID2 = PARAM.WRKPARAM_ID
                                    LEFT JOIN cremarq AS REMARQUE
                                    ON PARAM.PARAM_VALUE = REMARQUE.CREMARQ_ID
                                    WHERE PARAM.PARAM_IDENT in ('EnqDatDeb', 'EnqDatFin', 'EnqObjet')
                                   """
                                   )
    import_acropole.db.create_view("dossier_personne_vue",
                                   """
                                        SELECT DOSSIER.WRKDOSSIER_ID, DOSSIER.DOSSIER_NUMERO,
                                               PERSONNE.CPSN_NOM,
                                               PERSONNE.CPSN_PRENOM,
                                               PERSONNE.CPSN_TYPE,
                                               PERSONNE.CPSN_TEL1,
                                               PERSONNE.CPSN_TEL2,
                                               PERSONNE.CPSN_FAX,
                                               PERSONNE.CPSN_GSM,
                                               PERSONNE.CPSN_EMAIL,
                                               PERSONNE.CPSN_RN,
                                               PERSONNE.CPSN_TVA,
                                               PERSONNE.CPSN_ENABLED,
                                               PERSONNE.CPSN_BCE,
                                               ADRESSE_PERSONNE.CLOC_ID,
                                               ADRESSE_PERSONNE.CLOC_ADRESSE,
                                               ADRESSE_PERSONNE.CLOC_ZIP,
                                               ADRESSE_PERSONNE.CLOC_LOCALITE,
                                               ADRESSE_PERSONNE.CLOC_NOM,
                                               ADRESSE_PERSONNE.CLOC_TEL1,
                                               ADRESSE_PERSONNE.CLOC_TEL2,
                                               ADRESSE_PERSONNE.CLOC_FAX,
                                               ADRESSE_PERSONNE.CLOC_EMAIL,
                                               ADRESSE_PERSONNE.CLOC_GSM,
                                               ADRESSE_PERSONNE.CLOC_TVA,
                                               MAIN_JOIN.K2KND_ID
                                        FROM
                                            wrkdossier AS DOSSIER
                                        INNER JOIN k2 AS MAIN_JOIN
                                        ON MAIN_JOIN.K_ID2 = DOSSIER.WRKDOSSIER_ID
                                        INNER JOIN cpsn AS PERSONNE
                                        ON MAIN_JOIN.K_ID1 = PERSONNE.CPSN_ID
                                        INNER JOIN k2 AS MAIN_JOIN_BIS
                                        ON MAIN_JOIN_BIS.K_ID2 = PERSONNE.CPSN_ID
                                        INNER JOIN cloc AS ADRESSE_PERSONNE
                                        ON MAIN_JOIN_BIS.K_ID1 = ADRESSE_PERSONNE.CLOC_ID;
                                   """
                                   )
    import_acropole.db.create_view("dossier_parcelles_vue",
                                   """
                                        SELECT DOSSIER.WRKDOSSIER_ID, DOSSIER.DOSSIER_NUMERO,
                                               CADASTRE.CAD_NOM
                                        FROM
                                            wrkdossier AS DOSSIER
                                        INNER JOIN urbcadastre AS CADASTRE
                                        ON CADASTRE.CAD_DOSSIER_ID = DOSSIER.WRKDOSSIER_ID;
                                   """
                                   )
    import_acropole.db.create_view("dossier_adresse_vue",
                                   """
                                        SELECT DOSSIER.WRKDOSSIER_ID, DOSSIER.DOSSIER_NUMERO,
                                               ADR.ADR_ADRESSE,
                                               ADR.ADR_NUM,
                                               ADR.ADR_ZIP,
                                               ADR.ADR_LOCALITE
                                        FROM
                                            wrkdossier AS DOSSIER
                                        INNER JOIN k2adr AS MAIN_JOIN
                                        ON MAIN_JOIN.K_ID1 = DOSSIER.WRKDOSSIER_ID
                                        INNER JOIN adr AS ADR
                                        ON MAIN_JOIN.K_ID2 = ADR.ADR_ID;
                                """
                                   )
    import_acropole.db.create_view("dossier_evenement_vue",
                                   """
                                    SELECT DOSSIER.WRKDOSSIER_ID, DOSSIER.DOSSIER_NUMERO, DOSSIER_DATEDELIV,
                                           WRKETAPE_ID,
                                           ETAPE_NOMFR,
                                           ETAPE_TETAPEID,
                                           ETAPE_DATEDEPART,
                                           ETAPE_DATEBUTOIR,
                                           ETAPE_DELAI,
                                           MAIN_JOIN.K2KND_ID
                                    FROM
                                        wrkdossier AS DOSSIER
                                    INNER JOIN k2 AS MAIN_JOIN
                                    ON MAIN_JOIN.K_ID1 = DOSSIER.WRKDOSSIER_ID
                                    INNER JOIN wrketape AS ETAPE
                                    ON MAIN_JOIN.K_ID2 = ETAPE.WRKETAPE_ID;
                                   """
                                   )
    import_acropole.db.dossier_evenement_vue.set_index([
        'WRKDOSSIER_ID',
        'WRKETAPE_ID',
        'K2KND_ID',
        'ETAPE_TETAPEID'
        ])
    import_acropole.db.create_view("dossier_param_vue",
                                   """
                                        SELECT DOSSIER.WRKDOSSIER_ID, DOSSIER.DOSSIER_NUMERO,
                                               WRKPARAM_ID,
                                               PARAM_TPARAMID,
                                               PARAM_NOMFUSION,
                                               PARAM_VALUE,
                                               MAIN_JOIN.K2KND_ID
                                        FROM
                                            wrkdossier AS DOSSIER
                                        INNER JOIN k2 AS MAIN_JOIN
                                        ON MAIN_JOIN.K_ID1 = DOSSIER.WRKDOSSIER_ID
                                        INNER JOIN wrkparam AS PARAM
                                        ON MAIN_JOIN.K_ID2 = PARAM.WRKPARAM_ID;
                                   """
                                   )
