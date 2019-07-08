# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 13:03:32 2019

@author: ybendre
"""

import os


def pushToDeltaFile(filename,myheader,mycsvdata,deleteIfNoData=True):
        
    try:
        if (mycsvdata is None) or (len(mycsvdata) < 2):
            mydata=""
        else:
            myheader = 'date|vcName|component|pid|boot_time_in_sec|last_started_at|last_triggered_at\n'
            mydata = myheader+mycsvdata
        
        with open(mydeltaoutputfile,"w") as fp:
            fp.write(mydata)
            

    except Exception as e:
        print("pushToDeltaFile failed: "+str(e))

    