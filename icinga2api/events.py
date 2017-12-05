# -*- coding: utf-8 -*-
'''
Icinga 2 API events
'''

from __future__ import print_function
import logging

from icinga2api.base import Base

LOG = logging.getLogger(__name__)


class Events(Base):
    '''
    Icinga 2 API events class
    '''

    base_url_path = 'v1/events'

    def subscribe(self,
                  types,
                  queue,
                  filters=None,
                  filter_vars=None):
        '''
        subscribe to an event stream

        example 1:
        types = ["CheckResult"]
        queue = "monitor"
        filters = "event.check_result.exit_status==2"
        for event in subscribe(types, queue, filters):
            print event

        :param types: the event types to return
        :type types: array
        :param queue: the queue name to subscribe to
        :type queue: string
        :param filters: filters matched object(s)
        :type filters: string
        :param filter_vars: variables used in the filters expression
        :type filter_vars: dict
        :returns: the events
        :rtype: string
        '''
        payload = {
            "types": types,
            "queue": queue,
        }
        if filters:
            payload["filter"] = filters
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
