export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/java/jre-vmware/bin:/opt/vmware/bin"
myscriptpath = "/root/ser4/"
echo $myscriptpath
#Below script can use 2 parameters: -v for vc name and -f for output folder
/usr/bin/python3 ${myscriptpath}ServiceStartTimeCalculator.py > ${myscriptpath}stdout.txt 2> ${myscriptpath}stderr.txt

