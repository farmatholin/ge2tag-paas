import logging
import os

log = logging.getLogger(__name__)


class NginxConfig(object):
    def __init__(self, template_path, site):
        self.template_path = template_path
        self.template = self.load_template()
        self.nginx_sites_path = '/etc/nginx/sites-enabled/'
        self.site = site

    def load_template(self):
        with open(self.template_path) as tmplt:
            return tmplt.read()

    def create_config(self, user, container, port):
        container_name = "{}-{}".format(container.container_id, user.user_id)
        config = self.template \
            .replace("%user_container%", container_name) \
            .replace("%site%", self.site) \
            .replace("%port%", str(port))
        conf_file = os.path.join(container.path, "nginx.conf")
        with open(conf_file, "w+") as compose:
            compose.write(config)
        os.symlink(conf_file, os.path.join(self.nginx_sites_path, container_name))
        log.info('instance path: {}.{}'.format(container_name, self.site))

    def remove(self, user, container_id):
        container_name = "{}-{}".format(container_id, user.user_id)
        os.remove(os.path.join(self.nginx_sites_path, container_name))
