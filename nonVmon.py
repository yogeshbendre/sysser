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
    



def runMyCmd(cmd):
    d = str(sp.check_output(cmd,shell=True)).replace("b'","").replace("'","")
    return(d)

def getServiceStatNonVmon(sname):
    try:
        d = runMyCmd("pidof "+sname)
        mypid = d.split(" ")[0].replace("\\n","")
        print(mypid)
        print("Service: "+sname)
        pidStartTime = getStartTimeOfPID(mypid)
        getStartTimeOfService(sname)
    except Exception as e:
        print("Failed stat for "+sname + " : "+str(e))

def getStartTimeOfService(sname):
    
    return(getattr(sys.modules[__name__], "getStartTimeOf_%s" % sname)())
    


def getStartTimeOf_vmafdd():
    print("Getting start time of vmafdd")
    mycmd = "cat /var/log/vmware/vmafdd/vmafdd-syslog.log | grep 'Starting VMware afd Servicedone' | tail -n 1"
    d = runMyCmd(mycmd)
    mytimestr = d.split("+")[0]
    myStartDate = dt.strptime(mytimestr, '%Y-%m-%dT%H:%M:%S.%f')
    print(myStartDate)
    
    
getServiceStatNonVmon("vmafdd")