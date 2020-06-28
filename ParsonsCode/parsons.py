#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 17:48:38 2020

@author: albertovaldez
"""

def LoudestBand(x,y):
    highest = []
    for i in range(len(y)):
        m = max(y[i])
        ind = y[i].index(m)
        freq = x[ind]
        highest.append(freq)
    return highest
    
def GetPCode(sequence):
    code = ["*"]
    for i in range(len(sequence)-1):
        if sequence[i+1] > sequence[i]:
            code.append("U")
        elif sequence[i+1] == sequence[i]:
            code.append("R")
        elif sequence[i+1] < sequence[i]:
            code.append("D")
    return code
    
def GetPCode_Num(sequence):
    value = 0
    code = [value]
    for i in range(len(sequence)-1):
        if sequence[i+1] > sequence[i]:
            value = value + 1 
            code.append(value)
        elif sequence[i+1] == sequence[i]:
            value = value
            code.append(value)
        elif sequence[i+1] < sequence[i]:
            value = value - 1
            code.append(value)
    return code

def GetPCode_Silence(x,y):
    value = 0
    code = [value]
    for i in range(len(y)-1):
        if y[i+1] > y[i]:
            value = value + 1 
            code.append(value)
        elif y[i+1] == y[i]:
            value = value
            code.append(value)
        elif y[i+1] < y[i]:
            value = value - 1
            code.append(value)
    return code

def Cube():
    pass