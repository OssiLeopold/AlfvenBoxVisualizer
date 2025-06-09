import os, sys
os.environ['PATH']='/home/rxelmer/Documents/turso/appl/tex-basic/texlive/2023/bin/x86_64-linux:'+ os.environ['PATH'] #enabling use of latex
os.environ['PTNOLATEX']='1' #enabling use of latex

# Import packages
import numpy as np                  # For math
import matplotlib.pyplot as plt     # For plotting
import analysator as pt             # For manipulating .vlsv files
import multiprocessing as mp        # For multiprocessing 

# Import user defined classes
from anim_specs import AnimSpecs

# Packages for gif animation
from matplotlib.animation import PillowWriter
import matplotlib.animation as animation
    
# Set path where to find simulation bulk files
bulkpath = "/home/rxelmer/Documents/turso/bulks/sim15/"

vobj = pt.vlsvfile.VlsvReader(bulkpath + "bulk.0000000.vlsv")
r_e = 6371e3 # Earth radius
x_length = vobj.read_parameter("xcells_ini") # Used for formatting numpy mesh
xmax = vobj.read_parameter("xmax")/r_e # For now only used for placement of time legend
ymax = vobj.read_parameter("ymax")/r_e # For now only used for placement of time legend

# Enter number of bulkfiles, for example if your last bulkfile is named bulk.0000100.vlsv -> then enter 100, or the specific amount of frames you want to animate
bulkfile_n = 10

# Which type of animation?: 
# 1: for 2D heat map 
# 2: for 3D waves in box
animation_setting = 2

# Do you want to animate magnetic field components or velocity field components?:
# 1: for magnetic field components
# 2: for proton velocity components
variables = 1

# Which components do you wish to animate?:
# 1: for only y component
# 2: for only z component
# 3: for both
# 4: for total magnitude
def_components = 4


# Obtain coordinates for cells expressed as Earth's radii, and format to same standards as numpy meshgrid
cellids = vobj.read_variable("CellID")
x = np.array([vobj.get_cell_coordinates(c)[0] for c in np.sort(cellids)])/r_e
x_mesh = x.reshape(-1,x_length)
y = np.array([vobj.get_cell_coordinates(c)[1] for c in np.sort(cellids)])/r_e
y_mesh = y.reshape(-1,x_length)
colors = ["blue", "orange"]
    
# Defining components that will be used:
if def_components == 1:
    components = ['y']
elif def_components == 2:
    components = ['z']
elif def_components == 3:
    components = ['y','z']
elif def_components == 4:
    components = ['y','z']
else:
    print("def_components defined incorrectly")

# Defining functions used in the animations
def update_B_2D(frame):
    fname = "bulk.{}.vlsv".format(str(frame).zfill(7))                                                         # Setting bulkpath to correspond with the current frame, i.e. bulkfile
    vobj = pt.vlsvfile.VlsvReader(bulkpath + fname)                                                            # Defining new vojbect with new bulkpath
    time = vobj.read_parameter("time")
    timelabel.set_text(f"{time:.1f}s")
    for artist in p:                                                                                           # Removing old artist to make way for new frame
        artist.remove()
    for i, component in enumerate(components):                                                                 # Constructing new artists 
        B = np.array(vobj.read_variable("vg_b_vol",operator="{}".format(component))[cellids.argsort()])/1e-9   # Magnetic field expressed in nano Tesla
        B_mesh = B.reshape(-1, x_length)                                                                       # Reshaping into numpy meshgrid
        p[i] = ax.contourf(x_mesh, y_mesh, B_mesh, level_boundaries)
    return p                                                                                                   # Returning artists to animator

def update_v_2D(frame):
    fname = "bulk.{}.vlsv".format(str(frame).zfill(7))
    vobj = pt.vlsvfile.VlsvReader(bulkpath + fname)
    time = vobj.read_parameter("time")
    timelabel.set_text(f"{time:.1f}s")
    for artist in p:
        artist.remove()
    for i, component in enumerate(components):
        v = np.array(vobj.read_variable("proton/vg_v",operator="{}".format(component))[cellids.argsort()])/1e3
        v_mesh = v.reshape(-1, x_length)
        p[i] = ax.contourf(x_mesh, y_mesh, v_mesh, level_boundaries)
    return p

def update_B_3D(frame):
    fname = "bulk.{}.vlsv".format(str(frame).zfill(7))
    vobj = pt.vlsvfile.VlsvReader(bulkpath + fname)
    time = vobj.read_parameter("time")
    timelabel.set_text(f"{time:.1f}s")
    for artist in p:
        artist.remove()
    if def_components == 4:
        By = np.array(vobj.read_variable("vg_b_vol",operator="y")[cellids.argsort()])/1e-9
        Bz = np.array(vobj.read_variable("vg_b_vol",operator="z")[cellids.argsort()])/1e-9
        Bt = np.sqrt(By**2 + Bz**2)
        Bt_mesh = Bt.reshape(-1, 100)
        p[0] = ax.plot_surface(x_mesh, y_mesh, Bt_mesh, color = colors[0])
    else:
        for i, component in enumerate(components):
            B = np.array(vobj.read_variable("vg_b_vol",operator="{}".format(component))[cellids.argsort()])/1e-9
            B_mesh = B.reshape(-1, x_length)
            p[i] = ax.plot_surface(x_mesh, y_mesh, B_mesh, color = colors[i])
    return p

def update_v_3D(frame):
    fname = "bulk.{}.vlsv".format(str(frame).zfill(7))
    vobj = pt.vlsvfile.VlsvReader(bulkpath + fname)
    time = vobj.read_parameter("time")
    timelabel.set_text(f"{time:.1f}s")
    for artist in p:
        artist.remove()
    for i, component in enumerate(components):
        v = np.array(vobj.read_variable("proton/vg_v",operator="{}".format(component))[cellids.argsort()])/1e3
        v_mesh = v.reshape(-1, x_length)
        p[i] = ax.plot_surface(x_mesh, y_mesh, v_mesh, color = colors[i])
    return p

# Logic for choosing which kind of animation
if animation_setting == 1: # 2D heat map animation
    # Logic for choosing if magnetic field or velocity field will be animated
    if variables == 1: # Magnetic field as variable
        fig = plt.figure()
        ax = fig.add_subplot()
        Bmin = 1.5 * min(vobj.read_variable("vg_b_vol",operator="y"))/1e-9
        Bmax = 1.5 * max(vobj.read_variable("vg_b_vol",operator="y"))/1e-9
        levels = 100                                                          # How many color levels will be drawn, choose less if you want quicker animation
        level_boundaries = np.linspace(Bmin, Bmax, levels + 1)                # Used to fix colorbar to a certain range
        p = []
        # Initializing artists
        for i, component in enumerate(components):
            B = np.array(vobj.read_variable("vg_b_vol",operator="{}".format(component))[cellids.argsort()])/1e-9
            B_mesh = B.reshape(-1, x_length)
            p.append(ax.contourf(x_mesh, y_mesh, B_mesh, level_boundaries))
        # Visual stuff
        cbar = plt.colorbar(p[0])
        cbar.set_label("B [nT]")
        ax.set_xlabel("x [RE]")
        ax.set_ylabel("y [RE]")
        timelabel = ax.text(xmax,ymax*1.01,"")
        anim = animation.FuncAnimation(fig, update_B_2D, frames = bulkfile_n + 1, interval = 20)
    elif variables == 2: # Velocity as variable
        fig = plt.figure()
        ax = fig.add_subplot()
        vmin = 1.5 * min(vobj.read_variable("proton/vg_v",operator="y"))/1e3
        vmax = 1.5 * max(vobj.read_variable("proton/vg_v",operator="y"))/1e3
        levels = 100                                                          # How many color levels will be drawn, choose less if you want quicker animation
        level_boundaries = np.linspace(vmin, vmax, levels + 1)                # Used to fix colorbar to a certain range
        p = []
        # Initializing artists
        for i, component in enumerate(components):
            v = np.array(vobj.read_variable("proton/vg_v",operator="{}".format(component))[cellids.argsort()])/1e3
            v_mesh = v.reshape(-1, x_length)
            p.append(ax.contourf(x_mesh, y_mesh, v_mesh, level_boundaries))
        # Visual stuff
        cbar = plt.colorbar(p[0])
        cbar.set_label("v [km/s]")
        ax.set_xlabel("x [RE]")
        ax.set_ylabel("y [RE]")
        timelabel = ax.text(xmax,ymax*1.01,"")
        anim = animation.FuncAnimation(fig, update_v_2D, frames = bulkfile_n + 1, interval = 20)
    else:
        print("variables defined incorrectly")
elif animation_setting == 2: # 3D animation
    if variables == 1: # Magnetic field as variable
        fig = plt.figure()
        ax = fig.add_subplot(projection = '3d')
        ax.set_box_aspect((4,4,1))
        p = []
        # Initializing artists
        if def_components == 4:
            By = np.array(vobj.read_variable("vg_b_vol",operator="y")[cellids.argsort()])/1e-9
            Bz = np.array(vobj.read_variable("vg_b_vol",operator="z")[cellids.argsort()])/1e-9
            Bt = np.sqrt(By**2 + Bz**2)
            Bt_mesh = Bt.reshape(-1, 100)
            p.append(ax.plot_surface(x_mesh, y_mesh, Bt_mesh, color = colors[0],label = "Bt"))
        else:
            for i, component in enumerate(components):
                B = np.array(vobj.read_variable("vg_b_vol",operator="{}".format(component))[cellids.argsort()])/1e-9
                B_mesh = B.reshape(-1, x_length)
                p.append(ax.plot_surface(x_mesh, y_mesh, B_mesh, color = colors[i], label = "B{}".format(component)))
        # Visual stuff
        Bmin = 1.5 * min(By)
        Bmax = 1.5 * max(By)
        ax.set_zlim(Bmin, Bmax)
        ax.set_ylim(0, ymax)
        ax.set_zticks([Bmin, 0, Bmax])
        ax.set_zlabel("B [nT]")
        ax.set_xlabel("x [RE]")
        ax.set_ylabel("y [RE]")
        timelabel = ax.text(xmax, ymax*1.01, Bmax*1.5, "")
        ax.legend()
        anim = animation.FuncAnimation(fig, update_B_3D, frames = bulkfile_n + 1, interval = 20)
    elif variables == 2: # Velocity as variable
        fig = plt.figure()
        ax = fig.add_subplot(projection = '3d')
        ax.set_box_aspect((4,4,1))
        p = []
        # Initializing artists
        for i, component in enumerate(components):
            v = np.array(vobj.read_variable("proton/vg_v",operator="{}".format(component))[cellids.argsort()])/1e3
            v_mesh = v.reshape(-1, x_length)
            p.append(ax.plot_surface(x_mesh, y_mesh, v_mesh, color = colors[i], label = "v{}".format(component)))
        vmin = 1.5 * min(v)
        vmax = 1.5 * max(v)
        ax.set_zlim(vmin, vmax)
        ax.set_zticks([vmin, 0, vmax])
        ax.set_zlabel("v [km/s]")
        ax.set_xlabel("x [RE]")
        ax.set_ylabel("y [RE]")
        timelabel = ax.text(xmax, ymax*1.01, vmax*1.5, "")
        ax.legend()
        anim = animation.FuncAnimation(fig, update_v_3D, frames = bulkfile_n + 1, interval = 20)
else:
    print("animation_setting defined incorrectly")

# Write and save animation with specified name
writer = PillowWriter(fps=5)
anim.save('sim15_1000s_Bt.gif', writer = writer)
plt.close()
print("Done")