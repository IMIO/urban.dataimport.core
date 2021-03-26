def create_bestaddress_views(import_object, locality):
    import_object.bestaddress.create_view("bestaddress_vue",
                                          """
                                            SELECT id, street, zip, entity, commune, key
                                            FROM public.addresses WHERE commune = '{0}' AND key not in (7051795, 7051797, 7051798, 7051799, 7051808, 7032638, 7032647, 7032651, 7032813, 7035794, 7019026, 7019026, 7051800, 7051801, 7018960, 7032476, 7049974, 7032566, 7051791, 7018995, 7018974, 7051806, 7051812);
                                          """.format(locality)
                                          )
    import_object.bestaddress.bestaddress_vue.set_index([
        'id',
        'key',
        'street',
    ])
