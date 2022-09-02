import io
import yaml


class Configuration:
    def __init__(self):
        # Read our configuration file
        with io.open('config.yaml') as stream:
            self.yaml_file = yaml.safe_load(stream)

    def get_endpoint(self):
        return self.yaml_file['endpoint']

    def get_paths(self):
        return self.yaml_file['paths']

