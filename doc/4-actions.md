# <a id="actions"></a> Actions

## <a id="actions-process-check-result"></a> actions.process\_check\_result()

Process a check result for a host or a service.

  Parameter         | Type       | Description
  ------------------|------------|--------------
  object\_type      | string     | **Required.** The object type to process the check result for, `Host` or `Service`.
  name              | string     | **Required.** The object`s name.
  exit\_status      | int        | **Required.** For services: 0=OK, 1=WARNING, 2=CRITICAL, 3=UNKNOWN, for hosts: 0=OK, 1=CRITICAL.
  plugin\_output    | string     | **Required.** The plugins main output.
  performance\_data | list       | **Optional.** The plugins performance data.
  check\_command    | list       | **Optional.** The first entry should be the check commands path, then one entry for each command line option followed by an entry for each of its argument.
  check\_source     | string     | **Optional.** Usually the name of the `command\_endpoint`.

Example:

    client.actions.process_check_result(
        'Service',
        'localhost!ping4',
        'exit_status': 2,
        'plugin_output': 'PING CRITICAL - Packet loss = 100%',
        'performance_data': [
            'rta=5000.000000ms;3000.000000;5000.000000;0.000000',
            'pl=100%;80;100;0'],
        'check_source': 'icinga')


## <a id="actions-reschedule-check"></a> actions.reschedule\_check()

Reschedule a check.

  Parameter        | Type       | Description
  -----------------|------------|--------------
  object\_type     | string     | **Required.** The object type to process the check result for, `Host` or `Service`.
  filters          | string     | **Required.** Filter expression to match the objects.
  filter\_vars     | dictionary | **Optional.** Variables which are available to your filter expression.
  next\_check      | string     | **Optional.** Timestamp to run the check.
  force\_check     | bool       | **Optional.** Force execution, e.g. ignore period restrictions.

Example:

    client.actions.reschedule_check(
        'Host',
        'host.name=="localhost"',
        '1577833200')


## <a id="actions-send-custom-notification"></a> actions.send\_custom\_notification()

Send a custom notification.

  Parameter        | Type       | Description
  -----------------|------------|--------------
  object\_type     | string     | **Required.** The object type to process the check result for, `Host` or `Service`.
  filters          | string     | **Required.** Filter expression to match the objects.
  filter\_vars     | dictionary | **Optional.** Variables which are available to your filter expression.
  author           | string     | **Required.** Name of the author.
  comment          | string     | **Required.** Comment text.
  force            | bool       | **Optional.** Force execution, e.g. ignore downtimes. Default: False.

Example:

    client.actions.send_custom_notification(
        'Host',
        'host.name==localhost',
        'icingaadmin',
        'test comment')


## <a id="actions-delay-notification"></a> actions.delay\_notification()

Delay a notification.

  Parameter        | Type       | Description
  -----------------|------------|--------------
  object\_type     | string     | **Required.** The object type to process the check result for, `Host` or `Service`.
  filters          | string     | **Required.** Filter expression to match the objects.
  filter\_vars     | dictionary | **Optional.** Variables which are available to your filter expression.
  timestamp        | int        | **Required.** Timestamp to delay the notification to.

Example:

    client.actions.delay_notification(
        'Host',
        'host.name==localhost',
        '1446389894')


## <a id="actions-acknowledge-problem"></a> actions.acknowledge\_problem()

Acknowledge a problem.

  Parameter        | Type       | Description
  -----------------|------------|--------------
  object\_type     | string     | **Required.** The object type to process the check result for, `Host` or `Service`.
  filters          | string     | **Required.** Filter expression to match the objects.
  filter\_vars     | dictionary | **Optional.** Variables which are available to your filter expression.
  author           | string     | **Required.** Name of the author.
  comment          | string     | **Required.** Comment text.
  expiry           | int        | **Optional.** If set the acknowledgement will vanish after this timestamp.
  sticky           | bool       | **Optional.** If `true`, the default, the acknowledgement will remain until the service or host fully recovers.
  notify           | bool       | **Optional.** If `true` a notification will be sent out to contacts to indicate this problem has been acknowledged. The default is false.

Example:

    client.actions.acknowledge_problem(
        'Host',
        'host.name==localhost',
        'icingaadmin',
        'host is in maintenance')
        1446389894)


## <a id="actions-remove-acknowledgement"></a> actions.remove\_acknowledgement()

Remove the acknowledgement for services or hosts.

  Parameter        | Type       | Description
  -----------------|------------|--------------
  object\_type     | string     | **Required.** The object type to process the check result for, `Host` or `Service`.
  filters          | string     | **Required.** Filter expression to match the objects.
  filter\_vars     | dictionary | **Optional.** Variables which are available to your filter expression.

Example:

    client.actions.acknowledge_problem(
        'Service',
        'service.state==2')


## <a id="actions-add-comment"></a> actions.add\_comment()

Add a comment from an author for services or hosts.

  Parameter        | Type       | Description
  -----------------|------------|--------------
  object\_type     | string     | **Required.** The object type to process the check result for, `Host` or `Service`.
  filters          | string     | **Required.** Filter expression to match the objects.
  filter\_vars     | dictionary | **Optional.** Variables which are available to your filter expression.
  author           | string     | **Required.** Name of the author.
  comment          | string     | **Required.** Comment text.

Example:

    client.actions.acknowledge_problem(
        'Service',
        'service.name=="ping4"',
        'icingaadmin',
        'Incident ticket #12345 opened.')


## <a id="actions-remove-comment"></a> actions.remove\_comment()

Remove a comment using its name or a filter.

  Parameter        | Type       | Description
  -----------------|------------|--------------
  object\_type     | string     | **Required.** The object type to process the check result for.
  name             | string     | **Optional.** Name of the object.
  filters          | string     | **Optional.** Filter expression to match the objects.
  filter\_vars     | dictionary | **Optional.** Variables which are available to your filter expression.

Examples:

    client.actions.remove_comment(
        'Comment',
        'localhost!localhost-1458202056-25')

    client.actions.remove_comment(
        'Service',
        filters='service.name=="ping4"')


## <a id="actions-schedule-downtime"></a> actions.schedule\_downtime()

Schedule a downtime for services or hosts.

  Parameter        | Type       | Description
  -----------------|------------|--------------
  object\_type     | string     | **Required.** The object type to process the check result for, `Host` or `Service`.
  filters          | string     | **Required.** Filter expression to match the objects.
  filter\_vars     | dictionary | **Optional.** Variables which are available to your filter expression.
  author           | string     | **Required.** Name of the author.
  comment          | string     | **Required.** Comment text.
  start\_time      | int        | **Required.** Timestamp makring the beginning of the downtime.
  end\_time        | int        | **Required.** Timestamp makring the end of the downtime.
  duration         | int        | **Required.** Duration of the downtime in seconds.
  fixed            | bool       | **Optional.** Schedule fixed or flexible downtime.
  trigger\_name    | bool       | **Optional.** Schedule fixed or flexible downtime.

Example:

    client.actions.schedule_downtime(
        'Host',
        r'match("*", host.name)',
        'icingaadmin',
        'IPv4 network maintenance',
        1446388806,
        1446389806,
        1000)


## <a id="actions-remove-downtime"></a> actions.remove\_downtime()

Remove a downtime using its name or a filter.

  Parameter        | Type       | Description
  -----------------|------------|--------------
  object\_type     | string     | **Required.** The object type to process the check result for.
  name             | string     | **Optional.** Name of the object.
  filters          | string     | **Optional.** Filter expression to match the objects.
  filter\_vars     | dictionary | **Optional.** Variables which are available to your filter expression.

Examples:

    client.actions.remove_downtime(
        'Downtime',
        'localhost!ping4!localhost-1458202056-25')

    client.actions.remove_downtime(
        'Service',
        filters='service.name=="ping4"')


## <a id="actions-shutdown-process"></a> actions.shutdown\_process()

Shuts down Icinga 2.

Example:

    client.actions.shutdown_process()


## <a id="actions-restart-process"></a> actions.restart\_process()

Restarts Icinga 2.

Example:

    client.actions.restart_process()

