# <a id="Events"></a> Events

## <a id="events-subscribe"></a> events.subscribe()

Subscribe to an event stream.

  Parameter     | Type      | Description
  --------------|-----------|--------------
  types         | list      | **Required.** Event types to subscribe for.
  queue         | string    | **Required.** Unique queue name. A queue can be used by multiple clients.
  filters       | string    | **Optional.** Filter expression to match the events.
  filter\_vars  | dictionary | **Optional.** Variables which are available to your filter expression.

Example:

    types = ['CheckResult']
    queue = 'monitor'
    filter = 'event.check_result.exit_status==2'
    
    for event in client.events.subscribe(types, queue, filter):
        print(event)
