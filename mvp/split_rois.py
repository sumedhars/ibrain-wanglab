import numpy as np
import nibabel as nib
from ants import image_read, resample_image_to_target, registration, ANTsImage, from_numpy

from Patient import Patient

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

def set_atlas(atlas, atlas_loc, ref_loc):
    atlases[atlas] = nib.load(atlas_loc).get_fdata()
    atlas_refs[atlas] = image_read(ref_loc)

def split_ROIs(patients: list[Patient], atlas="Brainnetome", threshold=50):
    """
    Given a list of Patient objects and atlas, split patient scans into regions of interest defined by the atlas.
    
    Current supported atlases:
    - Brainnetome (atlas.brainnetome.org)

    Params:
    patient: iterable of Patient objects
        the patients to perform ROI-splitting for
    atlas: str
        Which atlas to use to perform splitting (see list of supported atlases)
    threshold: int
        The threshold to use for the atlas' probabilistic map to determine which voxels
        in the scan are included in each region
    """
    for patient in patients:
        for scan in patient.scans:
            scan.split_rois(atlases[atlas], atlas_refs[atlas], threshold=threshold)


if __name__ == "__main__":
    set_atlas("Brainnetome", "C:/Users/kirkpatricki/Downloads/BNA_PM_4D.nii", "C:/Users/kirkpatricki/Downloads/HCP40_MNI_1.25mm.nii")
    scan = nib.load("C:/Users/kirkpatricki/Downloads/HCP40_MNI_1.25mm.nii").get_fdata()
    rois = split_ROIs(scan)
    print(rois.shape)