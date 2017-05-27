from cx_Freeze import setup, Executable
#from distutils.core import setup
#import py2exe, sys


# Dependencies are automatically detected, but it might need fine tuning.
#build_exe_options = {"packages": ["os"], "excludes": ["tkinter"], "icon": "JWebDrain.ico"}

# appendScriptToExe doesn't work?
build_exe_options = {"icon": "server-source/JWebDrain.ico", "optimize": 2, "compressed": True, "silent": True}
#python.exe setup.py build_exe --append-script-to-exe

# python.exe setup.py build_exe -O 2 -c --append-script-to-exe -s
#build_exe_options = {"icon": "server-source/JWebDrain.ico"}

setup(  name = "JWebDrain",
        version = "1.4",
        description = "Joel's web-based chest drain audit software",
        options = {"build_exe": build_exe_options},
        executables = [Executable("server-source/server.py")])

