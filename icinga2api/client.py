# -*- coding: utf-8 -*-
"""
icinga2 api client

write for icinga2 2.4
"""

from __future__ import print_function
import logging
import requests
import sys
if sys.version_info >= (3, 0):
    from urllib.parse import urljoin
else:
    from urlparse import urljoin

import icinga2api

LOG = logging.getLogger(__name__)


class Icinga2ApiException(Exception):
    """
    Icinga 2 API exception class
    """

    def __init__(self, error):
        self.error = error

    def __str__(self):
        return str(self.error)


class Client(object):
    """
    Icinga 2 Client class
    """

    def __init__(self,
                 api_endpoint,
                 username,
                 password,
                 certificate=None,
                 ca_certificate=None):
        """
        initialize object
        """

        self.api_endpoint = api_endpoint
        self.certificate = certificate
        self.ca_certificate = ca_certificate
        self.password = password
        self.username = username
        self.objects = Objects(self)
        self.actions = Actions(self)
        self.events = Events(self)
        self.status = Status(self)
        self.version = icinga2api.__version__


class Base(object):
    """
    Icinga 2 API Base class
    """

    root = None  # 继承

    def __init__(self, manager):
        """
        initialize object
        """

        self.manager = manager
        self.stream_cache = ""

    def _create_session(self, method='POST'):
        '''
        create a session object
        '''

        session = requests.Session()
        # prefer certificate authentification
        # TODO: make it configurable
        if self.manager.certificate and self.manager.key:
            # certificate and key are in different files
            session.cert = (self.manager.certificate, self.manager.key)
        elif self.manager.certificate:
            # certificate and key are in the same file
            session.cert = self.manager.certificate
        elif self.manager.username and self.manager.password:
            # use username and password
            session.auth = (self.manager.username, self.manager.password)
        session.headers = {
            'User-Agent': 'Python-icinga2api/{0}'.format(self.manager.version),
            'X-HTTP-Method-Override': method.upper(),
            'Accept': 'application/json'
        }

        return session

    def _request(self, method, url, payload=None):
        '''
        make the request and return the body

        :param method: the HTTP method
        :type method: string
        :param url: the requested URL
        :type url: string
        :param payload: the payload to send
        :type payload: dictionary
        :returns: the response as json
        :rtype: dictionary
        '''

        request_url = urljoin(self.manager.api_endpoint, url)
        LOG.debug("Request URL: {0}".format(request_url))

        # create session
        session = self._create_session(method)

        # create arguments for the request
        request_args = {
            'url': request_url
        }
        if payload:
            request_args['json'] = payload
        if self.manager.ca_certificate:
            request_args['verify'] = self.manager.ca_certificate
        else:
            request_args['verify'] = False

        # do the request
        response = session.post(**request_args)

        session.close()
        from pprint import pprint
        pprint(request_url)
        pprint(payload)
        pprint(response)

        if not (200 <= response.status_code <=299):
            raise Icinga2ApiException('Request "{}" failed with status {}: {}'.format(
                response.url,
                response.status_code,
                response.text))

        return response.json()

    # TODO 使用stringIO
    def fetech_from_stream(self, stream, split_str='\n', chunk_size=1024):
        """将stream中的多个chunk合并,并返回其中完整的数据
        :param split: 每条数据之间的分隔符
        :param chunk_size: byte
        :return:
        """
        for chunk in stream(chunk_size):
            self.stream_cache += chunk
            lines = self.stream_cache.split(split_str)
            if len(lines) >= 2:
                self.stream_cache = lines[-1]  # 保留最后一行,他可能是不完整的.
                yield lines[:-1]


class Objects(Base):
    """
    Icinga 2 API objects class
    """

    root = '/v1/objects'

    def _convert_object_type(self, object_type=None):
        """
        check if the object_type is a valid Icinga 2 object type
        """

        type_conv = {
            'ApiListener': 'apilisteners',
            'ApiUser': 'apiusers',
            'CheckCommand': 'checkcommands',
            'Arguments': 'argumentss',
            'CheckerComponent': 'checkercomponents',
            'CheckResultReader': 'checkresultreaders',
            'Comment': 'comments',
            'CompatLogger': 'compatloggers',
            'Dependency': 'dependencys',
            'Downtime': 'downtimes',
            'Endpoint': 'endpoints',
            'EventCommand': 'eventcommands',
            'ExternalCommandListener': 'externalcommandlisteners',
            'FileLogger': 'fileloggers',
            'GelfWriter': 'gelfwriters',
            'GraphiteWriter': 'graphitewriters',
            'Host': 'hosts',
            'HostGroup': 'hostgroups',
            'IcingaApplication': 'icingaapplications',
            'IdoMySqlConnection': 'idomysqlconnections',
            'IdoPgSqlConnection': 'idopgsqlconnections',
            'LiveStatusListener': 'livestatuslisteners',
            'Notification': 'notifications',
            'NotificationCommand': 'notificationcommands',
            'NotificationComponent': 'notificationcomponents',
            'OpenTsdbWriter': 'opentsdbwriters',
            'PerfdataWriter': 'perfdatawriters',
            'ScheduledDowntime': 'scheduleddowntimes',
            'Service': 'services',
            'ServiceGroup': 'servicegroups',
            'StatusDataWriter': 'statusdatawriters',
            'SyslogLogger': 'syslogloggers',
            'TimePeriod': 'timeperiods',
            'User': 'users',
            'UserGroup': 'usergroups',
            'Zone': 'zones',
        }
        if not object_type in type_conv:
            raise Icinga2ApiException('Icinga 2 object type "{}" does not exist.'.format(object_type))

        return type_conv[object_type]

    def list(self, object_type, name=None, attrs=None, filters=None, joins=None):
        """
        get object by type or name

        :param object_type: type of the object
        :type object_type: string
        :param name: list object with this name
        :type name: string
        :param attrs: only return these attributes
        :type attrs: list
        :param filters: filter the object list
        :type filters: string
        :param joins: show joined object
        :type joins: list

        example 1:
        list('Host')

        example 2:
        list('Service', 'webserver01.domain!ping4')

        example 3:
        list('Host', attrs='["address", "state"])

        example 4:
        list('Host', filters='match("webserver*", host.name)')

        example 5:
        list('Service', joins=['host.name'])

        example 6:
        list('Service', joins=True)
        """

        url_object_type = self._convert_object_type(object_type)
        url = '{}/{}'.format(self.root, url_object_type)
        if name:
            url += '/{}'.format(name)

        payload = {}
        if attrs:
            payload['attrs'] = attrs
        if filters:
            payload['filter'] = filters
        if isinstance(joins, bool) and joins:
            payload['all_joins'] = '1'
        elif joins:
            payload['joins'] = joins

        return self._request('GET', url, payload)

    def create(self, object_type, name, templates=None, attrs=None):
        """
        create an object

        :param object_type: type of the object
        :type object_type: string
        :param name: the name of the object
        :type name: string
        :param templates: templates used
        :type templates: list
        :param attrs: object's attributes
        :type attrs: dictionary

        example 1:
        create('Host', 'localhost', ['generic-host'], {'address': '127.0.0.1'})

        example 2:
        create('Service', 'testhost3!dummy', {'check_command': 'dummy'}, ['generic-service'])
        """

        url_object_type = self._convert_object_type(object_type)

        payload = {}
        if attrs:
            payload['attrs'] = attrs
        if templates:
            payload['templates'] = templates

        url = '{}/{}/{}'.format(self.root, url_object_type, name)

        return self._request('PUT', url, payload)

    def update(self, object_type, name, attrs):
        """
        update an object

        :param object_type: type of the object
        :type object_type: string
        :param name: the name of the object
        :type name: string
        :param attrs: object's attributes to change
        :type attrs: dictionary

        example 1:
        update('Host', 'localhost', {'address': '127.0.1.1'})

        example 2:
        update('Service', 'testhost3!dummy', {'check_interval': '10m'})
        """
        url_object_type = self._convert_object_type(object_type)
        url = '{}/{}/{}'.format(self.root, url_object_type, name)

        return self._request('POST', url, attrs)

    def delete(self, object_type, name=None, filters=None, cascade=True):
        """
        delete an object

        :param object_type: type of the object
        :type object_type: string
        :param name: the name of the object
        :type name: string
        :param filters: filter the object list
        :type filters: string
        :param cascade: deleted dependent objects
        :type joins: bool

        example 1:
        delete('Host', 'localhost')

        example 2:
        delete('Service', filters='match("vhost*", service.name)')
        """

        url_object_type = self._convert_object_type(object_type)

        payload = {}
        if filters:
            payload['filter'] = filters
        if cascade:
            payload['cascade'] = 1

        url = '{}/{}'.format(self.root, url_object_type)
        if name:
            url += '/{}'.format(name)

        return self._request('DELETE', url, payload)


class Actions(Base):
    """
    Icinga 2 API actions class
    """

    root = '/v1/actions'

    def process_check_result(self,
                             filters,
                             exit_status,
                             plugin_output,
                             performance_data=None,
                             check_command=None,
                             check_source=None):
        """Process a check result for a host or a service.

        Parameter 	Type 	Description
        exit_status 	integer 	Required. For services: 0=OK, 1=WARNING, 2=CRITICAL, 3=UNKNOWN, for hosts: 0=OK, 1=CRITICAL.
        plugin_output 	string 	Required. The plugins main output. Does not contain the performance data.
        performance_data 	string array 	Optional. The performance data.
        check_command 	string array 	Optional. The first entry should be the check commands path, then one entry for each command line option followed by an entry for each of its argument.
        check_source 	string 	Optional. Usually the name of the command_endpoint

        In addition to these parameters a filters must be provided. The valid types for this action are Host and Service.


        expample 1:
        filters = {
            "service" : "youfu-zf!ping4"
        }

        kwargs = { "exit_status": 2,
                   "plugin_output": "PING CRITICAL - Packet loss = 100%",
                   "performance_data": [ "rta=5000.000000ms;3000.000000;5000.000000;0.000000", "pl=100%;80;100;0" ],
                   "check_source": "python client" }
        process_check_result(filters,**kwargs)


        example 1:
        filters = {
            "service" : "youfu-zf!ping4"
        }

        kwargs = { "exit_status": 2,
                   "plugin_output": "PING CRITICAL - Packet loss = 100%",
                   "performance_data": [ "rta=5000.000000ms;3000.000000;5000.000000;0.000000", "pl=100%;80;100;0" ],
                   "check_source": "python client" }
        process_check_result(filters,**kwargs)
        """
        if not filters:
            raise Icinga2ApiException("filters is empty or none")
        url = '{}/{}'.format(self.root, "process-check-result")

        # payload
        payload = {
            "exit_status": exit_status,
            "plugin_output": plugin_output,
        }
        if performance_data:
            payload["performance_data"] = performance_data
        if check_command:
            payload["check_command"] = check_command
        if check_source:
            payload["check_source"] = check_source
        payload.update(filters)
        return self._request('POST', url, payload=payload)

    def reschedule_check(self, filters, next_check=None, force_check=True):
        """Reschedule a check for hosts and services. The check can be forced if required.

        Parameter 	Type 	Description
        next_check 	timestamp 	Optional. The next check will be run at this time. If omitted the current time is used.
        force_check 	boolean 	Optional. Defaults to false. If enabled the checks are executed regardless of time period restrictions and checks being disabled per object or on a global basis.

        In addition to these parameters a filter must be provided. The valid types for this action are Host and Service.


        example 1:
        filters = {
            "type" : "Service",
            "filter": r'service.name=="ping4"',
        }
        reschedule_check(filters)

        example 2:
        filters = {
            "type" : "Host",
            "filter": r'host.name=="youfu-zf"',
        }
        reschedule_check(filters)
        """
        if not filters:
            raise Icinga2ApiException("filters is empty or none")
        url = '{}/{}'.format(self.root, "reschedule-check")

        payload = {
            "force_check": force_check
        }
        if next_check:
            payload["next_check"] = next_check
        payload.update(filters)
        return self._request('POST', url, payload=payload)

    def send_custom_notification(self, filters, author, comment, force=False):
        """Send a custom notification for hosts and services. This notification type can be forced being sent to all users.

        Parameter 	Type 	Description
        author 	string 	Required. Name of the author, may be empty.
        comment 	string 	Required. Comment text, may be empty.
        force 	boolean 	Optional. Default: false. If true, the notification is sent regardless of downtimes or whether notifications are enabled or not.

        In addition to these parameters a filter must be provided. The valid types for this action are Host and Service.


        example 1:
        filters = {
            "type" : "Host"
        }
        send_custom_notification(filters,'fmnisme',"test comment")
        """
        if not filters:
            raise Icinga2ApiException("filters is empty or none")
        url = '{}/{}'.format(self.root, "send-custom-notification")

        payload = {
            "author": author,
            "comment": comment,
            "force": force
        }
        payload.update(filters)
        return self._request('POST', url, payload)

    def delay_notification(self, filters, timestamp):
        """Delay notifications for a host or a service.
        Note that this will only have an effect if the service stays in the same problem state that it is currently in.
        If the service changes to another state, a new notification may go out before the time you specify in the timestamp argument.

        Parameter 	Type 	Description
        timestamp 	timestamp 	Required. Delay notifications until this timestamp.

        In addition to these parameters a filter must be provided. The valid types for this action are Host and Service.


        example 1:
        filters = {
            "type" : "Service",
        }
        delay_notification(filters,"1446389894")

        example 2:
        filters = {
            "type" : "Host",
            "filter" : r'host.name=="youfu-zf"'
        }
        delay_notification(filters,"1446389894")

        """
        if not filters:
            raise Icinga2ApiException("filters is empty or none")
        url = '{}/{}'.format(self.root, "delay-notification")

        payload = {
            "timestamp": timestamp
        }
        payload.update(filters)
        return self._request('POST', url, payload)

    def acknowledge_problem(self, filters, author, comment, expiry=None, sticky=None, notify=None):
        """Allows you to acknowledge the current problem for hosts or services.
        By acknowledging the current problem, future notifications (for the same state if sticky is set to false) are disabled.

        Parameter 	Type 	Description
        author 	string 	Required. Name of the author, may be empty.
        comment 	string 	Required. Comment text, may be empty.
        expiry 	timestamp 	Optional. If set the acknowledgement will vanish after this timestamp.
        sticky 	boolean 	Optional. If true, the default, the acknowledgement will remain until the service or host fully recovers.
        notify 	boolean 	Optional. If true a notification will be sent out to contacts to indicate this problem has been acknowledged. The default is false.

        In addition to these parameters a filter must be provided. The valid types for this action are Host and Service.
        """
        if not filters:
            raise Icinga2ApiException("filters is empty or none")
        url = '{}/{}'.format(self.root, "acknowledge-problem")

        payload = {
            "author": author,
            "comment": comment,
        }
        if expiry:
            payload["expiry"] = expiry
        if sticky:
            payload["sticky"] = sticky
        if notify:
            payload["notify"] = notify
        payload.update(filters)
        return self._request('POST', url, payload)

    def remove_acknowledgement(self, filters):
        """Removes the acknowledgements for services or hosts. Once the acknowledgement has been removed notifications will be sent out again.

        A filter must be provided. The valid types for this action are Host and Service.


        example 1:
        filters = {
            "type" : "Service",
            "filter" : r'service.state==2',
            "service.state_type": 1,
        }
        remove_acknowledgement(filters)
        """
        if not filters:
            raise Icinga2ApiException("filters is empty or none")
        url = '{}/{}'.format(self.root, "remove-acknowledgement")

        payload = {}
        payload.update(filters)
        return self._request('POST', url, payload)

    def add_comment(self, filters, author, comment):
        """Adds a comment from an author to services or hosts.

        Parameter 	Type 	Description
        author 	string 	Required. name of the author, may be empty.
        comment 	string 	Required. Comment text, may be empty.

        In addition to these parameters a filter must be provided. The valid types for this action are Host and Service.


        example 1:
        filters = {
            "type" : "Service",
            "filter" : r'service.name=="ping4"'
        }
        kwargs = { "author": "icingaadmin", "comment": "Troubleticket #123456789 opened." }
        add_comment(filters,**kwargs)
        """
        if not filters:
            raise Icinga2ApiException("filters is empty or none")
        url = '{}/{}'.format(self.root, "add-comment")

        payload = {
            "author": author,
            "comment": comment
        }
        payload.update(filters)
        return self._request('POST', url, payload)

    def remove_comment(self, filters):
        """Remove the comment using its name attribute , returns OK if the comment did not exist. Note: This is not the legacy ID but the comment name returned by Icinga 2 when adding a comment.

        A filter must be provided. The valid types for this action are Host, Service and Comment.


        example 1:
        filters = {
            "type" : "Service",
            "filter" : r'service.name=="ping4"'
        }
        remove_comment(filters)
        """
        if not filters:
            raise Icinga2ApiException("filters is empty or none")
        url = '{}/{}'.format(self.root, "remove-comment")

        payload = {}
        payload.update(filters)
        return self._request('POST', url, payload)

    def schedule_downtime(self,
                          filters,
                          start_time,
                          end_time,
                          duration,
                          fixed=None,
                          trigger_name=None,
                          comment=None,
                          author=None):
        """Schedule a downtime for hosts and services.

        Parameter 	Type 	Description
        start_time 	timestamp 	Required. Timestamp marking the beginning of the downtime.
        end_time 	timestamp 	Required. Timestamp marking the end of the downtime.
        duration 	integer 	Required. Duration of the downtime in seconds if fixed is set to false.
        fixed 	boolean 	Optional. Defaults to false. If true the downtime is fixed otherwise flexible. See downtimes for more information.
        trigger_name 	string 	Optional. Sets the trigger for a triggered downtime. See downtimes for more information on triggered downtimes.

        In addition to these parameters a filter must be provided. The valid types for this action are Host and Service.


        example 1:
        filters = {
            "type" : "Service",
            "filter" : r'service.name=="ping4"'
        }
        kwargs = { "start_time": 1446388806, "end_time": 1446389806, "duration": 1000, "author": "icingaadmin", "comment": "IPv4 network maintenance" }
        schedule_downtime(filters,**kwargs)
        """
        if not filters:
            raise Icinga2ApiException("filters is empty or none")
        url = '{}/{}'.format(self.root, "schedule-downtime")

        payload = {
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration
        }
        if fixed:
            payload["fixed"] = fixed
        if trigger_name:
            payload["trigger_name"] = trigger_name
        if comment:
            payload["comment"] = comment
        if author:
            payload["author"] = author
        payload.update(filters)
        return self._request('POST', url, payload)

    def remove_downtime(self, filters):
        """Remove the downtime using its name attribute , returns OK if the downtime did not exist. Note: This is not the legacy ID but the downtime name returned by Icinga 2 when scheduling a downtime.

        A filter must be provided. The valid types for this action are Host, Service and Downtime.


        example 1:
        filters = {
            "type" : "Service",
            "filter" : r'service.name=="ping4"'
        }
       remove_comment(filters)
        """
        if not filters:
            raise Icinga2ApiException("filters is empty or none")
        url = '{}/{}'.format(self.root, "remove-downtime")

        payload = {}
        payload.update(filters)
        return self._request('POST', url, payload)

    def shutdown_process(self):
        """Shuts down Icinga2. May or may not return.

        This action does not support a target type or filter.


        example 1:
        shutdown_process()
        """
        url = '{}/{}'.format(self.root, "shutdown-process")
        return self._request('POST', url)

    def restart_process(self):
        """Restarts Icinga2. May or may not return.

        This action does not support a target type or filter.


        example 1:
        restart_process()
        """
        url = '{}/{}'.format(self.root, "restart-process")
        return self._request('POST', url)


class Events(Base):
    """
    Icinga 2 API events class
    """

    root = "/v1/events"

    def subscribe(self, types, queue, filters=None):
        """You can subscribe to event streams by sending a POST request to the URL endpoint /v1/events.

        The following parameters need to be specified (either as URL parameters or in a JSON-encoded message body):
        Parameter 	Type 	Description
        types 	string array 	Required. Event type(s). Multiple types as URL parameters are supported.
        queue 	string 	Required. Unique queue name. Multiple HTTP clients can use the same queue as long as they use the same event types and filter.
        filter 	string 	Optional. Filter for specific event attributes using filter expressions.

        Event Stream Types

        The following event stream types are available:
        Type 	Description
        CheckResult 	Check results for hosts and services.
        StateChange 	Host/service state changes.
        Notification 	Notification events including notified users for hosts and services.
        AcknowledgementSet 	Acknowledgement set on hosts and services.
        AcknowledgementCleared 	Acknowledgement cleared on hosts and services.
        CommentAdded 	Comment added for hosts and services.
        CommentRemoved 	Comment removed for hosts and services.
        DowntimeAdded 	Downtime added for hosts and services.
        DowntimeRemoved 	Downtime removed for hosts and services.
        DowntimeTriggered 	Downtime triggered for hosts and services.

        Note: Each type requires API permissions being set.


        example 1:
        types = ["CheckResult"]
        queue = "michi"
        filters = "event.check_result.exit_status==2"
        for event in subscribe(types,queue,filters):
            print event
        :param types:
        :param queue:
        :param filters:
        :return:
        """
        payload = {
            "types": types,
            "queue": queue,
        }
        if filters:
            payload["filters"] = filters
        stream = self._request('POST', self.root, payload, stream=True)
        for events in self.fetech_from_stream(stream):   # return list
            for event in events:
                yield event


class Status(Base):
    """
    Icinga 2 API status class
    """

    root = "/v1/status"

    def list(self, status_type=None):
        """Send a GET request to the URL endpoint /v1/status to retrieve status information and statistics for Icinga 2.

        You can limit the output by specifying a status type in the URL, e.g. IcingaApplication.


        example 1:
        print list()
        """
        url = self.root
        if status_type:
            url += "/{}".format(status_type)

        return self._request('GET', url)
