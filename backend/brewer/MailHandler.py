from brewer.Handler import Handler, MessageType
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class MailHandler(Handler):
    '''
    Handler in charge of sending emails
    '''

    def __init__(self, brewer):
        Handler.__init__(self, brewer, __name__)

        self._server = None

    def onStart(self):
        if not self.brewer.config.smtpServer:
            return

        self._server = smtplib.SMTP(self.brewer.config.smtpServer,
            self.brewer.config.smtpPort)

        self._server.ehlo()
        self._server.starttls()
        self._server.ehlo()

        # Log in
        try:
            self._server.login(self.brewer.config.smtpUsername,
                self.brewer.config.smtpPassword)
        except Exception as e:
            self.createMessage(MessageType.WARNING, "Error logging in to SMTP: %s" % str(e))
            self._server = None
            return

    def isConfigured(self):
        '''
        Check if we're configured and ready to send mails

        @return True if configured False otherwise
        '''

        return self._server != None

    def send(self, toMail, subject, body, bodyType='plain'):
        '''
        Send an email

        @param toMail Target address
        @param subject Mail subject
        @param body Mail body
        @param bodyType Body MIME type
        '''

        message = MIMEMultipart("alternative")

        message["Subject"] = subject
        message["From"] = self.brewer.config.smtpUsername
        message["To"] = toMail

        message.attach( MIMEText(body, bodyType) )

        if not self._server:
            raise RuntimeError('Not logged in')

        self._server.sendmail(self.brewer.config.smtpUsername, toMail, message.as_string())
