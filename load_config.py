import yaml

def load_config(yml_file, *parameters):
    with open(yml_file) as yamlwriter:
        config = yaml.load(yamlwriter)
    if parameters:
        return {parameter: config[parameter] for parameter in parameters} 

    return config
