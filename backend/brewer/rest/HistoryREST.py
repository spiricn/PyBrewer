from ssc.servlets.RestServlet import RestHandler
from ssc.http.HTTP import CODE_OK, MIME_TEXT, MIME_JSON, MIME_HTML, CODE_BAD_REQUEST
from brewer.LogHandler import LogHandler
from brewer.HistoryHandler import HistoryHandler
from brewer.HardwareHandler import HardwareHandler, ComponentType
from brewer.rest.BaseREST import BaseREST

class HistoryREST(BaseREST):
    '''
    API used to fetch information from history hadnler
    '''

    def __init__(self, brewer):
        BaseREST.__init__(self, brewer, 'history/')

        self.addAPI('getSamples', self._getSamples)

        self.addAPI('createEvent', self._createEvent)

        self.addAPI('deleteEvent', self._deleteEvent)

        self.addAPI('updateEvent', self._updateEvent)

        self.addAPI('getEvents', self._getEvents)

        self.addAPI('getEvent', self._getEvent)

    def _createEvent(self, request):
        '''
        Create an event

        @param name Event name

        @return Created event object
        '''

        eventName = request.params['name'][0]

        return self._brewer.getModule(HistoryHandler).createEvent(eventName)

    def _deleteEvent(self, request):
        '''
        Delete an event

        @param id Event ID
        '''

        eventId = request.params['id'][0]

        self._brewer.getModule(HistoryHandler).deleteEvent(eventId)

    def _updateEvent(self, request):
        '''
        Updat event

        @param name New name
        @param time New time
        @param id Event ID
        '''

        eventName = request.params['name'][0]
        eventTime = request.params['time'][0]
        eventId = request.params['id'][0]

        self._brewer.getModule(HistoryHandler).updateEvent(eventId, eventName, eventTime)

    def _getEvents(self, request):
        '''
        Get all events

        @return List of events
        '''

        return [event._asdict() for event in self._brewer.getModule(HistoryHandler).getEvents()]

    def _getEvent(self, request):
        '''
        Get specific event

        @param id Event ID

        @return Event if found
        '''

        eventId = int(request.params['id'][0])

        event = self._brewer.getModule(HistoryHandler).getEvent(eventId)

        if event == None:
            raise RuntimeError('Event with id %d does not exist' % eventId)

        return event._asdict()

    def _getSamples(self, request):
        '''
        Get component samples

        @return Samples
        '''

        return self._brewer.getModule(HistoryHandler).getSamples()