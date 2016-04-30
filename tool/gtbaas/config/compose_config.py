import yaml


class ComposeConfig(object):

    def __init__(self, template_path):
        self.template_path = template_path
        self.template = self.load_template()

    def load_template(self):
        with open(self.template_path) as tmplt:
            return tmplt.read()

    def create_config(self, user):
        pass
