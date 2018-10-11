# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 13:22:36 2018

@author: engin
"""

import os
import subprocess, sys




if __name__ == "__main__":   
    cwd = os.getcwd()   
    print(cwd)
    
    scripts_folder = os.path.join(cwd, "scripts")
    print(scripts_folder)
    
    scripts = os.listdir(scripts_folder)
    
    
    script_path = os.path.join(scripts_folder, "run_match.ps1")
    
    
    
#    os.execl(script_path, "./algos/Dragon", "./algos/SkyBison" )
    
    p = subprocess.Popen(["powershell.exe", 
              "C:\\Users\\USER\\Desktop\\helloworld.ps1"], 
              stdout=sys.stdout)
    p.communicate()