# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 10:15:09 2019

@author: ybendre
"""

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


healthParams = ['advcfgsync', 'autohclupdate', 'clomdliveness', 'clustermembership', 'clusterpartition', 'componentmetadata', 'consistentconfig', 'controllerdiskmode', 'controllerdriver', 'controllerfirmware', 'controlleronhcl', 'controllerreleasesupport', 'dataprotectionversion', 'datastoreusage', 'diskbalance', 'diskspace', 'diskusage', 'dpcfgsync', 'dpdliveness', 'extendedconfig', 'firmwareproviderhealth', 'fwrecommendation', 'hcldbuptodate', 'hostconnectivity', 'hostdisconnected', 'hostlatencycheck', 'largeping', 'limit1hf', 'lsomheap', 'lsomslab', 'nodecomponentlimit', 'objectdphealth', 'objecthealth', 'perfsvcstatus', 'physdiskcapacity', 'physdiskcomplimithealth', 'physdiskcongestion', 'physdiskoverall', 'pnicconsistent', 'rcreservation', 'releasecataloguptodate', 'resynclimit', 'smalldiskstest', 'smallping', 'thickprovision', 'timedrift', 'upgradelowerhosts', 'upgradesoftware', 'vcauthoritative', 'vcuptodate', 'vmotionpinglarge', 'vmotionpingsmall', 'vsanenablesupportinsight', 'vsanvmknic', 'vumconfig', 'vumrecommendation']
healthParamHeader = '|'.join(healthParams)

healthLevel = {'red':'-1','yellow':'0','green':'1'}

vsanHealthDataJSON = '/var/log/vmware/vsanHealthData.json'
mytextoutputfile = '/var/log/vsanHealthData.txt'
mytextoutputfile2 = '/var/log/vsanHealthDataDetails.txt'
logFile = '/var/log/vmware/vsan-health/vmware-vsan-health-summary-result.log'


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


def pushHeaderAndCreateFileL1():
    
    try:
        fp=open(mytextoutputfile,"r")
        fp.close()
    except Exception as e:
        print("pushHeaderAndCreateFileLevel1 failed: "+str(e)+" Need to create file")
        
        myheader = 'date|vcName|clusterName|overallHealth|overallHealthLevel\n'
        with open(mytextoutputfile,"w") as fp:
            fp.write(myheader)
        

def pushvSANDataLevel1(mycsvdata):
    
    try:
        print("Pushing data to file")
        with open(mytextoutputfile,"a") as fp:
            fp.write(mycsvdata)
    except Exception as e:
        print("pushvSANDataLevel1 failed: "+str(e))
        

def pushHeaderAndCreateFileL2():
    
    try:
        fp=open(mytextoutputfile2,"r")
        fp.close()
    except Exception as e:
        print("pushHeaderAndCreateFileLevel2 failed: "+str(e)+" Need to create file")
        
        with open(mytextoutputfile2,"w") as fp:
            fp.write(healthParamHeader)
        

def pushvSANDataLevel2(mycsvdata):
    
    try:
        print("Pushing data to file")
        with open(mytextoutputfile2,"a") as fp:
            fp.write(mycsvdata)
    except Exception as e:
        print("pushvSANDataLevel2 failed: "+str(e))


def findvSanHealthLevel1(vcName,mymin):
    
    currTime = dt.now()
    lookback = currTime - td(minutes = mymin)
    myout = runCommand('cat '+logFile+' | grep "Overall Health" | tail -n 100').split("\\n")
    
    mycsvdata = None
    
    myprocessedclusters = {}
    myclusters = {}
    try:
        myprocessedclusters = json.load(open(vsanHealthDataJSON,'r'))
    except Exception as e1:
        print('findvSanHealthLevel1 failed: '+str(e1)+", but it's ok, maybe first run.")
        myprocessedclusters={}
    
    for d in reversed(myout):
        try:
            mtime = dt.strptime(d.split(' ')[0],'%Y-%m-%dT%H:%M:%S.%fZ')
            if mtime < lookback:
                break
            if mycsvdata is None:
                mycsvdata = ""
            
            clusterName = d.split('Cluster ')[1].split(' Overall')[0].strip()
            if clusterName in myclusters.keys():
                continue
            
            mydate = str(round(currTime.timestamp()))
            if clusterName+'_'+mydate in myprocessedclusters.keys():
                continue
            
            overallHealth = d.split('Overall Health : ')[1].split('\n')[0].strip()
            d1 = mydate +"|"+vcName+"|"+clusterName+"|"+overallHealth+"|"+healthLevel[overallHealth]+"\n"
            mycsvdata = mycsvdata + d1
            myprocessedclusters[clusterName+'_'+mydate] = overallHealth
            myclusters[clusterName] = overallHealth
        except Exception as e:
            print('findvSanHealthLevel1 failed: '+str(e))
    
    json.dump(myprocessedclusters,open(vsanHealthDataJSON,'w'))
    
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
    parser.add_argument("-l","--logfile", type=str,help="Specify vpxd log file path. Default: /var/log/vmware/vsan-health/vmware-vsan-health-summary-result.log")
    args = parser.parse_args()
    
    if args.folder:
        outputFolder = args.folder
        if(outputFolder[-1]!='/'):
            outputFolder=outputFolder+'/'
        mytextoutputfile = outputFolder+'vpxdBootData.txt'
        #myjsonoutputfile = outputFolder+'BootData.json'

        
    if args.vcName:
        vcName = args.vcName
    
    if args.logfile:
        logFile = args.logfile
    
    try:
        pushHeaderAndCreateFileL1()
        mycsvdata=""
        mycsvdata = findvSanHealthLevel1(vcName,12)
        print(mycsvdata)
        pushvSANDataLevel1(mycsvdata)
        
        #pushVpxdData(mycsvdata)
    
    except Exception as e:
        print("vsan health data collection failed: "+str(e))
        
    
    

