import pandas as pd
import numpy as np
import os
import Patient
from regional_radiomics import RadiomicsProcessor
from matplotlib import pyplot as plt
from matplotlib.animation import ArtistAnimation
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
import Scan
from joblib import dump
import preprocess
import modelling
import split_rois
import feature_engineering


def load_patients(folder_path):
    # create patient objects from folder of data
    patients = []
    # for each folder in the root folder
    for root, diagnosis_folders, _ in os.walk(folder_path):
        # for each diagnosis folder
        for diagnosis_folder in diagnosis_folders:
            # for each patient folder
            for _, patient_folders, _ in os.walk(os.path.join(root, diagnosis_folder)):
                for patient_folder in patient_folders:
                    # create a patient object and store paths to scans
                    patient = Patient.Patient([], patient_folder, diagnosis_folder)
                    patient.PTID = patient_folder
                    # for each scan in patient folder
                    for _, _, files in os.walk(os.path.join(root, diagnosis_folder, patient_folder)):
                        for file in files:
                            if file.endswith('.nii'):
                                s = os.path.join(root, diagnosis_folder, patient_folder, file)
                                patient.scan_paths.append(s)
                                patient.scans.append(Scan.Scan(s))
                    patients.append(patient)
    return patients


def load_scan(patient, scan_path):
    patient.scans.append(Scan(scan_path))


def save_to_csvs(patients):
        # GMV
    # Create GMV dataframe
    GMV_df = pd.DataFrame(["Patient ID", "Scan path"])

    for i in np.arange(246):
        new_col = pd.DataFrame(columns=["roi_" + str(i) + "_gmv"])
        GMV_df = pd.concat([GMV_df, new_col])

    # build all feature dfs
    for patient in patients:
        for scan in patient.scans:
            GMV_df.loc[len(GMV_df.index)] = [patient.PTID, scan.path, scan.GMVs]

    # r2f
    R2F_df = pd.DataFrame(["Patient ID", "Scan path"])
    # Create df (246 columns x 47 rows)
    for i in np.arange(246):
        new_col = pd.DataFrame(columns=["roi_" + str(i) + "_R2F"])
        R2F_df = pd.concat([R2F_df, new_col])

    # Write data to df
    for patient in patients:
        for scan in patient.scans:
            R2F_df.loc[len(R2F_df.index)] = [patient.PTID, scan.path, scan.R2F]

    # R2SN
    R2SN_df = pd.DataFrame(["Patient ID", "Scan path"])
    # Create df (246 columns x 246 rows)
    for i in np.arange(246):
        new_col = pd.DataFrame(columns=["roi_" + str(i) + "_R2SN"])
        R2SN_df = pd.concat([R2SN_df, new_col])

    # Write data to df
    for patient in patients:
        for scan in patient.scans:
            R2SN_df.loc[len(R2SN_df.index)] = [patient.PTID, scan.path, scan.R2SN]

    # RMCS
    RMCS_df = pd.DataFrame(["Patient ID", "Scan path"])
    # Create df (246 columns x 1 row)
    for i in np.arange(246):
        new_col = pd.DataFrame(columns=["roi_" + str(i) + "_RMCS"])
        RMCS_df = pd.concat([RMCS_df, new_col])

    # Write data to df
    for patient in patients:
        for scan in patient.scans:
            RMCS_df.loc[len(RMCS_df.index)] = [patient.PTID, scan.path, scan.RMCS]

    # save to csv
    file_location = "C:\\Users\\andrewss\\PycharmProjects\\wanglab-main\\data\\eng_features"

    if not os.path.exists(file_location):
        os.makedirs(file_location)

    GMV_df.to_csv(file_location + "\\GMV.csv")
    R2F_df.to_csv(file_location + "\\R2F.csv")
    R2SN_df.to_csv(file_location + "\\R2SN.csv")
    RMCS_df.to_csv(file_location + "\\RMCS.csv")


def main():
    # TODO - Update the paths below to match your local machine. If on ROSIE, comment this line out.
    # print("Setting Atlas locations...")
    # split_rois.set_atlas("Brainnetome", "../BNA_PM_4D.nii", "../HCP40_MNI_1.25mm.nii")
    
    # Path to the folder containing images
    root_scan_folder = '/mnt/c/Users/kirkpatricki/src/DataSciencePracticum/training'
    processed_scan_folder = './outputs/scans/'
    os.makedirs(processed_scan_folder, exist_ok=True)

    # data = pd.DataFrame(columns=['file_path', 'diagnosis'])

    print("Loading Patient Scans...")
    patients = load_patients(root_scan_folder)

    print("Preprocessing...")
    preprocess.main(patients, processed_scan_folder)
    
    print("Setting Atlas locations...")
    split_rois.set_atlas("Brainnetome", "./BNA_PM_4D.nii", "./HCP40_MNI_1.25mm.nii")

    print("Splitting ROIs...")
    split_rois.split_ROIs(patients)
    for p in patients[:5]:
        print("Patient:", p.PTID)
        for s, s_path in enumerate(p.scan_paths):
            print("\tScan:", s)
            scan = Scan.Scan.load(s_path)
            for r, roi in enumerate(scan.rois):
                fig = plt.figure()
                plt.title(f"ROI {r}")
                atlas_ims = []
                for i in range(roi.shape[1]):
                    im = plt.imshow(roi[:,i,:,0])
                    atlas_ims.append((im,))
                animation = ArtistAnimation(fig, atlas_ims, blit=True)
                animation.save(f"./{p.PTID}/scan_{s}/{r}.gif", fps=15)

    # feature_engineering.engineer_features(patients)

    # save_to_csvs(patients)

    # modelling.train_and_eval_models(patients)
    
if __name__ == '__main__':
    main()