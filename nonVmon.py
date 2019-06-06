# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 11:12:03 2019

@author: ybendre
"""

import subprocess as sp
from datetime import datetime as dt, timedelta as td
import json
import socket
import argparse
import sys


def runMyCmd(cmd):
    print("Running Cmd "+cmd)
    d = str(sp.check_output(cmd,shell=True)).replace("b'","").replace("'","")
    print(d)
    return(d)


def getStartTimeOfPID(pid):
    
    currentTime = dt.now()
    mycmd2 = 'ps -eo pid,etime | grep ' + pid
    d = runMyCmd(mycmd2)
    print("Current Time: "+str(currentTime))
    print("PID State: "+d)
    
    mytime = d.split(pid)[1].split('\\n')[0].strip()
    print("mytime: "+str(mytime))
    mydays = 0
    myhours = 0
    myminutes = 0
    myseconds = 0
    #'24250       20:47\n'
    try:
        if "-" in mytime:
            mydays = int(mytime.split('-')[0])
            print("mydays: "+str(mydays))
            mytime = mytime.split('-')[1].split(':')
            
        else:
            mytime = mytime.split(':')
            
        print("mytime split: "+str(mytime))
        
        try:
            myseconds = int(mytime[-1])
            myminutes = int(mytime[-2])
            myhours = int(mytime[-3])
        
        except Exception as e10:
            print('getServiceStat failed during time (expected): '+str(e10))
        
        
    except Exception as e5:
        print("getServiceStat Failed: "+str(e5) + " for "+sname)
                
    #print(sname+" Uptime: "+str(mydays)+" Days "+str(myhours)+" Hrs "+str(myminutes)+" Mins "+str(myseconds)+" Sec")    
    mystartduration = myseconds*1000 + myminutes*60*1000 + myhours*3600*1000+ mydays*24*3600*1000
    #print(sname+" Duration: "+str(mydays)+" Days "+str(myhours)+" Hrs "+str(myminutes)+" Mins "+str(myseconds)+" Sec")    
    myStartDate2 = currentTime-td(milliseconds = mystartduration)
    return(myStartDate2)
    #print(sname+" Start Date2: "+str(myStartDate2))
    




def getServiceStatNonVmon(sname):
    try:
        d = runMyCmd("pidof "+sname)
        mypid = d.split(" ")[0].replace("\\n","")
        print(mypid)
        print("Service: "+sname)
        pidStartTime = getStartTimeOfPID(mypid)
        print("Got pidStartTime: "+str(pidStartTime))
        serviceStartTime = getStartTimeOfService(sname)
        print("Got serviceStartTime : "+str(serviceStartTime))
        mydateepoch = pidStartTime.strftime("%s")
        vcName = "vcname"
        myinfo = mydateepoch+'|'+vcName+'|'+sname+'|'+str(mypid)+'|'+str((serviceStartTime-pidStartTime).total_seconds())+'|'+str(serviceStartTime)+'|'+str(pidStartTime)
        print(sname+" Final Info: "+myinfo)
        return(myinfo,sname+'_'+mypid)
    
    except Exception as e:
        print("Failed stat for "+sname + " : "+str(e))

def getStartTimeOfService(sname):
    sname = sname.replace("vmware-","")
    myf = getattr(sys.modules[__name__], "getStartTimeOf_%s" % sname)
    myStartTime=myf()
    print("Recieved start time : "+str(myStartTime))
    return(myStartTime)
    


def getStartTimeOf_vmafdd():
    print("Getting start time of vmafdd")
    mycmd = "cat /var/log/vmware/vmafdd/vmafdd-syslog.log | grep 'Starting VMware afd Servicedone' | tail -n 1"
    d = runMyCmd(mycmd)
    mytimestr = d.split("+")[0]
    myStartDate = dt.strptime(mytimestr, '%Y-%m-%dT%H:%M:%S.%f')
    print(myStartDate)
    return(myStartDate)
    

def getStartTimeOf_vmcad():
    print("Getting start time of vmcad")
    mycmd = "cat /var/log/vmware/vmcad/vmcad-syslog.log | grep 'Starting VMware Certificate Servicedone' | tail -n 1"
    d = runMyCmd(mycmd)
    mytimestr = d.split("+")[0]
    myStartDate = dt.strptime(mytimestr, '%Y-%m-%dT%H:%M:%S.%f')
    print(myStartDate)
    return(myStartDate)


def getStartTimeOf_vmdird():
    print("Getting start time of vmdird")
    mycmd = "cat /var/log/vmware/vmdird/vmdird-syslog.log | grep 'Starting VMware Directory Servicedone' | tail -n 1"
    d = runMyCmd(mycmd)
    mytimestr = d.split("+")[0]
    myStartDate = dt.strptime(mytimestr, '%Y-%m-%dT%H:%M:%S.%f')
    print(myStartDate)
    return(myStartDate)


def getStartTimeOf_pod():
    print("Getting start time of pod")
    mycmd = "cat /var/log/vmware/pod/pod-startup.log | grep 'Starting Pod' | tail -n 1"
    d = runMyCmd(mycmd)
    mytimestr = d.split("]")[0].split("[")[1]
    myStartDate = dt.strptime(mytimestr, '%a %b %d %H:%M:%S %Z %Y')
    print(myStartDate)
    return(myStartDate)
    

def getStartTimeOf_vmon():
    print("Getting start time of vmon")
    mycmd = "cat /var/log/vmware/vmon/vmon.log | grep -i 'Starting vmon' | tail -n 1"
    d = runMyCmd(mycmd)
    mytimestr = d.split("z|")[1]
    myStartDate = dt.strptime(mytimestr, '%Y-%m-%dT%H:%M:%S.%f')
    print(myStartDate)
    return(myStartDate)

def getStartTimeOf_lwsmd():
    return(None)
    
def getStartTimeForNonVmon():
    
    nonVmonServices = ["vmon","vmdird","vmcad","vmafdd","vmware-pod","lwsmd"]
    
    for sname in nonVmonServices:
        try:
            print("Check Service: "+sname)
            getServiceStatNonVmon(sname)
        except Exception as e:
            print("Failed Service "+sname+" : "+str(e))

getStartTimeForNonVmon()