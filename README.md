## Feature

1. basic auth
2. objects(zone support)
3. actions
4. events
5. status

## Developing

1. cert auth
2. Configuration Management

## Requirements :

* Python >= 2.7
* Requests
* pip

To install the requirements :

```
pip install -r requirements.txt
```

To install the API :

```
python setup.py install
```

## Usage



```
from icinga2api.client import Client
client = Client('https://localhost:5665','username','password')
```

### list host

```
filters = {
    'attrs' : ['name', 'address'],
}
client.objects.list('hosts',filters=filters)
```

### create host
```
config = {
    'templates': [ 'generic-host' ],
    'attrs': {
        'address': '192.168.1.100',
        'vars.os': 'Windows',
        'vars.services.mysql': {'ports': [3306, 3307]},
        'zone' : 'Zone1',
    }
}
print client.objects.create('hosts','test1',config)
```


**read source commentary for more examples.**
