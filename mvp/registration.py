import os
import subprocess
import matplotlib.pyplot as plt
from multiprocessing import Pool, cpu_count

FSL_BIN_DIR = "/home/kirkpatricki/fsl/share/fsl/bin/"
FSLREORIENT_PATH = os.path.join(FSL_BIN_DIR, "fslreorient2std")
FLIRT_PATH = os.path.join(FSL_BIN_DIR, "flirt")


def plot_middle(data, slice_no=None):
    if not slice_no:
        slice_no = data.shape[-1] // 2
    plt.figure()
    plt.imshow(data[..., slice_no], cmap="gray")
    plt.show()
    return


def registration(src_path, dst_path, ref_path):
    # Use absolute paths for the executables
    command = [FLIRT_PATH, "-in", src_path, "-ref", ref_path,
               "-out", dst_path, "-bins", "256", "-cost",
               "corratio", "-searchrx", "0", "0", "-searchry", "0", "0",
               "-searchrz", "0", "0", "-dof", "12", "-interp", "spline"]
    # print("\t" + " ".join(command))
    subprocess.call(command, stdout=open(os.devnull, "r"),
                    stderr=subprocess.STDOUT)
    return

def orient2std(src_path, dst_path):
    # Use absolute path for fslreorient2std
    command = [FSLREORIENT_PATH, src_path, dst_path]
    # print("\t" + " ".join(command))
    subprocess.call(command)
    return


def create_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    return


def unwarp_main(arg, **kwarg):
    return registration(*arg, **kwarg)


def registration1(src_path, dst_path, ref_path):
    print("Registration on:", src_path)
    # print("\tTo:", dst_path)
    try:
        orient2std(src_path, dst_path)
        registration(dst_path, dst_path, ref_path)
        # print("\tSuccess")
    except RuntimeError:
        print("\tFailed on: ", src_path)
    return


def main(image_path, output_dir, ref_path):
    # Prepare destination path
    filename = os.path.basename(image_path)
    dest_path = os.path.join(output_dir, filename)
    # if the path already exists, it is assumed to have been registered.
    # Permit compressed and non-compressed file types.
    if not (os.path.exists(dest_path) or os.path.exists(dest_path+".gz")):
        os.makedirs(output_dir, exist_ok=True)
        # create_dir(output_dir)
        # Perform registration
        registration1(image_path, dest_path, ref_path)
    else:
        print(f"Image {image_path} already registered, skipping...")


if __name__ == "__main__":
    # Define paths
    data_dst_dir = "/mnt/c/Users/kirkpatricki/src/DataSciencePracticum/wanglab/outputs/registration-output"
    ref_path = "/mnt/c/Users/kirkpatricki/DataSciencePracticum/wanglab/HCP40_MNI_1.25mm.nii.gz"

    # Input image path
    image_path = "/mnt/c/Users/kirkpatricki/DataSciencePracticum/wanglab/AD/002_S_0816/ADNI_002_S_0816_MR_MPR____N3__Scaled_2_Br_20081001115756935_S19532_I118684.nii"

    # Run registration
    main(image_path, data_dst_dir, ref_path)
