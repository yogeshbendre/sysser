# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 11:33:24 2019

@author: ybendre
"""

import json
import time
import requests
import pickle



class LIUtils:
    
    
    def __init__(self,host=None,user="admin",password="Admin!23",port='9543'):
        
        if host is None:
            self.host = self.getLogInsightIp()
        
        self.user = user
        self.password = password
        self.port = str(port)
        response = self.login()
        self.response = response
        
        

    def isCurrentSessionValid(self,sessionId):
        if(sessionId==None):
            return(False)
        uri = 'https://' + self.host + ':'+self.port+'/api/v1/sessions/current'
        headers = {'Content-type': 'application/json', 'Authorization': 'Bearer ' + sessionId}
        response = requests.get(uri, headers=headers, verify=False)
        print(response.status_code)
        print(response.text)
        return(int(response.status_code)==200)




    def login(self):
    
        try:
            response=pickle.load(open("./"+self.host+"_"+self.user+"_currentLISession.pickle","rb"))
            res = json.loads(response.text)
            sessionId = res['sessionId']
            if(self.isCurrentSessionValid(sessionId)):
                return(response)
        except:
            print('File IO Error. Reinitialize session')
        
        print("Need to Login")
        uri = 'https://'+self.host+':'+self.port+'/api/v1/sessions'
        
        query = json.dumps({
        "username": self.user,
        "password": self.password,
        "provider": "Local"
        })
        headers = {'Content-type': 'application/json'}
        response = requests.post(uri, data=query,headers=headers,verify=False)
        print(response.text)
        pickle.dump(response,open("./"+self.host+"_"+self.user+'_currentLISession.pickle','wb'))
        return(response)


    def getLogInsightIp(self):
        
        li_ip=None
        
        try:
            fullContent = None
            with open("/etc/liagent.ini","r") as fp:
                fullContent = fp.read().split("\n")
                for l in fullContent:
                    if("hostname=" in l):
                        if(";hostname=" not in l):
                            li_ip = l.split("hostname=")[1]
            
            
        except Exception as e:
            print("getLogInsightIp failed: "+str(e))
    
        return(li_ip)
    

    def getQueryResults(self,query,content_pack='st.vmware',fromTimestamp = None, toTimestamp = None):
        
        #Login to LI if not already and get session ID
        response=self.login()
        res=json.loads(response.text)
        headers={'Content-type': 'application/json', 'Authorization': 'Bearer '+res['sessionId']}
        
        uri = 'https://'+self.host+':'+self.port+'/api/v1/events/'+query
        
            
        if fromTimestamp is not None:
            fromTimestamp = str(fromTimestamp)
            if uri[-1]!='/':
                uri = uri+"/"
        
            uri = uri+"timestamp/>="+fromTimestamp+"/"
        
        if toTimestamp is not None:
            toTimestamp = str(toTimestamp)
            if uri[-1]!='/':
                uri = uri+"/"
        
            uri = uri+"timestamp/<"+toTimestamp
        
        if uri[-1]=='/':
            uri = uri[:-1]
        
        uri = uri + '?content-pack-fields='+content_pack+'&view=simple&order-by-direction=ASC&limit=10000&timeout=240000'
        print("Sending bellow query:")
        print("query: "+uri)
        queryResponse = None
        try:
            queryResponse = requests.get(uri,headers=headers,verify=False)
            
            #print("query response: "+response2.text)
            
        
        except Exception as e:
            print("getQueryResults failed: "+str(e))
            
        
        return(queryResponse)
                            
            