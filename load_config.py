import yaml

def load_config(yml_file):
	with open(yml_file) as yamlwriter:
		return yaml.load(yamlwriter)
