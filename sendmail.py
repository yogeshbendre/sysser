# -*- coding: utf-8 -*-
"""
Created on Wed May 15 14:04:09 2019

@author: ybendre
"""

import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 

def getAttachment(fname):
    
    attachment = open(fname, "rb") 
    # instance of MIMEBase and named as p 
    p = MIMEBase('application', 'octet-stream') 
    # To change the payload into encoded form 
    p.set_payload((attachment).read()) 
    # encode into base64 
    encoders.encode_base64(p) 
    p.add_header('Content-Disposition', "attachment; filename= %s" % fname) 
    
    return(p)

   
fromaddr = "cloud02@vmware.com"
toaddr = "ybendre@vmware.com"
   
# instance of MIMEMultipart 
msg = MIMEMultipart() 
  
# storing the senders email address   
msg['From'] = fromaddr 
  
# storing the receivers email address  
msg['To'] = toaddr 
  
# storing the subject  
msg['Subject'] = "Report"
  
# string to store the body of the mail 
body = "Hi,\n PFA.\nregards,\nCloud02"
  
# attach the body with the msg instance 
msg.attach(MIMEText(body, 'plain')) 
  
# open the file to be sent  
try:
    # attach the instance 'p' to instance 'msg' 
    msg.attach(getAttachment("/var/log/vmware/BootData.txt"))
except Exception as e1:
    print(str(e1))
    
try:
    # attach the instance 'p' to instance 'msg' 
    msg.attach(getAttachment("/var/log/vmware/BootData.json"))
except Exception as e2:
    print(str(e2))

try:
    # attach the instance 'p' to instance 'msg' 
    msg.attach(getAttachment("/root/Ser/stdout.txt"))
except Exception as e3:
    print(str(e3))


try:
    # attach the instance 'p' to instance 'msg' 
    msg.attach(getAttachment("/root/Ser/stderr.txt"))
except Exception as e4:
    print(str(e4))


# creates SMTP session 
s = smtplib.SMTP('smtp.vmware.com') 
  
# Converts the Multipart msg into a string 
text = msg.as_string() 
  
# sending the mail 
s.sendmail(fromaddr, toaddr, text) 
  
# terminating the session 
s.quit() 