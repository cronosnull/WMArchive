#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : Methods.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: This module consists of all REST APIs required by WMArchive service
Every API is designed as a class with appropriate get/post/put/delete
methods, see RESTEntity class for more details.
"""
# futures
from __future__ import print_function, division

# system modules
import json
import traceback
from types import GeneratorType

# 3d party modules
import cherrypy

# WMCore modules
from WMCore.REST.Server import RESTEntity, restcall
from WMCore.REST.Tools import tools
from WMCore.REST.Validation import validate_str
from WMCore.REST.Format import JSONFormat

# WMArchive modules
from WMArchive.Service.Manager import WMArchiveManager
from WMArchive.Utils.Regexp import PAT_UID, PAT_QUERY, PAT_INFO

def results(result):
    "Return results as a list data type. Set proper status in case of failures"
    if 'status' in result and 'Not supported' in result['status']:
        cherrypy.response.status = 406 # Not Acceptable
    if  not isinstance(result, list):
        return [result]
    return result

class WMAData(RESTEntity):
    "REST interface for WMArchvie"
    def __init__(self, app, api, config, mount):
        RESTEntity.__init__(self, app, api, config, mount)
        self.config = config
        self.mgr = WMArchiveManager(config)

    def validate(self, apiobj, method, api, param, safe):
        """
        Validate request input data.
        Has to be implemented, otherwise the service fails to start.
        If it's not implemented correctly (e.g. just pass), the arguments
        are not passed in the method at all.

        """
        if  method == 'GET':
            if 'query' in param.kwargs.keys():
                validate_str('query', param, safe, PAT_QUERY, optional=True)
            for key in ['status', 'jobs', 'adocs', '_']:
                if  key in param.kwargs.keys():
                    validate_str(key, param, safe, PAT_INFO, optional=True)
                    # underscore may come from ajax call via jQuery
                    validate_str('_', param, safe, PAT_INFO, optional=True)
            # test if user provided uid
            if len(param.args) == 1 and PAT_UID.match(param.args[0]):
                safe.args.append(param.args[0])
                param.args.remove(param.args[0])
                return True
        elif method == 'POST':
            if  not param.args or not param.kwargs:
                return False # this class does not need any parameters
        return True

    @restcall(formats=[('application/json', JSONFormat())])
    @tools.expires(secs=-1)
    def get(self, *args, **kwds):
        """
        Implement GET request with given uid or set of parameters
        All work is done by WMArchiveManager
        """
        if  kwds.get('status', ''):
            return results(dict(status=self.mgr.status()))
        if  kwds.get('jobs', ''):
            return results(dict(jobs=self.mgr.jobs()))
        if  kwds.get('adocs', ''):
            return results(dict(adocs=self.mgr.adocs()))
        if  args and len(args) == 1: # requested uid
            return results(self.mgr.read(args[0], []))
        return results({'request': kwds, 'results': 'Not available'})

    @restcall(formats=[('application/json', JSONFormat())])
    @tools.expires(secs=-1)
    def post(self):
        """
        Implement POST request API, all work is done by WMArchiveManager.
        The request should either provide query to fetch results from back-end
        or data to store to the back-end.

        The input HTTP request should be either
        {"data":some_data} for posting the data into WMArchive or
        {"spec":some_query, "fields":return_fields} for querying the data in WMArchive.
        The some_data should be proper JSON document(s).
        The some_query should be use MongoDB QL.
        """
        msg = 'expect "data", "query" attributes in your request'
        result = {'status':'Not supported, %s' % msg, 'data':[]}
        try:
            request = json.load(cherrypy.request.body)
            if  'spec' in request.keys() and 'fields' in request.keys():
                result = self.mgr.read(request['spec'], request['fields'])
            elif 'data' in request.keys():
                result = self.mgr.write(request['data'])
            elif 'job' in request.keys():
                result = self.mgr.write(request['job'])
            if  isinstance(result, GeneratorType):
                result = [r for r in result]
            return results(result)
        except cherrypy.HTTPError:
            raise
        except Exception as exp:
            traceback.print_exc()
            raise cherrypy.HTTPError()

    @restcall(formats=[('application/json', JSONFormat())])
    @tools.expires(secs=-1)
    def put(self):
        """
        Implement PUT request API, all work is done by WMArchiveManager.
        The request should either provide query to fetch results from back-end
        or data to store to the back-end.

        The input HTTP request should be in a form
        {"ids":[list_of_ids], "spec": update_spec}
        """
        msg = 'expect "data", "query" attributes in your request'
        result = {'status':'Not supported, %s' % msg, 'data':[]}
        try:
            request = json.load(cherrypy.request.body)
            result = self.mgr.update(request['ids'], request['spec'])
            if  isinstance(result, GeneratorType):
                result = [r for r in result]
            return results(result)
        except cherrypy.HTTPError:
            raise
        except Exception as exp:
            traceback.print_exc()
            raise cherrypy.HTTPError()
