import analysator as pt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation

R_E = 6371e3 # Earth radius
COLORS = ["blue", "orange"]

class AnimationEngine:
    def __init__(self, object):
        self.object = object

        vlsvobj = pt.vlsvfile.VlsvReader(object.bulkpath + "bulk.0000000.vlsv")
        self.cellids = vlsvobj.read_variable("CellID")
        self.x_length = vlsvobj.read_parameter("xcells_ini") # Used for formatting numpy mesh
        self.xmax = vlsvobj.read_parameter("xmax")/R_E # For now only used for placement of time legend
        self.ymax = vlsvobj.read_parameter("ymax")/R_E # For now only used for placement of time legend

        x = np.array([vlsvobj.get_cell_coordinates(coord)[0] for coord in np.sort(self.cellids)]) / R_E
        y = np.array([vlsvobj.get_cell_coordinates(coord)[1] for coord in np.sort(self.cellids)]) / R_E
        self.x_mesh = x.reshape(-1,self.x_length)
        self.y_mesh = y.reshape(-1,self.x_length)
        
        self.vlsvobj = vlsvobj
        self.cid_sort = self.cellids.argsort()

        if object.animation_type == "2D":
            self.animation_2D()

        elif object.animation_type == "3D":
            self.animation_3D()

    def animation_2D(self):
        vlsvobj = self.vlsvobj
        object = self.object
        cid_sort = self.cid_sort

        fig = plt.figure()
        ax = fig.add_subplot()

        if object.component == "total":
            Min = 0
            Max = 1.5 * max(vlsvobj.read_variable(object.variable,operator="y")) / object.unit
        else:
            Min = min(vlsvobj.read_variable(vlsvobj.variable, operator=object.component)) / object.unit
            Max = max(vlsvobj.read_variable(vlsvobj.variable, operator=object.component)) / object.unit

        levels = 100                                                      
        level_boundaries = np.linspace(Min, Max, levels + 1)
        self.level_boundaries = level_boundaries

        p = []
        if object.component == "total":
            y = np.array(vlsvobj.read_variable(object.variable, operator="y")[cid_sort]) / object.unit
            z = np.array(vlsvobj.read_variable(object.variable, operator="z")[cid_sort]) / object.unit
            magnitude = np.sqrt(y**2 + z**2)
            magnitude_mesh = magnitude.reshape(-1, self.x_length)
            p.append(ax.contourf(self.x_mesh, self.y_mesh, magnitude_mesh, level_boundaries))
        else:
            value = np.array(vlsvobj.read_variable(object.variable, operator=object.component)[cid_sort]) / object.unit
            value_mesh = value.reshape(-1, self.x_length)
            p.append(ax.contourf(self.x_mesh, self.y_mesh, value_mesh, level_boundaries))
        
        self.p = p
        self.ax = ax

        cbar = plt.colorbar(p[0], cmap = "hot")
        if object.variable == "vg_b_vol":
            cbar.colorbar(f"B_{object.component} [nT]")
        elif object.variable == "proton/vg_v":
            cbar.set_zlabel(f"v_{object.component} [km/s]")

        p[0].set_xlabel("x [RE]")
        p[0].set_ylabel("y [RE]")
        self.timelabel = ax.text(self.xmax, self.ymax*1.01, "")

        anim = animation.FuncAnimation(fig, self.update_2D, frames = object.bulkfile_n + 1, interval = 20)

        writer = animation.PillowWriter(fps=5)
        anim.save(animation.name, writer = writer)
        plt.close()

    def update_2D(self, frame):
        self.p.remove()
        fname = f"bulk.{str(frame).zfill(7)}.vlsv"
        vlsvobj = pt.vlsvfile.VlsvReader(object.bulkpath + fname)   

        time = vlsvobj.read_parameter("time")
        self.timelabel.set_text(f"{time:.1f}s")
        
        if object.component == "total":
            y = np.array(vlsvobj.read_variable(object.variable, operator="y")[self.cid_sort]) / object.unit
            z = np.array(vlsvobj.read_variable(object.variable, operator="z")[self.cid_sort]) / object.unit
            magnitude = np.sqrt(y**2 + z**2)
            magnitude_mesh = magnitude.reshape(-1, self.x_length)
            self.p[0] = self.ax.contourf(self.x_mesh, self.y_mesh, magnitude_mesh, self.level_boundaries)
        else:
            value = np.array(vlsvobj.read_variable(object.variable, operator=object.component)[self.cid_sort]) / object.unit
            value_mesh = value.reshape(-1, self.x_length)
            self.p[0] = self.ax.contourf(self.x_mesh, self.y_mesh, value_mesh, self.level_boundaries)

        return self.p

