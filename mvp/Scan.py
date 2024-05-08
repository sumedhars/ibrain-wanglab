import os

import numpy as np
from ants import threshold_image, image_read, resample_image_to_target, registration, from_numpy
import nibabel as nib

from sklearn.preprocessing import MinMaxScaler
from scipy.stats import pearsonr
import dill

import preprocess

class Scan:

    path: str
    data: np.array
    clean_data: np.array
    rois: np.array

    GMVs: np.array
    R2F: np.array
    R2SN: np.array
    RMCS: np.array

    def __init__(self, path):
        self.path = path
        self.scan()

        self.GMVs = np.zeros((246, 1))
        self.R2F = np.zeros((246, 47))
        self.R2SN = np.zeros((246, 246))
        self.RMCS = np.zeros((246, 1))

    def scan(self):
        img = nib.load(self.path)
        self.data = np.array(img.dataobj)
        self.preprocess()

    def preprocess(self):
        reg_dir = "/data/csc4801/WangLab/cleaned_scans/registered"
        skull_strip_dir = "/data/csc4801/WangLab/cleaned_scans/skullstripped"
        ref_path = "/data/csc4801/WangLab/MNI152_T1_1mm.nii.gz"
        reg_input_image_path = self.path
        skull_strip_image_path = self.path  

        self.clean_data = preprocess.preprocess_main(reg_input_image_path, reg_dir, skull_strip_image_path,
                                                     skull_strip_dir, ref_path)
        if self.clean_data is None:
            self.clean_data = self.data  # Fallback to original data if preprocessing fails

    
    def split_rois(self, atlas, ref, threshold=50):
        """
        Given an MR scan and atlas, split into regions of interest defined by the atlas.

        Current supported atlases:
        - Brainnetome (atlas.brainnetome.org)

        Params:
        scan: Numpy.memmap or similar object | ANTsImage
            The scan to split into ROIs
        atlas: str
            Which atlas to use to perform splitting (see list of supported atlases)
        threshold: int
            The threshold to use for the atlas' probabilistic map to determine which voxels
            in the scan are included in each region
        """
        scan = from_numpy(self.clean_data)
        # register scan to atlas reference
        resampled = resample_image_to_target(image=scan, target=ref)
        registered_scan = registration(fixed=ref, moving=resampled, type_of_transform='SyN')['warpedmovout'].numpy()

        at = (atlas > threshold).astype('float')
        rois = []
        for i in range(at.shape[-1]):
            atlas_roi = at[:,:,:,i]
            roi = registered_scan * atlas_roi
            rois.append(roi)
        self.rois = np.array(rois)

    def save(self, dest):
        with open(dest, 'wb') as file:
            dill.dump(self, file)
    
    @staticmethod
    def load(src):
        with open(src, 'rb') as file:
            scan = dill.load(file)
        return scan
