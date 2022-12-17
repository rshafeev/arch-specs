import yaml
from jinja2 import Environment


class ConfigurationLoader:

    @staticmethod
    def load(config_file_name: str) -> dict:
        env = Environment(extensions=["jinja2_getenv_extension.GetenvExtension"])
        with open(config_file_name) as f:
            template = env.from_string(f.read())
            config_s = template.render()
            return yaml.safe_load(config_s)
