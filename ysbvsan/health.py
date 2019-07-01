#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright 2016-2017 VMware, Inc.  All rights reserved.

This file includes sample codes for vCenter and ESXi sides vSAN API accessing.

To provide an example of vCenter side vSAN API access, it shows how to get vSAN
cluster health status by invoking the QueryClusterHealthSummary() API of the
VsanVcClusterHealthSystem MO.

To provide an example of ESXi side vSAN API access, it shows how to get
performance server related host information by invoking the
VsanPerfQueryNodeInformation() API of the VsanPerformanceManager MO.

"""

__author__ = 'VMware, Inc'

#from pyVim.connect import SmartConnect, Disconnect
import sys
import ssl
import atexit
import argparse
import getpass
if sys.version[0] < '3':
   input = raw_input



import os
import sys
import subprocess

os.environ["VSAN_PYMO_SKIP_VC_CONN"] = "1"
if os.name == 'nt':
   #include vmw's python module into PATH, for windows only
   sys.path.append(os.environ["VMWARE_PYTHON_PATH"])
else:
   sys.path.append("/usr/lib/vmware/site-packages/")

import VCConnectionHelper

import six
if six.PY3:
   from http.cookies import SimpleCookie
else:
   from Cookie import SimpleCookie

#add the pypack path for importing pyVmomi module
sys.path.append(VCConnectionHelper.GetPyJackPath())
print(sys.path)
import pyVmomi
from pyVmomi import vim
# Import the vSAN API python bindings and utilities.
import vsanmgmtObjects
import vsanapiutils


from pyMoVsan.VsanHealthUtil import CollectMultiple
from pyMoVsan.VsanVcClusterUtil import FindAllVcClusters
from pyMoVsan.VsanHealthUtil import GetSSLConextForLocalhost
from pyMoVsan.VsanHealthHelpers import GetRhttpsproxyPortFromExtension
# Connect to the VC VSAN health service SOAP endpoint.
# Pass in a stub adapter to vpxd (e.g. si._stub)
# Returns an object of type VimClusterVsanVcClusterHealthSystem
def ConnectToHealthService(stub):
   sessionCookie = stub.cookie.split('"')[1]
   httpContext = pyVmomi.VmomiSupport.GetHttpContext()
   cookieObj = SimpleCookie()
   cookieObj["vmware_soap_session"] = sessionCookie
   httpContext["cookies"] = cookieObj
   hostname = stub.host.split(":")[0]

   vhStub = pyVmomi.SoapStubAdapter(host=hostname,
                                    version = "vim.version.version11",
                                    path = "/vsanHealth",
                                    poolSize = 0,
                                    sslContext = GetSSLConextForLocalhost())
   vhStub.cookie = stub.cookie
   chs = vim.VsanVcClusterHealthSystem('vsan-cluster-health-system',
                                       vhStub)
   return chs

conn, si, content = VCConnectionHelper.ConnectToLocalVC()
chs = ConnectToHealthService(conn)




def GetArgs():
   """
   Supports the command-line arguments listed below.
   """
   parser = argparse.ArgumentParser(
       description='Process args for vSAN SDK sample application')
   parser.add_argument('-s', '--host', required=True, action='store',
                       help='Remote host to connect to')
   parser.add_argument('-o', '--port', type=int, default=443, action='store',
                       help='Port to connect on')
   parser.add_argument('-u', '--user', required=True, action='store',
                       help='User name to use when connecting to host')
   parser.add_argument('-p', '--password', required=False, action='store',
                       help='Password to use when connecting to host')
   parser.add_argument('--cluster', dest='clusterName', metavar="CLUSTER",
                      default='VSAN-Cluster')
   args = parser.parse_args()
   return args

def getClusterInstance(clusterName, serviceInstance):
   content = serviceInstance.RetrieveContent()
   searchIndex = content.searchIndex
   datacenters = content.rootFolder.childEntity
   for datacenter in datacenters:
      cluster = searchIndex.FindChild(datacenter.hostFolder, clusterName)
      if cluster is not None:
         return cluster
   return None




def main():
   args = GetArgs()
   if args.password:
      password = args.password
   else:
      password = getpass.getpass(prompt='Enter password for host %s and '
                                        'user %s: ' % (args.host,args.user))

   # For python 2.7.9 and later, the default SSL context has more strict
   # connection handshaking rule. We may need turn off the hostname checking
   # and client side cert verification.
   context = None
   if sys.version_info[:3] > (2,7,8):
      context = ssl.create_default_context()
      context.check_hostname = False
      context.verify_mode = ssl.CERT_NONE



   clusters = [args.clusterName]
   clustersProps = CollectMultiple(content, clusters,['configurationEx'])
   configs = [clustersProps[c]['configurationEx'].vsanConfigInfo for c in clusters]
   anyVsan = len([c for c in configs if c is not None and c.enabled]) > 0

   if True:

      # Get vSAN health system from the vCenter Managed Object references.
      vhs = chs #vcMos['vsan-cluster-health-system']
      cluster = args.clusterName
      print("Checking "+cluster)
      vsanConfig = clustersProps[cluster]['configurationEx'].vsanConfigInfo
      vsanEnabled = vsanConfig is not None and vsanConfig.enabled
      if not vsanEnabled:
         print("Cluster doesn't have VSAN enabled, skipping ...")
      else:
         try:
            summary = chs.VsanQueryVcClusterHealthSummary(cluster=cluster,
                                                          includeObjUuids = True)
            print("Health summary: %s (%s)" % (
                  summary.overallHealth, summary.overallHealthDescription))
            print("Groups: %s" % str(summary.groups))
         except Exception as ex:
            print("Failed to gather health status: %s" % str(ex))
      print("")
      print("")

if __name__ == "__main__":
   main()
