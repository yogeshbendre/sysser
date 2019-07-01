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


from LIUtils import LIUtils

bootDataJSON = '/var/log/BootData.json'
vpxdBootDataJSON = '/var/log/vpxdBootData.json'
mytextoutputfile = '/var/log/vpxdBootData.txt'
vpxdLogFile = '/var/log/vmware/vpxd/vpxd.log'


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


def isLIAttached():
    return False
    li = LIUtils()
    if(li.getLogInsightIp() is not None):
        return True
    else:
        return False


def getVpxdComponentTimes(vpxdPIDTime, vpxdStartTime):
    
    try:
        li = LIUtils()
        myquery = 'hostname/CONTAINS '+socket.gethostname()+'/filepath/CONTAINS vpxd*/text/CONTAINS took*'
        vpxdPIDTime = dt.strptime(vpxdPIDTime,"%Y-%m-%d %H:%M:%S.%f")-td(minutes=10)
        vpxdStartTime = dt.strptime(vpxdStartTime,"%Y-%m-%d %H:%M:%S.%f") + td(minutes=10)
        f = int(vpxdPIDTime.timestamp())*1000
        t = int(vpxdStartTime.timestamp())*1000
        
        # Query with 10 minutes buffer on each side
        a=li.getQueryResults(query=myquery,fromTimestamp=str(f),toTimestamp=str(t))
        
        #Reset to original times
        vpxdPIDTime = vpxdPIDTime+td(minutes=10)
        vpxdStartTime = vpxdStartTime - td(minutes=10)
        f = int(vpxdPIDTime.timestamp())*1000
        t = int(vpxdStartTime.timestamp())*1000
        
        
        
        print(a.text)
        d=json.loads(a.text)
        mydata = None
        for msg in d['results']:

            try:
                
                m = msg['text']

                mtime = m.split(' ')[0].replace("Z","").replace("T"," ")
                mtimeStamp = int(dt.strptime(mtime,"%Y-%m-%d %H:%M:%S.%f").timestamp())*1000
            
                if mtimeStamp>t or mtimeStamp<f:
                    continue

                print("Next LI Message")

                print(msg)
                mcomp = m.split(' took ')[0].split('VpxProfiler] ')[1].replace(" ","")
    
                mtook = m.split(' took ')[1].split(' ms')[0]
                if mydata is None:
                    mydata = {}
                if mcomp in mydata.keys():
                    if mydata[mcomp]["took"]<mtook:
                        mydata[mcomp] = {"took":mtook,"time":mtime,"timestamp":mtimeStamp}
                else:
                    mydata[mcomp] = {"took":mtook,"time":mtime,"timestamp":mtimeStamp}
                print(mydata[mcomp])
            
            except Exception as e2:
                print("getVpxdComponentTimes: "+str(e2))
        
        return(mydata)
        
        
    except Exception as e:
        print("getVpxdComponentTimes failed: "+str(e))
        return(None)
    
    
def computeVpxdComponentTimes(mydata,hostname,vpxdPID):
    print("Computing vpxd times for vpxd PID: "+str(vpxdPID))
    print(mydata)
    
    if mydata is None:
        print("computeVpxdComponent: No data to process")
        return
    
    mycsvdata=""
    mysorter = {}
    for c in mydata.keys():
        try:
            fromTimestamp = int(mydata[c]['timestamp'])-int(mydata[c]['took'])
            fromTimestamp = round(fromTimestamp/1000)
            fromTime = dt.fromtimestamp(fromTimestamp).strftime("%Y-%m-%d %H:%M:%S.%f")
            
            fromTime = str(fromTime)[:-3]
            tookTime = round(int(mydata[c]['took'])/1000)
            d1 = str(fromTimestamp)+"|"+str(hostname)+"|"+str(c)+"|"+str(vpxdPID)+"|"+str(tookTime)+"|"+str(fromTime)+"|"+str(mydata[c]["time"])+"\n"
            print("Computed Data: ")
            print(d1)
            
            if fromTimestamp not in mysorter.keys():
                mysorter[fromTimestamp] = []
            mysorter[fromTimestamp].append(d1)
            
        
        except Exception as e:
            print("computeVpxdComponentTimes failed: "+str(e))
    
    try:
        for mydt in sorted(mysorter.keys()):
            for e in mysorter[mydt]:
                mycsvdata = mycsvdata + e
    except Exception as e2:
        print("computeVpxdComponentTimes failed: "+str(e2))

    
    
    return(mycsvdata)




def processed(vpxdPID):
    
    try:
        vpxdBootData = json.load(open(vpxdBootDataJSON,"r"))
        if "vpxd_"+str(vpxdPID) in vpxdBootData.keys():
            return(True)
        else:
            return(False)
    except Exception as e:
        print("processed failed: "+str(e)+". But it's ok, may be first run.")
        return(False)

def getVpxdTimesFromJson():
    
    vpxdData = json.load(open(bootDataJSON,"r"))
    myvpxdTimes = []
    myvpxdData ={}
    for p in vpxdData.keys():
        try:
#            print("Trying now")

            parts = p.split("_")
#            print(p)

#            print(parts)

            if parts[0]=='vpxd':
                if processed(parts[1]):
                    continue
                print("Unprocessed instance")
                print(p)
                d1 = vpxdData[p]
                print(d1)
                mytimestamp = d1.split("|")[0].replace('\n','')
                print(mytimestamp)


                myvpxdTimes.append(int(mytimestamp))
                myvpxdData[mytimestamp]=d1
        except Exception as e3:
            print("getVpxdTimesFromJson failed: "+str(e3))
    
    myvpxdTimes.sort()
    print("Finished getVpxdTimesFromJson")
    return(myvpxdTimes,myvpxdData)
    
    
def findVpxdComponentTimes(hostname):
    mycsvdata = None
    try:
        #Get unprocessed vpxd restarts
        myvpxdTimes,myvpxdData = getVpxdTimesFromJson()
        mycsvdata = ""
        print("myvpxdTimes")

        print(myvpxdTimes)
        print("myvpxdData")
        print(myvpxdData)
        for t in myvpxdTimes:

            vpxdRestartInstance = myvpxdData[str(t)]
            print("Processing: "+vpxdRestartInstance)        
            mytimedata = vpxdRestartInstance.split('|')
            vpxdStartTime = mytimedata[-2].replace("\n","")
            vpxdPIDTime = mytimedata[-1].replace("\n","")
            vpxdPID = mytimedata[3].replace("\n","")
            print(str(vpxdPID)+" "+vpxdPIDTime+" "+vpxdStartTime)
            vpxdTook = round(dt.strptime(vpxdStartTime,"%Y-%m-%d %H:%M:%S.%f").timestamp()-dt.strptime(vpxdPIDTime,"%Y-%m-%d %H:%M:%S.%f").timestamp())
            mydata = getVpxdComponentTimes(vpxdPIDTime, vpxdStartTime)
            print("Received my data")
            csvdata = computeVpxdComponentTimes(mydata,hostname,vpxdPID)
            
            vpxddt = ""+str(dt.strptime(vpxdPIDTime,"%Y-%m-%d %H:%M:%S.%f").timestamp())+"|"+str(hostname)+"|vpxd|"+str(vpxdPID)+"|"+str(vpxdTook)+"|"+str(vpxdPIDTime)[:-3]+"|"+str(vpxdStartTime)[:-3]
            print("Received CSV Data")
            if csvdata is not None:
                csvdata = vpxddt+"\n"+csvdata
                mycsvdata = mycsvdata+csvdata
        
        with open(mytextoutputfile,"w") as fp:
            fp.write(mycsvdata)
            
    
    except Exception as e:
        print("findVpxdComponentTimes failed: "+str(e))
        mycsvdata = None
    
    return(mycsvdata)




def parseCompTimes(mycomplogs,hostname,vpxdPID,vpxdPIDTime,vpxdStartTime):
    
    mycsvdata = None
    try:
        
        vpxdPIDTime = dt.strptime(vpxdPIDTime,"%Y-%m-%d %H:%M:%S.%f")
        vpxdStartTime = dt.strptime(vpxdStartTime,"%Y-%m-%d %H:%M:%S.%f")
        
        f = vpxdPIDTime.timestamp()
        t = vpxdStartTime.timestamp()
        print("vpxdPIDTime: "+str(vpxdPIDTime))
        print("vpxdStartTime: "+str(vpxdStartTime))
        for m in mycomplogs:

            try:
                print(m)
                mtime = m.split(' ')[0].replace("Z","").replace("T"," ")
                mtimeStamp = dt.strptime(mtime,"%Y-%m-%d %H:%M:%S.%f").timestamp()
            
                if mtimeStamp>t or mtimeStamp<f:
                    continue
                print("Log: "+str(m))
                
                mcomp = m.split(' took ')[0].split('VpxProfiler] ')[1].replace(" ","")
    
                mtook = m.split(' took ')[1].split(' ms')[0]
                if mycsvdata is None:
                    mycsvdata = ""
                
                mtimestamp0 = round((mtimestamp*1000-int(mtook))/1000)
                mtime0 = dt.fromtimestamp(mtimestamp0)
                d1 = str(mtimestamp0)+"|"+str(hostname)+"|"+str(mcomp)+"|"+str(vpxdPID)+"|"+str(mtook)+"|"+str(mtime0)[:-3]+"|"+str(mtime)+"\n"
                mycsvdata = mycsvdata+d1
                if ("ServerApp::Start" in mcomp):
                    break
                
            
            except Exception as e2:
                print("parseCompTimes failed: "+str(e2))
        
        return(mycsvdata)
        
        
    except Exception as e:
        print("parseCompTimes failed: "+str(e))
        return(None)
    




def getVpxdComponentTimesFromVpxdFile(hostname,vpxdPID,vpxdPIDTime,vpxdStartTime):
    csvdata = None
    
    try:
        mycomplogs = runCommand("cat "+vpxdLogFile+" | grep took | grep ms")
        mycomplogs = mycomplogs.split("\\n")
        print(mycomplogs)
        csvdata = parseCompTimes(mycomplogs,hostname,vpxdPID,vpxdPIDTime,vpxdStartTime)
        
    
    except Exception as e:
        print("getVpxdComponentTimesFromVpxdFile faile: "+str(e))    
    
    return csvdata
            
def grepVpxdComponentTimes(hostname):            
    csvdata = None
    try:
        #Get unprocessed vpxd restarts
        myvpxdTimes,myvpxdData = getVpxdTimesFromJson()
        mycsvdata = ""
        print("myvpxdTimes")

        print(myvpxdTimes)
        print("myvpxdData")
        print(myvpxdData)
        print("Non-LI mode, will check for only latest vpxd boot")
        t = myvpxdTimes[-1]
        vpxdRestartInstance = myvpxdData[str(t)]
        print("Processing: "+vpxdRestartInstance)        
        mytimedata = vpxdRestartInstance.split('|')
        vpxdStartTime = mytimedata[-2].replace("\n","")
        vpxdPIDTime = mytimedata[-1].replace("\n","")
        vpxdPID = mytimedata[3].replace("\n","")
        print(str(vpxdPID)+" "+vpxdPIDTime+" "+vpxdStartTime)
        vpxdTook = round(dt.strptime(vpxdStartTime,"%Y-%m-%d %H:%M:%S.%f").timestamp()-dt.strptime(vpxdPIDTime,"%Y-%m-%d %H:%M:%S.%f").timestamp())
        print("Received my data")
        csvdata = getVpxdComponentTimesFromVpxdFile(hostname,vpxdPID,vpxdPIDTime,vpxdStartTime)
            
        vpxddt = ""+str(dt.strptime(vpxdPIDTime,"%Y-%m-%d %H:%M:%S.%f").timestamp())+"|"+str(hostname)+"|vpxd|"+str(vpxdPID)+"|"+str(vpxdTook)+"|"+str(vpxdPIDTime)[:-3]+"|"+str(vpxdStartTime)[:-3]
        print("Received CSV Data")
        if csvdata is not None:
            csvdata = vpxddt+"\n"+csvdata
        print(csvdata)    
        
        return csvdata    
            
        

    except Exception as e:
        print("grepVpxdComponentTimes failed: "+str(e))            
        
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
    parser.add_argument("-x","--vpxdfile", type=str,help="Specify vpxd log file path. Default: /var/log/vmware/vpxd/vpxd.log")
    args = parser.parse_args()
    
    if args.folder:
        outputFolder = args.folder
        if(outputFolder[-1]!='/'):
            outputFolder=outputFolder+'/'
        mytextoutputfile = outputFolder+'vpxdBootData.txt'
        #myjsonoutputfile = outputFolder+'BootData.json'

        
    if args.vcName:
        vcName = args.vcName
    
    if args.vpxdfile:
        vpxdLogFile = args.vpxdfile
    
    
    
    if isLIAttached():
        findVpxdComponentTimes(vcName)
    else:
        print("No LogInsight found, fallback to greppin the vpxd file")
        grepVpxdComponentTimes(vcName)
    
    
    

