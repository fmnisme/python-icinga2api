#Feature
1. basic auth
2. objects (list,create,update,delete) 
3. actions
4. events

#Developing
1. cert auth

#Usage
```
from icinga2api.client import Client
client = Client('https://localhost:5665/v1','username','passowrd')

#list
filter = {
    "attrs" : ["name", "address"],
}
client.objects.list('hosts',filter=filter)

```

**read source commentary for more examples.**
