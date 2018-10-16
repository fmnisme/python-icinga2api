# -*- coding: utf-8 -*-
'''
Copyright 2017 fmnisme@gmail.com

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Icinga 2 API client

The Icinga 2 API allows you to manage configuration objects and resources in a simple,
programmatic way using HTTP requests.
'''

from __future__ import print_function
import logging

from icinga2api.base import Base
from icinga2api.exceptions import Icinga2ApiException

LOG = logging.getLogger(__name__)


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
                         filters,
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
        :param filters: filters matched object(s)
        :type filters: string
        :param filter_vars: variables used in the for filters expression
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
            'filter': filters,
            'force_check': force_check
        }
        if next_check:
            payload['next_check'] = next_check
        if filter_vars:
            payload['filter_vars'] = filter_vars

        return self._request('POST', url, payload)

    def send_custom_notification(self,
                                 object_type,
                                 filters,
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
        :param filters: filters matched object
        :type filters: string
        :param author: name of the author
        :type author: string
        :param comment: comment text
        :type comment: string
        :param force: ignore downtimes and notification settings
        :type force: bool
        :param filter_vars: variables used in the filters expression
        :type filter_vars: dict
        :returns: the response as json
        :rtype: dictionary
        '''

        url = '{}/{}'.format(self.base_url_path, 'send-custom-notification')

        payload = {
            'type': object_type,
            'filter': filters,
            'author': author,
            'comment': comment,
            'force': force
        }
        if filter_vars:
            payload['filter_vars'] = filter_vars

        return self._request('POST', url, payload)

    def delay_notification(self,
                           object_type,
                           filters,
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
        :param filters: filters matched object(s)
        :type filters: string
        :param timestamp: timestamp to delay the notifications to
        :type timestamp: int
        :param filter_vars: variables used in the filters expression
        :type filter_vars: dict
        :returns: the response as json
        :rtype: dictionary
        '''

        url = '{}/{}'.format(self.base_url_path, 'delay-notification')

        payload = {
            'type': object_type,
            'filter': filters,
            'timestamp': timestamp
        }
        if filter_vars:
            payload['filter_vars'] = filter_vars

        return self._request('POST', url, payload)

    def acknowledge_problem(self,
                            object_type,
                            filters,
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
        :param filters: filters matched object(s)
        :type filters: string
        :param author: name of the author
        :type author: string
        :param comment: comment text
        :type comment: string
        :param filter_vars: variables used in the filters expression
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
            'filter': filters,
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
                               filters,
                               filter_vars=None):
        '''
        Remove the acknowledgement for services or hosts.

        example 1:
        remove_acknowledgement(object_type='Service',
                               'service.state==2')

        :param object_type: Host or Service
        :type object_type: string
        :param filters: filters matched object(s)
        :type filters: string
        :param filter_vars: variables used in the filters expression
        :type filter_vars: dict
        :returns: the response as json
        :rtype: dictionary
        '''

        url = '{}/{}'.format(self.base_url_path, 'remove-acknowledgement')

        payload = {
            'type': object_type,
            'filter': filters
        }
        if filter_vars:
            payload['filter_vars'] = filter_vars

        return self._request('POST', url, payload)

    def add_comment(self,
                    object_type,
                    filters,
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
        :param filters: filters matched object(s)
        :type filters: string
        :param author: name of the author
        :type author: string
        :param comment: comment text
        :type comment: string
        :param filter_vars: variables used in the filters expression
        :type filter_vars: dict
        :returns: the response as json
        :rtype: dictionary
        '''

        url = '{}/{}'.format(self.base_url_path, 'add-comment')

        payload = {
            'type': object_type,
            'filter': filters,
            'author': author,
            'comment': comment
        }
        if filter_vars:
            payload['filter_vars'] = filter_vars

        return self._request('POST', url, payload)

    def remove_comment(self,
                       object_type,
                       name,
                       filters,
                       filter_vars=None):
        '''
        Remove a comment using its name or filters.

        example 1:
        remove_comment('Comment'
                       'localhost!localhost-1458202056-25')

        example 2:
        remove_comment('Service'
                       filters='service.name=="ping4"')

        :param object_type: Host, Service or Comment
        :type object_type: string
        :param name: name of the Comment
        :type name: string
        :param filters: filters matched object(s)
        :type filters: string
        :param filter_vars: variables used in the filters expression
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
        if filters:
            payload['filter'] = filters
        if filter_vars:
            payload['filter_vars'] = filter_vars

        return self._request('POST', url, payload)

    def schedule_downtime(self,
                          object_type,
                          filters,
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
            'filters': r'service.name=="ping4"',
            'author': 'icingaadmin',
            'comment': 'IPv4 network maintenance',
            'start_time': 1446388806,
            'end_time': 1446389806,
            'duration': 1000
        )

        example 2:
        schedule_downtime(
            'object_type': 'Host',
            'filters': r'match("*", host.name)',
            'author': 'icingaadmin',
            'comment': 'IPv4 network maintenance',
            'start_time': 1446388806,
            'end_time': 1446389806,
            'duration': 1000
        )

        :param object_type: Host or Service
        :type object_type: string
        :param filters: filters matched object(s)
        :type filters: string
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
        :param filter_vars: variables used in the filters expression
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
            'filter': filters,
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
                        filters=None,
                        filter_vars=None):
        '''
        Remove the downtime using its name or filters.

        example 1:
        remove_downtime('Downtime',
                        'localhost!ping4!localhost-1458148978-14')

        example 2:
        remove_downtime('Service',
                        filters='service.name=="ping4"')

        :param object_type: Host, Service or Downtime
        :type object_type: string
        :param name: name of the downtime
        :type name: string
        :param filters: filters matched object(s)
        :type filters: string
        :param filter_vars: variables used in the filters expression
        :type filter_vars: dict
        :returns: the response as json
        :rtype: dictionary
        '''

        if not name and not filters:
            raise Icinga2ApiException("name and filters is empty or none")

        url = '{}/{}'.format(self.base_url_path, 'remove-downtime')

        payload = {
            'type': object_type
        }
        if name:
            payload[object_type.lower()] = name
        if filters:
            payload['filter'] = filters
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
