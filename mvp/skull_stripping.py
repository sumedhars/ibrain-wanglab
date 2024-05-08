from __future__ import print_function
import os
import subprocess
import nibabel as nib
import numpy as np
import zipfile

FSL_BIN_DIR = "/home/kirkpatricki/fsl/share/fsl/bin/"
BET_PATH = os.path.join(FSL_BIN_DIR, "bet")


def create_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def bet(src_path, dst_path, frac="0.5"):
    command = [BET_PATH, src_path, dst_path, "-R", "-f", frac, "-g", "0"]
    subprocess.call(command)
    return


def unwarp_strip_skull(arg, **kwarg):
    return strip_skull(*arg, **kwarg)


def strip_skull(src_path, dst_path, frac="0.4"):
    print("Working on :", src_path)
    try:
        bet(src_path, dst_path, frac)
    except RuntimeError:
        print("\tFailed on: ", src_path)
    return


def main(image_path, output_dir):

    if not os.path.exists(image_path):
        print("Error: Image path does not exist.")
        return
    if not os.path.isdir(output_dir):
        print("Error: Output directory does not exist.")
        return

    dest_filename = os.path.basename(image_path)
    dest_path = os.path.join(output_dir, dest_filename)

    if not os.path.exists(dest_path):
        if dest_path.endswith('.gz'):
            dest_path = dest_path[:-3]

        create_dir(dest_path)
        strip_skull(image_path, dest_path)
    else:
        print(f"Skull-stripped image {dest_filename} found. Skipping...")

    processed_img = nib.load(dest_path + ".gz")
    data = processed_img.get_fdata()
    output_array = np.array(data)

    return output_array



if __name__ == "__main__":
    image_path = "/mnt/c/Users/sanjeevs/PycharmProjects/csc4801-scripts/outputs-v0/registration-output/ADNI_002_S_0729_MR_MPR____N3__Scaled_2_Br_20081001114302922_S17535_I118668.nii.gz"
    output_dir = "/mnt/c/Users/sanjeevs/PycharmProjects/wanglab/data_prep"  # Replace with the path to your output directory
    main(image_path, output_dir)     
