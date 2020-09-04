"""
Be careful with modification : it can affect all import profile!
"""

main_licence_decision_mapping = {
    # '': '0',
    'OctroiCollege': 'favorable',
    'RefusCollege': 'defavorable',
    'OctroiTutelle': 'favorable',
    'RefusTutelle': 'defavorable',
    'OctroiFD': 'favorable',
    'RefusFD': 'defavorable',
    'Recevable': 'favorable',
    'Irrecevable': 'defavorable',
    'Irrecevable_2xI': 'defavorable',
    'AbandonDemandeur': '',
    'RefusTaciteFonctionnaire': 'defavorable',
    'Abandon': '',
    # '': '13',
    # '': '14',
    # '': '15',
    # '': '16',
}

main_licence_deposit_event_id_mapping = {
    'BuildLicence': 'depot-de-la-demande',
    'ParcelOutLicence': 'depot-de-la-demande',
    'UrbanCertificateOne': 'depot-de-la-demande',
    'UrbanCertificateTwo': 'depot-de-la-demande',
    'PreliminaryNotice': 'depot-de-la-demande',
    'EnvClassOne': 'depot-de-la-demande',
    'NotaryLetter': 'depot-de-la-demande',
    'Declaration': 'depot-de-la-demande',
    'UniqueLicence': 'depot-de-la-demande',
    'EnvClassThree': 'depot-de-la-demande',
    'IntegratedLicence': 'depot-de-la-demande',
    'MiscDemand': 'depot-de-la-demande',
    'CODT_CommercialLicence': 'depot-de-la-demande',
    'CODT_BuildLicence': 'depot-de-la-demande-codt',
    'CODT_UrbanCertificateTwo': 'depot-de-la-demande-codt',
    'CODT_ParcelOutLicence': 'depot-de-la-demande-codt',
    'ProjectMeeting': 'demande-de-reunion-de-projet',
    'Division': 'depot-de-la-demande',
    'Article127': 'depot-de-la-demande',
    'EnvClassTwo': 'depot-de-la-demande',
}

main_licence_not_receivable_event_id_mapping = {
    'BuildLicence': 'dossier-irrecevable',
    'ParcelOutLicence': 'dossier-incomplet-irrecevable',
    'UrbanCertificateOne': '',
    'UrbanCertificateTwo': '',
    'PreliminaryNotice': '',
    'EnvClassOne': 'dossier-irrecevable',
    'NotaryLetter': '',
    'Declaration': '',
    'UniqueLicence': 'dossier-irrecevable',
    'EnvClassThree': 'copy_of_passage-college',
    'MiscDemand': '',
    'IntegratedLicence': '',
    'CODT_CommercialLicence': 'dossier-incomplet-irrecevable-codt',
    'CODT_BuildLicence': 'dossier-incomplet-irrecevable-codt',
    'CODT_UrbanCertificateTwo': 'dossier-incomplet-irrecevable-codt',
    'CODT_ParcelOutLicence': 'dossier-incomplet-irrecevable-codt',
    'ProjectMeeting': '',
    'Division': '',
    'Article127': 'dossier-irrecevable',
    'EnvClassTwo': 'copy_of_dossier-irrecevable',
}

main_licence_decision_event_id_mapping = {
    'BuildLicence': 'delivrance-du-permis-octroi-ou-refus',
    'ParcelOutLicence': 'delivrance-du-permis-octroi-ou-refus',
    'UrbanCertificateOne': 'octroi-cu1',
    'UrbanCertificateTwo': 'octroi-cu2',
    'PreliminaryNotice': '',
    'EnvClassOne': 'decision',
    'NotaryLetter': 'octroi-lettre-notaire',
    'Declaration': 'deliberation-college',
    'UniqueLicence': 'delivrance-du-permis-octroi-ou-refus',
    'EnvClassThree': 'passage-college',
    'MiscDemand': 'deliberation-college',
    'IntegratedLicence': 'deliberation-college',
    'CODT_CommercialLicence': 'decision',
    'CODT_BuildLicence': 'delivrance-du-permis-octroi-ou-refus-codt',
    'CODT_UrbanCertificateTwo': 'delivrance-du-permis-octroi-ou-refus-codt',
    'CODT_ParcelOutLicence': 'copy_of_depot-de-la-demande-codt',
    'ProjectMeeting': 'avis-college',
    'Division': 'decision-octroi-refus',
    'Article127': 'delivrance-du-permis-octroi-ou-refus',
    'EnvClassTwo': 'decision',
}


main_portal_type_workflow_mapping = {
    'BuildLicence': 'urban_licence_workflow',
    'ParcelOutLicence': 'urban_licence_workflow',
    'UrbanCertificateOne': 'urban_licence_workflow',
    'UrbanCertificateTwo': 'urban_licence_workflow',
    'PreliminaryNotice': 'urban_licence_workflow',
    'EnvClassOne': 'urban_licence_workflow',
    'NotaryLetter': 'urban_licence_workflow',
    'Declaration': 'urban_licence_workflow',
    'UniqueLicence': 'urban_licence_workflow',
    'EnvClassThree': 'urban_licence_workflow',
    'MiscDemand': 'urban_licence_workflow',
    'IntegratedLicence': 'urban_licence_workflow',
    'CODT_CommercialLicence': 'codt_buildlicence_workflow',
    'CODT_BuildLicence': 'codt_buildlicence_workflow',
    'CODT_UrbanCertificateTwo': 'codt_buildlicence_workflow',
    'CODT_ParcelOutLicence': 'codt_buildlicence_workflow',
    'ProjectMeeting': 'urban_licence_workflow',
    'Division': 'urbandivision_workflow',
    'Article127': 'urban_licence_workflow',
    'EnvClassTwo': 'urban_licence_workflow',
}

