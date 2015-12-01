#Feature
1. basic auth
2. objects(zone support)
3. actions
4. events
5. status

#Developing
1. cert auth
2. Configuration Management

#Usage
```
from icinga2api.client import Client
client = Client('https://localhost:5665','username','passowrd')

#list host
```
filters = {
    "attrs" : ["name", "address"],
}
client.objects.list('hosts',filters=filters)
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
print client.objects.create('hosts','test1',config)
```


**read source commentary for more examples.**
