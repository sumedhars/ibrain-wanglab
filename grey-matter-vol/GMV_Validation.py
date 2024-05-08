#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import os
import numpy as np
import pandas as pd
from scipy import stats
from ants import vol, image_read, image_write, ANTsImage, weingarten_image_curvature, vol_fold, threshold_image
from nipype.interfaces.ants.visualization import ConvertScalarImageToRGB
import seaborn as sns


# In[3]:


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
    print("Number of grey matter voxels: ", volume)
    print("Percent of brain that is GMV: ", volume / (np.sum(wm_np >= 0)))
    return volume


# In[4]:


# Test just the two images with no loop
# establish image paths
NL_image_path = "../../../data/csc4801/WangLab/gmv_validation_files/ADNI_002_S_0413_MR_MPR____N3__Scaled_2_Br_20081001114937668_S14782_I118675_NL.nii"
AD_image_path = "../../../data/csc4801/WangLab/gmv_validation_files/ADNI_002_S_0816_MR_MPR____N3__Scaled_2_Br_20081001115756935_S19532_I118684_AD.nii"
MCI_image_path = "../../../data/csc4801/WangLab/images_organizedMCI/002_S_0729/ADNI_002_S_0729_MR_MPR____N3__Scaled_2_Br_20081001114302922_S17535_I118668.nii"

# Run method
print("NL Test")
NL_vol = calculate_GMV(NL_image_path)
print()
print("MCI Test")
NL_vol = calculate_GMV(MCI_image_path)
print()
print("AD Test")
AD_vol = calculate_GMV(AD_image_path)


# In[5]:


# Test just the two adjusted images
# establish image paths
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

    # print(len(GMV_df.columns))
    # print(len(roi_gmvs))
    
    GMV_df.loc[len(GMV_df.index)] = roi_gmvs

#os.mkdir(outdir)
GMV_df.head()


# # Test calculate gmv method to see if the total gmv percentage and voxels are the same

# In[6]:


def test_calculate_GMV(path):
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
    # print("Number of grey matter voxels: ", volume)
    percentage = volume / (np.sum(wm_np >= 0))
    # print("Percent of brain that is GMV: ", percentage)
    return volume, percentage


# In[7]:


def calculate_percentage(path):
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
    # print("Number of grey matter voxels: ", volume)
    percentage = volume / (np.sum(wm_np >= 0))
    # print("Percent of brain that is GMV: ", percentage)
    return percentage


# In[8]:


# Test just the two adjusted images
# establish image paths
data_path = "../../../data/csc4801/WangLab/"
scan_folder = data_path + "atlas_registered_rois/"
GMV_df = pd.DataFrame(columns=["scan_name"])

outdir = data_path + "GMV_Test/"

for i in np.arange(246):
    new_col = pd.DataFrame(columns=["roi_" + str(i) + "_gmv"])
    GMV_df = pd.concat([GMV_df, new_col])

for roi_folder in os.listdir(scan_folder):
    percentages = np.array([])
    total_GMVs = np.array([])
    roi_gmvs = np.array([])
    roi_gmvs = np.append(roi_gmvs, roi_folder)
    for scan in os.listdir(scan_folder + roi_folder):
        scan_path = scan_folder + roi_folder + "/" + scan
        GMV, percentage = test_calculate_GMV(scan_path)
        roi_gmvs = np.append(roi_gmvs, GMV)
        percentages = np.append(percentages, percentage)
        total_GMVs = np.append(total_GMVs, GMV)

    print(sum(percentages))
    print(sum(total_GMVs))
    # print(len(GMV_df.columns))
    # print(len(roi_gmvs))
    
    GMV_df.loc[len(GMV_df.index)] = roi_gmvs

#os.mkdir(outdir)
GMV_df.head()


# # Run Kruskal Wallis to test statistical signifance

# In[9]:


# The data is not normalized and as such Kruskal Wallis will be used to accomplish this
# stats.kruskal(x, y, z)
scores = []
for col in GMV_df.columns.values:
    if(col == "scan_name"):
        print()
    else:
        x = GMV_df.at[0, col]
        y = GMV_df.at[1, col]
        z = GMV_df.at[2, col]
        temp_stat = stats.kruskal(x, y, z)
        scores.append(temp_stat)

print(scores)


# In[ ]:


sns.barplot(df, x="island", y="body_mass_g")

