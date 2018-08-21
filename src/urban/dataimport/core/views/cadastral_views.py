def create_views(import_object):

    import_object.cadastral.create_view("vieilles_parcelles_cadastrales_vue",
                                        """
                                            SELECT DISTINCT prca,
                                                    prcc,
                                                    prcb1 as prc,
                                                    DA.divname,
                                                    PAS.da as division,
                                                    section,
                                                    radical,
                                                    exposant,
                                                    bis,
                                                    puissance
                                            FROM pas AS PAS
                                            LEFT JOIN DA on DA.da = PAS.da;
                                        """,
                                        without_use=True
                                        )
    import_object.cadastral.create_view("parcelles_cadastrales_vue",
                                        """
                                            SELECT CAPA.da as division,
                                                    divname,
                                                    prc,
                                                    section,
                                                    radical,
                                                    exposant,
                                                    bis,
                                                    puissance,
                                                    pe as proprietary,
                                                    adr1 as proprietary_city,
                                                    adr2 as proprietary_street,
                                                    sl1 as location
                                            FROM map AS MAP
                                            LEFT JOIN capa AS CAPA
                                            ON MAP.capakey = CAPA.capakey
                                            LEFT JOIN da AS DA
                                            ON CAPA.da = DA.da;
                                        """,
                                        without_use=True
                                        )
