def create_bestaddress_views(import_object, locality):
    import_object.bestaddress.create_view("bestaddress_vue",
                                          """
                                            SELECT id, street, zip, entity, commune, key
                                            FROM public.addresses WHERE commune = '{0}';
                                          """.format(locality)
                                          )
    import_object.bestaddress.bestaddress_vue.set_index([
        'id',
        'key',
        'street',
    ])
