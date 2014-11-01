# coding: gbk
import os
import _winreg
import win32gui
import win32api
import win32con
import subprocess
import time
from xml.etree import ElementTree
from ctypes import windll
import re
import commands
import sys
import shutil

from common.path_mgmt import PathMgmt
from common.application import Application
from TestResultApi import TestResultApi, TestCase

global isDNA

gLogMode = "-V" # -V -S
gDefaultItemToAdd = "FtSafeTest"
gTitle1 = 't1'
gTitle2 = 't2'
gTitle3 = 't3'
gTitleDNA1 = 'td1'
gTitleDNA2 = 'td2'
gTitleDNA3 = 'td3'
gImagePath = 'image'

currPath = os.path.split(sys.argv[0])[0]
gItemValue = currPath + '\\blackapp.exe'
gItemValue2= currPath + '\\blackapp2.exe'



path_mgmt = PathMgmt()
path_mgmt.change_cur_dir(sys.argv[0])


print "argc:%s" % len(sys.argv);
print "argv:%s" % sys.argv[1:];

task_id = '-1'
center_id = '-1'
verify_serial_no = '-1'
verify_type_name = 'BRautotest'
job_name = '-'
build_num = '-1'
mgr_url = ''
test_job_name = '-'

if len(sys.argv) < 12:
	print 'Usage:%s  -T TaskId -C CenterID -S vsn -J JobName -B BuildNum -U url -L TestJobName' % (os.path.basename(sys.argv[0]))
	sys.exit(-1)
else:
	if sys.argv.count('-T') == 1:
			task_id = sys.argv[sys.argv.index('-T') + 1]
			
	if sys.argv.count('-C') == 1:
			center_id = sys.argv[sys.argv.index('-C') + 1]

	if sys.argv.count('-S') == 1:
			verify_serial_no = sys.argv[sys.argv.index('-S') + 1]

	if sys.argv.count('-J') == 1:
			job_name = sys.argv[sys.argv.index('-J') + 1]

	if sys.argv.count('-B') == 1:
			build_num = sys.argv[sys.argv.index('-B') + 1]

	if sys.argv.count('-U') == 1:
			mgr_url = sys.argv[sys.argv.index('-U') + 1]
			
	if sys.argv.count('-L') == 1:
			test_job_name = sys.argv[sys.argv.index('-L') + 1]    

print "Trunk Name:%s" % job_name;
print "Job Name:%s" % test_job_name;
print "Build ID:%s" % build_num;
print "Packge Url:%s" % mgr_url;

trunk_name = job_name
build_id = build_num
download_url = mgr_url


tapi = TestResultApi(task_id,center_id,verify_serial_no,verify_type_name,job_name,build_num)




listIDsToExclude = ['2']
listIDsWithoutTips = ['2002']


def IsVisibleWnd(hwnd, wndLst):
	if(win32gui.IsWindowVisible(hwnd)):
		wndLst.append(hwnd)

def GetHwndByTitle(title):
	wndLst = []
	win32gui.EnumWindows(IsVisibleWnd, wndLst)
	for hwnd in wndLst:
		wndTitle = win32gui.GetWindowText(hwnd)
		if wndTitle.find(title) != -1:
			return hwnd
	return 0

def CloseWindow(hwnd):
	try:
		(left, top, right, bottom) = win32gui.GetWindowRect(hwnd)
	except:
		print 'GetWindowRect failed'
		return 0
	xx = right - 10
	yy = top + 10
	cmd = 'leftClick.exe %s %s' % (xx, yy)
	print 'left click : cmd = %s' % cmd
	p = subprocess.Popen(cmd)
	p.wait()
	
def CloseWindowDNA(hwnd):
	try:
		(left, top, right, bottom) = win32gui.GetWindowRect(hwnd)
	except:
		print 'GetWindowRect failed'
		return 0
	xx = right - 30
	yy = top + 30
	cmd = 'leftClick.exe %s %s' % (xx, yy)
	print 'left click : cmd = %s' % cmd
	p = subprocess.Popen(cmd)
	p.wait()

def GrabScreenImage(filename):
	width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
	height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
	image_name = '%s.png' % filename
	pic_path = '%s/%s' % (gImagePath, image_name)
	print 'image_name = %s, pic_path = %s' % (image_name, pic_path)
	dll = windll.LoadLibrary('CCommonFunDll.dll')
	dll.CF_CutScreenToFile(0, 0, width, height, pic_path)
	time.sleep(2)

def GrabWindowImage(hwnd, filename):
	print 'grab image'
	try:
		(left, top, right, bottom) = win32gui.GetWindowRect(hwnd)
	except:
		print 'GetWindowRect failed'
		return 
	
	image_name = '%s.png' % filename
	pic_path = '%s/%s' % (gImagePath, image_name)
	print 'image_name = %s, pic_path = %s' % (image_name, pic_path)
	dll = windll.LoadLibrary('CCommonFunDll.dll')
	dll.CF_CutScreenToFile(left, top, right, bottom, pic_path)
	time.sleep(2)

def ExecCmd(cmd):
	p = subprocess.Popen(cmd)
		
def OpenRegPath(regPath, tryCreate = False):
	rootKeys = ["HKEY_CLASSES_ROOT", "HKEY_CURRENT_USER", "HKEY_LOCAL_MACHINE", "HKEY_USERS", "HKEY_CURRENT_CONFIG"]
	pos = -1
	for rootKey in rootKeys:
		pos = regPath.find(rootKey)
		if pos != -1:
			break
			
	if pos != -1:
		if rootKey == "HKEY_CLASSES_ROOT":
			regRoot = _winreg.HKEY_CLASSES_ROOT
		elif rootKey == "HKEY_CURRENT_USER":
			regRoot = _winreg.HKEY_CURRENT_USER
		elif rootKey == "HKEY_LOCAL_MACHINE":
			regRoot = _winreg.HKEY_LOCAL_MACHINE
		elif rootKey == "HKEY_USERS":
			regRoot = _winreg.HKEY_USERS
		elif rootKey == "HKEY_CURRENT_CONFIG":
			regRoot = _winreg.HKEY_CURRENT_CONFIG
		else:
			print "Wrong reg path: ", regPath
			return None
	else:
			print "Wrong reg path: ", regPath
			return None

	subKey = regPath[pos + len(rootKey) + 1:]
	try:
			#key = win32api.RegOpenKey(regRoot, subKey, win32con.KEY_ALL_ACCESS)
			key = _winreg.OpenKey(regRoot, subKey, 0, _winreg.KEY_ALL_ACCESS)
	except:
		if tryCreate == True:
			try:
				key = _winreg.CreateKey(regRoot, subKey)
			except:
				return None
		else:
			return None
	return key

def GetValues(regPath):
	values = []
	key = OpenRegPath(regPath)
	if key == None:
		return values    
	try:
		i = 0
		while True:
			name,value,type = _winreg.EnumValue(key,i)
			values.append((name, value, type))
			i = i + 1
	except WindowsError:
		return values

def GetSubKeys(regPath):
	subKeys = []
	key = OpenRegPath(regPath)
	if key == None:
		return subKeys
	try:
		i = 0
		while True:
			name = _winreg.EnumKey(key,i)
			subKeys.append(name)
			i = i + 1
	except WindowsError:
		return subKeys

def GetSStar():
	subKeys = GetSubKeys('HKEY_USERS')
	sStar = ''
	sStarClass = ''
	for subKey in subKeys:
		if re.match(r"S(-|[0-9])+", subKey):
			sStar = subKey
			break
	for subKey in subKeys:
		if re.match(r"S(-|[0-9])+_Classes", subKey):
			sStarClass = subKey
			break
	#print sStar, sStarClass
	return (sStar, sStarClass)
		
def PreHandleSubject1(subject1):
		
	sStar, sStarClass = GetSStar()
	subject1 = subject1.replace(r'\REGISTRY\MACHINE', 'HKEY_LOCAL_MACHINE')
	subject1 = subject1.replace(r'\REGISTRY\USER', 'HKEY_USERS')
	if subject1.find('HKEY_USERS') != -1:
		subject1 = subject1.replace(r'S-*_CLASSES', sStarClass)
		subject1 = subject1.replace(r'S-*', sStar)
		
	subject1 = subject1.replace('*CONTROLSET*', 'CurrentControlSet')
	subject1 = subject1.replace(r'\*', r'\test')

	subject1 = subject1.replace(r'|*', r'||||')
	subject1 = subject1.replace('*', '')
	subject1 = subject1.replace(r'||||', r'*')
	return subject1

def PreHandleSubject2(subject2):
	subject2 = subject2.replace('*', gDefaultItemToAdd)
	return subject2

def IsKeyExist(regPath):
	key = OpenRegPath(regPath)
	if key == None:
		return False
	else:
		_winreg.CloseKey(key)
		return True

def IsValueExist(regPath, valueName):
	values = GetValues(regPath)
	for value in values:
			print value[0], valueName
			if value[0] == valueName:
				return True
	return False
	
class OneMonitorItemTest:

	def __init__(self, id, type, operation, regPath, itemName, itemValue, driverSupport):
		self.enumRegCreateKey = 0x10
		self.enumRegDeleteKey = 0x20
		self.enumRegCreateValue = 0x40
		self.enumRegModifyValue = 0x80
		self.enumRegDeleteValue = 0x100        
		self.id = id
		self.type = type
		self.operation = operation
		self.regPath = regPath 
		self.itemName = itemName
		self.itemValue = itemValue
		self.driverSupport = driverSupport
		self.currentTestCase = ''
		self.log = ""
		#self.log = ""
		if id in listIDsWithoutTips:
			self.withoutTips = True
		else:
			self.withoutTips = False

	def VerifyTips(self):
		for i in range(1, 5):
			hWnd1 = GetHwndByTitle(gTitle1)
			hWnd2 = GetHwndByTitle(gTitle2)
			hWnd3 = GetHwndByTitle(gTitle3)
			
			hWndDNA1 = GetHwndByTitle(gTitleDNA1)
			hWndDNA2 = GetHwndByTitle(gTitleDNA2)
			hWndDNA3 = GetHwndByTitle(gTitleDNA3)
			
			if hWnd1 != 0 or hWnd2 != 0 or hWnd3 != 0:
				isDNA = 'False'
			else:
				isDNA = 'True'
			
			if isDNA == 'False':
				if hWnd3 != 0:
					hWnd = hWnd3
					gTitle = gTitle3
				elif hWnd1 != 0:
					hWnd = hWnd1
					gTitle = gTitle1
				else:
					hWnd = hWnd2
					gTitle = gTitle2
				if hWnd != 0:
					GrabWindowImage(hWnd, self.id)
					
					for j in range(1, 5):
						CloseWindow(hWnd)
						hWnd = GetHwndByTitle(gTitle)
						if hWnd == 0:
							break
						else:
							time.sleep(1)
					return True
				else:
					GrabScreenImage(self.id)
					time.sleep(1)
			else:
				if hWndDNA3 != 0:
					hWnd = hWndDNA3
					gTitle = gTitleDNA3
				elif hWndDNA1 != 0:
					hWnd = hWndDNA1
					gTitle = gTitleDNA1
				else:
					hWnd = hWndDNA2
					gTitle = gTitleDNA2
				if hWnd != 0:
					GrabWindowImage(hWnd, self.id)
					
					for j in range(1, 5):
						CloseWindowDNA(hWnd)
						hWnd = GetHwndByTitle(gTitle)
						if hWnd == 0:
							break
						else:
							time.sleep(1)
					return True
				else:
					GrabScreenImage(self.id)
					time.sleep(1)			
			
		return False
				
	def ResetLog(self):
		self.log = ""

	def AddLog(self, logStr):
		self.log += logStr
		self.log += "\n"
	
	def RecordResult(self, result):
		if result == 'Pass':
			if (gLogMode == '-V'):
				print self.log
			
		else:
			if (gLogMode != '-S'):
				print self.log
		print self.currentTestCase, ":", result
		if result == 'Pass':
			case = TestCase("XPSP3_REG",self.currentTestCase,tapi)
			case.SetResult(result)
			case.flushResultToDB()
		elif result == 'Fail':
			case = TestCase("XPSP3_REG",self.currentTestCase,tapi)
			case.SetResult(result)
			case.SetLog(self.log)
			case.flushResultToDB()
	
	def RunRegTool(self, operation, regPath, itemName, itemValue = None):
		newToolName = 'regtool_' + time.strftime('%Y%m%d%H%M%S') + r'.exe'
		try:
			shutil.copyfile(r'regtool.exe', newToolName)
			time.sleep(0.5)
		except:
			pass
		
		if itemValue == None:
			cmdLine = newToolName + ' ' + operation + ' "' + regPath + '" "' + itemName + '"'
		else:
			cmdLine = newToolName + ' ' + operation + ' "' + regPath + '" "' + itemName + '" ' + itemValue
		self.AddLog("CmdLine: " + cmdLine)
		ret = ExecCmd(cmdLine)
		time.sleep(1)

	def CreateKeyTest(self):
		self.ResetLog()
		self.currentTestCase = 'CreateKeyTest_' + self.regPath

		pos = self.regPath.rfind('\\')      
		regPath = self.regPath[:pos]
		subKey = self.regPath[pos + 1:]

		key = OpenRegPath(regPath, True)
		if key == None:
			self.AddLog('Cannot create regpath: ' + regPath)
			self.RecordResult('Skip') 
			
			return
		else:
			_winreg.CloseKey(key)
			
		if IsKeyExist(self.regPath):
			self.AddLog(self.regPath + ' is already there')
			self.RecordResult('Skip') 
			return
	
		self.RunRegTool('add', regPath, subKey)

		if self.withoutTips == False:
			if self.VerifyTips() == False:
				self.AddLog("No tips window")
				self.RecordResult('Fail')
				return
			
		if IsKeyExist(self.regPath):
			self.AddLog(self.regPath + ' is created')
			self.RecordResult('Fail')

		else:
			self.RecordResult('Pass')

	def DeleteKeyTest(self):
		self.ResetLog()
		self.currentTestCase = 'DeleteKeyTest_' + self.regPath
		
		pos = self.regPath.rfind('\\')      
		regPath = self.regPath[:pos]
		subKey = self.regPath[pos + 1:]
		
		if not IsKeyExist(self.regPath):
			self.AddLog("The key doesn't exist")
			self.RecordResult('Skip')
			return            

		self.RunRegTool('del', regPath, subKey)
		
		if self.withoutTips == False:
			if self.VerifyTips() == False:
				self.AddLog("No tips window")
				self.RecordResult('Fail')
				return
			
		if not IsKeyExist(self.regPath):
			self.AddLog(self.regPath + ' is deleted')
			self.RecordResult('Fail')
		else:
			self.RecordResult('Pass')

	def CreateValueTest(self):
		self.ResetLog()
		self.currentTestCase = 'CreateValueTest' + self.regPath + '_' +  self.itemName
		values1 = GetValues(self.regPath)
		self.RunRegTool('set', self.regPath, self.itemName, self.itemValue)
		
		if self.withoutTips == False:
			if self.VerifyTips() == False:
				self.AddLog("No tips window")
				self.RecordResult('Fail')
				return
				
		values2 = GetValues(self.regPath)
		if values1 != values2:
			self.AddLog(str(values1) + " vs " + str(values2))
			self.RecordResult('Fail')
		else:
			self.AddLog(str(values1) + " vs " + str(values2))
			self.RecordResult('Pass') 
	
	def ModifyValueTest(self):
		self.ResetLog()
		self.currentTestCase = 'ModifyValueTest' + self.regPath + '_' +  self.itemName
		values1 = GetValues(self.regPath)
		if self.itemName == gDefaultItemToAdd and len(values1) > 0:
			itemName = values1[0][0]
		else:
			itemName = self.itemName
		if self.itemValue == gItemValue:
			self.RunRegTool('set', self.regPath, self.itemName, gItemValue2)  # to avoid the conflict with CreateValueTest
		else:
			self.RunRegTool('set', self.regPath, self.itemName, self.itemValue)
		
		if self.withoutTips == False:
			if self.VerifyTips() == False:
				self.AddLog("No tips window")
				self.RecordResult('Fail')
				return
				
		values2 = GetValues(self.regPath)
		if values1 != values2:
			self.AddLog(str(values1) + " vs " + str(values2))
			self.RecordResult('Fail')
			
		else:
			self.AddLog(str(values1) + " vs " + str(values2))
			self.RecordResult('Pass')

	def DeleteValueTest(self):
		self.ResetLog()
		values1 = GetValues(self.regPath)
		if self.itemName == gDefaultItemToAdd and len(values1) > 0:
			itemName = values1[0][0]
		else:
			itemName = self.itemName

		self.currentTestCase = 'DeleteValueTest' + self.regPath + '_' + itemName
		if not IsValueExist(self.regPath, itemName):
			self.AddLog("The reg value doesn't exist")
			self.RecordResult('Skip')
			return
		
		self.RunRegTool('delvalue', self.regPath, itemName)
		
		if self.withoutTips == False:
			if self.VerifyTips() == False:
				self.AddLog("No tips window")
				self.RecordResult('Fail')
				return
				
		values2 = GetValues(self.regPath)
		if values1 != values2:
			self.AddLog(str(values1) + " vs " + str(values2))
			self.RecordResult('Fail')
			
		else:
			self.AddLog(str(values1) + " vs " + str(values2))
			self.RecordResult('Pass')
	
	def Run(self):
		print "\nCurrently testing:", self.id
		
		
		if self.driverSupport == '2':
			self.AddLog('Skip 64 bit regpath: ' + self.regPath)
			self.RecordResult('Skip')
			
			return

		if self.operation & self.enumRegCreateKey != 0:
			self.CreateKeyTest()

		key = OpenRegPath(self.regPath, True)
		if key == None:
			self.AddLog('Cannot create regpath: ' + self.regPath)
			self.RecordResult('Skip')
			
			return
		else:
			_winreg.CloseKey(key)
				

		if self.operation & self.enumRegCreateValue != 0:
			self.CreateValueTest()
		if self.operation & self.enumRegModifyValue != 0:
			self.ModifyValueTest()
		if self.operation & self.enumRegDeleteValue != 0:
			self.DeleteValueTest()
			
		if self.operation & self.enumRegDeleteKey != 0:
			self.DeleteKeyTest()
		#增加了等待时间，等待窗口被关闭
		time.sleep(5)
		
		try:
			os.system("del regtool_*.exe")
		except:
			pass


				
try:
	app = Application('qqpcmgr')
	#app.update(package_url)
	pack_path = app.download(download_url)
	app.install(pack_path)
	proc_list = ['qqpctray.exe', 'qqpcrtp.exe']
	if not app.wait_install(proc_list):
			print 'qqpcmgr install fail'
			sys.exit(ERR_CODE['ERR_INSTALL'])
	#       except Exception, e:
	#               logging.error(str(e))


	print 'wait for install' 
	#time.sleep(120)
except Exception, e:
			print str(e)
			
		
if not os.path.exists(gImagePath):
	os.mkdir(gImagePath)

fileObject1 = open('hips-policy.xml')
fileObject2 = open('hips-policy2.xml', 'w')
for line in fileObject1:
	if line.find(r"<monitor-item") != -1 or line.find(r"hips-config") != -1:
		fileObject2.write(line)
fileObject1.close()
fileObject2.close()


root = ElementTree.parse('hips-policy2.xml')
lstMonitorItems = root.getiterator('monitor-item')
for monitorItem in lstMonitorItems:
	id = monitorItem.attrib['id']
	type = monitorItem.attrib['type']
	operation = int(monitorItem.attrib['operation'])
	regPath = PreHandleSubject1(monitorItem.attrib['subject1'])
	itemName = PreHandleSubject2(monitorItem.attrib['subject2'])
	itemValue = gItemValue
	if type == '2' and (not id in listIDsToExclude):
		try:
				driverSupport = monitorItem.attrib['DriverSupport']
		except:
				print id, "has no driver support"
				driverSupport = '1'
		oneMonitorItem = OneMonitorItemTest(id, type, operation, regPath, itemName, itemValue, driverSupport)           
		oneMonitorItem.Run()

