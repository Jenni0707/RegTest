#coding:gbk
'''
Created on 2012-12-12

@author: oppochen
'''

import os

class PathMgmt(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
    
    def change_cur_dir(self, main_path):
        cur_dir = os.path.dirname(main_path)
        os.chdir(cur_dir)
        
