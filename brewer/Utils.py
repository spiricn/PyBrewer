class Utils:

    @staticmethod
    def getHumanReadableSize(size):
        '''
        Formats size into human readable string
        
        @param size: Size in bytes
        @return: Human readable string 
        '''

        if size < 1024:
            unit = 'B'
        elif size < 1024 * 1024:
            unit = 'KB'
            size = size / 1024.0
        elif size < 1024 * 1024 * 1024:
            unit = 'MB'
            size = size / (1024.0 * 1024.0)
        else:
            unit = 'GB'
            size = size / (1024.0 * 1024.0 * 1024.0)

        res = ''

        if size - int(size) == 0.0:
            res += '%d' % size
        else:
            res += '%.2f' % size

        res += ' ' + unit

        return res
