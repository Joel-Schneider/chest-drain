#!/bin/bash
echo "JWebDrain v1.4 builder"
echo "This script will remove any existing build & JWebDrain folders, build the exe and create a new JWebDrain folder ready for distribution."
#About to overwrite JWebDrainAudit and remove build files."
echo "Continue?"
read yesno
if [ "x$yesno" != "xyes" ]; then
	exit 0
fi

rm -R build
if [ "x$WINEPREFIX" == "x" ]; then
	export WINEPREFIX="/home/joel/JCDr.wine"
fi

wine C:/Python27/python.exe setup.py build_exe --append-script-to-exe
retval=$?
if [ "$retval" != "0" ]; then
	echo "Error building. Exiting."
	exit $retval
fi

rm -R JWebDrainAudit/
mkdir -p JWebDrainAudit/server

cp build/exe.win32*/* JWebDrainAudit/server
cp python*dll JWebDrainAudit/server
cp records.csv templateprint.rtf JWebDrainAudit/
files=`ls server-source | grep -v 'py$' | grep -v 'ico$' | grep -v 'log$'`
for file in $files; do
	cp server-source/$file JWebDrainAudit/server
done
rm -R build

wine C:/Program\ Files/7-Zip/7z.exe a -r -sfx JWD.exe JWebDrainAudit/
#7za a -r -sfx JWD JWebDrainAudit/

echo "Done!"
