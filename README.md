# chest-drain
Record chest drain insertion electronically. 
Software to allow the electronic recording and auditing of chest drain insertion.

Originally hosted on Google code <https://code.google.com/archive/p/chest-drain/>, having been written for a medical school project. 

##Requirements
* Python
* cx_freeze (optional)
* py2exe (optional, Windows)

##Limitations
* HTTP, not HTTPS!
* Meant to run on the same computer as the data entry, so the above isn't an issue.
* No security/login

##Installation (optional)
$ python setup.py
or, on windows:
$ python.exe setup.py build_exe --append-script-to-exe

See setup.py source for more info

##Running
python server-source/server.py
Open on http://localhost:8000/

##Data storage and output
server-source/server.log: server logs
records.template.csv: template for data records
templateprint.rtf: template for "printout" of records (can be edited, best edited in plain text editor)

##TODO ideas
* HTTPS
* Authentication
* PDF output
* SCI store/Trak integration/output
