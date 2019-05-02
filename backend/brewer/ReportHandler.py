from brewer.Handler import Handler, MessageType
import logging
import datetime
import time

from brewer.SettingsHandler import SettingsHandler
from brewer.HistoryHandler import HistoryHandler
from brewer.LogHandler import LogHandler
from brewer.MailHandler import MailHandler

logger = logging.getLogger(__name__)

class ReportHandler(Handler):
    '''
    In charge of compiling daily reports and sending them via e-mail
    '''

    # Time format used to parse config
    TIME_FORMAT = '%H:%M:%S'

    # Settings key used to store last sent report time
    STG_LAST_SENT_REPORT = 'last_sent_report'

    # Number of retries before giving up on sending the report
    NUM_SEND_RETRIES = 3

    def __init__(self, brewer):
        Handler.__init__(self, brewer, __name__)

    def update(self, elapsedTime):
        # Are we enabled?
        if not self._enabled:
            return

        currentTime = time.time()

        # When was the last time we sent a report ?
        lastSentReport = datetime.datetime.fromtimestamp(self.brewer.getModule(SettingsHandler).getFloat(self.STG_LAST_SENT_REPORT, 0.0))

        currentDate = datetime.datetime.fromtimestamp(currentTime)

        if currentDate.day == lastSentReport.day:
            # Sent todays report
            return

        if currentDate < self._reportTime:
            # Not yet time to send report
            return

        # Send report now
        for i in range(self.NUM_SEND_RETRIES):
            try:
                self.sendReport()
                break
            except Exception as e:
                logger.error('Error sending report: %s' % str(e))
                # Retry
                continue

        # Remember when we last attempted to send it
        self.brewer.getModule(SettingsHandler).putFloat(self.STG_LAST_SENT_REPORT, currentTime)

    def onStart(self):
        # Check if enabled
        self._enabled = self.brewer.config.reportMails != ''

        if not self._enabled:
            return

        # Check if we have mailing capability
        if not self.brewer.getModule(MailHandler).isConfigured():
            self.createMessage(MessageType.WARNING, 'Mail client not configured, reports disabled')
            self._enabled = False
            return

        # Parse report time
        self._reportTime = datetime.datetime.strptime(self.brewer.config.reportTime, self.TIME_FORMAT)

    def sendReport(self):
        '''
        Send report to configured email addresses
        '''

        if not self._enabled:
            logger.warning('report mails not configured')
            return

        title, htmlReport = self._generateReportHtml()

        try:
            self.brewer.getModule(MailHandler).send(self.brewer.config.reportMails, title, htmlReport, 'html')

            logger.debug('Report sent')
        except Exception as e:
            logger.error('Error sending report %s' % str(e))

    def _generateReportHtml(self):
        '''
        Generate HTML report
        '''

        statusOk = True

        # Get error logs
        errors = self.brewer.getModule(LogHandler).getLogs(
            startTime = datetime.datetime.now() - datetime.timedelta(hours=24),
            level=logging.ERROR)

        # Status not ok due to errors
        if errors:
            statusOk = False


        # Generate title
        title = 'PyBrewer Report - %s' % ('All good !' if statusOk else 'Attention needed')

        reportHtml = '''
        <html>
        <head>
        <title> %s </title>
        </head>
        <body>''' % title

        # List out all errors
        if errors:
            reportHtml += "<h2> Warning: %d errors detected </h2>" % len(errors)

            reportHtml += '<table>\n'
            for error in errors:
                message = error.message

                # Truncated message to 64 characters (just a preview)
                if len(message) > 64:
                    message = message[:64] + ' ...'

                # Remove new lines
                message = message.replace('\n', ' ')

                reportHtml += '<tr> <td> %s </td> </tr>\n' % message

            reportHtml += '</table>\n'


        # Get sensor readings for this day
        samples = self.brewer.getModule(HistoryHandler).getSamplesRange(
            datetime.datetime.now() - datetime.timedelta(hours=24),
            datetime.datetime.now())

        # Check temperatures
        if self.brewer.config.wortSensor in samples['samples']:
            # Get wort samples
            wortSamples = samples['samples'][self.brewer.config.wortSensor]

            # Calculate minimum and maximum temperatures
            minTemperatureC = None
            maxTemperatureC = None

            for sample in wortSamples:
                if minTemperatureC == None:
                    minTemperatureC = sample
                else:
                    minTemperatureC = min(minTemperatureC, sample)

                if maxTemperatureC == None:
                    maxTemperatureC = sample
                else:
                    maxTemperatureC = max(maxTemperatureC, sample)

            # Display range
            reportHtml += '<p> Wort temperature range: %.2f C - %.2f C</p>\n' % (minTemperatureC, maxTemperatureC)

        else:
            logger.warning('could not find wort samples')

        reportHtml += '''
</body>
</html>'''

        return title, reportHtml
