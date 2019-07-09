# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 13:03:32 2019

@author: ybendre
"""

import os


def pushToDeltaFile(filename,myheader,mycsvdata,deleteIfNoData=True):
        
    print("Push to delta file: "+filename)
    try:
        if (mycsvdata is None) or (len(mycsvdata) < 2):
            if deleteIfNoData:
                try:
                    print("No delta data, will attempt to delete the delta file if it exists")
                    os.remove(filename)
                except Exception as e4:
                    print('pushToDeltaFile failed: '+str(e4)+', probably file was deleted previously.')
                return
            
            mydata=""
        else:
            myheader = 'date|vcName|component|pid|boot_time_in_sec|last_started_at|last_triggered_at\n'
            mydata = myheader+mycsvdata
        
        with open(filename,"w") as fp:
            fp.write(mydata)
            

    except Exception as e:
        print("pushToDeltaFile failed: "+str(e))

def pushToFullFile(filename,myheader,mycsvdata):

    print("pushToFullFile: "+filename)    
    
    try:
        fp=open(filename,"r")
        fp.close()
    except Exception as e1:
        print("pushToFullFile failed: "+str(e1)+" Need to create file")
        try:
            fp=open(filename,"w")
            fp.write(myheader)
            fp.close()
        
        except Exception as e3:
            print('pushToFullFile header write failed: '+str(e))
            return
        
    
    try:
        print("Pushing data to file")
        with open(filename,"a") as fp:
            fp.write(mycsvdata)
    except Exception as e:
        print("pushToFullFile failed: "+str(e))

