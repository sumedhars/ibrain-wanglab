import os

import numpy as np
import pandas as pd
from ants import threshold_image, image_read, resample_image_to_target, registration, from_numpy
import nibabel as nib

from Patient import Patient
# import Preprocess
# import regional_radiomics as r2f
# from regional_radiomics import RadiomicsBatchProcessor
# from regional_radiomics import RadiomicsProcessor

from sklearn.preprocessing import MinMaxScaler
from scipy.stats import pearsonr

import gc

def calculate_gmvs(numpy_arr, batch_offset):
    # calculate GMV for each roi and load into patient object
    """
    Given an MRI scan calculate the GMV for each roi in said scan
    """
    batch_size = numpy_arr.shape[0]

    # Create df to hold data
    columns = []
    # gmv_df = pd.DataFrame(columns=["diagnosis", "PTID", "scan_name"])
    for i in np.arange(batch_size):
        columns.append("roi_" + str(i + batch_offset) + "_gmv")

    gmv_df = pd.DataFrame(columns=columns)

    roi_gmvs = []

    for i in np.arange(batch_size):
        roi_gmvs.append(calculate_gmv(numpy_arr[i]))

    # roi_gmvs_array = np.array(roi_gmvs)
    gmv_df.loc[len(gmv_df)] = roi_gmvs

    # add new row to the end of the gmv df
    # gmv_df.loc[len(gmv_df.index)] = roi_gmvs`
    
    # print(gmv_df.head())

    # gmv_df.to_csv("C:\\Users\\andrewss\\PycharmProjects\\wanglab\\test_images\\test_gmv\\scan_1_gmv.csv")
    return gmv_df


def calculate_gmv(roi: np.array) -> float:
    # convert np array to image
    roi_scan = from_numpy(roi)
    # Thresholds/segments image
    scan2seg = threshold_image(roi_scan, "Otsu", 3)
    # Calculates white matter (this will need to be changed)
    wm = threshold_image(scan2seg, 2, 2)
    # Convert to a NumPy array
    wm_np = wm.numpy()
    # find total of any positive voxel in the image
    #volume = np.sum(wm_np > 0)
    volume = np.sum(wm_np > 0)

    return volume


def drop_redundancy(r2f_values, scaled_radiomics_features):
    correlation_matrix = np.zeros((47, 47))

    for i in range(0, scaled_radiomics_features.shape[1]):
        for j in range(0, scaled_radiomics_features.shape[1]):
            feature_1= scaled_radiomics_features[:, j]
            feature_2 = scaled_radiomics_features[:, i]
            corr, _ = pearsonr(feature_1, feature_2)
            correlation_matrix[i, j] = corr
    correlation = correlation_matrix.mean(axis=1)
    
    # make correlation mask to remove redundancy
    correlation_mask = (correlation > 0.9)  # boolean mask for correlated features
    
    # get indices of correlated features
    correlated_indices = np.where(correlation_mask)[0]
    
    # remove correlated features
    cleaned = np.delete(r2f_values, correlated_indices, axis=1)
    return cleaned


def build_similarity_matrix(cleaned):
    similarity_matrix = np.zeros((246, 246))

    for i in range(0, cleaned.shape[0]):
        for j in range(0, cleaned.shape[0]):
            roi_1 = cleaned[i, :]
            roi_2 = cleaned[j, :]
            corr, _ = pearsonr(roi_1, roi_2)
            similarity_matrix[i, j] = corr

    return similarity_matrix


# def calculate_R2Fs(numpy_arr):
#     # calculate R2F for each roi and load into patient object
#     path = self.path
#     processor = r2f.RadiomicsProcessor()
#     roi_mask_source_folder = "roi_masks"
#     result_df = processor.mri_radiomics_to_csv(path, roi_mask_source_folder)
#     df_val_array = result_df.values
#     self.R2F = df_val_array


def calculate_r2fs(numpy_arr: np.array, batch_offset):
    """
    Given an MRI scan, calculate the radiomics features for each ROI in said scan.
    """

    batch_size = numpy_arr.shape[0]

    # Building DataFrame columns
    columns = []
    roi_masks = []
    print("building r2f dataframe")
    for i in range(batch_size):
        for j in range(47):  # Assuming 47 features per ROI
            columns.append(f"roi_{i + batch_offset}_r2f_{j}_feature")
            roi_masks.append(get_roi_mask(i + batch_offset + 1))

    roi_masks = np.array(roi_masks)
    roi_masks = np.reshape(roi_masks, (batch_size, 145, 173, 145, 47))
    # Create an empty DataFrame with the specified columns
    r2f_df = pd.DataFrame(columns=columns)

    # Instantiate the processor with batch size
    # processor = RadiomicsBatchProcessor(batch_size=10)
    processor = RadiomicsProcessor()

    # Process radiomics data
    radiomics_df = processor.np_radiomics_to_csv(numpy_arr, roi_masks)

    # Add patient info to the DataFrame
    
    # for _, row in radiomics_df.iterrows():
        # info = ["AD", "test_PTID", "test_scan"] + row.tolist()
        # concatenate all of the rows into a single row

    # print("radiomics calculated! df with shape:")
    # print(radiomics_df.shape)
        
    r2f_df.loc[len(r2f_df)] = radiomics_df.values.flatten()

    # Save DataFrame to CSV
    # r2f_df.to_csv("mvp/features/r2f/scan_1_r2f.csv")
    # print(r2f_df.head())
    return r2f_df

def calculate_r2sn_and_rmcs(r2f_df: pd.DataFrame):

    # calculate R2SN for each roi and load into patient object
    min_max_scaler = MinMaxScaler()
    scaled_radiomics_features = min_max_scaler.fit_transform(r2f_df)
    r2f_data = np.reshape(r2f_df.values, (246, 47))
    scaled_radiomics_features = np.reshape(scaled_radiomics_features, (246, 47))
    features = drop_redundancy(r2f_data, scaled_radiomics_features)
    similarity_matrix = build_similarity_matrix(features)
    rmcs = np.mean(similarity_matrix, axis=1)

    r2sn_columns = []
    for i in range(similarity_matrix.shape[0]):
        for j in range(similarity_matrix.shape[1]):
            r2sn_columns.append(f"roi_{i}_roi_{j}_similarity")
    
    rmcs_columns = []
    for i in range(similarity_matrix.shape[0]):
            rmcs_columns.append(f"roi_{i}_rmcs")

    r2sn_df = pd.DataFrame(columns=r2sn_columns)
    new_row = similarity_matrix.flatten()
    r2sn_df.loc[len(r2sn_df)] = new_row

    rmcs_df = pd.DataFrame(columns=rmcs_columns)
    rmcs_df.loc[len(rmcs_df)] = rmcs

    return r2sn_df, rmcs_df



def get_roi_mask(roi_number):
    roi_mask_source_folder = "/mnt/c/Users/watermana/2023-24/CSC4801-DataSciencePracticum/newWangLab/wanglab/mvp/roi_masks/"
    roi_mask = nib.load(roi_mask_source_folder + f"{roi_number}.nii").get_fdata()
    return roi_mask





































































import SimpleITK as sitk
import pandas as pd
import os
from radiomics import featureextractor
from tqdm import tqdm
from memory_profiler import profile

import gc

"""
USE THIS FOR DATA_PREP.PY
regional_radiomics - v2.0
"""

class RadiomicsProcessor:
    def __init__(self):
        self.selected_radiomics_features = ['original_firstorder_Energy', 'original_firstorder_Entropy', 'original_firstorder_Kurtosis',
                                  'original_firstorder_Maximum', 'original_firstorder_MeanAbsoluteDeviation',
                                  'original_firstorder_Mean', 'original_firstorder_Median', 'original_firstorder_Minimum',
                                  'original_firstorder_Range', 'original_firstorder_RootMeanSquared',
                                  'original_firstorder_Skewness', 'original_firstorder_MeanAbsoluteDeviation',
                                  'original_firstorder_Uniformity', 'original_firstorder_Variance',
                                  'original_glcm_Autocorrelation', 'original_glcm_ClusterProminence',
                                  'original_glcm_ClusterShade', 'original_glcm_ClusterTendency', 'original_glcm_Contrast',
                                  'original_glcm_Correlation', 'original_glcm_DifferenceEntropy',
                                   'original_glcm_JointEnergy', 'original_glcm_JointEntropy', 'original_glcm_Imc1',
                                   'original_glcm_Imc2', 'original_glcm_Idmn', 'original_glcm_Idn',
                                   'original_glcm_InverseVariance', 'original_glcm_MaximumProbability',
                                   'original_glcm_SumAverage', 'original_glcm_SumEntropy', 'original_glrlm_LongRunEmphasis',
                                   'original_glrlm_ShortRunEmphasis', 'original_glszm_GrayLevelNonUniformity']
        # dissimilarity, Homogeneity 1, Homogeneity 2 deprecated in pyradiomics

        self.extractor = featureextractor.RadiomicsFeatureExtractor()
        self.extractor.enableFeatureClassByName('firstorder')


    def np_radiomics_to_csv(self, scan_np, roi_masks_np: np.array):
        # row --> radiomics feature || column --> ROI number
        mri_radiomics_list = []
        #mri_radiomics_df = pd.DataFrame(columns=self.selected_radiomics_features)

        # print("calculating r2f for each roi")
        for i in tqdm(range(roi_masks_np.shape[0])):
            roi_mask = roi_masks_np[i]
            indv_roi_dict = self.np_roi_to_radiomics(scan_np[i], roi_mask)
            if not indv_roi_dict:
                print("Skipping current mask as no radiomics features were extracted.")
                continue
            # subset_roi_dict = {key:indv_roi_dict[key] for key in self.selected_radiomics_features}
            # mri_radiomics_list.append(subset_roi_dict)
            mri_radiomics_list.append(indv_roi_dict)
        
        mri_radiomics_df = pd.DataFrame(mri_radiomics_list)

        # mri_radiomics_df.to_csv("C:\\Users\\andrewss\\PycharmProjects\\wanglab\\test_images\\test_r2f\\scan_1_r2f.csv")

        # print(mri_radiomics_df.tail(47))
        mri_radiomics_df = mri_radiomics_df.iloc[:, -47:]

        # print("Columns!")
        # print(mri_radiomics_df.columns)
        return mri_radiomics_df


    # @profile
    def np_roi_to_radiomics(self, image_np, roi_mask_np):
        gc.collect()
        # print("inside np_roi_to_radiomics")

        radiomics_values = {}

        image = sitk.GetImageFromArray(image_np)
        
        # print("checking roi mask is empty")
        if roi_mask_np.max() == 0:
            print("No labels found in the mask. Skipping radiomics feature extraction.")
            return radiomics_values
        
        # Modify mask array in-place to save memory
        # print("Before setting non-zero values to 1")
        roi_mask_np[roi_mask_np != 0] = 1
        # print("After setting non-zero values to 1")

        # print("converting roi mask to sitk image")
        mask = sitk.GetImageFromArray(roi_mask_np)
        # print("resampling mask")
        resampled_mask = sitk.Resample(mask, image, interpolator=sitk.sitkNearestNeighbor)
        
        try:
            feature_vector = self.extractor.execute(image, resampled_mask)
            radiomics_values.update(feature_vector)
        except ValueError as e:
            print("Error during radiomics feature extraction:", e)
        
        return radiomics_values