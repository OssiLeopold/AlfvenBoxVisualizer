import analysator as pt
bulkpath = "/home/rxelmer/Documents/turso/bulks/sim15/"
vlsvobj = pt.vlsvfile.VlsvReader(bulkpath + "bulk.0000010.vlsv")
rho = vlsvobj.read_variable("proton/vg_rho")
print(min(rho)/1e6)
print("hello")