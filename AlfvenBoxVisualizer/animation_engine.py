import os
import analysator as pt
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
from multiprocessing import shared_memory
from matplotlib import animation
import matplotlib as mpl
from matplotlib.animation import FFMpegWriter
plt.rcParams['animation.ffmpeg_path'] = "/home/rxelmer/Documents/turso/appl_local/ffmpeg/bin/ffmpeg"
#enabling use of latex
os.environ['PATH']='/home/rxelmer/Documents/turso/appl_local/tex-basic/texlive/2023/bin/x86_64-linux:'+ os.environ['PATH'] 
os.environ['PTNOLATEX']='1'

R_E = 6371e3 # Earth radius
COLORS = ["blue", "orange"]

class AnimationEngine:
    def __init__(self, object):
        self.object = object

        vlsvobj = pt.vlsvfile.VlsvReader(object.bulkpath + "bulk.0000000.vlsv")
        self.cellids = vlsvobj.read_variable("CellID") # Used for sorting variables read by VlsvReader
        self.x_length = vlsvobj.read_parameter("xcells_ini") # Used for formatting numpy mesh
        self.xmax = vlsvobj.read_parameter("xmax") / R_E
        self.ymax = vlsvobj.read_parameter("ymax") / R_E

        # Used in plotting
        x = np.array([vlsvobj.get_cell_coordinates(coord)[0] for coord in np.sort(self.cellids)]) / R_E
        y = np.array([vlsvobj.get_cell_coordinates(coord)[1] for coord in np.sort(self.cellids)]) / R_E
        x_raw = np.array([vlsvobj.get_cell_coordinates(coord)[0] for coord in np.sort(self.cellids)]) # Used for fourier spatial frequency
        # Bring to class scope
        self.x_mesh = x.reshape(-1,self.x_length)
        self.y_mesh = y.reshape(-1,self.x_length)
        self.x_raw = x_raw
        
        # Bring to class scope
        self.vlsvobj = vlsvobj

        if self.object.animation_type == "2D":
            self.animation_2D()

        elif self.object.animation_type == "3D":
            self.animation_3D()

        elif self.object.animation_type == "fourier":
            if self.object.fourier_type == "princpile":
                self.animation_principle()

            elif self.object.fourier_type == "diag":
                self.animation_diag()

            elif self.object.fourier_type == "trace":
                self.animation_trace()

            elif self.object.fourier_type == "trace_diag":
                self.animation_trace_diag()

    def animation_principle(self):
        object = self.object # For shorter notation
        cellids = self.vlsvobj.read_variable("CellID")
        N = int(self.x_length) # scipy fourier transforms require that np.float -> int

        fig, ax = plt.subplots()
        
        value = np.array(self.vlsvobj.read_variable(object.variable, operator=object.component)[cellids.argsort()])

        if object.fourier_direc == "x":
            value_mesh = value.reshape(-1,100)
        elif object.fourier_direc == "y":
            value_mesh = value.reshape(-1,100)
            value_mesh = value_mesh.T

        # Take Fourier transfrom from a slice in the specified location
        value_ft = sp.fft.fft(value_mesh[int(N * float(object.fourier_loc))])

        # Define spatial frequency
        spatial_freq = sp.fft.fftfreq(N, np.diff(self.x_raw[0:N])[0])
        self.spatial_freq = spatial_freq

        # Define artists
        p = []
        p.append(ax.plot( 2*np.pi * spatial_freq[:N//2], np.abs(value_ft[:N//2])))

        # Find maximum for better plotting
        max_check = []
        for i in range(object.bulkfile_n):
            vlsvobj = pt.vlsvfile.VlsvReader(object.bulkpath + f"bulk.{str(i).zfill(7)}.vlsv")
            cellids = vlsvobj.read_variable("CellID")
            value_check = np.array(vlsvobj.read_variable(object.variable, operator=object.component)[cellids.argsort()])
            if object.fourier_direc == "x":
                value_mesh_check = value_check.reshape(-1,100)
            elif object.fourier_direc == "y":
                value_mesh_check = value_check.reshape(-1,100)
                value_mesh_check = value_mesh_check.T
            max_check.extend(sp.fft.fft(value_mesh_check[int(N * float(object.fourier_loc))])[1:N//2])
        Max = max(np.abs(max_check))

        a = Max * (10**(-6))**2
        b = Max * (10**(-6))**(5/3)

        # Define power spectrum curves. First element of spatial_freq deleted due to singularity
        spatial_freq_for_curve = np.delete(spatial_freq,0)
        p.append(ax.plot(2*np.pi * spatial_freq_for_curve[:N//2-1], a * (2*np.pi*spatial_freq_for_curve[:N//2-1])**(-2), label = "k**(-2)"))
        p.append(ax.plot(2*np.pi * spatial_freq_for_curve[:N//2-1], b * (2*np.pi*spatial_freq_for_curve[:N//2-1])**(-5/3), label = "k**(-5/3)"))

        # Bring to class scope
        self.p = p
        self.ax = ax

        ax.set_title(f"Fourier transform of {object.variable_name}")
        ax.set_xlabel("k")
        ax.set_ylabel(f"{object.unit_name}**2/k")

        ax.set_ylim(Max*10**(-3),Max*10)
        for i in range(1,10):
            ax.axvline(x = 2 * np.pi / (1.5*10**7 / i), lw = 0.5)
        ax.set_yscale("log")
        ax.set_xscale("log")
        ax.grid(axis="y")
        ax.legend()

        self.timelabel = ax.text(max(spatial_freq), max(np.abs(value_ft))*1.01, "")

        anim = animation.FuncAnimation(fig, self.update_princpile, frames = object.bulkfile_n + 1, interval = 20)
        
        writer = FFMpegWriter(fps=5)
        anim.save(object.name, writer = writer)
        plt.close()

    def update_princpile(self, frame):
        N = int(self.x_length)
        object = self.object
        vlsvobj = pt.vlsvfile.VlsvReader(object.bulkpath + f"bulk.{str(frame).zfill(7)}.vlsv")
        cellids = vlsvobj.read_variable("CellID")

        time = vlsvobj.read_parameter("time")
        self.timelabel.set_text(f"{time:.1f}s")

        value = np.array(vlsvobj.read_variable(object.variable, operator=object.component)[cellids.argsort()])
        if object.fourier_direc == "x":
            value_mesh = value.reshape(-1,100)
        elif object.fourier_direc == "y":
            value_mesh = value.reshape(-1,100)
            value_mesh = value_mesh.T

        value_ft = sp.fft.fft(value_mesh[int(N * float(object.fourier_loc))])

        self.p[0][0].set_data(2*np.pi*self.spatial_freq[:N//2], np.abs(value_ft[:N//2]))

        return self.p

    def animation_diag(self):
        vlsvobj = self.vlsvobj
        object = self.object
        cellids = vlsvobj.read_variable("CellID")
        N = int(self.x_length)

        fig = plt.figure()
        ax = fig.add_subplot()
        
        value = np.array(vlsvobj.read_variable(object.variable, operator=object.component)[cellids.argsort()])

        value_mesh = value.reshape(-1,100)

        diag_value_mesh = []

        if object.fourier_direc == 1:
            for i in range(N):
                diag_value_mesh.append(value_mesh[i][i])
        elif object.fourier_direc == 2:
            for i in range(N):
                diag_value_mesh.append(value_mesh[-i-1][i])

        # Take Fourier transfrom from a slice in the specified location
        value_ft = sp.fft.fft(diag_value_mesh)

        # Define spatial frequency
        spatial_freq = sp.fft.fftfreq(N, np.sqrt(2) * np.diff(self.x_raw[0:N])[0])
        self.spatial_freq = spatial_freq

        # Define artists
        p = []
        p.append(ax.plot( 2*np.pi * spatial_freq[:N//2], np.abs(value_ft[:N//2])))

        # Define power spectrum curves. First element of spatial_freq deleted due to singularity
        spatial_freq_for_curve = np.delete(spatial_freq,0)
        max_check = []
        for i in range(object.bulkfile_n):
            vlsvobj = pt.vlsvfile.VlsvReader(object.bulkpath + f"bulk.{str(i).zfill(7)}.vlsv")
            cellids = vlsvobj.read_variable("CellID")
            diag_value_mesh_check = []
            value_check = np.array(vlsvobj.read_variable(object.variable, operator=object.component)[cellids.argsort()])
            value_check_mesh = value_check.reshape(-1,100)
            if object.fourier_direc == 1:
                for j in range(N):
                    diag_value_mesh_check.append(value_check_mesh[j][j])
            elif object.fourier_direc == 2:
                for j in range(N):
                    diag_value_mesh_check.append(value_check_mesh[-j-1][j])
            max_check.extend(sp.fft.fft(diag_value_mesh_check)[1:N//2])
        Max = max(np.abs(max_check))
        a = Max * (10**(-6))**2
        b = Max * (10**(-6))**(5/3)

        p.append(ax.plot(2*np.pi * spatial_freq_for_curve[:N//2-1], a * (2*np.pi*spatial_freq_for_curve[:N//2-1])**(-2), label = "k**(-2)"))
        p.append(ax.plot(2*np.pi * spatial_freq_for_curve[:N//2-1], b * (2*np.pi*spatial_freq_for_curve[:N//2-1])**(-5/3), label = "k**(-5/3)"))

        self.p = p
        self.ax = ax

        ax.set_title(f"Fourier transform of {object.variable_name}")
        ax.set_xlabel("k")
        ax.set_ylabel(f"{object.unit_name}**2/k")

        ax.set_ylim(Max*10**(-3),Max*10)
        for i in range(1,10):
            ax.axvline(x = 2 * np.pi / (1.5*10**7 / i), lw = 0.5)
        ax.set_yscale("log")
        ax.set_xscale("log")
        ax.grid(axis="y")
        ax.legend()

        self.timelabel = ax.text(max(spatial_freq), max(np.abs(value_ft))*1.01, "")

        anim = animation.FuncAnimation(fig, self.update_diag, frames = object.bulkfile_n + 1, interval = 20)
        
        writer = FFMpegWriter(fps=5)
        anim.save(object.name, writer = writer)
        plt.close()

    def update_diag(self, frame):
        N = int(self.x_length)
        object = self.object
        vlsvobj = pt.vlsvfile.VlsvReader(object.bulkpath + f"bulk.{str(frame).zfill(7)}.vlsv")
        cellids = vlsvobj.read_variable("CellID")

        time = vlsvobj.read_parameter("time")
        self.timelabel.set_text(f"{time:.1f}s")

        value = np.array(vlsvobj.read_variable(object.variable, operator=object.component)[cellids.argsort()])

        value_mesh = value.reshape(-1,100)

        diag_value_mesh = []

        if object.fourier_direc == 1:
            for i in range(N):
                diag_value_mesh.append(value_mesh[i][i])
        elif object.fourier_direc == 2:
            for i in range(N):
                diag_value_mesh.append(value_mesh[-i-1][i])

        # Take Fourier transfrom from a slice in the specified location
        value_ft = sp.fft.fft(diag_value_mesh)

        self.p[0][0].set_data(2*np.pi*self.spatial_freq[:N//2], np.abs(value_ft[:N//2]))

        return self.p
    
    def animation_trace(self):
        vlsvobj = self.vlsvobj
        object = self.object
        cellids = vlsvobj.read_variable("CellID")
        N = int(self.x_length)

        fig = plt.figure()
        ax = fig.add_subplot()
        
        value = np.array(vlsvobj.read_variable(object.variable, operator=object.component)[cellids.argsort()])

        value_mesh_x = value.reshape(-1,100)
        value_mesh_y = value_mesh_x.T

        # Take Fourier transfrom from a slice in the specified location
        value_ft_x = sp.fft.fft(value_mesh_x[int(N * float(object.fourier_loc_x))])
        value_ft_y = sp.fft.fft(value_mesh_y[int(N * float(object.fourier_loc_y))])
        trace_ft = value_ft_x + value_ft_y

        # Define spatial frequency
        spatial_freq = sp.fft.fftfreq(N, np.diff(self.x_raw[0:N])[0])
        self.spatial_freq = spatial_freq

        # Define artists
        p = []
        p.append(ax.plot( 2*np.pi * spatial_freq[:N//2], np.abs(trace_ft[:N//2])))

        # Define power spectrum curves. First element of spatial_freq deleted due to singularity
        spatial_freq_for_curve = np.delete(spatial_freq,0)
        max_check = []
        for i in range(object.bulkfile_n):
            vlsvobj = pt.vlsvfile.VlsvReader(object.bulkpath + f"bulk.{str(i).zfill(7)}.vlsv")
            cellids = vlsvobj.read_variable("CellID")
            value_check = np.array(vlsvobj.read_variable(object.variable, operator=object.component)[cellids.argsort()])
            value_mesh_check_x = value_check.reshape(-1,100)
            value_mesh_check_y = value_mesh_check_x.T
            value_ft_check_x = sp.fft.fft(value_mesh_check_x[int(N * float(object.fourier_loc_x))])
            value_ft_check_y = sp.fft.fft(value_mesh_check_y[int(N * float(object.fourier_loc_y))])
            max_check.extend((value_ft_check_x + value_ft_check_y)[1:N//2])
        Max = max(np.abs(max_check))
        a = Max * (10**(-6))**2
        b = Max * (10**(-6))**(5/3)

        p.append(ax.plot(2*np.pi * spatial_freq_for_curve[:N//2-1], a * (2*np.pi*spatial_freq_for_curve[:N//2-1])**(-2), label = "k**(-2)"))
        p.append(ax.plot(2*np.pi * spatial_freq_for_curve[:N//2-1], b * (2*np.pi*spatial_freq_for_curve[:N//2-1])**(-5/3), label = "k**(-5/3)"))

        self.p = p
        self.ax = ax

        ax.set_title(f"Fourier transform of {object.variable_name}")
        ax.set_xlabel("k")
        ax.set_ylabel(f"{object.unit_name}**2/k")

        ax.set_ylim(Max*10**(-3),Max*10)
        for i in range(1,10):
            ax.axvline(x = 2 * np.pi / (1.5*10**7 / i), lw = 0.5)
        ax.set_yscale("log")
        ax.set_xscale("log")
        ax.grid(axis="y")
        ax.legend()

        self.timelabel = ax.text(max(spatial_freq), max(np.abs(trace_ft))*1.01, "")

        anim = animation.FuncAnimation(fig, self.update_trace, frames = object.bulkfile_n + 1, interval = 20)
        
        writer = FFMpegWriter(fps=5)
        anim.save(object.name, writer = writer)
        plt.close()

    def update_trace(self, frame):
        N = int(self.x_length)
        object = self.object
        vlsvobj = pt.vlsvfile.VlsvReader(object.bulkpath + f"bulk.{str(frame).zfill(7)}.vlsv")
        cellids = vlsvobj.read_variable("CellID")

        time = vlsvobj.read_parameter("time")
        self.timelabel.set_text(f"{time:.1f}s")

        value = np.array(vlsvobj.read_variable(object.variable, operator=object.component)[cellids.argsort()])

        value_mesh_x = value.reshape(-1,100)
        value_mesh_y = value_mesh_x.T

        # Take Fourier transfroms from a slice in the specified location
        value_ft_x = sp.fft.fft(value_mesh_x[int(N * float(object.fourier_loc_x))])
        value_ft_y = sp.fft.fft(value_mesh_y[int(N * float(object.fourier_loc_y))])
        trace_ft = value_ft_x + value_ft_y

        self.p[0][0].set_data(2*np.pi*self.spatial_freq[:N//2], np.abs(trace_ft[:N//2]))

        return self.p
    
    def animation_trace_diag(self):
        vlsvobj = self.vlsvobj
        object = self.object
        cellids = vlsvobj.read_variable("CellID")
        N = int(self.x_length)

        fig = plt.figure()
        ax = fig.add_subplot()
        
        value = np.array(vlsvobj.read_variable(object.variable, operator=object.component)[cellids.argsort()])
        value_mesh = value.reshape(-1,100)

        diag_value_SW = []
        diag_value_NW = []

        for i in range(N):
            diag_value_SW.append(value_mesh[i][i])
            diag_value_NW.append(value_mesh[-i-1][i])

        # Take Fourier transfrom from a slice in the specified location
        value_ft_SW = sp.fft.fft(diag_value_SW)
        value_ft_NW = sp.fft.fft(diag_value_NW)
        trace_ft = value_ft_SW + value_ft_NW

        # Define spatial frequency
        spatial_freq = sp.fft.fftfreq(N, np.sqrt(2) * np.diff(self.x_raw[0:N])[0])
        self.spatial_freq = spatial_freq

        # Define artists
        p = []
        p.append(ax.plot( 2*np.pi * spatial_freq[:N//2], np.abs(trace_ft[:N//2])))

        # Define power spectrum curves. First element of spatial_freq deleted due to singularity
        spatial_freq_for_curve = np.delete(spatial_freq,0)
        max_check = []
        for i in range(object.bulkfile_n):
            vlsvobj = pt.vlsvfile.VlsvReader(object.bulkpath + f"bulk.{str(i).zfill(7)}.vlsv")
            cellids = vlsvobj.read_variable("CellID")
            value_check = np.array(vlsvobj.read_variable(object.variable, operator=object.component)[cellids.argsort()])
            value_check_mesh = value_check.reshape(-1,100)
            diag_value_check_SW = []
            diag_value_check_NW = []
            for j in range(N):
                diag_value_check_SW.append(value_check_mesh[j][j])
                diag_value_check_NW.append(value_check_mesh[-j-1][j])
            diag_value_check_SW_ft = sp.fft.fft(diag_value_check_SW)
            diag_value_check_NW_ft = sp.fft.fft(diag_value_check_NW)
            max_check.extend((diag_value_check_SW_ft + diag_value_check_NW_ft)[1:N//2])
        Max = max(np.abs(max_check))
        a = Max * (10**(-6))**2
        b = Max * (10**(-6))**(5/3)

        p.append(ax.plot(2*np.pi * spatial_freq_for_curve[:N//2-1], a * (2*np.pi*spatial_freq_for_curve[:N//2-1])**(-2), label = "k**(-2)"))
        p.append(ax.plot(2*np.pi * spatial_freq_for_curve[:N//2-1], b * (2*np.pi*spatial_freq_for_curve[:N//2-1])**(-5/3), label = "k**(-5/3)"))

        self.p = p
        self.ax = ax

        ax.set_title(f"Fourier transform of {object.variable_name}")
        ax.set_xlabel("k")
        ax.set_ylabel(f"{object.unit_name}**2/k")

        ax.set_ylim(Max*10**(-3),Max*10)
        for i in range(1,10):
            ax.axvline(x = 2 * np.pi / (1.5*10**7 / i), lw = 0.5)
        ax.set_yscale("log")
        ax.set_xscale("log")
        ax.grid(axis="y")
        ax.legend()

        self.timelabel = ax.text(max(spatial_freq), max(np.abs(trace_ft))*1.01, "")

        anim = animation.FuncAnimation(fig, self.update_trace_diag, frames = object.bulkfile_n + 1, interval = 20)
        
        writer = FFMpegWriter(fps=5)
        anim.save(object.name, writer = writer)
        plt.close()

    def update_trace_diag(self, frame):
        N = int(self.x_length)
        object = self.object
        vlsvobj = pt.vlsvfile.VlsvReader(object.bulkpath + f"bulk.{str(frame).zfill(7)}.vlsv")
        cellids = vlsvobj.read_variable("CellID")

        time = vlsvobj.read_parameter("time")
        self.timelabel.set_text(f"{time:.1f}s")

        value = np.array(vlsvobj.read_variable(object.variable, operator=object.component)[cellids.argsort()])
        value_mesh = value.reshape(-1,100)

        diag_value_SW = []
        diag_value_NW = []

        for i in range(N):
            diag_value_SW.append(value_mesh[i][i])
            diag_value_NW.append(value_mesh[-i-1][i])

        # Take Fourier transfrom from a slice in the specified location
        value_ft_SW = sp.fft.fft(diag_value_SW)
        value_ft_NW = sp.fft.fft(diag_value_NW)
        trace_ft = value_ft_SW + value_ft_NW

        self.p[0][0].set_data(2*np.pi*self.spatial_freq[:N//2], np.abs(trace_ft[:N//2]))

        return self.p

    def animation_2D(self):
        fig, self.ax = plt.subplots()
        vlsvobj = self.vlsvobj
        self.Min, self.Max = self.def_min_max()

        if abs(self.Min) > abs(self.Max):
            self.Max = -self.Min
        else:
            self.Min = -self.Max

        self.p = [pt.plot.plot_colormap(
            vlsvobj = vlsvobj, var = self.object.variable, operator = self.object.component, axes=self.ax, vmin = self.Min, vmax = self.Max)]

        anim = animation.FuncAnimation(fig, self.update_2D, frames = self.object.bulkfile_n + 1, interval = 20)

        writer = FFMpegWriter(fps=5)
        anim.save(self.object.name, writer = writer)
        plt.close()

    def update_2D(self, frame):
        self.p.clear()
        # fetch vlsv file
        vlsvobj = pt.vlsvfile.VlsvReader(self.object.bulkpath + f"bulk.{str(frame).zfill(7)}.vlsv")
        pt.plot.plot_colormap(
            vlsvobj = vlsvobj, var = self.object.variable, operator = self.object.component, axes=self.ax, vmin = self.Min, vmax = self.Max, nocb = "No")
        return self.p

    def animation_3D(self):
        vlsvobj = self.vlsvobj
        object = self.object
        cellids = vlsvobj.read_variable("CellID")

        fig = plt.figure()
        ax = fig.add_subplot(projection = '3d')

        Min, Max = self.def_min_max()

        p = []
        value = np.array(vlsvobj.read_variable(object.variable, operator=object.component)[cellids.argsort()]) / object.unit
        value_mesh = value.reshape(-1, self.x_length)
        p.append(ax.plot_surface(self.x_mesh, self.y_mesh, value_mesh, color = COLORS[0]))

        self.p = p
        self.ax = ax

        ax.set_zlabel(f"{object.variable_name} [{object.unit_name}]")
        ax.set_title(f"{object.variable_name} [{object.unit_name}]")

        if object.variable == "vg_b_vol" and object.component == "x":
            ax.set_zlim(Min*0.9, Max*1.1)
        else:
            ax.set_zlim(Min, Max)
        
        ax.set_ylim(0, self.ymax)

        ax.set_xlabel("x [RE]")
        ax.set_ylabel("y [RE]")
        self.timelabel = ax.text(self.xmax, self.ymax*1.01, Max*1.01, "")

        anim = animation.FuncAnimation(fig, self.update_3D, frames = object.bulkfile_n + 1, interval = 20)

        writer = FFMpegWriter(fps=5)
        anim.save(object.name, writer = writer)
        plt.close()

    def update_3D(self, frame):
        self.p[0].remove()
        object = self.object
        vlsvobj = pt.vlsvfile.VlsvReader(object.bulkpath + f"bulk.{str(frame).zfill(7)}.vlsv")  
        cellids = vlsvobj.read_variable("CellID")

        time = vlsvobj.read_parameter("time")
        self.timelabel.set_text(f"{time:.1f}s")
        
        value = np.array(vlsvobj.read_variable(object.variable, operator=object.component)[cellids.argsort()]) / object.unit
        value_mesh = value.reshape(-1, self.x_length)
        self.p[0] = self.ax.plot_surface(self.x_mesh, self.y_mesh, value_mesh, color = COLORS[0])

        return self.p
    
    """ def PDF(self): """


    def def_min_max(self):
        object = self.object
        values = []
        for i in range(object.bulkfile_n):
            vlsvobj = pt.vlsvfile.VlsvReader(object.bulkpath + f"bulk.{str(i).zfill(7)}.vlsv")   
            values.extend(
                vlsvobj.read_variable(object.variable,operator=f"{object.component if object.component is not None else "pass"}"))
        return min(values), max(values)
    
