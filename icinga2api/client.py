#coding:utf-8
import requests
from requests.auth import HTTPBasicAuth


class Client(object):
    def __init__(self,api_endpoint,username,password):
        self.api_endpoint = api_endpoint
        self.password = password
        self.username = username
        self.objects = Objects(self)


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
            raise Exception(response.text)
        return response.json()


class Objects(Base):
    root = '/objects'

    def list(self,object_type,name=None,filter=None):
        url = '%s/%s' % (self.root,object_type)
        if name:
            url += '/%s' % name
        return self.request('get',url,payload=filter)

    def create(self,object_type,name,config):
        url = '%s/%s/%s' % (self.root,object_type,name)
        return self.request('put',url,payload=config)

    def update(self,object_type,name,config):
        url = '%s/%s/%s' % (self.root,object_type,name)
        return self.request('post',url,payload=config)

    def delete(self,object_type,name=None,filter=None,cascade=True):
        if not filter:
            filter = {}
        if cascade:
            filter["cascade"] = 1

        url = '%s/%s' % (self.root,object_type)
        if name:
            url += '/%s' % name
        return self.request('delete',url,payload=filter)
