#!/usr/bin/env python
# coding: utf-8

# In[10]:


get_ipython().system('pip install antspyx')


# In[1]:


import os
import numpy as np
import pandas as pd
from ants import vol, image_read, image_write, ANTsImage, weingarten_image_curvature, vol_fold, threshold_image
# from ants import ConvertScalarImageToRGB
from nipype.interfaces.ants.visualization import ConvertScalarImageToRGB


# In[12]:


def calculate_GMV(path):
    # Reads image
    scan = image_read(path)
    # scan.plot()
    # Thresholds/segments image
    scan2seg = threshold_image(scan, "Otsu", 3)
    # Calculates white matter (this will need to be changed)
    wm = threshold_image(scan2seg, 2, 2)
    # Convert to a NumPy array
    wm_np = wm.numpy()
    # find total of any positive voxel in the image
    volume = np.sum(wm_np > 0)
    return volume


# In[16]:


data_path = "../../../data/csc4801/WangLab/"
scan_folder = data_path + "atlas_registered_rois/"
GMV_df = pd.DataFrame(columns=["scan_name"])

outdir = data_path + "GMV_Test/"

for i in np.arange(246):
    new_col = pd.DataFrame(columns=["roi_" + str(i) + "_gmv"])
    GMV_df = pd.concat([GMV_df, new_col])

for roi_folder in os.listdir(scan_folder):
    roi_gmvs = np.array([])
    roi_gmvs = np.append(roi_gmvs, roi_folder)
    for scan in os.listdir(scan_folder + roi_folder):
        scan_path = scan_folder + roi_folder + "/" + scan
        GMV = calculate_GMV(scan_path)
        roi_gmvs = np.append(roi_gmvs, GMV)

    print(len(GMV_df.columns))
    print(len(roi_gmvs))
    
    GMV_df.loc[len(GMV_df.index)] = roi_gmvs

#os.mkdir(outdir)
GMV_df.head()


# In[50]:


csv_path = outdir + "GMV_df"
if os.path.isfile(csv_path + ".csv"):
    os.remove(csv_path + ".csv")
f = open(csv_path + ".csv", "x")
GMV_df.to_csv(csv_path + ".csv")


# In[18]:


print(csv_path)

