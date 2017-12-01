# -*- coding: utf-8 -*-
'''
Icinga 2 API status
'''

from __future__ import print_function
import logging

from icinga2api.base import Base

LOG = logging.getLogger(__name__)


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
