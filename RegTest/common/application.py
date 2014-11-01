#coding:gbk
'''
Created on 2012-12-12

@author: oppochen
'''

import time
import urllib
import logging
import subprocess

class Application(object):
    '''
    classdocs
    '''


    def __init__(self, app_name):
        '''
        Constructor
        '''
        self.__app_name = app_name

    def update(self, package_url):
        cmd = []
        cmd.append(r'.\common\tool\Tools\QQPCMgrUpdater.exe')
        cmd.append('0')
        cmd.append(package_url)
        logging.info('instal qqpcmgr')
        logging.info(cmd)
        subprocess.Popen(cmd).wait()

    def download(self, download_url):
        install_pack_path = r'PCMgr_Setup.exe'
        urllib.urlretrieve(download_url, install_pack_path)
        return install_pack_path

    def install(self, install_pack_path):
        cmd = [install_pack_path, '/S']
        subprocess.Popen(cmd)

    def check_install(self, proc_list):
        cmd = ['tasklist']
        task_list = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout.read()
        for proc_name in proc_list:
            if proc_name.lower() not in task_list.lower():
                logging.info('check install fail')
                return False
        logging.info('check install success')
        return True

    def wait_install(self, proc_list):
        for i in xrange(10):
            if self.check_install(proc_list):
                logging.info('install success, wait 60s for qqpcmgr ready')
                time.sleep(60)
                return True
            else:
                logging.info('%d. wait 60s for install ready' % i)
                time.sleep(60)
        logging.error('install error')
        return False
