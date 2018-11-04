# -*- coding: utf-8 -*-
"""
Created on Sun Nov  4 17:51:14 2018

@author: user
"""

class SuperDuper:
    def __init__(self):
        pass
    
    def DoStuff(self):
        self.MysteryFunction()
    
class DerivedDude(SuperDuper):
    def __init(self):
        pass
    
    def MysteryFunction(self):
        print("Mystery!")
        

a = DerivedDude()
a.DoStuff()