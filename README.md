#Feature
1. basic auth
2. objects (list,create,update,delete) 
3. actions
4. events
5. status

#Developing
1. cert auth
2. zone
3. Configuration Management

#Usage
```
from icinga2api.client import Client
client = Client('https://localhost:5665','username','passowrd')

#list
filters = {
    "attrs" : ["name", "address"],
}
client.objects.list('hosts',filters=filters)

```

**read source commentary for more examples.**
