# -*- coding: utf-8 -*-
'''
Icinga 2 API client base
'''

from __future__ import print_function
import logging
import sys
import requests
# pylint: disable=import-error,no-name-in-module
if sys.version_info >= (3, 0):
    from urllib.parse import urljoin
else:
    from urlparse import urljoin
# pylint: enable=import-error,no-name-in-module

from icinga2api.exceptions import Icinga2ApiException

LOG = logging.getLogger(__name__)


class Base(object):
    '''
    Icinga 2 API Base class
    '''

    base_url_path = None  # 继承

    def __init__(self, manager):
        '''
        initialize object
        '''

        self.manager = manager
        self.stream_cache = ""

    def _create_session(self, method='POST'):
        '''
        create a session object
        '''

        session = requests.Session()
        # prefer certificate authentification
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

    def _request(self, method, url_path, payload=None, stream=False):
        '''
        make the request and return the body

        :param method: the HTTP method
        :type method: string
        :param url_path: the requested url path
        :type url_path: string
        :param payload: the payload to send
        :type payload: dictionary
        :returns: the response as json
        :rtype: dictionary
        '''

        request_url = urljoin(self.manager.url, url_path)
        LOG.debug("Request URL: %s", request_url)

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
        if stream:
            request_args['stream'] = True

        # do the request
        response = session.post(**request_args)

        if not stream:
            session.close()
        # # for debugging
        # from pprint import pprint
        # pprint(request_url)
        # pprint(payload)
        # pprint(response)

        if not 200 <= response.status_code <= 299:
            raise Icinga2ApiException(
                'Request "{}" failed with status {}: {}'.format(
                    response.url,
                    response.status_code,
                    response.text,
                ))

        if stream:
            return response
        else:
            return response.json()

    @staticmethod
    def _get_message_from_stream(stream):
        '''
        make the request and return the body

        :param stream: the stream
        :type method: request
        :returns: the message
        :rtype: dictionary
        '''

        # TODO: test iter_lines()
        message = ''
        for char in stream.iter_content():
            if char == '\n':
                yield message
                message = ''
            else:
                message += char
