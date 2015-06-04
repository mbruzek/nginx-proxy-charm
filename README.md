# Overview

Nginx is a free open-source HTTP server and reverse proxy.  It can handle
multiple requests with low resource consumption. Proxying is used to
distribute load by passing requests along to multiple servers.

Consul-template is a service that connects to a Consul server that manages
the configuration files for other services based on the Service Discovery of
the Consul server.

# Usage

Step by step instructions on deploying this charm:

    juju deploy nginx-proxy
    juju deploy consul
    juju set consul bootstrap-expect: 1
    juju add-relation nginx-proxy:template consul:consul-api


# Configuration

**service-name** is the name that consul-template builds the reverse proxy list
from.

# Contact Information

Though this will be listed in the charm store itself don't assume a user will know that, so include that information here:


- [Nginx community](http://wiki.nginx.org/Main)
- [Getting started with Nginx](http://wiki.nginx.org/GettingStarted)
- [Nginx documentation](http://nginx.org/en/docs/)
- [Nginx bug tracker](http://trac.nginx.org/nginx/)
