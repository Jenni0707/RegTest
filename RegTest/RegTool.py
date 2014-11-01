#coding=utf-8
import sys
#import win32api
#import win32con
import _winreg

def PrintUsage():
    print """Usage:
    RegTest.exe add/del itemPath itemName
    RegTest.exe set itemPath itemName itemValue
    """

def OpenRegPath(regPath):
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
        return None
    return key
   

if len(sys.argv) < 4:
    PrintUsage()
else:
    cmd = sys.argv[1]
    itemPath = sys.argv[2]
    itemName = sys.argv[3]
    if len(sys.argv) > 4:
        itemValue = sys.argv[4]
    else:
        itemValue = ""

    key = OpenRegPath(itemPath)
    if key != None:
        if cmd == "add":
            #win32api.RegCreateKey(key, itemName)
            _winreg.CreateKey(key, itemName)
        elif cmd == "del":
            #win32api.RegDeleteKey(key, itemName)
            _winreg.DeleteKey(key, itemName)
        elif cmd == "delvalue":
            _winreg.DeleteValue(key, itemName)
        elif cmd == "set":
            _winreg.SetValueEx(key, itemName, 0, _winreg.REG_SZ, itemValue)
            #win32api.RegSetValueEx(key, itemName, 0, win32con.REG_SZ, itemValue)
        else:
            PrintUsage()
            
        #win32api.RegCloseKey(key)
        _winreg.CloseKey(key)

    else:
        print "Fail to open reg: ", itemPath
    
            







