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


    def roi_to_radiomics(self, image_path, mask_path):
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


    def mri_radiomics_to_csv(self, mri_image_path, roi_mask_source_folder):
        # row --> radiomics feature || column --> ROI number
        mri_radiomics_list = []
        #mri_radiomics_df = pd.DataFrame(columns=self.selected_radiomics_features)
        for individual_roi_mask in os.listdir(roi_mask_source_folder):
            individual_roi_mask_path = os.path.join(roi_mask_source_folder, individual_roi_mask)
            print(individual_roi_mask_path)
            indv_roi_dict = self.roi_to_radiomics(mri_image_path, individual_roi_mask_path)
            if not indv_roi_dict:
                print("Skipping current mask as no radiomics features were extracted.")
                continue
            subset_roi_dict = {key:indv_roi_dict[key] for key in self.selected_radiomics_features}
            mri_radiomics_list.append(subset_roi_dict)
            mri_radiomics_df = pd.DataFrame(mri_radiomics_list)
        return mri_radiomics_df
    

    # --------------------------------------------------------------------------------
    
    def np_radiomics_to_csv(self, scan_np, roi_mask_source_folder):
        # row --> radiomics feature || column --> ROI number
        mri_radiomics_list = []
        #mri_radiomics_df = pd.DataFrame(columns=self.selected_radiomics_features)

        print("calculating r2f for each roi")
        for individual_roi_mask in tqdm(os.listdir(roi_mask_source_folder)):
            individual_roi_mask_path = os.path.join(roi_mask_source_folder, individual_roi_mask)
            indv_roi_dict = self.np_roi_to_radiomics(scan_np, individual_roi_mask_path)
            if not indv_roi_dict:
                print("Skipping current mask as no radiomics features were extracted.")
                continue
            # subset_roi_dict = {key:indv_roi_dict[key] for key in self.selected_radiomics_features}
            # mri_radiomics_list.append(subset_roi_dict)
            mri_radiomics_list.append(indv_roi_dict)
        
        mri_radiomics_df = pd.DataFrame(mri_radiomics_list)

        # mri_radiomics_df.to_csv("C:\\Users\\andrewss\\PycharmProjects\\wanglab\\test_images\\test_r2f\\scan_1_r2f.csv")

        return mri_radiomics_df


    def np_roi_to_radiomics(self, image_np, mask_path):
        # print("inside np_roi_to_radiomics")
        radiomics_values = {}
        image = sitk.GetImageFromArray(image_np)
        mask = sitk.ReadImage(mask_path)
        
        if sitk.GetArrayFromImage(mask).max() == 0:
            print("No labels found in the mask. Skipping radiomics feature extraction.")
            return radiomics_values
        
        # Modify mask array in-place to save memory
        mask_array = sitk.GetArrayFromImage(mask)
        mask_array[mask_array != 0] = 1
        mask = sitk.GetImageFromArray(mask_array)
        resampled_mask = sitk.Resample(mask, image, interpolator=sitk.sitkNearestNeighbor)
        
        try:
            feature_vector = self.extractor.execute(image, resampled_mask)
            radiomics_values.update(feature_vector)
        except ValueError as e:
            print("Error during radiomics feature extraction:", e)
        
        return radiomics_values


    # def np_roi_to_radiomics(self, image_np, mask_path):
    #     print("inside np_roi_to_radiomics")
    #     radiomics_values = {}
    #     image = sitk.GetImageFromArray(image_np)
    #     mask = sitk.ReadImage(mask_path)
    #     if sitk.GetArrayFromImage(mask).max() == 0:
    #         print("No labels found in the mask. Skipping radiomics feature extraction.")
    #         return radiomics_values
    #     # added to replace all non 1 values w/ 1
    #     mask_array = sitk.GetArrayFromImage(mask)
    #     mask_array[mask_array != 0] = 1
    #     mask = sitk.GetImageFromArray(mask_array)
    #     resampled_mask = sitk.Resample(mask, image, interpolator=sitk.sitkNearestNeighbor)
    #     try:
    #         extractor = featureextractor.RadiomicsFeatureExtractor()
    #         extractor.enableFeatureClassByName('firstorder')
    #         feature_vector = extractor.execute(image, resampled_mask)
    #         for feature_name in feature_vector.keys():
    #             radiomics_values[feature_name] = feature_vector[feature_name]
    #     except ValueError as e:
    #         print("Error during radiomics feature extraction:", e)
    #     return radiomics_values


if __name__ == "__main__":
    brain_mri_source_folder = 'C:\\Users\\sanjeevs\\PycharmProjects\\csc4801-scripts\\atlas_registered_scans'
    roi_mask_source_folder = 'C:\\Users\\sanjeevs\\PycharmProjects\\csc4801-scripts\\radiomics\\3d_masks'
    processor = RadiomicsProcessor()
    result_df = processor.mri_radiomics_to_csv(brain_mri_source_folder, roi_mask_source_folder)
    print(result_df)































class RadiomicsBatchProcessor:
    def __init__(self, batch_size=10):
        self.batch_size = batch_size
        self.extractor = featureextractor.RadiomicsFeatureExtractor()
        self.extractor.enableFeatureClassByName('firstorder')

    def batch_process_radiomics(self, scan_np, roi_mask_source_folder):
        gc.collect()
        all_files = os.listdir(roi_mask_source_folder)
        total_files = len(all_files)
        batches = (total_files - 1) // self.batch_size + 1

        # Process each batch
        all_radiomics = []
        for i in range(batches):
            batch_files = all_files[i*self.batch_size:(i+1)*self.batch_size]
            batch_radiomics = self.process_batch(scan_np, roi_mask_source_folder, batch_files)
            all_radiomics.extend(batch_radiomics)
            print(f"Processed batch {i+1}/{batches}")

        # Convert to DataFrame
        radiomics_df = pd.DataFrame(all_radiomics)
        return radiomics_df

    def process_batch(self, scan_np, roi_mask_source_folder, batch_files):
        batch_radiomics = []
        print("processing batch")
        for filename in tqdm(batch_files):
            filepath = os.path.join(roi_mask_source_folder, filename)
            radiomics_features = self.np_roi_to_radiomics(scan_np, filepath)
            if radiomics_features:
                batch_radiomics.append(radiomics_features)
            gc.collect()
        return batch_radiomics

    # @profile
    def np_roi_to_radiomics(self, image_np, mask_path):
        print("inside np_roi_to_radiomics")
        radiomics_values = {}

        # Efficient handling of mask
        mask = sitk.ReadImage(mask_path)
        mask_array = sitk.GetArrayFromImage(mask)
        if mask_array.max() == 0:
            print("No labels found in the mask. Skipping radiomics feature extraction.")
            return {}

        # Convert non-zero mask values to 1 (do this in place to save memory)
        mask_array[mask_array != 0] = 1
        mask = sitk.GetImageFromArray(mask_array)

        # Reduce the frequency of resampling if possible
        image = sitk.GetImageFromArray(image_np)  # Consider moving this outside if image_np doesn't change
        resampled_mask = sitk.Resample(mask, image, interpolator=sitk.sitkNearestNeighbor)

        try:
            feature_vector = self.extractor.execute(image, resampled_mask)
            radiomics_values.update(feature_vector)
        except Exception as e:
            print("Error during radiomics feature extraction:", e)

        return radiomics_values