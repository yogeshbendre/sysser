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
import pyVmomi
from pyVmomi import vim


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

rhttpsProxyPort = GetRhttpsproxyPortFromExtension(content)
if rhttpsProxyPort == None:
   print("VSAN VC extension not properly registered, skipping...")
   exit()

clusters = FindAllVcClusters(content, content.rootFolder, includeVsanEnabledOnly=True)

clustersProps = CollectMultiple(content, clusters,
                                ['configurationEx'])
configs = [clustersProps[c]['configurationEx'].vsanConfigInfo
           for c in clusters]
anyVsan = len([c for c in configs if c is not None and c.enabled]) > 0

selectedMode = 'all'
if len(sys.argv) > 1:
   selectedMode = sys.argv[1]

if selectedMode == 'all' or selectedMode == 'cluster-health':
   for cluster in clusters:
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

if selectedMode in ['all', 'rvc-support-information', 'rvc-basic-support-information']:
   rvcpath = '/usr/bin/rvc'
   if os.name == 'nt':
      rvcpath = os.environ['VMWARE_RVC_BIN']

   if anyVsan and os.path.exists(rvcpath):
      os.environ['RVC_RBVMOMI_COOKIE'] = conn.cookie
      rvcEndpoint = 'vimhealth://localhost:' + str(rhttpsProxyPort)
      if 'HOME' not in os.environ and os.name != 'nt':
         os.environ['HOME'] = '/root'
      if selectedMode in ['all', 'rvc-support-information']:
         subprocess.call([rvcpath, rvcEndpoint,
                          '-c', 'vsan.support_information /localhost',
                          '-c', 'quit'])
      elif selectedMode == 'rvc-basic-support-information':
         subprocess.call([rvcpath, rvcEndpoint,
                          '-c', 'vsan.support_information --skip-hostvm-info /localhost',
                          '-c', 'quit'])
