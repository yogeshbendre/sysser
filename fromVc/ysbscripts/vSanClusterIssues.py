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
import RCADataFilesUtility as RDF

healthParams = ['advcfgsync', 'autohclupdate', 'clomdliveness', 'clustermembership', 'clusterpartition', 'componentmetadata', 'consistentconfig', 'controllerdiskmode', 'controllerdriver', 'controllerfirmware', 'controlleronhcl', 'controllerreleasesupport', 'dataprotectionversion', 'datastoreusage', 'diskbalance', 'diskspace', 'diskusage', 'dpcfgsync', 'dpdliveness', 'extendedconfig', 'firmwareproviderhealth', 'fwrecommendation', 'hcldbuptodate', 'hostconnectivity', 'hostdisconnected', 'hostlatencycheck', 'largeping', 'limit1hf', 'lsomheap', 'lsomslab', 'nodecomponentlimit', 'objectdphealth', 'objecthealth', 'perfsvcstatus', 'physdiskcapacity', 'physdiskcomplimithealth', 'physdiskcongestion', 'physdiskoverall', 'pnicconsistent', 'rcreservation', 'releasecataloguptodate', 'resynclimit', 'smalldiskstest', 'smallping', 'thickprovision', 'timedrift', 'upgradelowerhosts', 'upgradesoftware', 'vcauthoritative', 'vcuptodate', 'vmotionpinglarge', 'vmotionpingsmall', 'vsanenablesupportinsight', 'vsanvmknic', 'vumconfig', 'vumrecommendation']
healthParamHeader = 'date|vcName|clusterName|overall|'+'|'.join(healthParams)+"\n"

healthLevel = {'red':'-1','yellow':'0','green':'1'}

vsanHealthDataJSON = '/var/log/vmware/vsanHealthData.json'
mytextoutputfile = '/var/log/vmware/vsanHealthData.txt'
mydeltaoutputfile = '/var/log/vmware/vsanHealthDataDelta.txt'
mydeltaoutputfile2 = '/var/log/vmware/vsanHealthDataDetailsDelta.txt'
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



def findvSanHealthLevel2(lFrom,lTo):
    try:
        myout = runCommand("sed '"+str(lFrom)+","+str(int(lTo)-1)+"!d' "+logFile)
        myhealthstate = []
        for p in healthParams:
            try:
                print('Check: '+str(p))
                myhealth = myout.split(p)[1].split(':')[1].split('\\n')[0].strip()
                print(myhealth)
                myhealthstate.append(healthLevel[myhealth])
            except Exception as e2:
                print('findvSanHealthLevel2 failed: '+str(e2)+' marking as yellow')
                myhealthstate.append('0')
        
        print(myhealth)
        myhealthstate = '|'.join(myhealthstate)
        return(myhealthstate)
            
        
    except Exception as e:
        print("findvSanHealthLevel2 failed: "+str(e))
        return None



def findvSanHealthLevel1(vcName,mymin):
    
    currTime = dt.now()
    lookback = currTime - td(minutes = mymin)
    myout = runCommand('cat '+logFile+' | grep -n "Overall Health" | tail -n 100').split("\\n")
    
    mycsvdata = None
    mycsvdata2 = None
    myprocessedclusters = {}
    myclusters = {}
    try:
        myprocessedclusters = json.load(open(vsanHealthDataJSON,'r'))
    except Exception as e1:
        print('findvSanHealthLevel1 failed: '+str(e1)+", but it's ok, maybe first run.")
        myprocessedclusters={}
    
    print('Check If Enough Data Available')
    if len(myout)<3:
        return None
    print('Enough Data Available')
    lastline = myout[-2]
    myout = myout[:-2]
    #lines = [lastline.split(' ')[0].split(':')[0]]
    nextLine = lastline.split(' ')[0].split(':')[0]
    for d in reversed(myout):
        try:
            mtime = dt.strptime(':'.join(d.split(' ')[0].split(':')[1:]),'%Y-%m-%dT%H:%M:%S.%fZ')
            #lines.append(d.split(' ')[0].split(':')[0])
            currLine = d.split(' ')[0].split(':')[0]
            print(d)
            print('lookback: '+str(lookback))
            print('mtime: '+str(mtime))
            if mtime < lookback:
                print('Found an older entry, stop search')
                break
            if mycsvdata is None:
                mycsvdata = ""
            
            clusterName = d.split('Cluster ')[1].split(' Overall')[0].strip()
            if clusterName in myclusters.keys():
                nextLine = currLine
                continue
            
            mydate = str(round(currTime.timestamp()))
            if clusterName in myprocessedclusters.keys():
                if myprocessedclusters[clusterName]['times'][-1] > round(lookback.timestamp()):
                    nextLine = currLine
                    continue
            
            overallHealth = d.split('Overall Health : ')[1].split('\n')[0].strip()
            d1 = mydate +"|"+vcName+"|"+clusterName+"|"+overallHealth+"|"+healthLevel[overallHealth]+"\n"
            mycsvdata = mycsvdata + d1
            if clusterName not in myprocessedclusters.keys():
                myprocessedclusters[clusterName] = {'times':[],'states':[]}
            myprocessedclusters[clusterName]['times'].append(int(mydate))
            myprocessedclusters[clusterName]['states'].append(str(overallHealth))
            myclusters[clusterName] = overallHealth
            
            d2 = findvSanHealthLevel2(currLine,nextLine)
            d2 = mydate +"|"+vcName+"|"+clusterName+"|"+healthLevel[overallHealth]+"|"+d2+"\n"
            
            if mycsvdata2 is None:
                mycsvdata2 = ""
            mycsvdata2 = mycsvdata2+d2
            nextLine = currLine
            
        except Exception as e:
            print('findvSanHealthLevel1 failed: '+str(e))
    
    json.dump(myprocessedclusters,open(vsanHealthDataJSON,'w'))
    
    return(mycsvdata,mycsvdata2)
    

        
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
    parser.add_argument("-d","--deltafile", type=str,help="Specify delta output file. Default: current directory")
    parser.add_argument("-e","--deltafiledetailed", type=str,help="Specify delta output file for detailed data. Default: current directory")
    parser.add_argument("-l","--logfile", type=str,help="Specify vpxd log file path. Default: /var/log/vmware/vsan-health/vmware-vsan-health-summary-result.log")
    parser.add_argument("-m","--minutes", type=str,help="Specify time in minutes for collection. Default: 10 min")
    args = parser.parse_args()
    
    if args.folder:
        outputFolder = args.folder
        if(outputFolder[-1]!='/'):
            outputFolder=outputFolder+'/'
        mytextoutputfile = outputFolder+'vsanHealthData.txt'
        mytextoutputfile2 = outputFolder+'vsanHealthDataDetails.txt'
        #myjsonoutputfile = outputFolder+'BootData.json'

    if args.deltafile:
        mydeltaoutputfile = args.deltafile
        
    if args.deltafiledetailed:
        mydeltaoutputfile2 = args.deltafiledetailed
    
    if args.vcName:
        vcName = args.vcName
    
    if args.logfile:
        logFile = args.logfile
    
    minutes = 12
    if args.minutes:
        minutes = int(args.minutes)

    try:
        myheader1 = 'date|vcName|clusterName|overallHealth|overallHealthLevel\n'
        myheader2 = healthParamHeader
        
        pushHeaderAndCreateFileL1()
        pushHeaderAndCreateFileL2()
        mycsvdata,mycsvdata2 = findvSanHealthLevel1(vcName,minutes)
        
        print(mycsvdata)
        if mycsvdata is not None:
            print(mycsvdata)
            RDF.pushToFullFile(mytextoutputfile,myheader1,mycsvdata)

        else:    
            mycsvdata = ''
        
        RDF.pushToDeltaFile(mydeltaoutputfile,myheader1,mycsvdata)
        
        if mycsvdata2 is not None:
            print(mycsvdata2)
            RDF.pushToFullFile(mytextoutputfile2,myheader2,mycsvdata2)
        
        else:
            mycsvdata2 = ''
        
        RDF.pushToDeltaFile(mydeltaoutputfile2,myheader2,mycsvdata2)
        
    
    except Exception as e:
        print("vsan health data collection failed: "+str(e))
        
    
    

