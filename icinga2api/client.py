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
from icinga2api.objects import Objects
from icinga2api.actions import Actions
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
