import pandas as pd
import os
import glob

sd_lists_path_1t = "C:\\Users\\sanjeevs\\PycharmProjects\\csc4801-scripts\\adni-sd-lists\\ADNI_1.5T_MRI_Standardized_Lists"
sd_lists_path_3t = "C:\\Users\\sanjeevs\\PycharmProjects\\csc4801-scripts\\adni-sd-lists\\ADNI_3T_MRI_Standardized_Lists"
biomarker_data_csv = "C:\\Users\\sanjeevs\\PycharmProjects\\csc4801-scripts\\biomarker-data\\UPENNBIOMK4_09_06_12_10Feb2024.csv"

all_1t_files = glob.glob(os.path.join(sd_lists_path_1t, "*.csv"))
all_3t_files = glob.glob(os.path.join(sd_lists_path_3t, "*.csv"))

# sdl -> standardized list
sdl_df = pd.concat((pd.read_csv(f) for f in all_1t_files), ignore_index=True)
sdl_df = pd.concat([sdl_df] + [pd.read_csv(f) for f in all_3t_files], ignore_index=True)
# UPENN biomarker csv
biomarker_df = pd.read_csv(biomarker_data_csv)
biomarker_df["PTID"] = ""
biomarker_df["Screen.Diagnosis"] = ""

sdl_df_grouped = sdl_df.groupby('RID')
biomarker_df_grouped = biomarker_df.groupby('RID')

# print(list(sdl_df_grouped.groups.keys()))
# print(list(biomarker_df_grouped.groups.keys()))

output_df = pd.DataFrame()

for rid in biomarker_df_grouped.groups.keys():
    if rid in sdl_df_grouped.groups.keys():
        diagnosis = str(set(sdl_df_grouped.get_group(rid)['Screen.Diagnosis']))
        ptid = str(set(sdl_df_grouped.get_group(rid)['PTID']))
        df = biomarker_df_grouped.get_group(rid)
        df.loc[:, 'PTID'] = ptid
        df.loc[:, 'Screen.Diagnosis'] = diagnosis
        output_df = pd.concat([output_df, df], ignore_index=True)
    else:
        print(f"RID: {rid} not in Standardized List.")

output_df.to_csv('output.csv', index=False)