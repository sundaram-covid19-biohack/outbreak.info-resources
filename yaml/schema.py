import yaml
import os

class Schema:
    def __init__(self, id):
        self.context = {}
        self.graph = []
        self.id = id

    def add_to_context(self, name, url):
        self.context[name] = url

    def add_to_props(self, prop):
        self.graph.append(prop)

    def render(self, out):
        
        result = {}
        result["@context"] = self.context
        result["@id"] = self.id
        result["@graph"] = self.graph
        with open(out, 'w') as fout: 
            fout.write(yaml.dump(result))