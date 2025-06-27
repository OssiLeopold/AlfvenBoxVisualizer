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
bulkpath = "/home/rxelmer/Documents/turso/bulks/sim1/"

fig, axes = plt.subplots(3,3,figsize=(16,12))
axes = axes.flatten()

# Choose what variable and component you want to be animated
variable = "vg_b_vol"
component = "y"

fig.suptitle("B_y structure function")

# Choose nine deltas you want animated
delta_ls = [2,4,6,8,10,12,14,16,20]

# Generate titles
titles = []
for i in range(9):
    titles.append(f"delta_l_{delta_ls[i]}")

def update(frame):
    # Clear axes for new frame
    for ax in axes:
        ax.clear()

    # Fetch data from bulkfile
    vlsvobj = pt.vlsvfile.VlsvReader(bulkpath + f"bulk.{str(1+frame).zfill(7)}.vlsv")
    cellids = vlsvobj.read_variable("CellID")
    value = np.array(vlsvobj.read_variable(variable, operator = component))[cellids.argsort()]

    # Create two 2D_arrays. One in the x direction and one in the y direction and define length
    value_mesh_x = value.reshape(-1,100)
    value_mesh_y = value_mesh_x.T
    L = len(value_mesh_x)
    
    # Calculate statistical parameters from data in each frame
    mean = statistics.mean(value)
    SD = statistics.stdev(value)
    
    # Create empty arrays for differences
    delta_array_container = []

    # Determine delta_values from data
    for dl in delta_ls:
        delta = []
        #for j in range(L):
        value_slice_x = value_mesh_x[50]
        value_slice_y = value_mesh_y[50]

        for k in range(L):
            if k + dl >= L:
                delta.append(value_slice_x[k+dl-L]-value_slice_x[k])
                delta.append(value_slice_y[k+dl-L]-value_slice_y[k])
            else:
                delta.append(value_slice_x[k+dl]-value_slice_x[k])
                delta.append(value_slice_y[k+dl]-value_slice_y[k])
            
        delta_array_container.append(delta)

    deltas_np = []
    
    for delta in delta_array_container:
        deltas_np.append(np.array(delta))

    for i, ax in enumerate(axes):
        mean = statistics.mean(deltas_np[i])
        SD = statistics.stdev(deltas_np[i])
        deltas_np[i] = (deltas_np[i] - mean) / SD

        ax.hist(deltas_np[i], bins=100, density=True)
        #sns.kdeplot(deltas_np[i], fill=True, ax=ax)

        mean = statistics.mean(deltas_np[i])
        SD = statistics.stdev(deltas_np[i])
        x = np.linspace(mean - 4*SD, mean + 4*SD, 1000)
        gaussian = (1 / (SD * np.sqrt(2 * np.pi))) * np.exp(- (x - mean)**2 / (2 * SD**2))

        ax.plot(x,gaussian)

        ax.set_title(titles[i])
        if i >= 6:
            ax.set_xlabel("(delta_By - mean)/SD")

        ax.set_xlim(-6,6)
        ax.set_yscale("log")
        ax.set_ylim(1e-3,1)

anim = animation.FuncAnimation(fig, update, frames = 100, interval = 20)

writer = FFMpegWriter(fps=5)
anim.save("sim21_struct_func_By_one_slice.mp4", writer=writer)
plt.close()