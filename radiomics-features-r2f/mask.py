import numpy as np
import nibabel as nib

# Load the NIfTI image
nii_img = nib.load('C:\\Users\\sanjeevs\\PycharmProjects\\csc4801-scripts\\test-output-folder\\AD\\002_S_0816\\ADNI_002_S_0816_MR_MPR____N3__Scaled_2_Br_20081001115756935_S19532_I118684.nii')

# Get the shape of the image data array
depth, height, width = nii_img.shape[:3]

# Calculate the index where the bottom 1/4 of the image starts
bottom_start_index = depth - depth // 4

# Create a mask with all ones
mask_data = np.ones((depth, height, width), dtype=np.uint8)

# Set the bottom 1/4 of the mask to 0s
mask_data[bottom_start_index:, :, :] = 0

# Create a new NIfTI image for the mask
mask_img = nib.Nifti1Image(mask_data, affine=nii_img.affine)

# Save the mask image to a file
nib.save(mask_img, 'mask_image.nii')
