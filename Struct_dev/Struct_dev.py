import analysator as pt
import matplotlib.pyplot as plt
import os
from matplotlib import animation
from matplotlib.animation import FFMpegWriter
import numpy as np
import statistics
import seaborn as sns
plt.rcParams['animation.ffmpeg_path'] = "/home/rxelmer/Documents/turso/appl_local/ffmpeg/bin/ffmpeg"

os.environ['PATH']='/home/rxelmer/Documents/turso/appl_local/tex-basic/texlive/2023/bin/x86_64-linux:'+ os.environ['PATH'] 
os.environ['PTNOLATEX']='1'
bulkpath = "/home/rxelmer/Documents/turso/bulks/sim21/"

fig, axes = plt.subplots(3,3,figsize=(16,12))
axes = axes.flatten()

titles = ["delta_l11", "delta_l12", "delta_l14", "delta_l17", "delta_l20", "delta_l25", "delta_l33","delta_l50","delta_l75"]

def update(frame):
    # Clear axes for new frame
    for ax in axes:
        ax.clear()

    # Fetch data from bulkfile
    vlsvobj = pt.vlsvfile.VlsvReader(bulkpath + f"bulk.{str(frame).zfill(7)}.vlsv")
    cellids = vlsvobj.read_variable("CellID")
    value = np.array(vlsvobj.read_variable("vg_b_vol", operator = "y"))[cellids.argsort()]

    # Create two 2D_arrays. One in the x direction and one in the y direction
    value_mesh_x = value.reshape(-1,100)
    value_mesh_y = value_mesh_x.T
    
    # Calculate statistical parameters from data in each frame
    mean = statistics.mean(value)
    SD = statistics.stdev(value)
    
    # Create empty arrays for 
    delta_l11 = []
    delta_l12 = []
    delta_l14 = []
    delta_l17 = []
    delta_l20 = []
    delta_l25 = []
    delta_l33 = []
    delta_l50 = []
    delta_l75 = []

    L = 100

    # Loop through all slices
    for i in range(L):
        value_slice_x = value_mesh_x[i]
        value_slice_y = value_mesh_y[i]

        for j in range(0,L):
            if j + 11 >= L:
                delta_l11.append(value_slice_x[j+11-L]-value_slice_x[j])
                delta_l11.append(value_slice_y[j+11-L]-value_slice_y[j])
            else:
                delta_l11.append(value_slice_x[j+11]-value_slice_x[j])
                delta_l11.append(value_slice_y[j+11]-value_slice_y[j])

        for j in range(0,L):
            if j + 12 >= L:
                delta_l12.append(value_slice_x[j+12-L]-value_slice_x[j])
                delta_l12.append(value_slice_y[j+12-L]-value_slice_y[j])
            else:
                delta_l12.append(value_slice_x[j+12]-value_slice_x[j])
                delta_l12.append(value_slice_y[j+12]-value_slice_y[j])

        for j in range(0,L):
            if j + 14 >= L:
                delta_l14.append(value_slice_x[j+14-L]-value_slice_x[j])
                delta_l14.append(value_slice_y[j+14-L]-value_slice_y[j])
            else:
                delta_l14.append(value_slice_x[j+14]-value_slice_x[j])
                delta_l14.append(value_slice_y[j+14]-value_slice_y[j])

        for j in range(0,L):
            if j + 17 >= L:
                delta_l17.append(value_slice_x[j+17-L]-value_slice_x[j])
                delta_l17.append(value_slice_y[j+17-L]-value_slice_y[j])
            else:
                delta_l17.append(value_slice_x[j+17]-value_slice_x[j])
                delta_l17.append(value_slice_y[j+17]-value_slice_y[j])

        for j in range(0,L):
            if j + 25 >= L:
                delta_l25.append(value_slice_x[j+25-L]-value_slice_x[j])
                delta_l25.append(value_slice_y[j+25-L]-value_slice_y[j])
            else:
                delta_l25.append(value_slice_x[j+25]-value_slice_x[j])
                delta_l25.append(value_slice_y[j+25]-value_slice_y[j])

        for j in range(0,L):
            if j + 50 >= L:
                delta_l50.append(value_slice_x[j+50-L]-value_slice_x[j])
                delta_l50.append(value_slice_y[j+50-L]-value_slice_y[j])
            else:
                delta_l50.append(value_slice_x[j+50]-value_slice_x[j])
                delta_l50.append(value_slice_y[j+50]-value_slice_y[j])

        for j in range(0,L):
            if j + 75 >= L:
                delta_l75.append(value_slice_x[j+75-L]-value_slice_x[j])
                delta_l75.append(value_slice_y[j+75-L]-value_slice_y[j])
            else:
                delta_l75.append(value_slice_x[j+75]-value_slice_x[j])
                delta_l75.append(value_slice_y[j+75]-value_slice_y[j])

        for j in range(0,L):
            if j + 20 >= L:
                delta_l20.append(value_slice_x[j+20-L]-value_slice_x[j])
                delta_l20.append(value_slice_y[j+20-L]-value_slice_y[j])
            else:
                delta_l20.append(value_slice_x[j+20]-value_slice_x[j])
                delta_l20.append(value_slice_y[j+20]-value_slice_y[j])

        for j in range(0,L):
            if j + 33 >= L:
                delta_l33.append(value_slice_x[j+33-L]-value_slice_x[j])
                delta_l33.append(value_slice_y[j+33-L]-value_slice_y[j])
            else:
                delta_l33.append(value_slice_x[j+33]-value_slice_x[j])
                delta_l33.append(value_slice_y[j+33]-value_slice_y[j])


    deltas = [delta_l11,delta_l12,delta_l14,delta_l17,delta_l20,delta_l25,delta_l33,delta_l50,delta_l75]
    deltas_np = []
    
    for delta in deltas:
        deltas_np.append(np.array(delta))

    gaussians = []

    """ for i in range(len(deltas_np)):
        mean = statistics.mean(deltas_np[i])
        SD = statistics.stdev(deltas_np[i])
        gaussians.append((1 / (SD * np.sqrt(2*np.pi))) * np.exp(-(1/2)*(deltas_np[i]-mean)**2 / SD**2))
        deltas_np[i] = (deltas_np[i] - mean) / SD """

    gaussian = np.random.normal(mean, SD, 10000)/SD

    for i, ax in enumerate(axes):
        mean = statistics.mean(deltas_np[i])
        SD = statistics.stdev(deltas_np[i])
        deltas_np[i] = (deltas_np[i] - mean) / SD

        ax.hist(deltas_np[i], bins=100, density=True)
        
        gaussian = np.random.normal(mean, SD, 10000)/SD
        sns.kdeplot(gaussian, ax=ax, ls = ":")

        ax.set_title(titles[i])
        ax.set_xlim(-6,6)
        ax.set_yscale("log")
        ax.set_ylim(1e-3,1)

anim = animation.FuncAnimation(fig, update, frames = 50, interval = 20)

writer = FFMpegWriter(fps=5)
anim.save("struct_By_sim20_big_boy_100bins.mp4", writer=writer)
plt.close()