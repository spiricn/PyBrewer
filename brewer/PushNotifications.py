import http.client
import urllib.parse
import logging

logger = logging.getLogger(__name__)


class PushNotifications:
    '''
    Class used to send push notifications via pushover service
    '''

    # Pushover service endpoint
    PUSHOVER_ENDPOINT = "api.pushover.net:443"

    # Pushover service API
    PUSHOVER_API = "/1/messages.json"

    def __init__(self, userToken, appToken):
        self._userToken = userToken
        self._appToken = appToken

    def sendNotification(self, title, message):
        '''
        Send a notification
        
        @param title: Notification title
        @param message: Notification body
        '''

        logger.debug('[%s]: %s' % (title, message))

        if not self._userToken or not self._appToken:
            return

        # Create connection
        conn = http.client.HTTPSConnection(self.PUSHOVER_ENDPOINT)

        # Post request
        conn.request("POST", self.PUSHOVER_API,
          urllib.parse.urlencode({
            "token": self._appToken,
            "user": self._userToken,
            "message": message,
            "title" : title,
          }), { "Content-type": "application/x-www-form-urlencoded" })

        # Parse response
        response = conn.getresponse()
        if response.code != 200:
            logger.error('push notification failed: %d - %r' % (response.code, response.read()))
