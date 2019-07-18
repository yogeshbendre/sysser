# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 09:22:48 2019

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

bootDataJSON = '/var/log/BootData.json'
uiBootDataJSON = '/var/log/vmware/uiBootData.json'
mytextoutputfile = '/var/log/vmware/uiBootData.txt'
mytextoutputfile2 = '/var/log/vmware/uiPluginData.txt'
mydeltaoutputfile = '/var/log/vmware/uiDataDelta.txt'
mydeltaoutputfile2 = '/var/log/vmware/uiPluginDelta.txt'
uiLogFile = '/var/log/vmware/vsphere-ui/logs/vsphere-ui-runtime.log.stdout'


def runCommand(mycmd):
    print("Run Command: "+mycmd)
    try:
        d = str(sp.check_output(mycmd,shell=True))
        d = d.replace("b'","")
        d=d[:-1]
        print(d)    
        return d
    
    except Exception as e:
        print("runCommand failed: "+str(e))
        return None


def processed(uiPID):
    
    try:
        uiBootData = json.load(open(uiBootDataJSON,"r"))
        if "vspher-ui_"+str(uiPID) in uiBootData.keys():
            return(True)
        else:
            return(False)
    except Exception as e:
        print("processed failed: "+str(e)+". But it's ok, may be first run.")
        return(False)


def markProcessed(uiPID):
    uiBootData = {}
    try:
        uiBootData = json.load(open(uiBootDataJSON,"r"))
        
    except Exception as e:
        print("Mark Processed failed: "+str(e)+". But it's ok, may be first run.")
        uiBootData = {}
    
    try:
        uiBootData["vsphere-ui_"+str(uiPID)]="Done"
        json.dump(uiBootData,open(uiBootDataJSON,"w"))
    except Exception as e2:
        print("Mark Processed failed: "+str(e2))



def getuiTimesFromJson():
    
    uiData = json.load(open(bootDataJSON,"r"))
    myuiTimes = []
    myuiData ={}
    for p in uiData.keys():
        try:
#            print("Trying now")

            parts = p.split("_")
#            print(p)

#            print(parts)

            if parts[0]=='vsphere-ui':
                if processed(parts[1]):
                    continue
                print("Unprocessed instance")
                print(p)
                d1 = uiData[p]
                print(d1)
                mytimestamp = d1.split("|")[0].replace('\n','')
                print(mytimestamp)


                myuiTimes.append(int(mytimestamp))
                myuiData[mytimestamp]=d1
        except Exception as e3:
            print("getuiTimesFromJson failed: "+str(e3))
    
    myuiTimes.sort()
    print("Finished getuiTimesFromJson")
    return(myuiTimes,myuiData)
    
    

def parseCompTimes(mycomplogs,hostname,uiPID,uiPIDTime,uiStartTime):
    
    mycsvdata = None
    
    try:
        
        uiPIDTime = dt.strptime(uiPIDTime,"%Y-%m-%d %H:%M:%S.%f")
        uiStartTime = dt.strptime(uiStartTime,"%Y-%m-%d %H:%M:%S.%f")
        
        f = uiPIDTime.timestamp()
        t = uiStartTime.timestamp()
        mprevtimestamp = f
        mprevtime = uiPIDTime
        if(len(mycomplogs[-1])<2):
            mycomplogs = mycomplogs[:-1]
        mylen = len(mycomplogs)
        mnum = 0
        for m in mycomplogs:

            try:
                mnum = mnum + 1 
                #print(m)
                #[2019-07-15T15:59:07.653Z]
                if "[201" not in m:
                    continue
                mtime = m.split(' ')[0].replace("Z","").replace("T"," ").replace("[","").replace("]","")
                mtimestamp = dt.strptime(mtime,"%Y-%m-%d %H:%M:%S.%f").timestamp()
            
                if mtimestamp<f:
                    continue
                print("Log: "+str(m))
                mtimestamp0=""
                mcomp=""
                mtook=""
                mtime1 = ""
                mtime0 = ""
                if "End of configuration" in m:
                    mtimestamp0 = f
                    
                    mcomp = "Configuration" 
                    mtime1 = mtime
                    mtime0 = uiPIDTime
                    mtook = round(mtimestamp - mtimestamp0)
                    
                    mprevtimestamp = mtimestamp
                    mprevtime = mtime1
                    
                elif "Registering current configuration" in m:
                    mtimestamp0 = mprevtimestamp
                    mcomp = "Register Configuration" 
                    mtime1 = mtime
                    mtime0 = mprevtime
                    mtook = round(mtimestamp - mtimestamp0)
                    
                    mprevtimestamp = mtimestamp
                    mprevtime = mtime1
                
                elif "Platform bundles started" in m:
                    if len(mprevtimestamp)>25:
                        mprevtimestamp = mprevtimestamp[:-3]
                    mtimestamp0 = mprevtimestamp
                    mcomp = "Start Platform Bundles" 
                    mtime1 = mtime
                    mtime0 = mprevtime
                    mtook = round(mtimestamp - mtimestamp0)
                    
                    mprevtimestamp = mtimestamp
                    mprevtime = mtime1
                
                elif "Core plugins deployed" in m:
                    mtimestamp0 = mprevtimestamp
                    mcomp = "Deploy Core Plugins" 
                    mtime1 = mtime
                    mtime0 = mprevtime
                    mtook = round(mtimestamp - mtimestamp0)
                    
                    mprevtimestamp = mtimestamp
                    mprevtime = mtime1
                
                elif mnum==mylen:
                    #Last message
                    mtimestamp0 = mprevtimestamp
                    mcomp = "Deploy Other Plugins" 
                    mtime1 = mtime
                    mtime0 = mprevtime
                    mtook = round(mtimestamp - mtimestamp0)
                    
                    mprevtimestamp = mtimestamp
                    mprevtime = mtime1
                else:
                    continue
                
                
                d1 = str(mtimestamp0)+"|"+str(hostname)+"|"+str(mcomp)+"|"+str(uiPID)+"|"+str(mtook)+"|"+str(mtime1)+"|"+str(mtime0)+"\n"
                print(d1)
                if d1 is not None:
                    if mycsvdata is None:
                        mycsvdata=""
                    mycsvdata = mycsvdata+d1
                
            except Exception as e2:
                print("parseCompTimes failed: "+str(e2))
        
        return(mycsvdata)
        
        
    except Exception as e:
        print("parseCompTimes failed: "+str(e))
        return(None)
    

def parsePluginTimes(mycomplogs,hostname,uiPID,uiPIDTime,uiStartTime):
    
    mycsvdata = None
    
    try:
        
        uiPIDTime = dt.strptime(uiPIDTime,"%Y-%m-%d %H:%M:%S.%f")
        uiStartTime = dt.strptime(uiStartTime,"%Y-%m-%d %H:%M:%S.%f")
        
        f = uiPIDTime.timestamp()
        t = uiStartTime.timestamp()
        mprevtimestamp = f
        mprevtime = uiPIDTime
        mprevcomp = ''
        if(len(mycomplogs[-1])<2):
            mycomplogs = mycomplogs[:-1]
        mylen = len(mycomplogs)
        mnum = 0
        totalPluginTime = 0
        firstpluginstartTime = None
        firstpluginstartTimestamp = None
        lastpluginfinishTime = None
        lastpluginfinishTimestamp = None
        for m in mycomplogs:

            try:
                mnum = mnum + 1 
                #print(m)
                #[2019-07-15T15:59:07.653Z]
                if "Type=START" not in m:
                    continue
                mtime = m.split(' ')[0].replace("Z","").replace("T"," ").replace("[","").replace("]","")
                mtimestamp = dt.strptime(mtime,"%Y-%m-%d %H:%M:%S.%f").timestamp()
            
                if mtimestamp<f:
                    continue
                print("Log: "+str(m))
                mtimestamp0=""
                
                mtook=""
                mtime1 = ""
                mtime0 = ""
                mcomp = m.split('Bundle=')[1].split(' ')[0]
                if firstpluginstartTime is None:
                    firstpluginstartTime = mtime
                    firstpluginstartTimestamp = mtimestamp
                if "Type=STARTED" in m and mprevcomp in mcomp:
                    print('Previous data: ')
                    print(mprevcomp)
                    print(mprevtime)
                    print(mprevtimestamp)
                    print('----')
                    mtimestamp0 = mprevtimestamp
                    
                    mtime1 = mtime
                    mtime0 = mprevtime
                    mtook = round(mtimestamp - mtimestamp0)
                    totalPluginTime = totalPluginTime+mtook
                    lastpluginfinishTime = mtime
                    lastpluginfinishTimestamp = mtimestamp
                    
                elif "Type=STARTING" in m:
                    mprevtimestamp = mtimestamp
                    mprevtime = mtime
                    mprevcomp = mcomp
                    continue
                else:
                    continue
                
                
                d1 = str(mtimestamp0)+"|"+str(hostname)+"|"+str(mcomp)+"|"+str(uiPID)+"|"+str(mtook)+"|"+str(mtime1)+"|"+str(mtime0)+"\n"
                print(d1)
                if d1 is not None:
                    if mycsvdata is None:
                        mycsvdata=""
                    mycsvdata = mycsvdata+d1
                
            except Exception as e2:
                print("parsePluginTimes failed: "+str(e2))
        
        #print(mycsvdata)
        if mycsvdata is not None:
            totaltook = round(lastpluginfinishTimestamp-firstpluginstartTimestamp)
            d1 = str(firstpluginstartTimestamp)+"|"+str(hostname)+"|Start All Plugins|"+str(uiPID)+"|"+str(totaltook)+"|"+str(lastpluginfinishTime)+"|"+str(firstpluginstartTime)+"\n"
            mycsvdata=d1+mycsvdata
        
        
        return(mycsvdata)
        
        
    except Exception as e:
        print("parsePluginTimes failed: "+str(e))
        return(None)
    



def getuiComponentTimesFromUiFile(hostname,uiPID,uiPIDTime,uiStartTime):
    csvdata = None
    
    try:
        
        mylogs = ""
        with open(uiLogFile,"r") as fp:
            mylogs = fp.read().split("\n")
        csvdata = parseCompTimes(mylogs,hostname,uiPID,uiPIDTime,uiStartTime)
        mylogs = runCommand('cat '+uiLogFile+' | grep "Type=START"').split('\\n')
        csvdata2 = parsePluginTimes(mylogs,hostname,uiPID,uiPIDTime,uiStartTime)
    
    except Exception as e:
        print("getuiComponentTimesFromUiFile faile: "+str(e))    
    
    return(csvdata,csvdata2)
            
def grepUiComponentTimes(hostname):            
    csvdata = None
    try:
        
        myuiTimes,myuiData = getuiTimesFromJson()
        mycsvdata = ""
        print(myuiTimes)
        
        print(myuiData)
        
        t = myuiTimes[-1]
        uiRestartInstance = myuiData[str(t)]
        print("Processing: "+uiRestartInstance)        
        mytimedata = uiRestartInstance.split('|')
        uiStartTime = mytimedata[-2].replace("\n","")
        uiPIDTime = mytimedata[-1].replace("\n","")
        uiPID = mytimedata[3].replace("\n","")
        print(str(uiPID)+" "+uiPIDTime+" "+uiStartTime)
        uiTook = round(dt.strptime(uiStartTime,"%Y-%m-%d %H:%M:%S.%f").timestamp()-dt.strptime(uiPIDTime,"%Y-%m-%d %H:%M:%S.%f").timestamp())
        print("Received my data")
        csvdata,plugindata = getuiComponentTimesFromUiFile(hostname,uiPID,uiPIDTime,uiStartTime)
        uidt = ""+str(dt.strptime(uiPIDTime,"%Y-%m-%d %H:%M:%S.%f").timestamp())+"|"+str(hostname)+"|vsphere-ui|"+str(uiPID)+"|"+str(uiTook)+"|"+str(uiStartTime)[:-3]+"|"+str(uiPIDTime)[:-3]
        
        print("Received CSV Data")
        if csvdata is not None:
            csvdata = uidt+"\n"+csvdata
            markProcessed(uiPID)
        
        if plugindata is not None:
            plugindata = uidt+"\n"+plugindata
        
        #print(csvdata)    
        
        return(csvdata,plugindata)
            
        

    except Exception as e:
        print("grepuiComponentTimes failed: "+str(e))            
        
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
    parser.add_argument("-f","--folder", type=str,help="Specify output folder. Default: /var/log/vmware")
    parser.add_argument("-d","--deltafile", type=str,help="Specify path for delta file.")
    parser.add_argument("-e","--plugindeltafile", type=str,help="Specify path for plugin delta file.")
    
    args = parser.parse_args()
    
    if args.folder:
        outputFolder = args.folder
        if(outputFolder[-1]!='/'):
            outputFolder=outputFolder+'/'
        mytextoutputfile = outputFolder+'uiBootData.txt'
        mytextoutputfile2 = outputFolder+'uiPluginData.txt'
        #myjsonoutputfile = outputFolder+'BootData.json'
    if args.deltafile:
        #deltaoutputFolder = args.deltafolder
        #if(deltaoutputFolder[-1]!='/'):
#            deltaoutputFolder=deltaoutputFolder+'/'
        mydeltaoutputfile = args.deltafile
        #myjsonoutputfile = outputFolder+'BootData.json'

    if args.plugindeltafile:
        #deltaoutputFolder = args.deltafolder
        #if(deltaoutputFolder[-1]!='/'):
#            deltaoutputFolder=deltaoutputFolder+'/'
        mydeltaoutputfile2 = args.plugindeltafile
        
    if args.vcName:
        vcName = args.vcName
    
    try:
        #pushHeaderAndCreateFile()
        mycsvdata,myplugindata = grepUiComponentTimes(vcName)
        
        
        myheader = 'date|vcName|component|pid|boot_time_in_sec|last_started_at|last_triggered_at\n'
        if mycsvdata is not None:
            RDF.pushToDeltaFile(mydeltaoutputfile,myheader,mycsvdata)
            RDF.pushToFullFile(mytextoutputfile,myheader,mycsvdata)
        
        if myplugindata is not None:
            print(myplugindata)
            RDF.pushToDeltaFile(mydeltaoutputfile2,myheader,myplugindata)
            RDF.pushToFullFile(mytextoutputfile2,myheader,myplugindata)
        
        
    
    except Exception as e:
        print("ui component data collection failed: "+str(e))
        
    
    

