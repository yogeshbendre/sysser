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

def getServiceStat(sname='vsphere-ui',pid=0):

    ## Get the PID
    base_sname = sname
    mycmd = ' /usr/sbin/vmon-cli --status ' + base_sname  # + ' | grep CurrentRunStateDuration'
    d = str(sp.check_output(mycmd, shell=True))
    pid = d.split('ProcessId:')[1].split('\\n')[0].strip()

    #base_sname = sname.replace('.launcher','').replace('vmware-','')
    currentTime = dt.now()
    mycmd2 = 'ps -eo pid,etime | grep ' + pid

    d2 = str(sp.check_output(mycmd2, shell=True))
    print(d2)
    d = d2
    mytime = d.split(pid)[1].split('\\n')[0].strip()
    mydays = 0
    myhours = 0
    myminutes = 0
    myseconds = 0
    try:
        if "-" in mytime:
            mydays = int(mytime.split('-')[0])
            mytime = mytime.split('-')[1].split(':')
            
        else:
            mytime = mytime.split(':')
        
        if len(mytime)>2:
            myhours = int(mytime[0])
        if len(mytime)>1:
            myminutes = int(mytime[1])
        if len(mytime)>0:
            myseconds = int(mytime[2])
    except Exception as e5:
        print(str(e5))
                
        
    mystartduration = myseconds*1000 + myminutes*60*1000 + myhours*3600*1000+ mydays*24*3600*1000

    d3 = str(sp.check_output('ps -p '+pid+' -wo pid,lstart',shell=True))
    a = d3.split(pid)[1].split('\\n')[0].strip().split()
    b = '-'.join(a[1:])
    myStartDate = dt.strptime(b, '%b-%d-%H:%M:%S-%Y')
    myStartDate2 = currentTime-td(milliseconds = mystartduration)
    
    
    myvmonfiles = os.listdir("/var/log/vmware/vmon/")
    myendTime = None
    for vf in myvmonfiles:
        if 'vmon' not in vf:
            continue
        
        try:
            mycmd = 'cat /var/log/vmware/vmon/'+ vf +' | grep -i "Service STARTED successfully" | grep -i ' + base_sname
            d = str(sp.check_output(mycmd,shell=True))
            print(d)
            d = d.replace('b\'','').split('\\n')
            
            for entry in d:
                somedate = dt.strptime(entry.split('|')[0],'%Y-%m-%dT%H:%M:%S.%fz')
                if somedate > myStartDate2:
                    if myendTime is None:
                        myendTime = somedate
                    else:
                        if somedate < myendTime:
                            myendTime = somedate
        
        except Exception as e6:
            print(str(e6))

    
    

    print('Service '+str(base_sname))
    print('Started: '+str(myStartDate))
    print('Started: '+str(myStartDate2))
    #print('Start Time '+ str(mystartduration))
    print('Service Up Time '+str(myendTime))
    print('Time Taken: '+str((myendTime-myStartDate2).total_seconds()))
    #print('End Time '+ str(myendduration))
    #print('Time Taken: ' + str(myendduration-mystartduration))
    return(base_sname+'|'+str(pid)+'|'+str((myendTime-myStartDate2).total_seconds())+'|'+str(myendTime)+'|'+str(myStartDate2),base_sname+'_'+pid)


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
    
    
    
    
def checkPIDChangeAndGetInfo(fp):
    rootdir = '/var/log/vmware/vapi/monitoring/PROCESS-LEVEL-UTILIZATION'
    myservices = os.listdir(rootdir)

    for s in myservices:
        myfiles = os.listdir(rootdir+'/'+s)
        #print(myfiles)
        for f in myfiles:
            try:
                if '_Stats.mon' in f:
                    print(f)
                    d = str(sp.check_output('tail -n 6 '+rootdir+'/'+s+'/'+f,shell=True))
                    print(d)
                    sname = f.split('_Stats.mon')[0]
                    dpt = d.split(sname+'|')
                    print(dpt)
                    pid1 = dpt[1].split('|')[0]
                    pid2 = dpt[-2].split('|')[0]
                    print(pid1)
                    print(pid2)
                    if(pid1==pid2):
                        print('No issue')
                    #else:
                    if True:
                        print('PID Change Detected')
                        base_sname = sname.replace('.launcher','').replace('vmware-','')
                        myvalue,mykey = getServiceStat(base_sname,pid2)
                        checkAndPush(fp,'\n'+myvalue,mykey)
                
            except Exception as e:
                print(str(e))
                    


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
    checkPIDChangeAndGetInfo(fp)
    
    
    
    #getServiceData()
    




