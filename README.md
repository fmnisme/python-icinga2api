#Feature
1. basic and certificate auth
1. config file support
1. objects (zone support)
1. actions
1. events
1. status

#Developing
1. Code cleanup
1. Configuration Management

#Usage
```
from icinga2api.client import Client
client = Client('https://localhost:5665', 'username', 'password')
```

```
from icinga2api.client import Client
client = Client('https://localhost:5665', certificate='/etc/ssl/certs/myhostname.crt', key='/etc/ssl/keys/myhostname.key')
```

```
client = Client('https://localhost:5665', config_file='/etc/icinga2api')
```

#list host
```
filters = {
    "attrs" : ["name", "address"],
}
client.objects.list('Host', filters=filters)
```

#create host
```
config = {
    "templates": [ "generic-host" ],
    "attrs": {
        "address": "192.168.1.100",
        'vars.os': 'Windows',
        'vars.services.mysql': {'ports': [3306, 3307]},
        'zone' : 'Zone1',
    }
}
print client.objects.create('Host', 'test1', config)
```


**read source commentary for more examples.**
