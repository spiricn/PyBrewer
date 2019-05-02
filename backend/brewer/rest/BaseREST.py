from ssc.http.HTTP import CODE_OK, MIME_TEXT, MIME_JSON, MIME_HTML, CODE_BAD_REQUEST
from ssc.servlets.RestServlet import RestHandler
import time
import traceback
import logging

logger = logging.getLogger(__name__)

class BaseREST:
    '''
    Base REST API class.
    '''

    def __init__(self, brewer, prefix):
        self._brewer = brewer
        self._prefix = prefix

        self._apis = []

    def addAPI(self, location, fnc, help=''):
        '''
        Add new REST API

        @param location API URI location
        @param fnc API function
        @param help Help description
        '''

        self._apis.append(RestHandler(self._prefix + location, lambda request: self._apiCall(request, fnc), help))

        return self

    @property
    def brewer(self):
        '''
        Parent brewer instance
        '''

        return self._brewer

    def _apiCall(self, request, fnc):
        '''
        API call wrapper
        '''

        # Start measuring time
        startTime = time.time()

        response = {}
        code = CODE_OK
        success = True
        errorMessage = None

        try:
            # Call function
            result = fnc(request)

            # Remember result if it returned some
            if result != None:
                response['result'] = result

        except Exception as e:
            code = 500
            success = False
            logger.error('Exception ocurred during REST call: %s' % str(traceback.format_exc()))

            errorMessage = str(e)


        response['success'] = success
        response['executionTime'] = time.time()-startTime

        if errorMessage:
            response['errorMessage'] = errorMessage

        return code, MIME_JSON, response

    def getRestAPI(self):
        '''
        Gets the list of all the REST APIs

        @return List of REST APIs
        '''

        return self._apis