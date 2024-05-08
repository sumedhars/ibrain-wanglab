import SimpleITK as sitk
from radiomics import featureextractor

image_path = 'C:\\Users\\sanjeevs\\PycharmProjects\\csc4801-scripts\\test-output-folder\\AD\\002_S_0816\\ADNI_002_S_0816_MR_MPR____N3__Scaled_2_Br_20081001115756935_S19532_I118684.nii'
mask_path = "mask_image.nii"
image = sitk.ReadImage(image_path)
mask = sitk.ReadImage(mask_path)

extractor = featureextractor.RadiomicsFeatureExtractor()

extractor.enableFeatureClassByName('firstorder')

# extract features
feature_vector = extractor.execute(image, mask)

# the first-order features
for feature_name in feature_vector.keys():
    print(f"{feature_name}: {feature_vector[feature_name]}")