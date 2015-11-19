#Feature
1. basic auth
2. objects (list,create,update,delete) 

#Developing
1. action
2. cert auth

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

More Info: ![Icinga 2 API](http://docs.icinga.org/icinga2/latest/doc/module/icinga2/toc#!/icinga2/latest/doc/module/icinga2/chapter/icinga2-api)
