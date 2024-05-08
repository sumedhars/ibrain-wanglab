import os
import numpy as np
import pandas as pd
import nibabel as nib

from feature_engineering import calculate_gmvs, calculate_r2fs, calculate_r2sn_and_rmcs

# from tqdm import tqdm
from math import ceil

roi_superdir = "/data/csc4801/WangLab/training/cleaned_data/"

for diagnosis in os.listdir(roi_superdir):
    if diagnosis == 'registered' or diagnosis == 'skullstripped' or diagnosis == 'AD' or diagnosis == 'MCI':
        print("Skipping", diagnosis)
        continue
    for patient in os.listdir(os.path.join(roi_superdir, diagnosis)):
        # Read in images
        im_1_roi_dir = os.path.join(roi_superdir, diagnosis, patient)
        print("reading images from", im_1_roi_dir)
    
    
        # Building DataFrame columns
        columns = ["diagnosis", "PTID", "scan_name"]
        for i in range(246):
            for j in range(47):  # Assuming 47 features per ROI
                columns.append(f"roi_{i}_r2f_{j}_feature")
    
        gmv_list = []
        r2f_list = []
        rmcs_list = []
        r2sn_list = []
    
        d = {"diagnosis": [diagnosis], "PTID": [patient], "scan_name": ["latest_scan"]}
        info_df = pd.DataFrame(data=d)
    
        gmv_list.append(info_df)
        # r2f_list.append(info_df)
        # rmcs_list.append(info_df)
        # r2sn_list.append(info_df)
    
        ROI_BATCH_SIZE = 10
        print("Batching ROIs")
        # Convert to numpy array
        for batch_num in range(ceil(246 / ROI_BATCH_SIZE)):
            print(f"Engineering Features of batch {batch_num}")
    
            start_index = batch_num * ROI_BATCH_SIZE
            end_index = min(start_index + ROI_BATCH_SIZE, 246)
            batch_files = os.listdir(im_1_roi_dir)[start_index:end_index]
    
            batch_data = []
            for roi_file in batch_files:
                new_row = nib.load(os.path.join(im_1_roi_dir, roi_file)).get_fdata()
                batch_data.append(new_row)
            batch_array = np.stack(batch_data)
            np.reshape(batch_array, (len(batch_files), 145, 173, 145))
    
            # r2f_list.append(calculate_r2fs(batch_array, batch_num * ROI_BATCH_SIZE))
            gmv_list.append(calculate_gmvs(batch_array, batch_num * ROI_BATCH_SIZE))
        
        print("Successfully processed r2f and gmv for ROIs")
        
        # r2f_dir = "./features/r2f/"
        gmv_dir = "./features/gmv/"
        # os.makedirs(r2f_dir, exist_ok=True)
        os.makedirs(gmv_dir, exist_ok=True)
        
        print("Writing GMV file")
    
        # r2f_df = pd.concat(r2f_list, axis=1)
        # r2f_df.to_csv(os.path.join(r2f_dir, f"{patient}.csv"))
        gmv_df = pd.concat(gmv_list, axis=1)
        gmv_df.to_csv(os.path.join(gmv_dir, f"{patient}.csv"))
    
        # csv_files = os.listdir(r2f_dir)
        # for scan_r2f in csv_files:
        #     r2f_csv = pd.read_csv(r2f_dir + scan_r2f)
        #     r2f_values = r2f_csv.iloc[:, 4:]
        #     r2sn, rmcs = calculate_r2sn_and_rmcs(r2f_values)
        #     r2sn_list.append(r2sn)
        #     rmcs_list.append(rmcs)
    
        # print("Successfully processed R2F and RMCS")
        # os.makedirs("./features/r2sn/", exist_ok=True)
        # os.makedirs("./features/rmcs/", exist_ok=True)
    
        # r2sn_df = pd.concat(r2sn_list, axis=1)
        # r2sn_df.to_csv(f"./features/r2sn/{patient}.csv")
        # rmcs_df = pd.concat(rmcs_list, axis=1)
        # rmcs_df.to_csv(f"./features/rmcs/{patient}.csv")
        # print("Wrote R2SN and RMCS files")
