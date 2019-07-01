export POD_ROOT="/usr/lib/vmware-pod"
export POD_PROV_LIB="$POD_ROOT/vapi/provider/python:$POD_ROOT/py"
export POD_PY_LIB="$POD_ROOT/lib/python3.5/site-packages"
export POD_PYLIBS="$POD_PY_LIB"
export POD_VAPI_LIB="$POD_ROOT/lib/vapi"
export POD_VAPI_PYLIBS_COMMON_CLIENT=$(echo "$POD_VAPI_LIB"/vapi_common_client-*-py2.py3-none-any.whl)
export POD_VAPI_PYLIBS_COMMON=$(echo "$POD_VAPI_LIB"/vapi_common-*-py2.py3-none-any.whl)
export POD_VAPI_PYLIBS_RUNTIME=$(echo "$POD_VAPI_LIB"/vapi_runtime-*-py2.py3-none-any.whl)
export POD_VAPI_PYLIBS="$POD_VAPI_PYLIBS_COMMON_CLIENT:$POD_VAPI_PYLIBS_COMMON:$POD_VAPI_PYLIBS_RUNTIME:$POD_VAPI_LIB/"
export PYTHON35_LIBS="/usr/lib/python3.5:/usr/lib/python3.5/site-packages"
export VMWARE_PY_LIB="/usr/lib/vmware/site-packages"
export PYVMOMI_PATH="/usr/lib/vmware-pod/lib/vmware"
export POD_PHONEHOME_LIB="$POD_ROOT/lib/vmware/phclient.zip"
export VSAN_HEALTH_PATH="/usr/lib/vmware-vpx/vsan-health"
export PYJACK="/usr/lib/vmware-vpx/pyJack"
export PYTHONPATH="$PYTHON35_LIBS:$POD_PYLIBS:$POD_VAPI_PYLIBS:$PYVMOMI_PATH:$POD_PROV_LIB:$VMWARE_PY_LIB:$POD_PHONEHOME_LIB:$VSAN_HEALTH_PATH:$PYTHONPATH:$PYJACK"
python getHealth.py --help
python getHealth.py --host stras-cloud-vc.eng.vmware.com --user "administrator@vsphere.local" --password "Admin!23" --cluster vRealizeCluster
#$POD_ROOT/bin/vmware-pod "$@"
