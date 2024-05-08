import nibabel as nib
from nilearn import image, plotting
import os

img_4d = 'C:\\Users\\sanjeevs\\PycharmProjects\\csc4801-scripts\\radiomics\\BNA_PM_4D.nii'

output_directory = '3d_masks'
os.makedirs(output_directory, exist_ok=True)

print("Original Mask Image Shape: ", image.load_img(img_4d).shape)
roi_num = list(image.load_img(img_4d).shape)[3]

for i in range(roi_num):
    roi_img = image.index_img(img_4d, i)
    output_filename = os.path.join(output_directory, f'roi_mask_{i + 1}.nii')
    nib.save(roi_img, output_filename)