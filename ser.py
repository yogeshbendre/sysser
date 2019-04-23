 # -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 11:03:56 2019

@author: ybendre
"""

import os
import subprocess as sp
from datetime import datetime as dt, timedelta as td


def getServiceStat(sname='vsphere-ui'):

    ## Get the PID
    base_sname = sname
    mycmd = 'vmon-cli --status ' + base_sname  # + ' | grep CurrentRunStateDuration'
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

    
    

    print('Servide '+str(base_sname))
    print('Started: '+str(myStartDate))
    print('Started: '+str(myStartDate2))
    #print('Start Time '+ str(mystartduration))
    print('Service Up Time '+str(myendTime))
    print('Time Taken: '+str((myendTime-myStartDate2).total_seconds()))
    #print('End Time '+ str(myendduration))
    #print('Time Taken: ' + str(myendduration-mystartduration))
    return(base_sname+'|'+str((myendTime-myStartDate2).total_seconds())+'|'+str(myStartDate2))


#getServiceStat('vpxd')
    
def getSystemBootInfo():
    
    myout = str(sp.check_output("who -b",shell=True)).replace("b'","").replace('\\n','').replace("'","").strip()
    print(myout)
    sysbootttime = myout.split("system boot")[1].strip()
    myout = str(sp.check_output("systemd-analyze",shell=True)).replace("b'","").replace('\\n','').replace("'","").strip()
    sysb=myout.split('=')[1].strip()
    myvalue='SYSTEM|'+sysb+'|'+sysbootttime
    print(myout)
    return(myvalue)








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
                    d = str(sp.check_output('tail -n 200 '+rootdir+'/'+s+'/'+f,shell=True))
                    print(d)
                    sname = f.split('_Stats.mon')[0]
                    dpt = d.split(sname+'|')
                    print(dpt)
                    pid1 = dpt[1].split('|')[0]
                    pid2 = dpt[2].split('|')[0]
                    print(pid1)
                    print(pid2)
                    if(pid1==pid2):
                        print('No issue')
                    else:
                        print('PID Change Detected')
                        base_sname = sname.replace('.launcher','').replace('vmware-','')
                        myvalue = getServiceStat(base_sname)
                        fp.write('\n'+myvalue)
                
            except Exception as e:
                print(str(e))
                    


myheader = 'Service|BootTime|LastBootedAt'
try:
    fp = open('/root/Ser/BootData.txt','r')
    fp.close()
except Exception as e8:
    print(str(e8))
    with open('/root/Ser/BootData.txt','w') as fp:
        fp.write(myheader)

    


with open('/root/Ser/BootData.txt','a') as fp:
    #fp.write(myheader)
    myvalue = getSystemBootInfo()
    fp.write('\n'+myvalue)
    checkPIDChangeAndGetInfo(fp)
    
    
    
    #getServiceData()
    




