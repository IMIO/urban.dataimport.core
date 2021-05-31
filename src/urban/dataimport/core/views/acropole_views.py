def create_concat_views(import_acropole):
    # import_acropole.db.create_view("dossier_enquete",
    #                                """
    #                                 SELECT DOSSIER.WRKDOSSIER_ID,
    #                                        DOSSIER.DOSSIER_NUMERO,
    #                                        PARAM.PARAM_IDENT,
    #                                        PARAM.PARAM_VALUE,
    #                                        PARAM.PARAM_NOMFUSION,
    #                                        REMARQUE.REMARQ_LIB
    #                                 FROM
    #                                     wrkdossier AS DOSSIER
    #                                 INNER JOIN k2 AS MAIN_JOIN
    #                                 ON MAIN_JOIN.K_ID1 = DOSSIER.WRKDOSSIER_ID
    #                                 INNER JOIN wrkparam AS PARAM
    #                                 ON MAIN_JOIN.K_ID2 = PARAM.WRKPARAM_ID
    #                                 LEFT JOIN cremarq AS REMARQUE
    #                                 ON PARAM.PARAM_VALUE = REMARQUE.CREMARQ_ID
    #                                 WHERE PARAM.PARAM_IDENT in ('EnqDatDeb', 'EnqDatFin', 'EnqObjet')
    #                                """
    #                                )
    import_acropole.db.create_view("get_demandeurs",
                                  """
                                    SELECT
                                      DOSSIER.WRKDOSSIER_ID,
                                      GROUP_CONCAT(CONCAT_WS("",PERSONNE.CPSN_NOM, '|',
                                                                PERSONNE.CPSN_PRENOM, '|', 
                                                                ADRESSE_PERSONNE.CLOC_ADRESSE, '|',
                                                                ADRESSE_PERSONNE.CLOC_ZIP, '|', 
                                                                ADRESSE_PERSONNE.CLOC_LOCALITE, '|', 
                                                                PERSONNE.CPSN_TYPE, '|', 
                                                                PERSONNE.CPSN_TEL1, '|', 
                                                                PERSONNE.CPSN_FAX, '|', 
                                                                PERSONNE.CPSN_GSM, '|', 
                                                                PERSONNE.CPSN_EMAIL) SEPARATOR '#') AS `CONCAT_DEMANDEURS`
                                    FROM
                                      wrkdossier AS DOSSIER
                                      INNER JOIN k2 AS MAIN_JOIN ON MAIN_JOIN.K_ID2 = DOSSIER.WRKDOSSIER_ID
                                      LEFT JOIN cpsn AS PERSONNE ON MAIN_JOIN.K_ID1 = PERSONNE.CPSN_ID
                                      INNER JOIN k2 AS MAIN_JOIN_BIS ON MAIN_JOIN_BIS.K_ID2 = PERSONNE.CPSN_ID
                                      LEFT JOIN cloc AS ADRESSE_PERSONNE ON MAIN_JOIN_BIS.K_ID1 = ADRESSE_PERSONNE.CLOC_ID
                                      WHERE PERSONNE.CPSN_NOM NOT LIKE '%architec%' AND CPSN_ID != 1073255
                                    GROUP BY
                                      DOSSIER.WRKDOSSIER_ID;
                                  """
                                  )
    import_acropole.db.create_view("get_parcelles",
                                  """
                                        SELECT DOSSIER.WRKDOSSIER_ID, GROUP_CONCAT(CADASTRE.CAD_NOM SEPARATOR '@') AS `CONCAT_PARCELS`
                                        FROM
                                            wrkdossier AS DOSSIER
                                        INNER JOIN urbcadastre AS CADASTRE ON CADASTRE.CAD_DOSSIER_ID = DOSSIER.WRKDOSSIER_ID
                                        GROUP BY DOSSIER.WRKDOSSIER_ID;
                                  """
                                  )
    import_acropole.db.create_view("get_adresses",
                                  """
                                        SELECT DOSSIER.WRKDOSSIER_ID, GROUP_CONCAT(CONCAT_WS("",ADR.ADR_ADRESSE, '|',
                                                                                                ADR.ADR_NUM, '|',
                                                                                                ADR.ADR_ZIP, '|',
                                                                                                ADR.ADR_LOCALITE)
                                                                                    SEPARATOR '@') AS `CONCAT_ADRESSES`
                                        FROM
                                            wrkdossier AS DOSSIER
                                        INNER JOIN k2adr AS MAIN_JOIN
                                        ON MAIN_JOIN.K_ID1 = DOSSIER.WRKDOSSIER_ID
                                        INNER JOIN adr AS ADR
                                        ON MAIN_JOIN.K_ID2 = ADR.ADR_ID
                                        GROUP BY DOSSIER.WRKDOSSIER_ID;
                                  """
                                  )
    import_acropole.db.create_view("get_remarques",
                                  """
                                     SELECT DOSSIER.WRKDOSSIER_ID, GROUP_CONCAT(REMARQUE.REMARQ_LIB SEPARATOR '|') AS `CONCAT_REMARQUES`
                                     FROM
                                         wrkdossier AS DOSSIER
                                     LEFT JOIN k2 AS MAIN_JOIN
                                     ON MAIN_JOIN.K_ID1 = DOSSIER.WRKDOSSIER_ID
                                     INNER JOIN cremarq AS REMARQUE
                                     ON MAIN_JOIN.K_ID2 = REMARQUE.CREMARQ_ID
                                     GROUP BY DOSSIER.WRKDOSSIER_ID;
                                  """
                                  )


    # import_acropole.db.create_view("dossier_evenement_vue",
    #                                """
    #                                 SELECT DOSSIER.WRKDOSSIER_ID,
    #                                        DOSSIER.DOSSIER_NUMERO,
    #                                        DOSSIER_DATEDELIV,
    #                                        DOSSIER_OCTROI,
    #                                        DOSSIER_TDOSSIERID,
    #                                        WRKETAPE_ID,
    #                                        ETAPE_NOMFR,
    #                                        ETAPE_TETAPEID,
    #                                        CONVERT(ETAPE_DATEDEPART,CHAR CHARACTER SET utf8) AS ETAPE_DATEDEPART,
    #                                        MAIN_JOIN.K2KND_ID
    #                                 FROM
    #                                     wrkdossier AS DOSSIER
    #                                 INNER JOIN k2 AS MAIN_JOIN
    #                                 ON MAIN_JOIN.K_ID1 = DOSSIER.WRKDOSSIER_ID
    #                                 INNER JOIN wrketape AS ETAPE
    #                                 ON MAIN_JOIN.K_ID2 = ETAPE.WRKETAPE_ID
    #                                 WHERE K2KND_ID = -207;
    #                                """
    #                                )
    # import_acropole.db.create_view("dossier_param_vue",
    #                                """
    #                                     SELECT DOSSIER.WRKDOSSIER_ID, DOSSIER.DOSSIER_NUMERO,
    #                                            WRKPARAM_ID,
    #                                            PARAM_TPARAMID,
    #                                            PARAM_NOMFUSION,
    #                                            PARAM_VALUE,
    #                                            MAIN_JOIN.K2KND_ID
    #                                     FROM
    #                                         wrkdossier AS DOSSIER
    #                                     INNER JOIN k2 AS MAIN_JOIN
    #                                     ON MAIN_JOIN.K_ID1 = DOSSIER.WRKDOSSIER_ID
    #                                     INNER JOIN wrkparam AS PARAM
    #                                     ON MAIN_JOIN.K_ID2 = PARAM.WRKPARAM_ID;
    #                                """
    #                                )
    import_acropole.db.create_view("get_details",
                                   """
                                        SELECT DOSSIER.WRKDOSSIER_ID,
                                               INFOS.OBJET_KEY AS DETAILS
                                        FROM
                                            wrkdossier AS DOSSIER
                                        INNER JOIN finddoss_index AS INFOS
                                        ON INFOS.ID = DOSSIER.WRKDOSSIER_ID;
                                   """
                                   )


def create_views(import_acropole):
    # inspection licence ids removed
    import_acropole.db.create_view("dossiers_vue",
                                  """
                                    SELECT
                                      DOSSIER.WRKDOSSIER_ID,
                                      DOSSIER_NUMERO,
                                      DOSSIER_OBJETFR,
                                      DOSSIER_TDOSSIERID,
                                      DATE(DOSSIER_DATEDEPART) AS DOSSIER_DATEDEPART,
                                      DATE(DOSSIER_DATEDEPOT) AS DOSSIER_DATEDEPOT,
                                      DOSSIER_OCTROI,
                                      DATE(DOSSIER_DATEDELIV) AS DOSSIER_DATEDELIV,
                                      DOSSIER_TYPEIDENT,
                                      DOSSIER_REFCOM,
                                      DETAILS,
                                      CONCAT_PARCELS,
                                      CONCAT_DEMANDEURS,
                                      CONCAT_ADRESSES,
                                      CONCAT_REMARQUES
                                    FROM
                                      wrkdossier AS DOSSIER
                                      LEFT JOIN get_details AS DETAILS ON DETAILS.WRKDOSSIER_ID = DOSSIER.WRKDOSSIER_ID
                                      LEFT JOIN get_parcelles AS PARCELLES ON PARCELLES.WRKDOSSIER_ID = DOSSIER.WRKDOSSIER_ID
                                      LEFT JOIN get_demandeurs AS APPLICANT ON APPLICANT.WRKDOSSIER_ID = DOSSIER.WRKDOSSIER_ID
                                      LEFT JOIN get_adresses AS WORKLOCATIONS ON WORKLOCATIONS.WRKDOSSIER_ID = DOSSIER.WRKDOSSIER_ID
                                      LEFT JOIN get_remarques AS REMARQUES ON REMARQUES.WRKDOSSIER_ID = DOSSIER.WRKDOSSIER_ID
                                      WHERE DOSSIER_TDOSSIERID NOT IN (-104442, -36624, -31266, -13467);
                                  """
                                  )
    import_acropole.db.create_view("BuildLicence_vue",
                                  """
                                    SELECT
                                      DOSSIER.WRKDOSSIER_ID,
                                      DOSSIER_NUMERO,
                                      DOSSIER_OBJETFR,
                                      DOSSIER_TDOSSIERID,
                                      DATE(DOSSIER_DATEDEPART) AS DOSSIER_DATEDEPART,
                                      DATE(DOSSIER_DATEDEPOT) AS DOSSIER_DATEDEPOT,
                                      DOSSIER_OCTROI,
                                      DATE(DOSSIER_DATEDELIV) AS DOSSIER_DATEDELIV,
                                      DOSSIER_TYPEIDENT,
                                      DOSSIER_REFCOM,
                                      DETAILS,
                                      CONCAT_PARCELS,
                                      CONCAT_DEMANDEURS,
                                      CONCAT_ADRESSES
                                    FROM
                                      wrkdossier AS DOSSIER
                                      LEFT JOIN get_details AS DETAILS ON DETAILS.WRKDOSSIER_ID = DOSSIER.WRKDOSSIER_ID
                                      LEFT JOIN get_parcelles AS PARCELLES ON PARCELLES.WRKDOSSIER_ID = DOSSIER.WRKDOSSIER_ID
                                      LEFT JOIN get_demandeurs AS APPLICANT ON APPLICANT.WRKDOSSIER_ID = DOSSIER.WRKDOSSIER_ID
                                      LEFT JOIN get_adresses AS WORKLOCATIONS ON WORKLOCATIONS.WRKDOSSIER_ID = DOSSIER.WRKDOSSIER_ID
                                      WHERE DOSSIER_TDOSSIERID IN (-42575, -32669, -17277, -11889, -1014, 466601, 516507);
                                  """
                                  )