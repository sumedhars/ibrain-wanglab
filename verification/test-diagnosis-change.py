import pandas as pd
import glob

"""
This script checks for the prescence of multiple diagnoses for a single patient
amongst scans taken over a period of time, as recorded in the standardized lists.
"""

def list_equal(list):
    return all(i == list[0] for i in list)

def test_different_diagnosis_in_df(dataframe):
    no_differences = []
    grouped_by_ptid = dataframe.groupby('PTID')
    for ptid in grouped_by_ptid.groups.keys():
        diagnosis_list = list(grouped_by_ptid[['Screen.Diagnosis']].get_group(ptid)['Screen.Diagnosis'])
        #print(list_equal(diagnosis_list))
        if list_equal(diagnosis_list):
            no_differences.append(True)
        else:
            no_differences.append(False)
    return no_differences


sd_lists_path_1t = "C:\\Users\\sanjeevs\\PycharmProjects\\csc4801-scripts\\adni-sd-lists\\ADNI_1.5T_MRI_Standardized_Lists\\*.csv"
sd_lists_path_3t = "C:\\Users\\sanjeevs\\PycharmProjects\\csc4801-scripts\\adni-sd-lists\\ADNI_3T_MRI_Standardized_Lists\\*.csv"

final_list_1t = []
final_list_3t = []

for fname in glob.glob(sd_lists_path_1t):
    print(fname)
    df = pd.read_csv(fname)
    final_list_1t.extend(test_different_diagnosis_in_df(df))

#print(final_list_1t)
print("Prescence of different diagnosis in a single patient in 1.5T MRIs: ", False in final_list_1t)

for fname in glob.glob(sd_lists_path_3t):
    print(fname)
    df = pd.read_csv(fname)
    final_list_3t.extend(test_different_diagnosis_in_df(df))

#print(final_list_3t)
print("Prescence of different diagnosis in a single patient in 3.0T MRIs: ", False in final_list_3t)
