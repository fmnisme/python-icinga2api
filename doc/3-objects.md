# <a id="objects"></a> Objects

## <a id="objects-get"></a> objects.get()

To get a single object (`Host`, `Service`, ...) use the funtion `objects.get()`.

  Parameter      | Type      | Description
  ---------------|-----------|------------
  object\_type   | string    | **Required.** The object type to get, e.g. `Host`, `Service`.
  name           | string    | **Required.** The objects name.
  attrs          | list      | **Optional.** Get only the specified objects attributes.
  joins          | bool      | **Optional.** Also get the joined object, e.g. for a `Service` the `Host` object.

Examples:

Get host `webserver01.domain`:

    client.objects.get('Host', 'webserver01.domain')

Get service `ping4` of host `webserver01.domain`:

    client.objects.get('Service', 'webserver01.domain!ping4')

Get host `webserver01.domain` but the attributes `address` and `state`:

    client.objects.get('Host', 'webserver01.domain', attrs=['address', 'state'])

Get service `ping4` of host `webserver01.domain` and the host attributes:

    client.objects.get('Service', 'webserver01.domain!ping4', joins=True)

## <a id="objects-list"></a> objects.list()

To get a list of objects (`Host`, `Service`, ...) use the funtion `objects.list()`. You can use `filter` to ...

  Parameter     | Type       | Description
  --------------|------------|--------------
  object\_type  | string     | **Required.** The object type to get, e.g. `Host`, `Service`.
  name          | string     | **Optional.** The objects name.
  attrs         | list       | **Optional.** Get only the specified objects attributes.
  filter        | string     | **Optional.** The filter expression, see [documentation](http://docs.icinga.org/icinga2/latest/doc/module/icinga2/chapter/icinga2-api#icinga2-api-filters).
  filter\_vars  | dictionary | **Optional.** Variables which are available to your filter expression.
  joins         | bool       | **Optional.** Also get the joined object, e.g. for a `Service` the `Host` object.

Examples:

Get all hosts:

    client.objects.list('Host')

Get all hosts but limit attributes to `address` and `state`

    client.objects.list('Host', attrs=['address', 'state'])

Get all hosts which have "webserver" in their host name

    client.objects.list('Host', filter='match("webserver\*", host.name)')

Get all services which names start with "vHost" and are assigned to hosts named "webserver\*" using `filter_vars`

    hostname_pattern = 'webserver\*'
    service_pattern = 'vHost\*'
    client.objects.list('Service',
                        filter='match(hpattern, host.name) && match(spattern, service.name)',
                        filter_vars={'hpattern': hostname_pattern, 'spattern': service_pattern})

Get all services and the joined host name:

    client.objects.list('Service', joins=['host.name'])


## <a id="objects-create"></a> objects.create()

Create an object using `templates` and specify attributes (`attrs`).

  Parameter     | Type       | Description
  --------------|------------|--------------
  object\_type  | string     | **Required.** The object type to get, e.g. `Host`, `Service`.
  name          | string     | **Optional.** The objects name.
  templates     | list       | **Optional.** A list of templates to import.
  attrs         | dictionary | **Optional.** The objects attributes.

Examples:

Create a host:

    client.objects.create(
        'Host',
        'localhost',
        ['generic-host'],
        {'address': '127.0.0.1'})

Create a service for Host "localhost":

    client.objects.create(
        'Service',
        'localhost!dummy',
        ['generic-service'],
        {'check_command': 'dummy'})


## <a id="objects-update"></a> objects.update()

Update an object with the specified attributes.

  Parameter     | Type       | Description
  --------------|------------|--------------
  object\_type  | string     | **Required.** The object type to get, e.g. `Host`, `Service`.
  name          | string     | **Optional.** The objects name.
  attrs         | dictionary | **Optional.** The objects attributes.

Examples:

Change the ip address of a host:

    client.objects.update(
        'Host',
        'localhost',
        {'address': '127.0.1.1'})

Update a service and change the check interval:

    client.objects.create('Service',
           'localhost!dummy',
           ['generic-service'],
           {'check_interval': '10m'})


## <a id="objects-delete"></a> objects.delete()

Update an object with the specified attributes.

  Parameter     | Type       | Description
  --------------|------------|--------------
  object\_type  | string     | **Required.** The object type to get, e.g. `Host`, `Service`.
  name          | string     | **Optional.** The objects name.
  filter        | string     | **Optional.** Filter expression for matching the objects.
  filter\_vars  | dictionary | **Optional.** Variables which are available to your filter expression.
  cascade       | boolean    | **Optional.** Also delete dependent objects. Defaults to `True`.

Examples:

Delete the "localhost":

    client.objects.delete('Host', 'localhost')

Delete all services matching `vhost\*`:

    client.objects.delete('Service', filter='match("vhost\*", service.name)')
