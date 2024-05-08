import nibabel as nib
import SimpleITK as sitk
import pandas as pd
import os
from radiomics import featureextractor


# - for each brain MRI:
#     - apply each ROI mask &&
#     - get each radiomics feature values
#     - make df of: ROI vs. radiomics feature for each individual MRI
#     - export df as csv

brain_mri_source_folder = 'C:\\Users\\sanjeevs\\PycharmProjects\\csc4801-scripts\\atlas_registered_scans'
roi_mask_source_folder = 'C:\\Users\\sanjeevs\\PycharmProjects\\csc4801-scripts\\radiomics\\3d_masks'


"""
@:return dictionary of radiomics feature values for a single ROI (mask)
"""
def roi_to_radiomics(image_path, mask_path):
    radiomics_values = {}
    image = sitk.ReadImage(image_path)
    mask = sitk.ReadImage(mask_path)
    if sitk.GetArrayFromImage(mask).max() == 0:
        print("No labels found in the mask. Skipping radiomics feature extraction.")
        return radiomics_values
    # added to replace all non 1 values w/ 1
    mask_array = sitk.GetArrayFromImage(mask)
    mask_array[mask_array != 0] = 1
    mask = sitk.GetImageFromArray(mask_array)
    resampled_mask = sitk.Resample(mask, image, interpolator=sitk.sitkNearestNeighbor)
    try:
        extractor = featureextractor.RadiomicsFeatureExtractor()
        extractor.enableFeatureClassByName('firstorder')
        feature_vector = extractor.execute(image, resampled_mask)
        for feature_name in feature_vector.keys():
            radiomics_values[feature_name] = feature_vector[feature_name]
    except ValueError as e:
        print("Error during radiomics feature extraction:", e)
    return radiomics_values


# TODO: complete the list
selected_radiomics_features = ['original_firstorder_Energy', 'original_firstorder_Entropy', 'original_firstorder_Kurtosis',
                              'original_firstorder_Maximum', 'original_firstorder_MeanAbsoluteDeviation',
                              'original_firstorder_Mean', 'original_firstorder_Median', 'original_firstorder_Minimum',
                              'original_firstorder_Range', 'original_firstorder_RootMeanSquared',
                              'original_firstorder_Skewness', 'original_firstorder_MeanAbsoluteDeviation',
                              'original_firstorder_Uniformity', 'original_firstorder_Variance',
                              'original_glcm_Autocorrelation', 'original_glcm_ClusterProminence',
                              'original_glcm_ClusterShade', 'original_glcm_ClusterTendency', 'original_glcm_Contrast',
                              'original_glcm_Correlation', 'original_glcm_DifferenceEntropy',
                               'original_glcm_JointEnergy', 'original_glcm_JointEntropy', 'original_glcm_Imc1',
                               'original_glcm_Imc2', 'original_glcm_Idmn', 'original_glcm_Idn']
# dissimilarity, Homogeneity 1, Homogeneity 2 deprecated in pyradiomics

def mri_radiomics_to_csv(mri_image_path, roi_mask_source_folder):
    # row --> radiomics feature || column --> ROI number
    mri_radiomics_list = []
    #mri_radiomics_df = pd.DataFrame(columns=selected_radiomics_features)
    for individual_roi_mask in os.listdir(roi_mask_source_folder):
        individual_roi_mask_path = os.path.join(roi_mask_source_folder, individual_roi_mask)
        print(individual_roi_mask_path)
        indv_roi_dict = roi_to_radiomics(mri_image_path, individual_roi_mask_path)
        if not indv_roi_dict:
            print("Skipping current mask as no radiomics features were extracted.")
            continue
        subset_roi_dict = {key:indv_roi_dict[key] for key in selected_radiomics_features}
        mri_radiomics_list.append(subset_roi_dict)
        mri_radiomics_df = pd.DataFrame(mri_radiomics_list)
    return mri_radiomics_df


output_directory = 'r2f-csv'
os.makedirs(output_directory, exist_ok=True)

for filename in os.listdir(brain_mri_source_folder):
    parts = filename.split('\\')
    filename_no_extension = os.path.splitext(parts[-1])[0]
    # files --> .nii mri
    # if filename.endswith('.gz'):
    #     filename = filename[:-3]
    df = mri_radiomics_to_csv(filename, roi_mask_source_folder)
    output_filename = os.path.join(output_directory, f'r2f_{filename_no_extension}.csv')
    df.to_csv(output_filename)

# TESTING
# filename = 'C:\\Users\\sanjeevs\\PycharmProjects\\csc4801-scripts\\atlas_registered_scans_temp\\ADNI_002_S_0729_MR_MPR____N3__Scaled_Br_20081027115509985_S56800_I124008.nii\\ADNI_002_S_0729_MR_MPR____N3__Scaled_Br_20081027115509985_S56800_I124008.nii'
# parts = filename.split('\\')
# filename_no_extension = os.path.splitext(parts[-1])[0]
# print(filename_no_extension)
# df = mri_radiomics_to_csv(filename, roi_mask_source_folder)
# output_filename = os.path.join(output_directory, f'r2f_{filename_no_extension}.csv')
# df.to_csv(output_filename)

