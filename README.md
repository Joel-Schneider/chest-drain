# chest-drain
Record chest drain insertion electronically. 

Software to allow the electronic recording and auditing of chest drain insertion.

Originally hosted on Google code <https://code.google.com/archive/p/chest-drain/>, having been written for a medical school project. Written and built on Linux, for deployment on Windows (hence the apparently odd requirements/build process!).

## Requirements
* Python
* cx_freeze (optional, for Windows build)
* py2exe (optional, for Windows build)
* 7-zip (optional, for Windows build)

## Limitations
* HTTP, not HTTPS!
* Meant to run on the same computer as the data entry, so the above isn't an issue.
* No security/login

## Build
To build exe using Wine on Linux, run ```build.sh``` (if your username isn't joel, and you haven't set WINEPREFIX, edit build.sh first!)
## Installation (optional)
```
$ python setup.py
```
or, on windows:
```
$ python.exe setup.py build_exe --append-script-to-exe
```

See setup.py source for more details and customisation

## Running
```
$ python server-source/server.py
```
Open on http://localhost:8000/

## Data storage and output
```
server-source/server.log: server logs
records.template.csv: template for data records
templateprint.rtf: template for "printout" of records (can be edited, best edited in plain text editor)
```

## TODO ideas
* HTTPS
* Authentication
* PDF output
* SCI store/Trak integration/output
