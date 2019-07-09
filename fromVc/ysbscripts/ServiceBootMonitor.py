# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 12:57:22 2019

@author: ybendre
"""

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
import socket
import argparse
import sys
import RCADataFilesUtility as RDF


mytextoutputfile = 'BootData.txt'
myjsonoutputfile = '/var/log/vmware/BootData.json'
vcName = "localhost"
outputFolder = "/var/log/vmware/"
deltaoutputfile = '/var/log/vmware/BootDataDelta.txt'



######## Non VMON Services ##########


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
        #vcName = "vcname"
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
    
def getStartTimeForNonVmon(fp):
    
    nonVmonServices = ["vmon","vmdird","vmcad","vmafdd","vmware-pod","lwsmd"]
    mycsvdata = ""
    for sname in nonVmonServices:
        try:
            print("Check Service: "+sname)
            myvalue,mykey = getServiceStatNonVmon(sname)
            if checkIfDoneBefore(mykey):
                print(""+mykey+": Already done before")
                continue
            
            checkAndPush(fp,'\n'+myvalue,mykey)
            mycsvdata=mycsvdata + myvalue + '\n'
        except Exception as e:
            print("getStartTimeForNonVmon Failed Service "+sname+" : "+str(e))
    return(mycsvdata)





############ VMON Services ###############
def runCommand(cmd):
    print("Running command "+cmd)
    mycmd = 'export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/java/jre-vmware/bin:/opt/vmware/bin"'
    mycmd = mycmd + '\n' + cmd + ' > '+outputFolder+'myout.txt 2> ' + outputFolder+'myout.txt\n'
    with open(outputFolder+'myscript.sh','w') as fp:
        fp.write(mycmd)

    sp.check_output('chmod 777 '+outputFolder+'myscript.sh',shell=True)
    sp.check_output('/bin/bash '+outputFolder+'myscript.sh',shell=True)
    myout = ''
    with open(outputFolder+'myout.txt','r') as fp:
        myout = fp.read()
    print(myout)
    return(myout)

def getServiceList():
    mylist = []
    try:
        mylist = str(sp.check_output('/usr/sbin/vmon-cli --list',shell=True)).replace("b'","").split('\\n')[:-1]
        print("Getting Service ist")
        #mylist = str(runCommand('/usr/sbin/vmon-cli --list')).split('\n')[:-1]
    except Exception as e:
        mylist = []
        print('getServiceList Failed: '+str(e))
    
    print(mylist)
    return(mylist)
    
    


def getPIDVmonService(serviceName):
    try:
        mycmd = ' /usr/sbin/vmon-cli --status ' + serviceName
        d=str(sp.check_output(mycmd, shell=True))
        pid = d.split('ProcessId:')[1].split('\\n')[0].strip()
        print('Service: '+serviceName+'\n'+d)
        return pid
    except Exception as e:
        print('getPIDVmonService failed: '+str(e))
        return None
    

def getServiceStat(sname='vsphere-ui',pid=0):

    print("#### Processing "+sname+" ####")
    ## Get the PID
    base_sname = sname
    mycmd = ' /usr/sbin/vmon-cli --status ' + base_sname  # + ' | grep CurrentRunStateDuration'
    #d = str(runCommand(mycmd))
    d=str(sp.check_output(mycmd, shell=True))
    
    
    
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
    mydateepoch = myStartDate2.strftime("%s")
    myinfo = mydateepoch+'|'+vcName+'|'+sname+'|'+str(pid)+'|'+str((myendTime-myStartDate2).total_seconds())+'|'+str(myendTime)+'|'+str(myStartDate2)
    print(sname+" Final Info: "+myinfo)
    return(myinfo,sname+'_'+pid)


#getServiceStat('vpxd')
    
def getSystemBootInfo():
    
    myout = str(sp.check_output("who -b",shell=True)).replace("b'","").replace('\\n','').replace("'","").strip()
    print(myout)
    sysboottime = myout.split("system boot")[1].strip()
    mysysboottime = dt.strptime(sysboottime,"%Y-%m-%d %H:%M")
    myout = str(sp.check_output("systemd-analyze",shell=True)).replace("b'","").replace('\\n','').replace("'","").strip()
    sysb=myout.split('=')[1].strip().replace('s','')
    myvalue=mysysboottime.strftime("%s")+'|'+vcName+'|system|0|'+sysb+'|'+str(mysysboottime)+'|'+str(mysysboottime)
    print(myout)
    return(myvalue,'system'+'_'+str(sysboottime))







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
    
def checkIfDoneBefore(mykey):
    myjson = {}
    try:
        myjson = json.load(open(myjsonoutputfile,'r'))
        if mykey in myjson.keys():
            print(""+str(mykey)+" : Already done before")
            return True
    
    except Exception as e:
        print(str(e))
        myjson = {}
        return False
    
    
    
    
    
def getServiceBootInfo(fp):
    
    myservices = getServiceList()
    mycsvdata = ""
    for s in myservices:
        try:
            mypid = getPIDVmonService(s)
            if mypid is None:
                continue
            
            if checkIfDoneBefore(s+'_'+mypid):
                continue
            
            myvalue,mykey = getServiceStat(s)
            checkAndPush(fp,'\n'+myvalue,mykey)
            mycsvdata = mycsvdata + myvalue + '\n'
                
        except Exception as e:
            print("getServiceBootInfo failed: "+str(e))
            
    return(mycsvdata)









if __name__ == "__main__":

    vcName = "localhost"
    outputFolder = "/var/log/vmware/"
    helpstring = "Options: -v <vcname> -f <output folder path>"
    opts = None
    args = None
    
    try:
        vcName = socket.gethostname()
    except Exception as e0:
        print(str(e0))
    
    
    
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-v", "--vcName", help="Specify vCenter Name. Default: system hostname",type=str)
    parser.add_argument("-f","--folder", type=str,help="Specify output folder. Default: current directory")
    parser.add_argument("-d","--deltafile", type=str,help="Specify output folder. Default: current directory")
    args = parser.parse_args()
    
    
    if args.deltafile:
        deltaoutputfile = args.deltafile
    
    if args.folder:
        outputFolder = args.folder
        if(outputFolder[-1]!='/'):
            outputFolder=outputFolder+'/'
        mytextoutputfile = outputFolder+'BootData.txt'
        #myjsonoutputfile = outputFolder+'BootData.json'

        
    if args.vcName:
        vcName = args.vcName
    
    myheader = 'date|vcName|service|pid|boot_time_in_sec|last_started_at|last_triggered_at'
    print('Arguments: ')
    print('f '+outputFolder)
    print('v '+vcName)
    try:
        fp = open(mytextoutputfile,'r')
        fp.close()
        print('File exists  '+mytextoutputfile)
    except Exception as e8:
        print(str(e8))
        with open(mytextoutputfile,'w') as fp:
            fp.write(myheader)
    
    myjson = {}
    try:
        myjson = json.load(open(myjsonoutputfile,'r'))
        print('File exists  '+myjsonoutputfile)
        
    except Exception as e9:
        print(str(e9))
        with open(myjsonoutputfile,'w') as fp:
            myjson = {}
            json.dump(myjson,fp)
            fp.close()
        
    
    
    with open(mytextoutputfile,'a') as fp:
        #fp.write(myheader)
        
        myfullcsv = ''
        myvalue,mykey = getSystemBootInfo()
        if not checkIfDoneBefore(mykey):
            checkAndPush(fp,'\n'+myvalue,mykey)
            myfullcsv = myvalue+'\n'
        
        mycsvdata1 = getStartTimeForNonVmon(fp)
        mycsvdata2 = getServiceBootInfo(fp)
        myfullcsv = myfullcsv+mycsvdata1+mycsvdata2
        
        RDF.pushToDeltaFile(deltaoutputfile,myheader,myfullcsv)
        
        

