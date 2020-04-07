from schema import Schema
import os
import csv

schema = Schema("http://sulab.org/")

schema.add_to_context("schema", "http://schema.org")
schema.add_to_context("bioschemas", "http://bioschema.org")
schema.add_to_context("owl", "http://www.w3.org/2002/07/owl")

with open("c:/users/ben/desktop/schema.csv", "r") as fin:
    csv_reader = csv.reader(fin)

    cols = []
    for row in csv_reader:
        if len(cols) == 0:
            cols = row
        else:   
            prop = {}
            prop["@id"] = row[cols.index("Property")]
            prop["@type"] = "rdf:Property"
            prop["rdfs:subClassOf"] = {"@id" : row[cols.index("sameAs")].lower()}
            prop["rdfs:comment"] = row[cols.index("Description")]
            card_string = row[cols.index("cardinality")]
            if (card_string != "one"):
                card_string = "many"
            prop["owl:cardinality"] = card_string
            prop["marginality"] = row[cols.index("marginality")]
            prop["schema:rangeIncludes"] = {"@id" : row[cols.index("expected type")]}

            schema.add_to_props(prop)

schema.render('c:/users/ben/desktop/test.yaml')
