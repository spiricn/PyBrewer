import logging

from ssc.servlets.PageServlet import PageServlet

from http.cookies import SimpleCookie
from brewer.SessionHandler import SessionHandler
from ssc.http.HTTP import HDR_COOKIE, HDR_SET_COOKIE, HDR_LOCATION, CODE_REDIRECT
from ssc.servlets.Servlet import Servlet

logger = logging.getLogger(__name__)


class SessionServlet(Servlet):
    '''
    Servlet used to verify sessions and redirect to login page in case session is not authorized
    '''
    # Name of the page used to log in
    LOGIN_PAGE = 'Login.html'

    # Rest APIs allowed while logged out
    LOGGED_OUT_REST_WHITELIST = ['/rest/user/login']

    def __init__(self, brewer, servletContainer, pattern):
        Servlet.__init__(self, servletContainer, pattern)

        self._brewer = brewer
        self._sessionHandler = self._brewer.getModule(SessionHandler)

    def handleRequest(self, request, response):
        session = None

        # Get the session ID from cookie, or create one if it doesn't exist
        if HDR_COOKIE in request.headers:

            # Session exists in cookie
            cookie = SimpleCookie()
            cookie.load(request.headers[HDR_COOKIE])

            # Extract ID from cookie
            sessionId = cookie['id'].value

            # Check if session is valid
            session = self._sessionHandler.getSession(sessionId)

            if not session:
                # Session not valid, create a new one below
                session = None

        if not session:
            # Create new session
            session = self._sessionHandler.createSession()

            # Create a cookie
            cookie = SimpleCookie()
            cookie['id'] = session.id
            cookie['id']["expires"] = session.expires

            # Get a string representation
            cookie = cookie.output(header='')[1:]

            response.addHeader(HDR_SET_COOKIE, cookie)

        # If session is not authorized let the login servlet handle this
        if not session.authorized:
            # Allow only specific REST calls
            if request.url.path in self.LOGGED_OUT_REST_WHITELIST:
                return False

            # TODO Find a better way of redirecting to login servlet
            for i in self._brewer.server.servlets:
                if isinstance(i, PageServlet) and i.manifestEntry.filePath == self.LOGIN_PAGE:
                    return i.handleRequest(request, response)

        # Let the other servlets handle the request
        return False
