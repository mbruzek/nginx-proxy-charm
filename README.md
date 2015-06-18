# NGINX Proxy Charm

Nginx is a free open-source HTTP server and reverse proxy.  It can handle
multiple requests with low resource consumption. Proxying is used to
distribute load by passing requests along to multiple servers.

Consul-template is a service that connects to a Consul server that manages
the configuration files for other services based on the Service Discovery of
the Consul server.

# How to use the nginx-proxy charm


    juju deploy nginx-proxy
    juju deploy consul
    juju set consul bootstrap-expect: 1
    juju add-relation nginx-proxy:template consul:consul-api


# Charm Configuration

**service-name** is the name that consul-template builds the reverse proxy list
from.

### Reconfigure w/ auto forwarding from Consul

The charm has a `public-website` relationship, that implements a prototype
interface to setup automatic website proxy'ing based on data from Consul.

    juju deploy cs:~zoology/trusty/consul
    juju deploy cs:~zoology/trusty/dns
    juju set dns provider=rt53 provider_keys="AWS_ACESS_KEY_ID|XXX AWS_PRIVATE ACCESS_KEY|XXX"
    juju add-relation dns consul
    juju add-relation dns nginx-proxy



# Upstream Contact Information

- [Nginx community](http://wiki.nginx.org/Main)
- [Getting started with Nginx](http://wiki.nginx.org/GettingStarted)
- [Nginx documentation](http://nginx.org/en/docs/)
- [Nginx bug tracker](http://trac.nginx.org/nginx/)
