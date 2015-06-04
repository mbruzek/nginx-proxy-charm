#!/usr/bin/python

import json
import os

from charmhelpers.core import (hookenv, host)
from charmhelpers.fetch import archiveurl
from path import path

CONSUL_TEMPLATE_CONFIG = path('/etc/consul-template.json')
CONSUL_TEMPLATE_INIT = path('/etc/init/consul-template.conf')
CONSUL_TEMPLATE_SERVICE = 'consul-template'
DEFAULT_JSON = path(hookenv.charm_dir() + '/files/consul/consul-template.json')
MANAGED_CTMPL = path('/etc/nginx/nginx.ctmpl')
MANAGED_CONFIG = path('/etc/nginx/nginx.config')
MANAGED_SERVICE = 'nginx'
ORIGINAL_CTMPL = path(hookenv.charm_dir() + '/files/consul/nginx.ctmpl')
RELEASE_URL = 'https://github.com/hashicorp/consul-template/releases/download'
# The sha256sum of the consul-template releases.
SHA256SUMS = {
    'consul-template_0.9.0_linux_amd64.tar.gz':
        '3d8c9fcaee18a4369cc731528ce9d6a5be03d88b954a2fea0f4406fc54c70fc8',
    'consul-template_0.8.0_linux_amd64.tar.gz':
        '5a65c8df7ecfe2fbdedcac71743732a1c4e810987e294e7d733f2da39c2ebf17',
    'consul-template_0.7.0_linux_amd64.tar.gz':
        '7b8fb97caef72f9e67bbb9069042b8e01f7efed3acd2a32f560a8fe60146d874'
}
UPSTART_FILE = path(hookenv.charm_dir() + '/files/consul/consul-template.upstart')


def ensure_consul_template_running(reload=False):
    """
    Ensure consul-template is running, optionally reload the service.
    """
    if host.service_running('consul-template'):
        if reload:
            host.service_reload('consul-template', True)
    else:
        host.service_start('consul-template')


def start_managed_service(service_name):
    """
    Restart or start the service that consul-template manages the configuration for.
    """
    if host.service_running(service_name):
        host.service_restart(service_name)
    else:
        host.service_start(service_name)


def read_json_configuration(configuration_file):
    """
    Read the JSON file and return a data object.
    """
    if os.path.exists(configuration_file):
        print('Reading {0}'.format(configuration_file))
        with open(configuration_file) as stream:
            data = json.loads(stream.read())
    else:
        data = {}
    return data


def consul_template_config_changed(consul_server):
    """
    Return True when the consul-template configuration changed if the consul
    server address is different than the current configuration.
    """
    changed = True
    if CONSUL_TEMPLATE_CONFIG.isfile():
        current = read_json_configuration(CONSUL_TEMPLATE_CONFIG)
        # The consul server string is the only thing that can be different.
        if current['consul'] == consul_server:
            changed = False
    return changed


def configure_consul_template(consul_address, consul_port):
    """
    Configure the consul-template service, return True when config changed.
    See https://github.com/hashicorp/consul-template#options for more
    consul-template configuration options.
    """
    consul_server = '{0}:{1}'.format(consul_address, consul_port)

    # Read current configuration file to see if we need to configure anything.
    changed = consul_template_config_changed(consul_server)

    # Only continue when the consul server address has changed.
    if changed:
        data = read_json_configuration(DEFAULT_JSON)
        data['consul'] = consul_server
        # The template source is written in consul configuration language.
        data['template']['source'] = MANAGED_CTMPL
        data['template']['destination'] = MANAGED_CONFIG
        print('Writing file {0}'.format(CONSUL_TEMPLATE_CONFIG))
        with open(CONSUL_TEMPLATE_CONFIG, 'w') as stream:
            json.dump(data, stream)
    return changed


def consul_arch():
    """
    Generate the consul string based on platform values of this system.
    """
    import platform
    # Find the system type string and convert to lower case.
    system = platform.system().lower()
    # Consul builds are only available for 'darwin' and 'linux'
    if system in ['darwin', 'linux']:
        machine = platform.machine()
        # Consul builds are only available for 'amd64' and '386'
        if machine == 'x86_64':
            package_arch = 'amd64'
        elif machine == 'i386':
            package_arch = '386'
        else:
            raise Exception('Invalid machine type: {0}'.format(machine))
        if package_arch:
            architecture = '{0}_{1}'.format(system, package_arch)
            return architecture
    else:
        raise Exception('Invalid system type: {0}'.format(system))


def install_consul_template(version='0.9.0', destination_directory='/usr/local/bin'):
    """
    Install the desired version of consul-template for this architecture.
    """
    print('Installing consul-template version {0}'.format(version))
    architecture = consul_arch()
    name = 'consul-template_{0}_{1}.tar.gz'.format(version, architecture)
    # Find the sha256sum for the specific file name.
    sha256sum = SHA256SUMS[name]
    print('Expecting {0} for {1}'.format(sha256sum, name))
    # Build the full url with release/version/name
    url = '{0}/v{1}/{2}'.format(RELEASE_URL, version, name)
    print('Fetching {0}'.format(url))
    installer = archiveurl.ArchiveUrlFetchHandler()
    installer.install(url, dest=destination_directory, checksum=sha256sum,
                      hash_type='sha256')
    # The consul-template tar contains the binary in an extra directory.
    unpacked_directory = path(destination_directory +
        '/consul-template_{0}_{1}'.format(version, architecture))
    # Create a path object to the consul-template binary file.
    consul_template = path(unpacked_directory + '/consul-template')
    print('Copying {0} to {1}'.format(consul_template,
                                      destination_directory))
    consul_template.copy(destination_directory)
    # Remove the extra unpacked directory tree.
    unpacked_directory.rmtree_p()
    # Copy the upstart file to the init directory to survive restarts.
    UPSTART_FILE.copy(CONSUL_TEMPLATE_INIT)
