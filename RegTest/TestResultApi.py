#coding=utf-8
'''
Created on 2013-10-24

@author: jeremychang
'''
import time
import codecs
from cidcr import *


DB_ID = 258
HOST = "183.60.52.111"
PORT = 6380
db_proxy = idcr_db_proxy(DB_ID, HOST, PORT)

def ExecuteSQL(sql_str):
    print sql_str
    if db_proxy.query(sql_str, 1):
        return db_proxy.get_all_list()
    else:
        print db_proxy.get_last_error()
        print "database query fail"

def SetStr2Utf8(str):
    print "jer_hack", type(str),type(str).__name__,str

    if isinstance(str, unicode): 
        str = str.encode('utf-8')
    else:
        str = str.decode('gbk').encode('utf-8')
    
    print type(str),type(str).__name__,str
    return str

class TestResultApi(object):
    '''
    classdocs
    '''

    
    def __init__(self, taskId, centerId, verifySerialNo, verifyTypeName, jobName, buildNo, version = None, taskName = None):
        '''
        @ Desc : 测试结果上报接口构造函数
        @ Name : 测试结果上报接口构造函数
        @ Author : jeremychang
        @ Date : 20131024
        @ INPUT :
            [IN1]taskId:测试任务id(必填)
            [IN2]centerId:中心id(必填)
            [IN3]verifySerialNo:检查水号(必填)
            [IN4]verifyTypeName:检查项名称(必填)
            [IN5]jobName:打包job名(必填)
            [IN6]buildNo:构建id(必填)
            [IN7]version:被测对象版本号(选填)
            [IN8]taskName:测试任务名(选填)
        @ OUTPUT :
        @ Demo : TestResultApi(1, 18, 1, '接口测试', 'CEN_BlueRay_Build_Trunk', 327, '蓝光构建')
        @ Modify :
        @ Remark :
        '''
        
        if taskName == None:
            taskName = 'No Name'
        
        sql = "select id from t03_task_propreties where job_name = '%s' and build_no = %s"%(SetStr2Utf8(jobName), buildNo)

        l_id = ExecuteSQL(sql)
        print l_id
        
        if len(l_id) == 0 and version != None:
            sql = "insert into t03_task_propreties \
            (task_id, task_name, center_id, job_name, build_no, version) \
            values (%s, '%s', %s, '%s', %s, '%s')"%(taskId, SetStr2Utf8(taskName), centerId, SetStr2Utf8(jobName), buildNo, SetStr2Utf8(version))
            ExecuteSQL(sql)
            
            sql = "select id from t03_task_propreties where job_name = '%s' and build_no = %s"%(SetStr2Utf8(jobName), buildNo)

            l_id = ExecuteSQL(sql)
        
        elif len(l_id) == 0 and version == None:
            sql = "insert into t03_task_propreties \
            (task_id, task_name, center_id, job_name, build_no) \
            values (%s, '%s', %s, '%s', %s)"%(taskId, SetStr2Utf8(taskName), centerId, SetStr2Utf8(jobName), buildNo)
            ExecuteSQL(sql)
            
            sql = "select id from t03_task_propreties where job_name = '%s' and build_no = %s"%(SetStr2Utf8(jobName), buildNo)

            l_id = ExecuteSQL(sql)

        elif len(l_id) != 0 and version != None:
            
            sql = "update t03_task_propreties set version = '%s' where id = %s"%(SetStr2Utf8(version), l_id[0][0])
            
            ExecuteSQL(sql)
        
        begin_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        
        sql = "select id from t04_verify_type_status  \
        where task_id = %s and verify_serial_no = %s and verify_type_name = '%s'"%(taskId, verifySerialNo, SetStr2Utf8(verifyTypeName))
        
        l_vid = ExecuteSQL(sql)
        
        if len(l_vid) == 0:
            sql = "insert into t04_verify_type_status  \
            (task_id, verify_serial_no, verify_type_name, verified_num, status, begin_time)  \
            values (%s, %s, '%s', 0, 'running', now())"%(taskId, verifySerialNo, SetStr2Utf8(verifyTypeName))
            ExecuteSQL(sql)
            
            sql = "select id from t04_verify_type_status  \
            where task_id = %s and verify_serial_no = %s and verify_type_name = '%s'"%(taskId, verifySerialNo, SetStr2Utf8(verifyTypeName))

            l_vid = ExecuteSQL(sql)
          
        self.verify_id = l_vid[0][0]
        self.taskId = taskId
        self.taskName = SetStr2Utf8(taskName)
        self.centerId = centerId
        self.verifySerialNo = verifySerialNo
        self.verifyTypeName = SetStr2Utf8(verifyTypeName)
        self.jobName = SetStr2Utf8(jobName)
        self.buildNo = buildNo
        self.version = version
        
        return
    
    def SetTestStatus(self, status):
        '''
        @ Desc : 测试任务执行状态更新函数
        @ Name : 测试任务执行状态更新函数
        @ Author : jeremychang
        @ Date : 20131024
        @ INPUT :
            [IN1]status:验证项的执行状态，包括如下类型：
                'init','running','finished','error','exception'
        @ OUTPUT :
        @ Demo : SetTestStatus('running')
        @ Modify :
        @ Remark :
        '''
        sql = "update t04_verify_type_status set status = '%s', end_time = now() where id = %s"%(status, self.verify_id)
        
        ExecuteSQL(sql)
         
        return

    def SetTestURL(self, ResultURL):
        '''
        @ Desc : 测试结果链接更新函数
        @ Name : 测试结果链接更新函数
        @ Author : jeremychang
        @ Date : 20131024
        @ INPUT :
            [IN1]ResultURL:测试结果链接
        @ OUTPUT :
        @ Demo : SetTestURL(ResultURL)
        @ Modify :
        @ Remark :
        '''
        end_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        
        sql = "update t04_verify_type_status set system_url = '%s', end_time = '%s' where id = %s"%(ResultURL, end_time, self.verify_id)
        
        ExecuteSQL(sql)
         
        return


class TestCase(object):
    '''
    classdocs
    '''


    def __init__(self, moduleName, itemName, task):
        '''
        @ Desc : 测试结果上报接口构造函数
        @ Name : 测试结果上报接口构造函数
        @ Author : jeremychang
        @ Date : 20131024
        @ INPUT :
            [IN1]moduleName:用例所属模块名
            [IN2]itemName:用例名称
            [IN3]task:任务对象
        @ OUTPUT :
        @ Demo : TestCase('木马查杀', '接口测试', tapi)
        @ Modify :
        @ Remark :
        '''
        
        self.verify_id = task.verify_id
        self.taskId = task.taskId
        self.verifySerialNo = task.verifySerialNo
        self.verifyTypeName = task.verifyTypeName
        self.verify_module_name = SetStr2Utf8(moduleName)
        self.verify_item_name = SetStr2Utf8(itemName)
        self.verify_begin_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        self.verify_end_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        self.expectation = None
        self.actuality = None
        self.Result = None
        self.Log = None
        self.LogURL = None
        
    def SetBeginTime(self,begin_time = None):
        '''
        @ Desc : 设置用例执行开始时间
        @ Name : 设置用例执行开始时间
        @ Author : jeremychang
        @ Date : 20131024
        @ INPUT :
            [IN1]begin_time:开始时间戳(选填),格式为：'%Y-%m-%d %H:%M:%S'
        @ OUTPUT :
        @ Demo : SetBeginTime()
        @ Modify :
        @ Remark :
        '''
        
        self.verify_begin_time = begin_time

    
    def SetEndTime(self, end_time = None):
        '''
        @ Desc : 设置用例执行结束时间
        @ Name : 设置用例执行结束时间
        @ Author : jeremychang
        @ Date : 20131024
        @ INPUT :
            [IN1]end_time:结束时间戳(选填)，格式为：'%Y-%m-%d %H:%M:%S'
        @ OUTPUT :
        @ Demo : SetEndTime()
        @ Modify :
        @ Remark :
        '''
        if end_time == None:
            end_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        self.verify_end_time = end_time
        
    def SetResult(self, Result, Exp = None, Real = None):
        '''
        @ Desc : 设置用例执行结果
        @ Name : 设置用例执行结果
        @ Author : jeremychang
        @ Date : 20131024
        @ INPUT :
            [IN1]Result:测试结果(必填)
            [IN2]Exp:预期值(选填)
            [IN3]Real:实测值(选填)
        @ OUTPUT :
        @ Demo : SetResult('pass', '12', '11')
        @ Modify :
        @ Remark :
        '''       
        self.expectation = Exp
        self.actuality = Real
        self.Result = Result
        
    def SetLog(self, Log = None, LogURL = None):
        '''
        @ Desc : 设置用例执行情况及运行日志
        @ Name : 设置用例执行情况及运行日志
        @ Author : jeremychang
        @ Date : 20131024
        @ INPUT :
            [IN1]Log:执行日志内容(必填)
            [IN2]LogURL:服务器上日志文件的链接地址(选填)
        @ OUTPUT :
        @ Demo : SetLog(Log, LogURL)
        @ Modify :
        @ Remark :
        '''       
        self.Log = SetStr2Utf8(Log)
        self.LogURL = LogURL
        
    def flushResultToDB(self): 
        '''
        @ Desc : 用例结果入DB
        @ Name : 用例结果入DB
        @ Author : jeremychang
        @ Date : 20131024
        @ INPUT :
        @ OUTPUT :
        @ Demo : flushResultToDB()
        @ Modify :
        @ Remark :
        '''        
        sql = "insert into t05_verify_result \
        (task_id, verify_serial_no, verify_type_name, verify_module_name, \
        verify_item_name, expectation, actuality, result, verify_begin_time, \
        verify_end_time, verify_log, verify_log_url) values (%s, %s, '%s', '%s',\
         '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')\
        "%(self.taskId, self.verifySerialNo, self.verifyTypeName, self.verify_module_name,  
            self.verify_item_name, self.expectation, self.actuality, self.Result, 
            self.verify_begin_time, self.verify_end_time, self.Log, self.LogURL)
        ExecuteSQL(sql)
        
        sql = "select verified_num from t04_verify_type_status where id = %s"%self.verify_id
        l_vnum = ExecuteSQL(sql)
        
        str_vnum = l_vnum[0][0]
        vnum = int(str_vnum) + 1
        
        sql = "update t04_verify_type_status set verified_num = %s where id = %s"%(vnum, self.verify_id)
        ExecuteSQL(sql)
        
