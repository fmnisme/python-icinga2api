# -*- coding: utf-8 -*-
'''
Icinga 2 API client

The Icinga 2 API allows you to manage configuration objects and resources in a simple,
programmatic way using HTTP requests.
'''

from __future__ import print_function
import logging

import icinga2api
from icinga2api.base import Base
from icinga2api.configfile import ClientConfigFile
from icinga2api.exceptions import Icinga2ApiException

requests.packages.urllib3.disable_warnings()

LOG = logging.getLogger(__name__)


class Client(object):
    '''
    Icinga 2 Client class
    '''

    def __init__(self,
                 url=None,
                 username=None,
                 password=None,
                 timeout=None,
                 certificate=None,
                 key=None,
                 ca_certificate=None,
                 config_file=None):
        '''
        initialize object
        '''
        config_from_file = ClientConfigFile(config_file)
        if config_file:
            config_from_file.parse()
        self.url = url or \
            config_from_file.url
        self.username = username or \
            config_from_file.username
        self.password = password or \
            config_from_file.password
        self.timeout = timeout or \
            config_from_file.timeout
        self.certificate = certificate or \
            config_from_file.certificate
        self.key = key or \
            config_from_file.key
        self.ca_certificate = ca_certificate or \
            config_from_file.ca_certificate
        self.objects = Objects(self)
        self.actions = Actions(self)
        self.events = Events(self)
        self.status = Status(self)
        self.version = icinga2api.__version__

        if not self.url:
            raise Icinga2ApiException('No "url" defined.')
        if not self.username and not self.password and not self.certificate:
            raise Icinga2ApiException(
                'Neither username/password nor certificate defined.'
            )


class Objects(Base):
    '''
    Icinga 2 API objects class
    '''

    base_url_path = 'v1/objects'

    @staticmethod
    def _convert_object_type(object_type=None):
        '''
        check if the object_type is a valid Icinga 2 object type
        '''

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
        if object_type not in type_conv:
            raise Icinga2ApiException(
                'Icinga 2 object type "{}" does not exist.'.format(
                    object_type
                ))

        return type_conv[object_type]

    def get(self,
            object_type,
            name,
            attrs=None,
            joins=None):
        '''
        get object by type or name

        :param object_type: type of the object
        :type object_type: string
        :param name: list object with this name
        :type name: string
        :param attrs: only return these attributes
        :type attrs: list
        :param joins: show joined object
        :type joins: list

        example 1:
        get('Host', 'webserver01.domain')

        example 2:
        get('Service', 'webserver01.domain!ping4')

        example 3:
        get('Host', 'webserver01.domain', attrs=["address", "state"])

        example 4:
        get('Service', 'webserver01.domain!ping4', joins=True)
        '''

        return self.list(object_type, name, attrs, joins=joins)[0]

    def list(self,
             object_type,
             name=None,
             attrs=None,
             filter=None,
             filter_vars=None,
             joins=None):
        '''
        get object by type or name

        :param object_type: type of the object
        :type object_type: string
        :param name: list object with this name
        :type name: string
        :param attrs: only return these attributes
        :type attrs: list
        :param filter: filter the object list
        :type filter: string
        :param filter_vars: variables used in the filter expression
        :type filter_vars: dict
        :param joins: show joined object
        :type joins: list

        example 1:
        list('Host')

        example 2:
        list('Service', 'webserver01.domain!ping4')

        example 3:
        list('Host', attrs='["address", "state"])

        example 4:
        list('Host', filter='match("webserver*", host.name)')

        example 5:
        list('Service', joins=['host.name'])

        example 6:
        list('Service', joins=True)
        '''

        object_type_url_path = self._convert_object_type(object_type)
        url_path = '{}/{}'.format(self.base_url_path, object_type_url_path)
        if name:
            url_path += '/{}'.format(name)

        payload = {}
        if attrs:
            payload['attrs'] = attrs
        if filter:
            payload['filter'] = filter
        if filter_vars:
            payload['filter_vars'] = filter_vars
        if isinstance(joins, bool) and joins:
            payload['all_joins'] = '1'
        elif joins:
            payload['joins'] = joins

        return self._request('GET', url_path, payload)['results']

    def create(self,
               object_type,
               name,
               templates=None,
               attrs=None):
        '''
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
        create('Service',
               'testhost3!dummy',
               {'check_command': 'dummy'},
               ['generic-service'])
        '''

        object_type_url_path = self._convert_object_type(object_type)

        payload = {}
        if attrs:
            payload['attrs'] = attrs
        if templates:
            payload['templates'] = templates

        url_path = '{}/{}/{}'.format(
            self.base_url_path,
            object_type_url_path,
            name
        )

        return self._request('PUT', url_path, payload)

    def update(self,
               object_type,
               name,
               attrs):
        '''
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
        '''
        object_type_url_path = self._convert_object_type(object_type)
        url_path = '{}/{}/{}'.format(
            self.base_url_path,
            object_type_url_path,
            name
        )

        return self._request('POST', url_path, attrs)

    def delete(self,
               object_type,
               name=None,
               filter=None,
               filter_vars=None,
               cascade=True):
        '''
        delete an object

        :param object_type: type of the object
        :type object_type: string
        :param name: the name of the object
        :type name: string
        :param filter: filter the object list
        :type filter: string
        :param filter_vars: variables used in the filter expression
        :type filter_vars: dict
        :param cascade: deleted dependent objects
        :type joins: bool

        example 1:
        delete('Host', 'localhost')

        example 2:
        delete('Service', filter='match("vhost*", service.name)')
        '''

        object_type_url_path = self._convert_object_type(object_type)

        payload = {}
        if filter:
            payload['filter'] = filter
        if filter_vars:
            payload['filter_vars'] = filter_vars
        if cascade:
            payload['cascade'] = 1

        url = '{}/{}'.format(self.base_url_path, object_type_url_path)
        if name:
            url += '/{}'.format(name)

        return self._request('DELETE', url, payload)


class Actions(Base):
    '''
    Icinga 2 API actions class
    '''

    base_url_path = 'v1/actions'

    def process_check_result(self,
                             object_type,
                             name,
                             exit_status,
                             plugin_output,
                             performance_data=None,
                             check_command=None,
                             check_source=None):
        '''
        Process a check result for a host or a service.

        :param object_type: Host or Service
        :type object_type: string
        :param name: name of the object
        :type name: string
        :param exit_status: services: 0=OK, 1=WARNING, 2=CRITICAL, 3=UNKNOWN;
                            hosts: 0=OK, 1=CRITICAL
        :type filter: integer
        :param plugin_output: plugins main ouput
        :type plugin_output: string
        :param check_command: check command path followed by its arguments
        :type check_command: list
        :param check_source: name of the command_endpoint
        :type check_source: string
        :returns: the response as json
        :rtype: dictionary

        expample 1:
        process_check_result('Service',
                             'myhost.domain!ping4',
                             'exit_status': 2,
                             'plugin_output': 'PING CRITICAL - Packet loss = 100%',
                             'performance_data': [
                                 'rta=5000.000000ms;3000.000000;5000.000000;0.000000',
                                 'pl=100%;80;100;0'],
                             'check_source': 'python client'})
        '''

        if object_type not in ['Host', 'Service']:
            raise Icinga2ApiException(
                'object_type needs to be "Host" or "Service".'
            )

        url = '{}/{}'.format(self.base_url_path, 'process-check-result')

        payload = {
            '{}'.format(object_type.lower()): name,
            'exit_status': exit_status,
            'plugin_output': plugin_output,
        }
        if performance_data:
            payload['performance_data'] = performance_data
        if check_command:
            payload['check_command'] = check_command
        if check_source:
            payload['check_source'] = check_source

        return self._request('POST', url, payload)

    def reschedule_check(self,
                         object_type,
                         filter,
                         filter_vars=None,
                         next_check=None,
                         force_check=True):
        '''
        Reschedule a check for hosts and services.

        example 1:
        reschedule_check('Service'
                         'service.name=="ping4")

        example 2:
        reschedule_check('Host',
                         'host.name=="localhost"',
                         '1577833200')

        :param object_type: Host or Service
        :type object_type: string
        :param filter: filter the object
        :type filter: string
        :param filter_vars: variables used in the filter expression
        :type filter_vars: dict
        :param next_check: timestamp to run the check
        :type next_check: string
        :param force: ignore period restrictions and disabled checks
        :type force: bool
        :returns: the response as json
        :rtype: dictionary
        '''

        url = '{}/{}'.format(self.base_url_path, 'reschedule-check')

        payload = {
            'type': object_type,
            'filter': filter,
            'force_check': force_check
        }
        if next_check:
            payload['next_check'] = next_check
        if filter_vars:
            payload['filter_vars'] = filter_vars

        return self._request('POST', url, payload)

    def send_custom_notification(self,
                                 object_type,
                                 filter,
                                 author,
                                 comment,
                                 filter_vars=None,
                                 force=False):
        '''
        Send a custom notification for hosts and services.

        example 1:
        send_custom_notification('Host',
                                 'host.name==localhost',
                                 'icingaadmin',
                                 'test comment')

        :param object_type: Host or Service
        :type object_type: string
        :param filter: filter the object
        :type filter: string
        :param author: name of the author
        :type author: string
        :param comment: comment text
        :type comment: string
        :param force: ignore downtimes and notification settings
        :type force: bool
        :param filter_vars: variables used in the filter expression
        :type filter_vars: dict
        :returns: the response as json
        :rtype: dictionary
        '''

        url = '{}/{}'.format(self.base_url_path, 'send-custom-notification')

        payload = {
            'type': object_type,
            'filter': filter,
            'author': author,
            'comment': comment,
            'force': force
        }
        if filter_vars:
            payload['filter_vars'] = filter_vars

        return self._request('POST', url, payload)

    def delay_notification(self,
                           object_type,
                           filter,
                           timestamp,
                           filter_vars=None):
        '''
        Delay notifications for a host or a service.

        example 1:
        delay_notification('Service',
                           '1446389894')

        delay_notification('Host',
                           'host.name=="localhost"',
                           '1446389894')

        :param object_type: Host or Service
        :type object_type: string
        :param filter: filter the object
        :type filter: string
        :param timestamp: timestamp to delay the notifications to
        :type timestamp: int
        :param filter_vars: variables used in the filter expression
        :type filter_vars: dict
        :returns: the response as json
        :rtype: dictionary
        '''

        url = '{}/{}'.format(self.base_url_path, 'delay-notification')

        payload = {
            'type': object_type,
            'filter': filter,
            'timestamp': timestamp
        }
        if filter_vars:
            payload['filter_vars'] = filter_vars

        return self._request('POST', url, payload)

    def acknowledge_problem(self,
                            object_type,
                            filter,
                            author,
                            comment,
                            filter_vars=None,
                            expiry=None,
                            sticky=None,
                            notify=None):
        '''
        Acknowledge a Service or Host problem.

        :param object_type: Host or Service
        :type object_type: string
        :param filter: filter the object
        :type filter: string
        :param author: name of the author
        :type author: string
        :param comment: comment text
        :type comment: string
        :param filter_vars: variables used in the filter expression
        :type filter_vars: dict
        :param expiry: acknowledgement expiry timestamp
        :type expiry: int
        :param sticky: stay till full problem recovery
        :type sticky: bool
        :param notify: send notification
        :type notify: string
        :returns: the response as json
        :rtype: dictionary
        '''

        url = '{}/{}'.format(self.base_url_path, 'acknowledge-problem')

        payload = {
            'type': object_type,
            'filter': filter,
            'author': author,
            'comment': comment,
        }
        if filter_vars:
            payload['filter_vars'] = filter_vars
        if expiry:
            payload['expiry'] = expiry
        if sticky:
            payload['sticky'] = sticky
        if notify:
            payload['notify'] = notify

        return self._request('POST', url, payload)

    def remove_acknowledgement(self,
                               object_type,
                               filter,
                               filter_vars=None):
        '''
        Remove the acknowledgement for services or hosts.

        example 1:
        remove_acknowledgement(object_type='Service',
                               'service.state==2')

        :param object_type: Host or Service
        :type object_type: string
        :param filter: filter the object
        :type filter: string
        :param filter_vars: variables used in the filter expression
        :type filter_vars: dict
        :returns: the response as json
        :rtype: dictionary
        '''

        url = '{}/{}'.format(self.base_url_path, 'remove-acknowledgement')

        payload = {
            'type': object_type,
            'filter': filter
        }
        if filter_vars:
            payload['filter_vars'] = filter_vars

        return self._request('POST', url, payload)

    def add_comment(self,
                    object_type,
                    filter,
                    author,
                    comment,
                    filter_vars=None):
        '''
        Add a comment from an author to services or hosts.

        example 1:
        add_comment('Service',
                    'service.name=="ping4"',
                    'icingaadmin',
                    'Incident ticket #12345 opened.')

        :param object_type: Host or Service
        :type object_type: string
        :param filter: filter the object
        :type filter: string
        :param author: name of the author
        :type author: string
        :param comment: comment text
        :type comment: string
        :param filter_vars: variables used in the filter expression
        :type filter_vars: dict
        :returns: the response as json
        :rtype: dictionary
        '''

        url = '{}/{}'.format(self.base_url_path, 'add-comment')

        payload = {
            'type': object_type,
            'filter': filter,
            'author': author,
            'comment': comment
        }
        if filter_vars:
            payload['filter_vars'] = filter_vars

        return self._request('POST', url, payload)

    def remove_comment(self,
                       object_type,
                       name,
                       filter,
                       filter_vars=None):
        '''
        Remove a comment using its name or a filter.

        example 1:
        remove_comment('Comment'
                       'localhost!localhost-1458202056-25')

        example 2:
        remove_comment('Service'
                       filter='service.name=="ping4"')

        :param object_type: Host, Service or Comment
        :type object_type: string
        :param name: name of the Comment
        :type name: string
        :param filter: filter the object
        :type filter: string
        :param filter_vars: variables used in the filter expression
        :type filter_vars: dict
        :returns: the response as json
        :rtype: dictionary
        '''

        url = '{}/{}'.format(self.base_url_path, 'remove-comment')

        payload = {
            'type': object_type
        }
        if name:
            payload[object_type.lower()] = name
        if filter:
            payload['filter'] = filter
        if filter_vars:
            payload['filter_vars'] = filter_vars

        return self._request('POST', url, payload)

    def schedule_downtime(self,
                          object_type,
                          filter,
                          author,
                          comment,
                          start_time,
                          end_time,
                          duration,
                          filter_vars=None,
                          fixed=None,
                          trigger_name=None):
        '''
        Schedule a downtime for hosts and services.

        example 1:
        schedule_downtime(
            'object_type': 'Service',
            'filter': r'service.name=="ping4"',
            'author': 'icingaadmin',
            'comment': 'IPv4 network maintenance',
            'start_time': 1446388806,
            'end_time': 1446389806,
            'duration': 1000
        )

        example 2:
        schedule_downtime(
            'object_type': 'Host',
            'filter': r'match("*", host.name)',
            'author': 'icingaadmin',
            'comment': 'IPv4 network maintenance',
            'start_time': 1446388806,
            'end_time': 1446389806,
            'duration': 1000
        )

        :param object_type: Host or Service
        :type object_type: string
        :param filter: filter the object
        :type filter: string
        :param author: name of the author
        :type author: string
        :param comment: comment text
        :type comment: string
        :param start_time: timestamp marking the beginning
        :type start_time: string
        :param end_time: timestamp marking the end
        :type end_time: string
        :param duration: duration of the downtime in seconds
        :type duration: int
        :param filter_vars: variables used in the filter expression
        :type filter_vars: dict
        :param fixed: fixed or flexible downtime
        :type fixed: bool
        :param trigger_name: trigger for the downtime
        :type trigger_name: string
        :returns: the response as json
        :rtype: dictionary
        '''

        url = '{}/{}'.format(self.base_url_path, 'schedule-downtime')

        payload = {
            'type': object_type,
            'filter': filter,
            'author': author,
            'comment': comment,
            'start_time': start_time,
            'end_time': end_time,
            'duration': duration
        }
        if filter_vars:
            payload['filter_vars'] = filter_vars
        if fixed:
            payload['fixed'] = fixed
        if trigger_name:
            payload['trigger_name'] = trigger_name

        return self._request('POST', url, payload)

    def remove_downtime(self,
                        object_type,
                        name=None,
                        filter=None,
                        filter_vars=None):
        '''
        Remove the downtime using its name or a filter.

        example 1:
        remove_downtime('Downtime',
                        'localhost!ping4!localhost-1458148978-14')

        example 2:
        remove_downtime('Service',
                        filter='service.name=="ping4"')

        :param object_type: Host, Service or Downtime
        :type object_type: string
        :param name: name of the downtime
        :type name: string
        :param filter: filter the object
        :type filter: string
        :param filter_vars: variables used in the filter expression
        :type filter_vars: dict
        :returns: the response as json
        :rtype: dictionary
        '''

        if not name and not filter:
            raise Icinga2ApiException("name and filter is empty or none")

        url = '{}/{}'.format(self.base_url_path, 'remove-downtime')

        payload = {
            'type': object_type
        }
        if name:
            payload[object_type.lower()] = name
        if filter:
            payload['filter'] = filter
        if filter_vars:
            payload['filter_vars'] = filter_vars

        return self._request('POST', url, payload)

    def shutdown_process(self):
        '''
        Shuts down Icinga2. May or may not return.

        example 1:
        shutdown_process()
        '''

        url = '{}/{}'.format(self.base_url_path, 'shutdown-process')

        return self._request('POST', url)

    def restart_process(self):
        '''
        Restarts Icinga2. May or may not return.

        example 1:
        restart_process()
        '''

        url = '{}/{}'.format(self.base_url_path, 'restart-process')

        return self._request('POST', url)


class Events(Base):
    '''
    Icinga 2 API events class
    '''

    base_url_path = 'v1/events'

    def subscribe(self,
                  types,
                  queue,
                  filter=None,
                  filter_vars=None):
        '''
        subscribe to an event stream

        example 1:
        types = ["CheckResult"]
        queue = "monitor"
        filter = "event.check_result.exit_status==2"
        for event in subscribe(types, queue, filter):
            print event

        :param types: the event types to return
        :type types: array
        :param queue: the queue name to subscribe to
        :type queue: string
        :param filter: additional filter to apply
        :type filter: dictionary
        :param filter_vars: variables used in the filter expression
        :type filter_vars: dict
        :returns: the events
        :rtype: string
        '''
        payload = {
            "types": types,
            "queue": queue,
        }
        if filter:
            payload["filter"] = filter
        if filter_vars:
            payload["filter_vars"] = filter_vars

        stream = self._request(
            'POST',
            self.base_url_path,
            payload,
            stream=True
        )
        for event in self._get_message_from_stream(stream):
            yield event


class Status(Base):
    '''
    Icinga 2 API status class
    '''

    base_url_path = 'v1/status'

    def list(self, component=None):
        '''
        retrieve status information and statistics for Icinga 2

        example 1:
        list()

        example 2:
        list('IcingaApplication')

        :param component: only list the status of this component
        :type component: string
        :returns: status information
        :rtype: dictionary
        '''

        url = self.base_url_path
        if component:
            url += "/{}".format(component)

        return self._request('GET', url)
