import json

from brewer.SessionHandler import SessionHandler
from ssc.http.HTTP import CODE_OK, MIME_TEXT, MIME_JSON, MIME_HTML, CODE_BAD_REQUEST
from ssc.http.HTTP import HDR_COOKIE, HDR_SET_COOKIE
from ssc.servlets.RestServlet import RestHandler
from http.cookies import SimpleCookie


class UserREST:
    '''
    Rest API for user management
    '''

    def __init__(self, brewer):
        self._brewer = brewer

    def getRestAPI(self):
        return (
                RestHandler(
                    'user/login',
                    self._login
                ),

                RestHandler(
                    'user/logout',
                    self._logout
                ),
        )

    def _logout(self, request):
        '''
        '''
        sessionHandler = self._brewer.getModule(SessionHandler)

        sessionId = self._extractSessionId(request)

        if not sessionId:
            return (500, MIME_JSON, {'success' : False})

        success = sessionHandler.terminateSession(sessionId)

        return (500 if not success else 200, MIME_JSON, {'success' : success})

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
        '''

        body = request.read()
        if not body:
            return (500, MIME_JSON, {'success' : False})

        body = json.loads(body.decode('utf-8'))
        if 'username' not in body or 'password' not in body:
            return (500, MIME_JSON, {'success' : False})

        username = body['username']
        password = body['password']

        sessionId = self._extractSessionId(request)

        if not sessionId:
            return (500, MIME_JSON, {'success' : False})

        sessionHandler = self._brewer.getModule(SessionHandler)

        # Authorize session
        success = sessionHandler.authorizeSession(sessionId, username, password)

        return (500 if not success else 200, MIME_JSON, {'success' : success})
