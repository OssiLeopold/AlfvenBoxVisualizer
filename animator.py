import numpy as np                  # For math
import matplotlib.pyplot as plt     # For plotting
import analysator as pt             # For manipulating .vlsv files
# Packages for gif animation
from matplotlib.animation import PillowWriter
import matplotlib.animation as mpl_animation



def update_2D(frame):
    fname = "bulk.{}.vlsv".format(str(frame).zfill(7))                                                         # Setting bulkpath to correspond with the current frame, i.e. bulkfile
    vobj = pt.vlsvfile.VlsvReader(animation.bulkpath + fname)                                                            # Defining new vojbect with new bulkpath
    time = vobj.read_parameter("time")
    timelabel.set_text(f"{time:.1f}s")
    for artist in p:                                                                                           # Removing old artist to make way for new frame
        artist.remove()
    if animation.component == "total":
        y_component = np.array(vobj.read_variable(animation.variable,operator="y")[cellids.argsort()])/animation.unit
        z_component = np.array(vobj.read_variable(animation.variable,operator="z")[cellids.argsort()])/animation.unit
        total = np.sqrt(y_component**2 + z_component**2)
        total_mesh = total.reshape(-1, x_length)
        p[0] = ax.contourf(x_mesh, y_mesh, total_mesh, level_boundaries)
    else:
        value = np.array(vobj.read_variable(animation.variable,operator=animation.component)[cellids.argsort()])/animation.unit
        value_mesh = value.reshape(-1, x_length)
        p[0] = ax.contourf(x_mesh, y_mesh, value_mesh, level_boundaries)
    return p

def animatorFunc(def_animation):
    global xmax, ymax, x_length, cellids, x_mesh, y_mesh, colors, level_boundaries, ax, p, animation, timelabel
    animation = def_animation
    vobj = pt.vlsvfile.VlsvReader(animation.bulkpath + "bulk.0000000.vlsv")
    r_e = 6371e3 # Earth radius
    x_length = vobj.read_parameter("xcells_ini") # Used for formatting numpy mesh
    xmax = vobj.read_parameter("xmax")/r_e # For now only used for placement of time legend
    ymax = vobj.read_parameter("ymax")/r_e # For now only used for placement of time legend

    cellids = vobj.read_variable("CellID")
    x = np.array([vobj.get_cell_coordinates(c)[0] for c in np.sort(cellids)])/r_e
    x_mesh = x.reshape(-1,x_length)
    y = np.array([vobj.get_cell_coordinates(c)[1] for c in np.sort(cellids)])/r_e
    y_mesh = y.reshape(-1,x_length)
    colors = ["blue", "orange"]
    
    if animation.animation_type == "2D":
        fig = plt.figure()
        ax = fig.add_subplot()

        if animation.component == "total":
            Min = 0
            Max = 1.5 * max(vobj.read_variable(animation.variable,operator="y"))/animation.unit
        else:
            Min = min(vobj.read_variable(animation.variable,operator=animation.component))/animation.unit
            Max = max(vobj.read_variable(animation.variable,operator=animation.component))/animation.unit

        levels = 100                                                          # How many color levels will be drawn, choose less if you want quicker animation
        level_boundaries = np.linspace(Min, Max, levels + 1)                  # Used to fix colorbar to a certain range

        p = []
        if animation.component == "total":
            y_component = np.array(vobj.read_variable(animation.variable,operator="y")[cellids.argsort()])/animation.unit
            z_component = np.array(vobj.read_variable(animation.variable,operator="z")[cellids.argsort()])/animation.unit
            total = np.sqrt(y_component**2 + z_component**2)
            total_mesh = total.reshape(-1, x_length)
            p.append(ax.contourf(x_mesh, y_mesh, total_mesh, level_boundaries))
        else:
            value = np.array(vobj.read_variable(animation.variable,operator=animation.component)[cellids.argsort()])/animation.unit
            value_mesh = value.reshape(-1, x_length)
            p.append(ax.contourf(x_mesh, y_mesh, value_mesh, level_boundaries))

        cbar = plt.colorbar(p[0], cmap = "hot")
        cbar.set_label("B [nT]" if animation.variable == "vg_b_vol" else "v [km/s]")
        ax.set_xlabel("x [RE]")
        ax.set_ylabel("y [RE]")
        timelabel = ax.text(xmax, ymax*1.01, "")
        anim = mpl_animation.FuncAnimation(fig, update_2D, frames = animation.bulkfile_n + 1, interval = 20)

        writer = PillowWriter(fps=5)
        anim.save(animation.name, writer = writer)
        plt.close()
        print("Done")

    else:
        print("gukki")

