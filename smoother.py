#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 16:53:54 2022

@author: fanyang
"""
from scipy.integrate import simps
import numpy as np

def Gaussian_smoother(X, Y, x, y, xx, yy, F, h):
    #area = (y[-1] - y[0]) * (x[-1] - x[0])
    kernel = 1 / 2 / np.pi / h * np.exp(-0.5 * ((X - xx)**2 + (Y - yy)**2) / h**2)
    integrand = F * kernel
    z = simps([simps(z_x,x) for z_x in integrand],y)
    
    return z

def pattern_smoother(X, Y, x, y, F, h):
    
    light_pattern_smooth = np.zeros_like(X)
    light_pattern_smooth_nonnorm = np.zeros_like(X)
    unit_func = np.ones_like(X)
    
    for i in range(len(x)):
        for j in range(len(y)):
            xx = x[i]
            yy = y[j]
            
            light_pattern_smooth_nonnorm[j,i] = Gaussian_smoother(X, Y, x, y, xx, yy, F, h) 
            light_pattern_smooth[j,i] =  light_pattern_smooth_nonnorm[j,i]/ Gaussian_smoother(X, Y, x, y, xx, yy, unit_func, h)
            
    return [light_pattern_smooth, light_pattern_smooth_nonnorm]


    
    light_pattern_smooth = np.zeros_like(X)
    
    for i in range(len(x)):
        for j in range(len(y)):
            xx = x[i]
            yy = y[j]
            light_pattern_smooth[j,i] = Gaussian_smoother(X, Y, x, y, xx, yy, F, h) 
                                       
            
    return light_pattern_smooth