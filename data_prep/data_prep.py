import pandas as pd
import numpy as np
import os
from mvp import Patient
from regional_radiomics import RadiomicsProcessor
from matplotlib import pyplot as plt
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
import Scan
from joblib import dump

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
                    patient = Patient.Patient()
                    patient.PTID = patient_folder
                    # for each scan in patient folder
                    for _, _, files in os.walk(os.path.join(root, diagnosis_folder, patient_folder)):
                        for file in files:
                            if file.endswith('.nii'):
                                patient.scan_paths.append(os.path.join(root, diagnosis_folder, patient_folder, file))
                    patients.append(patient)
    return patients


def load_scan(patient, scan_path):
    patient.scans.append(Scan(scan_path))


def main():
    
    on_rosie = False

    # Path to the folder containing images
    root_scan_folder = '../training'
    roi_mask_source_folder = '../masks'

    data = pd.DataFrame(columns=['file_path', 'diagnosis'])

    patients = load_patients(root_scan_folder)

    for patient in patients:
        # load scans and split rois
        for scan_path in patient.scan_paths:
            load_scan(patient, scan_path)
        
        for scan in patient.scans:
            scan.split_rois(scan)
            

            if not on_rosie:
                # calculate R2F
                processor = RadiomicsProcessor()
                result_df = processor.mri_radiomics_to_csv(scan, roi_mask_source_folder)
            else:
                # calculate R2SN
                scan.calculate_R2SNs()
                # calculate RMCS
                scan.calculate_RMCSs()
                # calculate GMV
                scan.calculate_GMVs()


    models = train_feature_models(patients)

    # Save the models
    for model in models:
        if type(model) == tuple:
            for m in model:
                dump(m, m.name + ".joblib")
        else:
            dump(model, model.name + ".joblib")


if __name__ == '__main__':
    main()