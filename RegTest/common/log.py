#coding:gbk
'''
Created on 2012-12-12

@author: oppochen
'''

import os
import time
import logging

class LogConfig(object):
    '''
    classdocs
    '''


    def __init__(self, log_file = False):
        '''
        Constructor
        '''
        self.log_file = log_file
        self.filename = os.path.abspath(r'log\%s' % time.strftime('%Y%m%d'))
        self.format = '[%(asctime)s] [%(levelname)s] [%(filename)s: %(lineno)s: %(funcName)s] %(message)s'
        if log_file:
            logging.basicConfig(
                filename = self.filename,
                format = self.format,
                level = logging.DEBUG
                )
        else:
            logging.basicConfig(
                format = self.format,
                level = logging.DEBUG
                )
    
    def get_log_file(self):
        return self.filename if self.log_file else ''
            
if __name__ == '__main__':
    LogConfig()
    logging.info('test_info')
    logging.error('test_error')
