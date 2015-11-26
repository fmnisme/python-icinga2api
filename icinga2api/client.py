#coding:utf-8
"""
icinga2 api client

write for icinga2 2.4
"""
import logging
import requests
from requests.auth import HTTPBasicAuth


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
        self.events = Events(self)
        self.status = Status(self)


class Base(object):
    root = None #继承

    def __init__(self,manager):
        self.manager = manager
        self.stream_cache = ""

    def request(self,method,url,payload=None,stream=False):
        headers = {
            "Accept": "application/json",
        }

        #request参数
        kwargs = {
            "headers" : headers,
            "auth" : HTTPBasicAuth(self.manager.username, self.manager.password),
            "verify" : False,
            "stream" : stream,
        }
        if method in ["get",]:
            kwargs["params"] = payload
        else:
            kwargs["json"] = payload

        print url
        print kwargs
        request_method = getattr(requests,method)
        response = request_method(self.manager.api_endpoint+url, **kwargs)
        if not (200 <= response.status_code <=299):
            raise Icinga2ApiException(response.text)

        if stream:
            return lambda chunk_size : response.iter_content(chunk_size=chunk_size)
        else:
            return response.json()

    #TODO 使用stringIO
    def fetech_from_stream(self,stream,split_str='\n',chunk_size=1024):
        """将stream中的多个chunk合并,并返回其中完整的数据
        :param split: 每条数据之间的分隔符
        :param chunk_size: byte
        :return:
        """
        for chunk in stream(chunk_size):
            self.stream_cache += chunk
            lines = self.stream_cache.split(split_str)
            if len(lines) >= 2:
                self.stream_cache = lines[-1]#保留最后一行,他可能是不完整的.
                yield lines[:-1]


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
        url = '%s/%s' % (self.root,"process-check-result")

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
        payload.update(filters)
        return self.request('post',url,payload=payload)

    def reschedule_check(self,filters,next_check=None,force_check=True):
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
        url = '%s/%s' % (self.root,"reschedule-check")

        payload = {
            "force_check" : force_check
        }
        if next_check:
            payload["next_check"] = next_check
        payload.update(filters)
        return self.request('post',url,payload=payload)

    def send_custom_notification(self,filters,author,comment,force=False):
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
        url = '%s/%s' % (self.root,"send-custom-notification")

        payload = {
            "author" : author,
            "comment" : comment,
            "force" : force
        }
        payload.update(filters)
        return self.request('post',url,payload)

    def delay_notification(self,filters,timestamp):
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
        url = '%s/%s' % (self.root,"delay-notification")

        payload = {
            "timestamp" : timestamp
        }
        payload.update(filters)
        return self.request('post',url,payload)

    def acknowledge_problem(self,filters,author,comment,expiry=None,sticky=None,notify=None):
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
        url = '%s/%s' % (self.root,"acknowledge-problem")

        payload = {
            "author" : author,
            "comment" : comment,
        }
        if expiry:
            payload["expiry"] = expiry
        if sticky:
            payload["sticky"] = sticky
        if notify:
            payload["notify"] = notify
        payload.update(filters)
        return self.request("post",url,payload)

    def remove_acknowledgement(self,filters):
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
        url = '%s/%s' % (self.root,"remove-acknowledgement")

        payload = {}
        payload.update(filters)
        return self.request("post",url,payload)

    def add_comment(self,filters,author,comment):
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
        url = '%s/%s' % (self.root,"add-comment")

        payload = {
            "author" : author,
            "comment" : comment
        }
        payload.update(filters)
        return self.request("post",url,payload)

    def remove_comment(self,filters):
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
        url = '%s/%s' % (self.root,"remove-comment")

        payload = {}
        payload.update(filters)
        return self.request("post",url,payload)

    def schedule_downtime(self,filters,start_time,end_time,duration,fixed=None,trigger_name=None,comment=None,author=None):
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
        url = '%s/%s' % (self.root,"schedule-downtime")

        payload = {
            "start_time" : start_time,
            "end_time" : end_time,
            "duration" : duration
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
        return self.request("post",url,payload)

    def remove_downtime(self,filters):
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
        url = '%s/%s' % (self.root,"remove-downtime")

        payload = {}
        payload.update(filters)
        return self.request("post",url,payload)

    def shutdown_process(self):
        """Shuts down Icinga2. May or may not return.

        This action does not support a target type or filter.


        example 1:
        shutdown_process()
        """
        url = '%s/%s' % (self.root,"shutdown-process")
        return self.request("post",url)

    def restart_process(self):
        """Restarts Icinga2. May or may not return.

        This action does not support a target type or filter.


        example 1:
        restart_process()
        """
        url = '%s/%s' % (self.root,"restart-process")
        return self.request("post",url)


class Events(Base):
    root = "/v1/events"

    def subscribe(self,types,queue,filters=None):
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
            "types" : types,
            "queue" : queue,
        }
        if filters:
            payload["filters"] = filters
        stream = self.request('post',self.root,payload,stream=True)
        for events in self.fetech_from_stream(stream):   #return list
            for event in events:
                yield event


class Status(Base):
    root = "/v1/status"

    def list(self,status_type=None):
        """Send a GET request to the URL endpoint /v1/status to retrieve status information and statistics for Icinga 2.

        You can limit the output by specifying a status type in the URL, e.g. IcingaApplication.


        example 1:
        print list()
        """
        url = self.root
        if status_type:
            url += "/%s" % (status_type)

        return self.request('get',url)