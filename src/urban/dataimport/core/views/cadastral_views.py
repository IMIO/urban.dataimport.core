def create_cadastral_views(import_object):
    """
    """
    # import_object.cadastral.create_view("vieilles_parcelles_cadastrales_vue",
    #                                     """
    #                                         SELECT DISTINCT prca,
    #                                                 prcc,
    #                                                 prcb1 as prc,
    #                                                 DA.divname,
    #                                                 CAST(PAS.da AS TEXT) as division,
    #                                                 section,
    #                                                 CAST(radical AS TEXT) as radical,
    #                                                 exposant,
    #                                                 CAST(bis AS TEXT) bis,
    #                                                 CAST(puissance AS TEXT) puissance
    #                                         FROM pas AS PAS
    #                                         LEFT JOIN DA on DA.da = PAS.da;
    #                                     """
    #                                     )
    # import_object.cadastral.vieilles_parcelles_cadastrales_vue.set_index([
    #     'division',
    #     'section',
    #     'radical',
    #     'bis',
    #     'exposant',
    #     'puissance'
    # ])
    # import_object.cadastral.create_view("parcelles_cadastrales_vue",
    #                                     """
    #                                         SELECT  CAPA.da as division,
    #                                                 divname,
    #                                                 prc,
    #                                                 section,
    #                                                 radical,
    #                                                 exposant,
    #                                                 bis,
    #                                                 puissance,
    #                                                 pe as proprietary,
    #                                                 adr1 as proprietary_city,
    #                                                 adr2 as proprietary_street,
    #                                                 sl1 as location
    #                                         FROM map AS MAP
    #                                         LEFT JOIN capa AS CAPA
    #                                         ON MAP.capakey = CAPA.capakey
    #                                         LEFT JOIN da AS DA
    #                                         ON CAPA.da = DA.da;
    #                                     """
    #                                     )
    # import_object.cadastral.parcelles_cadastrales_vue.set_index([
    #     'division',
    #     'section',
    #     'radical',
    #     'bis',
    #     'exposant',
    #     'puissance'
    # ])
    import_object.cadastral.create_view("cadastre_parcelles_vue",
                                        """
                                        SELECT
                                            divcad AS division, section, primarynumber AS radical,
                                            bisnumber AS bis, exponentletter AS exposant, exponentnumber AS puissance
                                        FROM parcels;
                                        """
                                        )
    # import_object.cadastral.cadastre_parcelles_vue.set_index([
    #     'division',
    #     'section',
    #     'radical',
    #     'bis',
    #     'exposant',
    #     'puissance'
    # ])
    # import_object.cadastral.create_view("parcelles_vieilles_vue",
    #                                     """
    #                                         SELECT
    #                                             PARCELS1.urbainkey,
    #                                             PARCELS1.daa
    #                                         FROM map AS PARCELS1;
    #                                     """
    #                                     )
    # import_object.cadastral.parcelles_postgres_old_vue.set_index([
    #     'division',
    #     'section',
    #     'radical',
    #     'bis',
    #     'exposant',
    #     'puissance'
    # ])
