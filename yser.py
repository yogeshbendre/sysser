#!/usr/bin/python3
 # -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 11:03:56 2019

@author: ybendre
"""

import os
import subprocess as sp
from datetime import datetime as dt, timedelta as td
import json

mytextoutputfile = '/var/log/vmware/BootData.txt'
myjsonoutputfile = '/var/log/vmware/BootData.json'


def getServiceList():
    mylist = []
    try:
        mylist = str(sp.check_output('/usr/sbin/vmon-cli --list',shell=True)).replace("b'","").split('\\n')[:-1]
    except Exception as e:
        mylist = []
        print('getServiceList Failed: '+str(e))
    
    return(mylist)
    
    


def getServiceStat(sname='vsphere-ui',pid=0):

    print("#### Processing "+sname+" ####")
    ## Get the PID
    base_sname = sname
    mycmd = ' /usr/sbin/vmon-cli --status ' + base_sname  # + ' | grep CurrentRunStateDuration'
    d = str(sp.check_output(mycmd, shell=True))
    pid = d.split('ProcessId:')[1].split('\\n')[0].strip()
    print('Service: '+sname+'\n'+d)
    
    #base_sname = sname.replace('.launcher','').replace('vmware-','')
    currentTime = dt.now()
    mycmd2 = 'ps -eo pid,etime | grep ' + pid
    d = str(sp.check_output(mycmd2, shell=True))
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
                
    print(sname+" Uptime: "+str(mydays)+" Days "+str(myhours)+" Hrs "+str(myminutes)+" Mins "+str(myseconds)+" Sec")    
    mystartduration = myseconds*1000 + myminutes*60*1000 + myhours*3600*1000+ mydays*24*3600*1000
    print(sname+" Duration: "+str(mydays)+" Days "+str(myhours)+" Hrs "+str(myminutes)+" Mins "+str(myseconds)+" Sec")    
    myStartDate2 = currentTime-td(milliseconds = mystartduration)
    print(sname+" Start Date2: "+str(myStartDate2))
    
    d3 = str(sp.check_output('ps -p '+pid+' -wo pid,lstart',shell=True))
    print("PID State2: "+d3)
    a = d3.split(pid)[1].split('\\n')[0].strip().split()
    b = '-'.join(a[1:])
    myStartDate = dt.strptime(b, '%b-%d-%H:%M:%S-%Y')
    print(sname + " Start Date: "+str(myStartDate))
    
    
    myvmonfiles = os.listdir("/var/log/vmware/vmon/")
    myendTime = None
    for vf in myvmonfiles:
        if 'vmon' not in vf:
            continue
        
        try:
            mycmd = 'cat /var/log/vmware/vmon/'+ vf +' | grep -i "Service STARTED successfully" | grep -i ' + base_sname
            d = str(sp.check_output(mycmd,shell=True))
            print(sname+" vmon info from " +vf+": "+d)
            d = d.replace('b\'','').split('\\n')
            
            for entry in d:
                somedate = dt.strptime(entry.split('|')[0],'%Y-%m-%dT%H:%M:%S.%fz')
                print(sname+" somedate: "+str(somedate))
                if somedate > myStartDate2:
                    if myendTime is None:
                        myendTime = somedate
                    else:
                        if somedate < myendTime:
                            myendTime = somedate
                    print(sname+" End Date Now: "+str(myendTime))
        
        except Exception as e6:
            print(sname+" getServiceStat failed: "+str(e6))

    
    

    print('Service '+str(base_sname))
    print(sname + ' Started: '+str(myStartDate))
    print(sname+' Started2: '+str(myStartDate2))
    #print('Start Time '+ str(mystartduration))
    print(sname+' End Time '+str(myendTime))
    print(sname + ' Time Taken: '+str((myendTime-myStartDate2).total_seconds()))
    #print('End Time '+ str(myendduration))
    #print('Time Taken: ' + str(myendduration-mystartduration))
    myinfo = sname+'|'+str(pid)+'|'+str((myendTime-myStartDate2).total_seconds())+'|'+str(myendTime)+'|'+str(myStartDate2)
    print(sname+" Final Info: "+myinfo)
    return(myinfo,sname+'_'+pid)


#getServiceStat('vpxd')
    
def getSystemBootInfo():
    
    myout = str(sp.check_output("who -b",shell=True)).replace("b'","").replace('\\n','').replace("'","").strip()
    print(myout)
    sysboottime = myout.split("system boot")[1].strip()
    myout = str(sp.check_output("systemd-analyze",shell=True)).replace("b'","").replace('\\n','').replace("'","").strip()
    sysb=myout.split('=')[1].strip().replace('s','')
    myvalue='SYSTEM|0|'+sysb+'|'+sysboottime
    print(myout)
    return(myvalue,'SYSTEM'+'_'+str(sysboottime))







def checkAndPush(fp,myval,mykey):
    myjson = {}
    try:
        myjson = json.load(open(myjsonoutputfile,'r'))
    
    except Exception as e:
        print(str(e))
        myjson = {}
    
    if mykey not in myjson.keys():
        myjson[mykey] = myval
        fp.write(myval)
        json.dump(myjson,open(myjsonoutputfile,'w'))
    
    
    
    
def getServiceBootInfo(fp):
    rootdir = '/var/log/vmware/vapi/monitoring/PROCESS-LEVEL-UTILIZATION'
    myservices = getServiceList()

    for s in myservices:
        try:
            myvalue,mykey = getServiceStat(s)
            checkAndPush(fp,'\n'+myvalue,mykey)
                
        except Exception as e:
            print("getServiceBootInfo failed: "+str(e))
                    


myheader = 'Service|PID|BootTimeInSec|LastBootedAt'
try:
    fp = open(mytextoutputfile,'r')
    fp.close()
except Exception as e8:
    print(str(e8))
    with open(mytextoutputfile,'w') as fp:
        fp.write(myheader)

myjson = {}
try:
    myjson = json.load(open(myjsonoutputfile,'r'))
    
except Exception as e9:
    print(str(e9))
    with open(myjsonoutputfile,'w') as fp:
        myjson = {}
        json.dump(myjson,fp)
        fp.close()
    


with open(mytextoutputfile,'a') as fp:
    #fp.write(myheader)
    
    
    myvalue,mykey = getSystemBootInfo()
    checkAndPush(fp,'\n'+myvalue,mykey)
    getServiceBootInfo(fp)
    
    
    
    #getServiceData()
    




