from brewer.Handler import Handler, MessageType

import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError
import logging

logger = logging.getLogger(__name__)

class DropboxHandler(Handler):
    '''
    Dropbox handler used to upload/download files to and from Dropbox.

    Requires Dropbox token to be configured.
    '''

    def __init__(self, brewer):
        Handler.__init__(self, brewer, __name__)

        self._dbx = None

    def onStart(self):
        if not self.brewer.config.dropboxToken:
            return

        # Create dropbox instance
        self._dbx = dropbox.Dropbox(self.brewer.config.dropboxToken)

        # Check that the access token is valid
        try:
            self._dbx.users_get_current_account()
        except AuthError:
            self.createMessage(MessageType.WARNING, "Invalid Dropbox token")

            self._dbx = None
            return

    def upload(self, localPath, remotePath):
        '''
        Upload file

        @param localPath Local file path
        @param remotePath Remote file path
        '''

        logger.debug('upload %r -> %r', localPath, remotePath)

        if not self._dbx:
            raise RuntimeError('Not initialized')

        with open(localPath, 'rb') as fileObj:
            self._dbx.files_upload(fileObj.read(), remotePath, mode=WriteMode('overwrite'))

    def download(self,  remotePath, localPath):
        '''
        Download file

        @param remotePath Remote file path
        @param localPath Local file path
        '''

        if not self._dbx:
            raise RuntimeError('Not initialized')

        self._dbx.files_download_to_file(localPath, remotePath)
