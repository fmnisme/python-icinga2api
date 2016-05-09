# <a id="Status"></a> Status

## <a id="status-list"></a> status.list()

Subscribe to an event stream.

  Parameter     | Type      | Description
  --------------|-----------|--------------
  component     | string    | **Optional.** List the status of the specified component only.

Examples:

List complete status:

    client.status.list()

List status of the core application:

    client.status.list('IcingaApplication')
