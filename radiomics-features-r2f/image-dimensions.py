import nibabel as nib

nii_img = nib.load('C:\\Users\\sanjeevs\\PycharmProjects\\csc4801-scripts\\test-output-folder\\AD\\002_S_0816\\ADNI_002_S_0816_MR_MPR____N3__Scaled_2_Br_20081001115756935_S19532_I118684.nii')
#nii_img = nib.load('mask_image.nii')

data = nii_img.get_fdata()

# shape of the image data array
depth, height, width = data.shape

print("Depth:", depth)
print("Height:", height)
print("Width:", width)
