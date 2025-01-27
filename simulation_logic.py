#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  5 12:37:16 2022

@author: fanyang
"""
import functions as fct
import numpy as np
import os
import json
from uuid import uuid4
from matplotlib import pyplot, colors
from smoother import pattern_smoother

uid = str(uuid4())
DATA_DIR = f"./tmp/{uid}"  # We want to work on fast memory (but we already work there so this can be a local tmp folder)
os.makedirs(DATA_DIR, exist_ok=True)

def  do_one_parameter_config(ang, length, width,
                             AS, nx1, ny1, nx2, ny2, q, 
                             err_0, err_w,
                             num_iter, dt0, aq, t_save, dt_save, gpx, gpy,
                             gamma, zeta, kkappa, lambdat, gp, poff, pn1, pn2, pu,
                             pm, bell_shape_x, bell_shape_y, 
                             bell_shape_x_2, bell_shape_y_2, xis, 
                             eta, n_expos, sp, a, bf, ka, psi, 
                             pei0, peim, nft, inner_light_ratio, h, artv, artv_flag,
                             SAVE=False, ex=None, SAVE_data=False, Create_mesh=True):

    rx1 = length * np.sin(ang/2)
    ry1 = length * np.cos(ang/2) / 2
    slope = np.tan(ang/2)
    
    ryi = ry1 - width / np.sin(ang/2)
    nf = 0


    x1 = np.linspace(- 1.5 * rx1,  1.5 * rx1, nx1)
    y1 = np.linspace(- 1.5 * ry1, 1.5 * ry1, ny1)
    dx1 = x1[2] - x1[1]
    dy1 = y1[2] - y1[1]


    x2 = x1[-1] + dx1 * (1 - q ** np.linspace(1, nx2, nx2)) / (1 - q)
    y2 = y1[-1] + dy1 * (1 - q ** np.linspace(1, ny2, ny2)) / (1 - q)
    '''
    x2 = x1[-1] + dx1 * np.linspace(1, nx2, nx2)
    y2 = y1[-1] + dy1 * np.linspace(1, ny2, ny2)'''
    x = np.concatenate((-np.flipud(x2), x1, x2))
    y = np.concatenate((-np.flipud(y2), y1, y2))
    #y = x.copy()

    X, Y = np.meshgrid(x, y)
    nx = nx1 + 2 * nx2 
    ny = ny1 + 2 * ny2




    dx = X[:, 1:] - X[:, 0:-1]
    dx = np.concatenate((np.zeros((ny,1)), dx), axis=1)
    
    dy = Y[1:, :] - Y[0:-1, :]
    dy = np.concatenate((np.zeros((1,nx)), dy), axis=0)
    

    d2x = X[:, 2:] - X[:, 0:-2]
    d2y = Y[2:, :] - Y[0:-2, :]
    '''
    d2x = np.delete(d2x, (0, -1), 0)
    d2y = np.delete(d2y, (0, -1), 1)'''

    d2x = np.delete(d2x, 0, 0)
    d2x = np.delete(d2x, -1, 0)
    d2y = np.delete(d2y, 0, 1)
    d2y = np.delete(d2y, -1, 1)
    
    dxp = d2x / 2
    dyp = d2y / 2

    ##videos





    #light frequency
    t_light = 0
    light_period = dt_save
    expos = n_expos * dt0
    n_light_period = 0
    light_flag = 0
    ##physical variables

    #pei = 0.01 ## inverse of Peclet number Pe^{-1}

    pemi = peim
    pedi = peim
    peai = pei0*10
    pei = pei0
    
  

    #pf = 1



    t = 0 



    ux = np.zeros((ny, nx))
    uy = np.zeros((ny, nx))

    vx = np.zeros((ny, nx))
    vy = np.zeros((ny, nx))
    
    vfx = np.zeros((ny, nx))
    vfy = np.zeros((ny, nx))


    df = np.zeros((ny, nx))
    dc = np.zeros((ny, nx)) 
    m = np.ones((ny, nx))
    ca = np.ones((ny, nx))
    
    #cs = s_grad * X

    cf = np.ones((ny, nx))
    c = np.zeros((ny, nx))
    
    mt_save = np.zeros((ny, nx, nft+1))
    #ux_save = np.zeros((ny, nx, nft+1))
    #uy_save = np.zeros((ny, nx, nft+1))
    c_save = np.zeros((ny, nx, nft+1))
    m_save = np.zeros((ny, nx, nft+1))
    df_save = np.zeros((ny, nx, nft+1))
    dc_save = np.zeros((ny, nx, nft+1))
    #cs_save = np.zeros((ny, nx, nft+1))
    
    gf = gamma * bf * c / (bf * c + gamma)
    
    out_tri = np.where(np.abs(X) <= (Y + ry1)* slope, AS, 0 )
    out_tri = np.where(Y <= ry1, out_tri, 0 )
    
    in_tri = np.where(np.abs(X) <= (Y + ryi)* slope, AS, 0 )
    in_tri = np.where(Y <= ry1, in_tri, 0 )
    
    if Create_mesh:
        light_pattern_og = out_tri - in_tri
        
        figlight = pyplot.figure(figsize=(9, 9))
        axlight = pyplot.axes()
        pyplot.pcolor(X, Y, light_pattern_og, cmap='YlGn', vmin=np.amin(light_pattern_og), vmax=AS)    
        pyplot.colorbar()
        axlight.set_xlim(-2.*rx1, 2.*rx1)
        axlight.set_ylim(-2 * ry1, 2 * ry1)
        pyplot.gca().set_aspect('equal')
        figlight.suptitle('Original Light pattern', fontsize=20)
        if SAVE:
            fname = f"{DATA_DIR}/light_original.png"
            figlight.savefig(fname)
            fname_lo = f"{DATA_DIR}/light_og.npy"
            np.save(fname_lo, light_pattern_og)
            
            if ex is not None:
                ex.add_artifact(fname)
                ex.add_artifact(fname_lo)
            pyplot.close(figlight)
        
        light_pattern_smooth, light_pattern_smooth_nonnorm = pattern_smoother(X, Y, x, y, light_pattern_og, h)

    else:
        light_pattern_smooth = np.load('light_smoothed.npy')



    sigmapxx, sigmapxy, sigmapyy = [np.zeros((ny, nx)) for _ in range(3)]


    i = 0
    
        
    figls = pyplot.figure(figsize=(9, 9))
    axls = pyplot.axes()
    pyplot.pcolor(X, Y, light_pattern_smooth, cmap='YlGn', vmin=np.amin(light_pattern_smooth), vmax=np.amax(light_pattern_smooth))    
    pyplot.colorbar()
    axls.set_xlim(-2.*rx1, 2.*rx1)
    axls.set_ylim(-2. * ry1, 2. * ry1)
    pyplot.gca().set_aspect('equal')
    figls.suptitle('Smoothed Light Pattern', fontsize=20)
    if SAVE:
        fname = f"{DATA_DIR}/light_smoothed.png"
        figls.savefig(fname)
        fname_ls = f"{DATA_DIR}/light_smoothed.npy"
        np.save(fname_ls, light_pattern_smooth)
        if ex is not None:
            ex.add_artifact(fname)
            ex.add_artifact(fname_ls)
        pyplot.close(figls)
    
    '''
    figls = pyplot.figure(figsize=(9, 9))
    axls = pyplot.axes()
    pyplot.pcolor(X, Y, light_pattern_smooth_nonnorm, cmap='YlGn', vmin=np.amin(light_pattern_smooth_nonnorm), vmax=np.amax(light_pattern_smooth_nonnorm))    
    pyplot.colorbar()
    axls.set_xlim(-2.*rx1, 2.*rx1)
    axls.set_ylim(-2. * rx1, 2. * rx1)
    pyplot.gca().set_aspect('equal')
    figls.suptitle('Nonnormal Smoothed Light Pattern', fontsize=20)
    if SAVE:
        fname = f"{DATA_DIR}/light_smoothed_nonnorm.png"
        figls.savefig(fname)
        if ex is not None:
            ex.add_artifact(fname)
        pyplot.close(figls)
    '''
    
    

#title = 'texp2e-3poff0.5pn6tpt1e-2as8ga0.1zeta10kappa1ambda0bx6by4xiv10eta0.5'
    while n_light_period < nft + 1:
     
        #dtux = dx / np.abs(ux) / 2
        #dtuy = dy / np.abs(uy) / 2
        dtvx = dx / np.abs(vx) / 2
        dtvy = dy / np.abs(vy) / 2 
       
        dt = min(dt0, dtvx[ny2:-ny2, nx2:-nx2].min(),
                dtvy[ny2:-ny2, nx2:-nx2].min())
        
        
        if t - t_light <= 1.01 * expos and t >= t_light:
            light_flag = 1
           
            pd = light_pattern_smooth
           # print('light is on, current time is %f' % t)
            
            
        else:
            pd = np.zeros((ny, nx))
            if light_flag == 1:
                light_flag = 0
                t_light += light_period
                n_light_period += 1
                
        ## calculate motor concentration
        mn = fct.timestep_m(df, m, ux, uy, pd, pm, pemi, dx, dy, dxp, dyp, d2x, d2y, dt, X, Y)
        
        dfn = fct.timestep_df(df, c, cf, ux, uy, m, poff, pn1, pn2, pedi, dx, dy, dxp, dyp, d2x, 
                d2y, dt, pm, pd, X, Y, dc)
        
        
        dcn = fct.timestep_dc(df, c, cf, vx, vy, poff, pn1, pn2, dx, dy, dxp, 
                dyp, d2x, d2y, dt, X, Y, dc)
        
        
        ## calculate microtubule concentration
        cn = fct.timestep_c(c, cf, df, vx, vy, pu, pn1, dx, dy, dxp, dyp, d2x, d2y, dt, X, Y, artv, artv_flag)
        cfn = fct.timestep_cf(c, cf, df, vfx, vfy, pu, pn1, dx, dy, dxp, dyp, d2x, d2y, dt, X, Y, pei, artv, artv_flag)
        can = fct.timestep_atp(ca, dc, ux, uy, ka, dx, dy, dxp, dyp, d2x, d2y, dt, X, Y, peai)
        #csn = fct.timestep_S(cs, ux, uy, dx, dy, dxp, dyp, d2x, d2y, dt, X, Y, pesi)
        
        sigmapxxn, sigmapyyn, sigmapxyn = fct.timestep_sigmap(
            sigmapxx, sigmapxy, sigmapyy, vx, vy, dx, dy, dc, d2x, d2y, dt, X, Y, sp, c, pu)
       
       
        ## update information
        m = mn.copy()
        df = dfn.copy()
        dc = dcn.copy()
        c = cn.copy()
        cf = cfn.copy()
        ca = can.copy()
        #cs = csn.copy()
        sigmapxx = sigmapxxn.copy()
        sigmapxy = sigmapxyn.copy()
        sigmapyy = sigmapyyn.copy()
        
        mt = c + cf
        dmt = df + dc
        gf = gamma * bf * c / (bf * c + gamma)
     
        

        
        
        vmin = abs(min(vx.min(), vx.max(), vy.min(), vy.max(), 
                       ux.min(), ux.max(), uy.min(), uy.max(), key=abs)) 
        errbar_v = max(vmin * err_w, err_0)
        vx, vy, ux, uy = fct.iter_V_2(c, dx, dy, dxp, dyp, d2x, d2y, gamma, vx, vy, ux, uy, X, Y, dc, xis, 
            eta, zeta, sigmapxx, sigmapxy, sigmapyy, gf, cf, ca, psi, bf)
           
   
        err_v = 1
        iter_v = 0
        
        
        
        ## calculate velocity
        
        while err_v > errbar_v and iter_v < num_iter:
            
            vxn, vyn, uxn, uyn = fct.iter_V_2(c, dx, dy, dxp, dyp, d2x, d2y, gamma, vx, vy, ux, uy, X, Y, dc, xis, 
            eta, zeta, sigmapxx, sigmapxy, sigmapyy, gf, cf, ca, psi, bf)
            
            err_v = (np.abs(vxn - vx).max() + np.abs(vyn - vy).max()
                    + np.abs(uxn - ux).max() + np.abs(uyn - uy).max()) 
            iter_v += 1
            
            vx, vy, ux, uy = [vxn.copy(), vyn.copy(), uxn.copy(), uyn.copy()]
        
        vfx, vfy = fct.update_vf(c, vx, vy, gamma, bf, ux, uy, d2x, d2y)

       
        if abs(t - t_save) <= 0.51 * dt0:

            t_save += dt_save
            
            mt_save[:, :, nf] = mt
            #ux_save[:, :, nf] = ux
            #uy_save[:, :, nf] = uy
            c_save[:, :, nf] = c
            m_save[:, :, nf] = m
            df_save[:, :, nf] = df
            dc_save[:, :, nf] = dc
            #cs_save[:, :, nf] = cs
            if SAVE_data:
                if nf == nft:
                    fname_mt = f"{DATA_DIR}/mt.npy"
                    np.save(fname_mt, mt_save)
                    #fname_ux = f"{DATA_DIR}/ux.npy"
                    #np.save(fname_ux, ux_save)
                    #fname_uy = f"{DATA_DIR}/uy.npy"
                    #np.save(fname_uy, uy_save)
                    fname_c = f"{DATA_DIR}/c.npy"
                    np.save(fname_c, c_save)
                    fname_x = f"{DATA_DIR}/x.npy"
                    np.save(fname_x, x)
                    fname_y = f"{DATA_DIR}/y.npy"
                    np.save(fname_y, y)
                    fname_m = f"{DATA_DIR}/m.npy"
                    np.save(fname_m, m_save)
                    fname_df = f"{DATA_DIR}/df.npy"
                    np.save(fname_df, df_save)
                    fname_dc = f"{DATA_DIR}/dc.npy"
                    np.save(fname_dc, dc_save)
                    #fname_cs = f"{DATA_DIR}/cs.npy"
                    #np.save(fname_cs, cs)
                    
                    
                    if ex is not None:
                        ex.add_artifact(fname_mt)
                        #ex.add_artifact(fname_ux)
                        #ex.add_artifact(fname_uy)
                        ex.add_artifact(fname_c)
                        ex.add_artifact(fname_x)
                        ex.add_artifact(fname_y)
                        ex.add_artifact(fname_m)
                        ex.add_artifact(fname_df)
                        ex.add_artifact(fname_dc)
                        #ex.add_artifact(fname_cs)
                
            '''
            figc = pyplot.figure(figsize=(9, 9))
            ax = pyplot.axes()
            pyplot.pcolor(X, Y, dmt, cmap='Purples', vmin=0, vmax=3)    
            pyplot.colorbar()
            ax.set_xlim(-2.*rx1, 2.*rx1)
            ax.set_ylim(-2.*ry1, 2.*ry1)
            pyplot.gca().set_aspect('equal')
            figc.suptitle('Dimer motor', fontsize=20)
    
            if SAVE:
                fname = f"{DATA_DIR}/dmt{nf}.png"
                figc.savefig(fname)
                if ex is not None:
                    ex.add_artifact(fname)
                pyplot.close(figc)
            
            
            figs = pyplot.figure(figsize=(16, 4))
            #u = np.sqrt(ux**2 + uy**2)
            strm = pyplot.streamplot(X, Y, ux, uy, linewidth=2, density=1) 
                                     #color=u, cmap='Blues', norm=colors.Normalize(vmin=0, vmax=2.5, clip=True))                                                                    
            #figs.colorbar(strm.lines, color=u, cmap='Blues', norm=colors.Normalize(vmin=0, vmax=2.5, clip=True))
            figs.suptitle('fluid Streamlines', fontsize=20)
            pyplot.axis('equal')
            figs.savefig('fluidstreamline%d.png' % nf)
            pyplot.close(figs) 
            
            vor =  fct.vorticity(ux, uy, d2x, d2y)
            figP = pyplot.figure(figsize = (9, 8))
            ax2 = pyplot.axes()
            pyplot.pcolor(X[1:-1, 1:-1], Y[1:-1, 1:-1], vor, cmap='bwr', vmin=-2, vmax=2)    
            cbar = pyplot.colorbar()
            cbar.set_label('vorticity')
            pyplot.quiver(X[::gpy, ::gpx], Y[::gpy, ::gpx], ux[::gpy, ::gpx], uy[::gpy, ::gpx])
            ax2.set_xlim(-2.5*rx1+cx1, 2.5*rx2+cx2)
            ax2.set_ylim(-rx1+cx1, rx2+cx2)
            #figP.suptitle('microtubule velocity', fontsize=20)
            pyplot.gca().set_aspect('equal')
    
            
            if SAVE:
                fname = f"{DATA_DIR}/FlowVelocity{nf}.png"
                figP.savefig(fname)
                if ex is not None:
                    ex.add_artifact(fname)
                pyplot.close(figP)
            
            figmv = pyplot.figure(figsize = (9, 8))
            axmv = pyplot.axes()
            pyplot.quiver(X[::gpy, ::gpx], Y[::gpy, ::gpx], vx[::gpy, ::gpx], vy[::gpy, ::gpx])
            axmv.set_xlim(-2.5*rx1, 2.5*rx1)
            axmv.set_ylim(-2.5*rx1, 2.5*rx1)
            #figP.suptitle('microtubule velocity', fontsize=20)
            pyplot.gca().set_aspect('equal')
            
            if SAVE:
                fname = f"{DATA_DIR}/MicrotubuleVelocity{nf}.png"
                figmv.savefig(fname)
                if ex is not None:
                    ex.add_artifact(fname)
                pyplot.close(figmv)
            
            figm = pyplot.figure(figsize=(9, 8))
            axm = pyplot.axes()
            pyplot.pcolor(X, Y, df, cmap='YlGn', vmin=0, vmax=0.5)    
            pyplot.colorbar()
            axm.set_xlim(-2.5*rx1, 2.5*rx1)
            axm.set_ylim(-2.5*rx1, 2.5*rx1)
            pyplot.gca().set_aspect('equal')
            figm.suptitle('free dimer density', fontsize=20)

            if SAVE:
                fname = f"{DATA_DIR}/freedimer{nf}.png"
                figm.savefig(fname)
                if ex is not None:
                    ex.add_artifact(fname)
                pyplot.close(figm)
           '''
            
            figrc = pyplot.figure(figsize=(9, 9))
            axrc = pyplot.axes()
            pyplot.pcolor(X, Y, mt, cmap='YlGn', vmin=0.4, vmax=4)    
            pyplot.colorbar()
            axrc.set_xlim(-2.*rx1, 2.*rx1)
            axrc.set_ylim(-2. * ry1, 2. * ry1)
            pyplot.gca().set_aspect('equal')
            figrc.suptitle('Microtubule density', fontsize=20)
            if SAVE:
                fname = f"{DATA_DIR}/c{nf}.png"
                figrc.savefig(fname)
                if ex is not None:
                    ex.add_artifact(fname)
                pyplot.close(figrc)
            '''    
            figrd = pyplot.figure(figsize=(9, 9))
            axrd = pyplot.axes()
            pyplot.pcolor(X, Y, dmt, cmap='Purples', vmin=0., vmax=3)    
            pyplot.colorbar()
            axrd.set_xlim(-2.*rx1, 2.*rx1)
            axrd.set_ylim(-2. * ry1, 2. * ry1)
            pyplot.gca().set_aspect('equal')
            figrd.suptitle('Dimer motor density', fontsize=20)
            if SAVE:
                fname = f"{DATA_DIR}/dmt{nf}.png"
                figrd.savefig(fname)
                if ex is not None:
                    ex.add_artifact(fname)
                pyplot.close(figrd)
            '''
            '''
            figcp = pyplot.figure(figsize=(9, 8))
            axcp = pyplot.axes()
            pyplot.pcolor(X, Y, cf, cmap='YlGn', vmin=0, vmax=1)    
            pyplot.colorbar()
            axcp.set_xlim(-2.5*rx1, 2.5*rx1)
            axcp.set_ylim(-2.5*rx1, 2.5*rx1)
            pyplot.gca().set_aspect('equal')
            figcp.suptitle('Free Microtubule density', fontsize=20)
    
            if SAVE:
                fname = f"{DATA_DIR}/cf{nf}.png"
                figcp.savefig(fname)
                if ex is not None:
                    ex.add_artifact(fname)
                pyplot.close(figcp)
                
            figdc = pyplot.figure(figsize=(9, 8))
            axdc = pyplot.axes()
            pyplot.pcolor(X, Y, dc, cmap='YlGn', vmin=0, vmax=1.)    
            pyplot.colorbar()
            axdc.set_xlim(-2.5*rx1, 2.5*rx1)
            axdc.set_ylim(-2.5*rx1, 2.5*rx1)
            pyplot.gca().set_aspect('equal')
            figdc.suptitle('Crosslinker density', fontsize=20)
            
            if SAVE:
                fname = f"{DATA_DIR}/dc{nf}.png"
                figdc.savefig(fname)
                if ex is not None:
                    ex.add_artifact(fname)
                pyplot.close(figdc)
            
           
            figa = pyplot.figure(figsize=(9, 8))
            axa = pyplot.axes()
            pyplot.pcolor(X, Y, ca, cmap='YlGn', vmin=0, vmax=1.)    
            pyplot.colorbar()
            axa.set_xlim(-2.5*rx1, 2.5*rx1)
            axa.set_ylim(-2.5*rx1, 2.5*rx1)
            pyplot.gca().set_aspect('equal')
            figa.suptitle('ATP', fontsize=20)
            
            if SAVE:
                fname = f"{DATA_DIR}/ATP{nf}.png"
                figa.savefig(fname)
                if ex is not None:
                    ex.add_artifact(fname)
                pyplot.close(figa)'''
            
            
                
            #print('iteration is %d' % iter_v)
            #print('any ratio=1? ' + str(flag))
            
            nf +=1
        t += dt
        i += 1

        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
