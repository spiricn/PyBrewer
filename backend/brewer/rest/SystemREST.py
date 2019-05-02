from ssc.servlets.RestServlet import RestHandler
from brewer.MailHandler import MailHandler
from brewer.ReportHandler import ReportHandler
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

        self.addAPI('sendReport',
            lambda request: self.brewer.getModule(ReportHandler).sendReport()
        )


    def _mailTest(self, request):
        '''
        Test if email client is configured correctly
        '''

        targetMail = request.params['target'][0]

        self.brewer.getModule(MailHandler).send(targetMail, 'PyBrewer test mail', 'Test message')
