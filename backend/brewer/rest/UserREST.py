import json

from brewer.SessionHandler import SessionHandler
from ssc.http.HTTP import HDR_COOKIE, HDR_SET_COOKIE
from ssc.servlets.RestServlet import RestHandler
from http.cookies import SimpleCookie

from brewer.rest.BaseREST import BaseREST

class UserREST(BaseREST):
    '''
    Rest API for user management
    '''

    def __init__(self, brewer):
        BaseREST.__init__(self, brewer, 'user/')

        self.addAPI('login',
            self._login
        )

        self.addAPI('logout',
            self._logout
        )

    def _logout(self, request):
        '''
        Logout current session
        '''
        sessionHandler = self._brewer.getModule(SessionHandler)

        sessionId = self._extractSessionId(request)

        if not sessionId:
            raise RuntimeError('Could not find session ID')

        success = sessionHandler.terminateSession(sessionId)

        if not success:
            raise RuntimeError('Error terminating session')

    @staticmethod
    def _extractSessionId(request):
        rawCookie = None if HDR_COOKIE not in request.headers else request.headers[HDR_COOKIE]

        if not rawCookie:
            return None

        # Extract session ID from cookie
        cookie = SimpleCookie()
        cookie.load(rawCookie)

        if 'id' not in cookie:
            return None

        return cookie['id'].value

    def _login(self, request):
        '''
        Login
        '''

        body = request.read()

        body = json.loads(body.decode('utf-8'))
        if 'username' not in body or 'password' not in body:
            raise RuntimeError('Could not find username/password')

        username = body['username']
        password = body['password']

        sessionId = self._extractSessionId(request)

        if not sessionId:
            raise RuntimeError('Could not find session ID')

        sessionHandler = self._brewer.getModule(SessionHandler)

        # Authorize session
        success = sessionHandler.authorizeSession(sessionId, username, password)

        if not success:
            raise RuntimeError('Could not authorize session')

