from ssc.servlets.RestServlet import RestHandler
from brewer.MailHandler import MailHandler
from brewer.ReportHandler import ReportHandler
from brewer.HardwareHandler import HardwareHandler
from brewer.AComponent import ComponentType
from brewer.rest.BaseREST import BaseREST


class SystemREST(BaseREST):
    '''
    Various system APIs
    '''

    def __init__(self, brewer):
        BaseREST.__init__(self, brewer, 'system/')


        self.addAPI('testMail',
            self._mailTest
        )

        # Send report via email
        self.addAPI('sendReport',
            lambda request: self.brewer.getModule(ReportHandler).sendReport()
        )

        self.addAPI('getStatus',
            self._getStatus)

        # Backup system
        self.addAPI('backup',
            lambda request: self.brewer.backup())

        # Restart app
        self.addAPI('restart',
            lambda request: self.brewer.restart())

        # Stop app
        self.addAPI('stop',
            lambda request: self.brewer.stop())

    def _getStatus(self, request):
        '''
        Get component status

        @return List of component statuses
        '''

        status = []

        for component in self.brewer.getModule(HardwareHandler).getComponents():
            if component.componentType == ComponentType.SENSOR:
                value = component.getValue()
            elif component.componentType == ComponentType.SWITCH:
                value = 1.0 if component.isOn() else 0.0

            status.append({
                "value" : value,
                "name" : component.name,
                "type" : component.componentType.name
            })

        return status

    def _mailTest(self, request):
        '''
        Test if email client is configured correctly
        '''

        targetMail = request.params['target'][0]

        self.brewer.getModule(MailHandler).send(targetMail, 'PyBrewer test mail', 'Test message')
