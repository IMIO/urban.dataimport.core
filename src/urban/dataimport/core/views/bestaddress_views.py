def create_bestaddress_views(import_object):
    import_object.bestaddress.create_view("bestaddress_vue",
                                          """
                                            SELECT id, street, entity, commune
                                            FROM public.addresses WHERE commune = 'Fontaine-l''Evêque';
                                          """
                                          )
    import_object.bestaddress.bestaddress_vue.set_index([
        'id',
        'street',
    ])
