# -*- coding: utf-8 -*-
'''
Icinga 2 API client exceptions
'''

class Icinga2ApiException(Exception):
    '''
    Icinga 2 API exception class
    '''

    def __init__(self, error):
        super(Icinga2ApiException, self).__init__(error)
        self.error = error

    def __str__(self):
        return str(self.error)


class Icinga2ApiConfigFileException(Exception):
    '''
    Icinga 2 API config file exception class
    '''

    def __init__(self, error):
        super(Icinga2ApiConfigFileException, self).__init__(error)
        self.error = error

    def __str__(self):
        return str(self.error)
