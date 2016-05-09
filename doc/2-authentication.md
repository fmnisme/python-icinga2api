# <a id="basics"></a> Basics

## <a id="authentication"></a> Authentication

You can use the client with either username/password combination or using certificates.

Example using username and password:

    from icinga2api.client import Client
    client = Client('https://localhost:5665', 'username', 'password')

Example using certificates:

    from icinga2api.client import Client
    client = Client('https://icinga2:5665',
                    certificate='/etc/ssl/certs/myhostname.crt',
                    key='/etc/ssl/keys/myhostname.key')

If your public and private are in the same file, just use the `certificate` parameter.


## <a id="config-file"></a> Config file

You can also specify a config file (in ini format) containing all necessary information.

Example:

    client = Client('https://localhost:5665', config_file='/etc/icinga2api')

The config file looks like:

    [api]
    url = https://icinga2:5665
    certificate = /etc/ssl/certs/myhostname.crt
    key = /etc/ssl/private/myhostname.key
    ca_certificate = /etc/ssl/certs/ca.crt


## <a id="server-verification"></a> Server verification

To verify the server certificate specify a ca file as `ca_file` parameter.

Example:

    from icinga2api.client import Client
    client = Client('https://icinga2:5665',
                    certificate='/etc/ssl/certs/myhostname.crt',
                    key='/etc/ssl/keys/myhostname.key',
                    ca_file='/etc/ssl/certs/my_ca.crt')
