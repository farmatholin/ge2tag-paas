import os


class ComposeConfig(object):
    def __init__(self, template_path, image_container):
        self.template_path = template_path
        self.template = self.load_template()
        self.image_container = image_container

    def load_template(self):
        with open(self.template_path) as tmplt:
            return tmplt.read()

    def create_config(self, user, port, container):
        config = self.template \
            .replace("%container_id%", str(container.container_id)) \
            .replace("%user_id%", str(user.user_id)) \
            .replace("%port%", str(port)) \
            .replace("%image_container%", self.image_container) \
            .replace("%plugins_path%", container.plugins_path) \
            .replace("%logs_path%", container.logs_path) \
            .replace("%db_path%", container.db_path) \
            .replace("%cpu_shares%", str(container.cpu_shares)) \
            .replace("%cpu_quota%", str(container.cpu_quota)) \
            .replace("%mem_limit%", str(container.mem_limit))
        with open(os.path.join(container.path, "docker-compose.yml"), "w+") as compose:
            compose.write(config)
