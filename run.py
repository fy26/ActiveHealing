import sacred
from sacred.observers import FileStorageObserver
from simulation_logic import do_one_parameter_config
import numpy as np

ex = sacred.Experiment("simulation")
ex.observers.append(FileStorageObserver("data"))


@ex.config
def cfg():    
    artv = 0.01
    artv_flag = False
    ang = 75. / 180. * np.pi
    width = 0.5
    ar = 5.5
    length = width * ar
    AS = 20.
    h = 0.2
    nr = 0
    
    nft = 30
    nx1 = 151
    ny1 = 101
    nx2 = 40
    ny2 = 40
    q = 1.035
    err_0 = 1e-4
    err_w = 1e-4
    num_iter = 500
    dt0 = 1e-3
    aq = 0
    xis = 8e-2
    t_save = 0
    n_expos = 60
    ns = 5
    dt_save = ns * n_expos * dt0
    gpx = 10
    gpy = 10
    gamma = 0.045
    zeta = 20.5
    
    kkappa = 0
    lambdat = 0
    gp = 0
    
    sp = 0.5
    
    bf = 10 * gamma
    
    psi = 0

    poff = 15.
        
    pn1 = 15.
    pn2 = pn1 / 20.
    
    pu = poff / 2.

    
    pm = 15.
    bell_shape_x = 6.
    bell_shape_y = 6.
    bell_shape_x_2 = 6.
    bell_shape_y_2 = 6.

    eta = 1.
    a = 1.
    ka = 0.8
    pei0 = 0.001
    peim = 0.001
    inner_light_ratio = 0
    
    



@ex.automain
def run_one_simulation(_config, _run):
    do_one_parameter_config(
        ang=_config["ang"],
        length=_config["length"],
        width=_config["width"],
        AS=_config["AS"],
        nx1=_config["nx1"],
        ny1=_config["ny1"],
        nx2=_config["nx2"],
        ny2=_config["ny2"],
        q=_config["q"],
        err_0=_config["err_0"],
        err_w=_config["err_w"],
        num_iter=_config["num_iter"],
        dt0=_config["dt0"],
        aq=_config["aq"],
        t_save=_config["t_save"],
        dt_save=_config["dt_save"],
        gpx=_config["gpx"],
        gpy=_config["gpy"],
        gamma=_config["gamma"],
        zeta=_config["zeta"],
        kkappa=_config["kkappa"],
        lambdat=_config["lambdat"],
        gp=_config["gp"],
        poff=_config["poff"],
        pn1=_config["pn1"],
        pn2 =_config["pn2"],
        pu=_config["pu"],
        pm=_config["pm"],
        bell_shape_x=_config["bell_shape_x"],
        bell_shape_y=_config["bell_shape_y"],
        bell_shape_x_2=_config["bell_shape_x_2"],
        bell_shape_y_2=_config["bell_shape_y_2"],
        xis=_config["xis"],
        eta=_config["eta"],
        n_expos=_config["n_expos"],
        sp=_config["sp"],
        a = _config["a"],
        bf= _config["bf"],
        ka= _config["ka"],
        psi= _config["psi"],
        pei0= _config["pei0"],
        peim= _config["peim"],
        nft= _config["nft"],
        inner_light_ratio=_config["inner_light_ratio"],
        h= _config["h"],
        artv= _config["artv"],
        artv_flag= _config["artv_flag"],
        SAVE=True,
        ex=ex,
        SAVE_data=False,
        Create_mesh=True
    )
