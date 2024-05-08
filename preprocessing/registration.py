import os
import subprocess
import matplotlib.pyplot as plt
from multiprocessing import Pool, cpu_count

FSL_BIN_DIR = "/home/sumedhars/fsl/share/fsl/bin/"
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
    command = [FLIRT_PATH, "-in", src_path, "-ref", ref_path, "-out", dst_path,
               "-bins", "256", "-cost", "corratio", "-searchrx", "0", "0",
               "-searchry", "0", "0", "-searchrz", "0", "0", "-dof", "12",
               "-interp", "spline"]
    subprocess.call(command, stdout=open(os.devnull, "r"),
                    stderr=subprocess.STDOUT)
    return

def orient2std(src_path, dst_path):
    # Use absolute path for fslreorient2std
    command = [FSLREORIENT_PATH, src_path, dst_path]
    subprocess.call(command)
    return


def create_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    return


def unwarp_main(arg, **kwarg):
    return registration(*arg, **kwarg)


def registration(src_path, dst_path, ref_path):
    print("Registration on: ", src_path)
    try:
        orient2std(src_path, dst_path)
        registration(dst_path, dst_path, ref_path)
    except RuntimeError:
        print("\tFailed on: ", src_path)

    return


def main():
    data_src_dir = "/mnt/c/Users/sanjeevs/PycharmProjects/csc4801-scripts/test-output-folder"
    data_dst_dir = "/mnt/c/Users/sanjeevs/PycharmProjects/csc4801-scripts/outputs/registration-output"

    ref_path = "/mnt/c/Users/sanjeevs/PycharmProjects/csc4801-scripts/registration-template/MNI152_T1_1mm.nii.gz"

    data_src_paths, data_dst_paths = [], []
    for root, _, files in os.walk(data_src_dir):
        for filename in files:
            src_path = os.path.join(root, filename)
            dest_path = os.path.join(data_dst_dir,filename)
            create_dir(dest_path)
            data_src_paths.append(src_path)
            data_dst_paths.append(dest_path)
            #print(src_path, dest_path)

    # Test
    # main(data_src_paths[0], data_dst_paths[0], ref_path)

    # running through every image
    for i in range(len(data_src_paths)):
        registration(data_src_paths[i], data_dst_paths[i], ref_path)