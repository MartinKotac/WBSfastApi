# -*- coding: utf-8 -*-
"""

Pipeline of NER model predicting and constructing rdf triples from medicine content.

@author: Martin Kotevski
"""

from Bio_Epidemiology_NER.bio_recognizer import ner_prediction
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, XSD


def make_predictions(corpus):
    return ner_prediction(corpus=corpus, compute='cpu')


ner_to_schema_org_property = {
    "Sex": "suggestedGender",
    "Age": "suggestedAge",
    "Disease_disorder": "diagnosis",
    "Medication": "drug",
    "Frequency": "frequency",
    "Severity": "adverseOutcome",
    "Sign_symptom": "signOrSymptom",
    "Clinical_event": "guideline",
    "Biological_structure": "relatedStructure",
    "Diagnostic_procedure": "availableService",
    "Lab_value": "availableTest",
    "Detailed_description": "availableService",
    "Nonbiological_location": "location",
    "Administration": "audience",
    "Therapeutic_procedure": "possibleTreatment",
    "Duration": "Duration",
    "Coreference": "additionalType",
    "History": "riskFactor",
}

ner_to_schema_org_type = {
    "Sex": "GenderType",
    "Age": "QuantitativeValue",
    "Disease_disorder": "MedicalCondition",
    "Medication": "Drug",
    "Sign_symptom": "MedicalSignOrSymptom",
    "Clinical_event": "MedicalGuideline",
    "Biological_structure": "AnatomicalStructure",
    "Diagnostic_procedure": "DiagnosticProcedure",
    "Frequency": "",
    "Severity": "MedicalEnumeration",
    "Lab_value": "MedicalTest",
    "Detailed_description": "MedicalProcedure",
    "Nonbiological_location": "Place",
    "Administration": "AdministrativeArea",
    "Therapeutic_procedure": "MedicalTherapy",
    "Duration": "Duration",
    "Coreference": "MedicalCondition",
    "History": "MedicalRiskFactor",
}


def create_rdf_triples(df):
    # Creating an empty graph
    g = Graph()
    ns_schema = Namespace("https://schema.org/")
    ns_example = Namespace("https://example.com/")
    for index, row in df.iterrows():
        entity_group = row['entity_group']
        value = row['value']
        if entity_group == 'Age':
            value = ''.join(filter(str.isdigit, value))
            entity_uri = URIRef(ns_example[value.replace(" ", "_")])
            g.add((entity_uri, RDF.type, ns_schema[ner_to_schema_org_type[entity_group]]))
            g.add((entity_uri, RDFS.label, Literal(entity_group + " NER")))
            g.add((entity_uri, ns_schema['value'], Literal(value, datatype=XSD.integer)))
        else:
            # Adding rdf type and rdf label
            entity_uri = URIRef(ns_example[value.replace(" ", "_")])
            g.add((entity_uri, RDF.type, ns_schema[ner_to_schema_org_type[entity_group]]))
            g.add((entity_uri, RDFS.label, Literal(entity_group + " NER")))

        # Defining relationships between the entities (Consultation)
        g.add((ns_schema['Patient'], ns_schema[ner_to_schema_org_property[entity_group]], entity_uri))

    return g.serialize(format='ntriples')


def pipelineRDF(text):
    df = make_predictions(text)
    rdf_triples = create_rdf_triples(df)
    return rdf_triples


if __name__ == '__main__':
    corpus = """A 48 year-old female presented with vaginal bleeding and abnormal Pap smears.
                 Upon diagnosis of invasive non-keratinizing SCC of the cervix, she underwent a radical hysterectomy
                 with salpingo-oophorectomy which demonstrated positive spread to the pelvic lymph nodes and the parametrium.
                 Pathological examination revealed that the tumour also extensively involved the lower uterine segment.
                 Patient presents with persistent cough, shortness of breath, and chest pain.
                 The physical examination revealed decreased breath sounds in the lower left lung.
                 The doctor ordered a chest X-ray and prescribed antibiotics.
                 The patient has a history of asthma and is currently taking albuterol."""
    rdf_graph = pipelineRDF(corpus)
    print(rdf_graph)
