import sys

# Dictionary for translating instructions for VlsvReader
translate = {"B_x":("vg_b_vol", "x", 1e-9, "nT"),
                "B_y":("vg_b_vol", "y", 1e-9, "nT"),
                "B_z":("vg_b_vol", "z", 1e-9, "nT"),
                "dB_y/dx":("vg_derivatives/vg_dperbyvoldx", "pass", 1e-15, "fT"),
                "dB_z/dx":("vg_derivatives/vg_dperbzvoldx", "pass", 1e-15, "fT"),
                "B_tot":("vg_b_vol", "magnitude", 1e-9, "nT"),
                "J_y":("vg_j", "y", 1e-9, "nA/m**2"),
                "J_z":("vg_j", "z", 1e-9, "nA/m**2"),
                "J_x":("vg_j", "x", 1e-9, "nA/m**2"),
                "v_x":("proton/vg_v", "x", 1e3, "km/s"),
                "v_y":("proton/vg_v", "y", 1e3, "km/s"),
                "v_z":("proton/vg_v", "z", 1e3, "km/s"),
                "v_tot":("proton/vg_v", "magnitude", 1e3, "km/s"),
                "rho":("proton/vg_rho", None, 1e6, "n/cell")}

# Defining AnimationSpecs object and checking instructions
class AnimationSpecs():
    def __init__(self, animation_type, variable, name, bulkfile_n, bulkpath, fourier_spec):
        if animation_type not in ["3D", "2D", "fourier"]:
            print("animation_type defined incorrectly")
            print(animation_type, variable, name, bulkfile_n, bulkpath, fourier_spec)
            sys.exit(1)

        if variable not in ["B_y", "B_z", "B_x", "dB_y/dx", "dB_z/dx", "B_tot", "J_x", "J_y", "J_z", "v_y", "v_z", "v_x", "v_tot", "rho"]:
            print("variable defined incorrectly")
            print(animation_type, variable, name, bulkfile_n, bulkpath, fourier_spec)
            sys.exit(1)

        if name[-3:] not in ["gif", "mp4"]:
            print("filetype defined incorrectly")
            print(animation_type, variable, name, bulkfile_n, bulkpath, fourier_spec)
            sys.exit(1)

        if animation_type == "fourier":
            if fourier_spec[0] == "x" or fourier_spec[0] == "y":
                self.fourier_type = "princpile"
                self.fourier_direc = fourier_spec[0]
                self.fourier_loc = fourier_spec[1]
            elif fourier_spec[0] == "diag":
                self.fourier_type = "diag"
                self.fourier_direc = fourier_spec[1]
            elif fourier_spec[0] == "trace":
                self.fourier_type = "trace"
                self.fourier_loc_x = fourier_spec[1]
                self.fourier_loc_y = fourier_spec[2]
            elif fourier_spec == "trace_diag":
                self.fourier_type = "trace_diag"
            else:
                print("fourier spec defined incorrectly")
                print(animation_type, variable, name, bulkfile_n, bulkpath, fourier_spec)
                sys.exit(1)

        self.animation_type = animation_type
        self.variable_name = variable
        self.variable = translate[variable][0]
        self.component = translate[variable][1]
        self.unit = translate[variable][2]
        self.unit_name = translate[variable][3]
        self.name = name
        self.bulkfile_n = bulkfile_n
        self.bulkpath = bulkpath
        