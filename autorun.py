# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 13:22:36 2018

@author: engin
"""

import os



if __name__ == "__main__":   
    cwd = os.getcwd()   
    print(cwd)
    
    scripts_folder = os.path.join(cwd, "scripts")
    print(scripts_folder)
    