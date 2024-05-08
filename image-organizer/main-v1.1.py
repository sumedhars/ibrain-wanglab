import os
import shutil
import glob
import pandas as pd

"""
This version combines both 1.5T and 3T images amongst patients
(There is some overlap in patient IDs between 1.5T and 3T MRIs)
Author: Sumedha Sanjeev
"""

def create_subfolders(directory, items):
    # Create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)
    for item in items:
        subfolder_path = os.path.join(directory, str(item))
        if not os.path.exists(subfolder_path):
            os.makedirs(subfolder_path)
            print(f"Created subfolder: {subfolder_path}")


def patientID_in_filename(filename, patient_id_list):
    results = []
    for index, ptid in enumerate(patient_id_list):
        if ptid in filename:
            results.append((index, True))
    return results if results else None

#TODO: If using this file, update the paths
source_folder = "C:\\Users\\sanjeevs\\PycharmProjects\\csc4801-imageorg\\test-source-folder"
output_folder = "C:\\Users\\sanjeevs\\PycharmProjects\\csc4801-imageorg\\test-output-folder\\"
sd_lists_path_1t = "/\\adni-sd-lists\\ADNI_1.5T_MRI_Standardized_Lists"
sd_lists_path_3t = "/\\adni-sd-lists\\ADNI_3T_MRI_Standardized_Lists"


all_1t_files = glob.glob(os.path.join(sd_lists_path_1t, "*.csv"))
all_3t_files = glob.glob(os.path.join(sd_lists_path_3t, "*.csv"))
df_1t = pd.concat((pd.read_csv(f) for f in all_1t_files), ignore_index=True)
df_3t = pd.concat((pd.read_csv(f) for f in all_3t_files), ignore_index=True)


unique_diagnosis_1t = list(set(df_1t['Screen.Diagnosis']))
unique_ptids_1t = list(set(df_1t['PTID']))

unique_diagnosis_3t = list(set(df_3t['Screen.Diagnosis']))
unique_ptids_3t = list(set(df_3t['PTID']))

create_subfolders(output_folder, unique_diagnosis_1t)
create_subfolders(output_folder, unique_diagnosis_3t)

diag_groups = df_1t.groupby('Screen.Diagnosis')
for diagnosis in diag_groups.groups.keys():
    new_df = pd.DataFrame(diag_groups.get_group(diagnosis))
    unique_patient_ids = list(set(new_df['PTID']))
    diagnosis_subfolder = output_folder + diagnosis
    create_subfolders(diagnosis_subfolder, unique_patient_ids)
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            ptid_tuple = patientID_in_filename(file, unique_patient_ids)
            if ptid_tuple:
                patient_folder = unique_patient_ids[ptid_tuple[0][0]]
                file_to_copy = os.path.join(root,file)
                new_output_dir = os.path.join(diagnosis_subfolder, patient_folder)
                shutil.copy(file_to_copy, new_output_dir)



diag_groups = df_3t.groupby('Screen.Diagnosis')
for diagnosis in diag_groups.groups.keys():
    new_df = pd.DataFrame(diag_groups.get_group(diagnosis))
    unique_patient_ids = list(set(new_df['PTID']))
    diagnosis_subfolder = output_folder + diagnosis
    create_subfolders(diagnosis_subfolder, unique_patient_ids)
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            ptid_tuple = patientID_in_filename(file, unique_patient_ids)
            if ptid_tuple:
                patient_folder = unique_patient_ids[ptid_tuple[0][0]]
                file_to_copy = os.path.join(root,file)
                new_output_dir = os.path.join(diagnosis_subfolder, patient_folder)
                shutil.copy(file_to_copy, new_output_dir)