import logging

from ssc.servlets.PageServlet import PageServlet

from brewer.SessionHandler import SessionHandler
from ssc.http.HTTP import HDR_COOKIE, HDR_SET_COOKIE, HDR_LOCATION, CODE_REDIRECT
from ssc.servlets.Servlet import Servlet

logger = logging.getLogger(__name__)


class SessionServlet(Servlet):
    '''
    Servlet used to verify sessions and redirect to login page in case session is not authorized
    '''

    LOGIN_PAGE = 'Login.html'

    def __init__(self, brewer, servletContainer, pattern):
        Servlet.__init__(self, servletContainer, pattern)

        self._brewer = brewer
        self._sessionHandler = self._brewer.getModule(SessionHandler)

    def handleRequest(self, request, response):
        # Get the session ID from cookie, or create one if it doesn't exist
        if HDR_COOKIE in request.headers:
            # Session exists in cookie
            sessionId = request.headers[HDR_COOKIE]

        else:
            # Create new session
            sessionId = self._sessionHandler.createSession()

            response.addHeader(HDR_SET_COOKIE, sessionId)

        # If session is not authorized let the login servlet handle this
        if not self._sessionHandler.isSessionAuthorized(sessionId):
            # TODO Find a better way of redirecting to login servlet
            for i in self._brewer.server.servlets:
                if isinstance(i, PageServlet) and i.manifestEntry.filePath == self.LOGIN_PAGE:
                    return i.handleRequest(request, response)

        # Let the other servlets handle the request
        return False
