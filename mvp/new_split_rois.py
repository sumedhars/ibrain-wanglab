import os
import numpy as np
import nibabel as nib
from ants import image_read

from Scan import Scan

try:
    atlases = {
        "Brainnetome": nib.load("/data/csc4801/WangLab/BNA_PM_4D.nii").get_fdata()
    }

    atlas_refs = {
        "Brainnetome": image_read("/data/csc4801/WangLab/atlas_reference/HCP40_MNI_1.25mm.nii")
    }
except FileNotFoundError:
    print("WARNING: Atlas and Atlas reference were not in the expected locations. Please use set_atlas() to set custom atlas paths.")
    atlases = {}
    atlas_refs = {}

atlases = {}
atlas_refs = {}

def set_atlas(atlas, atlas_loc, ref_loc):
    print("Setting atlases")
    atlases[atlas] = nib.load(atlas_loc).get_fdata()
    atlas_refs[atlas] = image_read(ref_loc)
    print("Atlas loaded")


def process_scans(directory, output_directory, atlas="Brainnetome", threshold=50):
    print("Preprocessing Scans")
    for patient_id in os.listdir(directory):
        patient_path = os.path.join(directory, patient_id)
        if os.path.isdir(patient_path):
            for filename in os.listdir(patient_path):
                if filename.endswith(".nii"):
                    scan_path = os.path.join(patient_path, filename)
                    scan = Scan(scan_path)
                    scan.split_rois(atlases[atlas], atlas_refs[atlas], threshold)
                    save_rois(scan.rois, patient_id, output_directory)


def save_rois(rois, patient_id, output_directory):
    output_dir = os.path.join(output_directory, patient_id)
    os.makedirs(output_dir, exist_ok=True)
    for i, roi in enumerate(rois):
        roi_img = nib.Nifti1Image(roi, np.eye(4))  # Assuming affine as identity for simplicity
        nib.save(roi_img, os.path.join(output_dir, f"roi_{i}.nii"))
    print("Saved ROIs")


def main():
    print("running main")
    set_atlas("Brainnetome", "/mnt/c/Users/sanjeevs/PycharmProjects/csc4801-scripts/other-data/atlas/BNA_PM_4D.nii", "/mnt/c/Users/sanjeevs/PycharmProjects/csc4801-scripts/other-data/atlas/HCP40_MNI_1.25mm.nii")
    process_scans("/mnt/c/Users/sanjeevs/PycharmProjects/wanglab/mvp/training_images", "/mnt/c/Users/sanjeevs/PycharmProjects/wanglab/mvp/cleaned_data")

main()