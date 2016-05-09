# <a id="Events"></a> Events

## <a id="events-subscribe"></a> events.subscribe()

Subscribe to an event stream.

  Parameter     | Type      | Description
  --------------|-----------|--------------
  types         | list      | **Required.** Event types to subscribe for.
  queue         | string    | **Required.** Unique queue name. A queue can be used by multiple clients.
  filters       | string    | **Optional.** Filter expression to match the events.

Example:

    types = ['CheckResult']
    queue = 'monitor'
    filters = 'event.check_result.exit_status==2'
    
    for event in client.events.subscribe(types, queue, filters):
        print(event)
