from ssc.servlets.RestServlet import RestHandler
from brewer.MailHandler import MailHandler
from brewer.rest.BaseREST import BaseREST


class SystemREST(BaseREST):
    '''
    Various system APIs
    '''

    def __init__(self, brewer):
        BaseREST.__init__(self, brewer, 'system/')


        self.addAPI('mailTest',
            self._mailTest
        )


    def _mailTest(self, request):
        '''
        Test if email client is configured correctly
        '''

        targetMail = request.params['target'][0]

        self._brewer.getModule(MailHandler).send(targetMail, 'PyBrewer test mail', 'Test message')
