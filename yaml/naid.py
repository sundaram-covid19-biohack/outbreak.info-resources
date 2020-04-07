
import yaml

with open('yaml/naid.yaml', 'r') as fin:
    data = yaml.load(fin, Loader=yaml.FullLoader)

print(data) 