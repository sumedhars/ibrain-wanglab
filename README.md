## MSOE EECS - CSC 4801: Data Science Practicum - WangLab - IBrain++

This project aims to replication the IBRAIN model created in the paper, "A neuroimaging biomarker for Individual Brain-Related Abnormalities In Neurodegeneration (IBRAIN): a cross-sectional study" by using information from the paper and its supplemental information. This replicated model is called IBRAIN++. 

The following steps are a brief overview of what was done:
1. Obtained the ADNI dataset since this was what was used in the paper
2. EDA on non-MRI features from the ADNI dataset to identify any non-MRI features that were significant
3. Organize ADNI MRI data by diagnosis & patient ID
4. Visualization script for MRI images
5. Preprocessing - registration & skull stripping MR Images using FSL
6. Reshape images to match Brainnetome atlas orientation & size
7. Break image into 246 Regions of Interest (ROIs)
8. Perform feature engineering to extract four features from the images for each ROI for each image:
   a) Gray matter volume (GMV)
   b) Regional Radiomics Features (R2F)
   c) Regional Radiomics Similarity Network (R2SN)
   d) Regional Radiomics Mean Connectivity Strength (RMCS)
9. Use a linear model to build a final model from predicting using these engineered features
10. Build an additional model using ADAS Cog scores provided in the ADNI clinical data

### Authors and acknowledgment
- Aidan Waterman
- Ian Kirkpatrick
- Sierra Andrews
- Sumedha Sanjeev
