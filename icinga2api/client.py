#coding:utf-8
import logging
import requests
from requests.auth import HTTPBasicAuth
import urllib2


LOG = logging.getLogger(__name__)


class Icinga2ApiException(Exception):
    def __init__(self,error):
        self.error = error

    def __str__(self):
        return str(self.error)


class Client(object):
    def __init__(self,api_endpoint,username,password):
        self.api_endpoint = api_endpoint
        self.password = password
        self.username = username
        self.objects = Objects(self)
        self.actions = Actions(self)


class Base(object):
    root = None #继承

    def __init__(self,manager):
        self.manager = manager

    def request(self,method,url,payload=None):
        headers = {
            "Accept": "application/json",
        }

        #request参数
        kwargs = {
            "headers" : headers,
            "auth" : HTTPBasicAuth(self.manager.username, self.manager.password),
            "verify" : False,
        }
        if method in ["get",]:
            kwargs["params"] = payload
        else:
            kwargs["json"] = payload

        request_method = getattr(requests,method)
        response = request_method(self.manager.api_endpoint+url, **kwargs)

        if not (200 <= response.status_code <=299):
            raise Icinga2ApiException(response.text)
        return response.json()


class Objects(Base):
    root = '/v1/objects'

    def list(self,object_type,name=None,filters=None):
        url = '%s/%s' % (self.root,object_type)
        if name:
            url += '/%s' % name
        return self.request('get',url,payload=filters)

    def create(self,object_type,name,config):
        url = '%s/%s/%s' % (self.root,object_type,name)
        return self.request('put',url,payload=config)

    def update(self,object_type,name,config):
        url = '%s/%s/%s' % (self.root,object_type,name)
        return self.request('post',url,payload=config)

    def delete(self,object_type,name=None,filters=None,cascade=True):
        if not filters:
            filters = {}
        if cascade:
            filters["cascade"] = 1

        url = '%s/%s' % (self.root,object_type)
        if name:
            url += '/%s' % name
        return self.request('delete',url,payload=filters)


class Actions(Base):
    root = '/v1/actions'

    def process_check_result(self,filters,exit_status,plugin_output,performance_data=None,check_command=None,check_source=None):
        """Process a check result for a host or a service.
        Send a POST request to the URL endpoint /v1/actions/process-check-result.

        exit_status 	integer 	Required. For services: 0=OK, 1=WARNING, 2=CRITICAL, 3=UNKNOWN, for hosts: 0=OK, 1=CRITICAL.
        plugin_output 	string 	Required. The plugins main output. Does not contain the performance data.
        performance_data 	string array 	Optional. The performance data.
        check_command 	string array 	Optional. The first entry should be the check commands path, then one entry for each command line option followed by an entry for each of its argument.
        check_source 	string 	Optional. Usually the name of the command_endpoint

        In addition to these parameters a filters must be provided. The valid types for this action are Host and Service.
        :return:
        """
        if not filters:
            raise Icinga2ApiException("filters is None")

        #生成url. url包含filters
        filters_list = []
        for k,v in filters.iteritems():
            filters_list.append('%s=%s' % (urllib2.quote(k),urllib2.quote(v)))
        filters_str = '&'.join(filters_list)
        url = '%s/%s' % (self.root,filters_str)

        #payload
        payload = {
            "exit_status" : exit_status,
            "plugin_output" : plugin_output,
        }
        if performance_data:
            payload["performance_data"] = performance_data
        if check_command:
            payload["check_command"] = check_command
        if check_source:
            payload["check_source"] = check_source

        return self.request('post',url,payload=payload)


