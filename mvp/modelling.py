import pandas as pd
from joblib import dump
from sklearn.linear_model import LogisticRegression
import numpy as np
from sklearn.svm import SVC

def train_and_eval_models(patients):
    
    on_rosie = False

    # Path to the folder containing images
    root_scan_folder = '../training'
    roi_mask_source_folder = '../masks'

    data = pd.DataFrame(columns=['file_path', 'diagnosis'])

    for patient in patients:
        for scan in patient.scans:
            rois = scan.rois

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



def train_feature_models(patients):
    gmv_linear = train_gmv_model(patients)
    r2f_svms, r2f_linear = train_r2f_model(patients)
    r2sn_svms, r2sn_linear = train_r2sn_model(patients)
    rmcs_linear = train_rmcs_model(patients)

    return [gmv_linear, (r2f_svms, r2f_linear), (r2sn_svms, r2sn_linear), rmcs_linear]


def train_gmv_model(patients):
    # Build the GMV dataframe
    column_titles = ['PTID', 'Path', 'Diagnosis']
    for i in np.arange(0, 245):
        # for each roi
        column_titles.append("GMV_" + str(i))

    # Fill the GMV dataframe
    gmv_df = pd.DataFrame(columns=column_titles)
    for patient in patients:
        for scan in patient.scans:
            scan_info = pd.DataFrame(columns=['PTID', 'Path', 'Diagnosis'])
            scan_info = scan_info.append({'PTID': patient.PTID, 'Path': scan.path, 'Diagnosis': patient.diagnosis}, ignore_index=True)

            scan_gmvs = pd.DataFrame(scan.GMVs)
            scan_gmvs = pd.concat([scan_info, scan_gmvs], axis=1)
            gmv_df = gmv_df.append(scan_gmvs)

    # Train a linear model on the GMV data
    X = gmv_df.drop(['PTID', 'Path', 'Diagnosis'], axis=1)
    y = gmv_df['Diagnosis']
    linear_model = LogisticRegression()
    linear_model.fit(X, y)

    return linear_model



def train_r2f_model(patients):

    # Build the R2F dataframe
    column_titles = ['PTID', 'Path', 'Diagnosis']
    for i in np.arange(0, 245):
        # for each roi
        for feature in np.arange(0, 47):
            column_titles.append("R2F_" + str(i) + "_" + str(feature))
    r2f_df = pd.DataFrame(columns=column_titles)

    # Fill the R2F dataframe
    for patient in patients:
        for scan in patient.scans:
            scan_info = pd.DataFrame(columns=['PTID', 'Path', 'Diagnosis'])
            scan_info = scan_info.append({'PTID': patient.PTID, 'Path': scan.path, 'Diagnosis': patient.diagnosis}, ignore_index=True)

            r2f_list = []
            for i in np.arange(0, scan.R2F.shape[0]):
                for j in np.arange(0, scan.R2F.shape[1]):
                    r2f_list.append(scan.R2F[i][j])
            scan_r2f = pd.DataFrame(r2f_list)
            scan_r2f = pd.concat([scan_info, scan_r2f], axis=1)
            r2f_df = r2f_df.append(scan_r2f)

    X_all = r2f_df.drop(['PTID', 'Path', 'Diagnosis'], axis=1)
    y = r2f_df['Diagnosis']

    # Train an SVM for each ROI
    svms = []
    for roi in np.arange(0, 245):
        X = X_all[X_all.columns[roi*47:(roi+1)*47]]

        # create a classifier
        cls = SVC(kernel="linear")
        # train the model
        cls.fit(X, y)
        svms.append(cls)

    # Predict diagnosis for each ROI using the SVMs
    svm_df = pd.DataFrame(columns=['PTID', 'Path', 'Diagnosis'])
    for patient in patients:
        for scan in patient.scans:
            scan_info = pd.DataFrame(columns=['PTID', 'Path', 'Diagnosis'])
            scan_info = scan_info.append({'PTID': patient.PTID, 'Path': scan.path, 'Diagnosis': patient.diagnosis}, ignore_index=True)

            r2f_svm_preds = []
            # for each roi
            for i in np.arange(0, scan.R2F.shape[0]):
                # predict diagnosis
                pred = svms[i].predict(scan.R2F[i])
                r2f_svm_preds.append(pred)
            
            scan_r2f_svm = pd.DataFrame(r2f_svm_preds)
            scan_r2f_svm = pd.concat([scan_info, scan_r2f_svm], axis=1)
            svm_df = svm_df.append(scan_r2f_svm)

    # Train a linear model on the SVM predictions
    X = svm_df.drop(['PTID', 'Path', 'Diagnosis'], axis=1)
    y = svm_df['Diagnosis']
    linear_model = LogisticRegression()
    linear_model.fit(X, y)

    return svms, linear_model

def train_r2sn_model(patients):
    column_titles = ['PTID', 'Path', 'Diagnosis']
    for i in np.arange(0, 245):
        # for each roi
        for j in np.arange(0, 245):
            column_titles.append("R2SN_" + str(i) + "_" + str(j))

    r2sn_df = pd.DataFrame(columns=column_titles)
    for patient in patients:
        for scan in patient.scans:
            scan_info = pd.DataFrame(columns=['PTID', 'Path', 'Diagnosis'])
            scan_info = scan_info.append({'PTID': patient.PTID, 'Path': scan.path, 'Diagnosis': patient.diagnosis}, ignore_index=True)

            r2sn_list = []
            for i in np.arange(0, scan.R2SN.shape[0]):
                for j in np.arange(0, scan.R2SN.shape[1]):
                    r2sn_list.append(scan.R2SN[i][j])
            scan_r2sn = pd.DataFrame(r2sn_list)
            scan_r2sn = pd.concat([scan_info, scan_r2sn], axis=1)
            r2sn_df = r2sn_df.append(scan_r2sn)

    X_all = r2sn_df.drop(['PTID', 'Path', 'Diagnosis'], axis=1)
    y = r2sn_df['Diagnosis']

    # Train an SVM for each ROI
    svms = []
    for roi in np.arange(0, 245):
        X = X_all[X_all.columns[roi*47:(roi+1)*47]]

        # create a classifier
        cls = SVC(kernel="linear")
        # train the model
        cls.fit(X, y)
        svms.append(cls)

    # Predict diagnosis for each ROI using the SVMs
    svm_df = pd.DataFrame(columns=['PTID', 'Path', 'Diagnosis'])
    for patient in patients:
        for scan in patient.scans:
            scan_info = pd.DataFrame(columns=['PTID', 'Path', 'Diagnosis'])
            scan_info = scan_info.append({'PTID': patient.PTID, 'Path': scan.path, 'Diagnosis': patient.diagnosis}, ignore_index=True)

            r2sn_svm_preds = []
            # for each roi
            for i in np.arange(0, scan.R2F.shape[0]):
                # predict diagnosis
                pred = svms[i].predict(scan.R2F[i])
                r2sn_svm_preds.append(pred)
            
            scan_r2f_svm = pd.DataFrame(r2sn_svm_preds)
            scan_r2f_svm = pd.concat([scan_info, scan_r2f_svm], axis=1)
            svm_df = svm_df.append(scan_r2f_svm)

    # Train a linear model on the SVM predictions
    X = svm_df.drop(['PTID', 'Path', 'Diagnosis'], axis=1)
    y = svm_df['Diagnosis']
    linear_model = LogisticRegression()
    linear_model.fit(X, y)

    return svms, linear_model


def train_rmcs_model(patients):
    column_titles = ['PTID', 'Path', 'Diagnosis']
    for i in np.arange(0, 245):
        # for each roi
        column_titles.append("RMCS_" + str(i))

    rmcs_df = pd.DataFrame(columns=column_titles)
    for patient in patients:
        for scan in patient.scans:
            scan_info = pd.DataFrame(columns=['PTID', 'Path', 'Diagnosis'])
            scan_info = scan_info.append({'PTID': patient.PTID, 'Path': scan.path, 'Diagnosis': patient.diagnosis}, ignore_index=True)

            scan_rmcs = pd.DataFrame(scan.RMCS)
            scan_rmcs = pd.concat([scan_info, scan_rmcs], axis=1)
            rmcs_df = rmcs_df.append(scan_rmcs)

    X = rmcs_df.drop(['PTID', 'Path', 'Diagnosis'], axis=1)
    y = rmcs_df['Diagnosis']
    linear_model = LogisticRegression()
    linear_model.fit(X, y)

    return linear_model

