"""
translate orientation.py, registration.py, skull_stripping.py,
and bias_correction.py to work for the project.
"""
import skull_stripping as skullstripping
import registration as regis
import os
import traceback
from pathlib import Path

def main(patients, out_dir):
    reg_dir = "/mnt/c/Users/kirkpatricki/src/DataSciencePracticum/wanglab/outputs/registration-output"
    skull_strip_dir = "/mnt/c/Users/kirkpatricki/src/DataSciencePracticum/wanglab/outputs/skull-stripping-output"
    ref_path = "/mnt/c/Users/kirkpatricki/src/DataSciencePracticum/wanglab/HCP40_MNI_1.25mm.nii"
    # Input image path
    # reg_input_image_path = "/mnt/c/Users/sanjeevs/PycharmProjects/csc4801-scripts/test-output-folder/AD/002_S_0816/ADNI_002_S_0816_MR_MPR____N3__Scaled_2_Br_20081001115756935_S19532_I118684.nii"
    # skull_strip_image_path = "/mnt/c/Users/kirkpatricki/src/DataSciencePracticum/wanglab/outputs/registration-output/ADNI_002_S_0729_MR_MPR____N3__Scaled_2_Br_20081001114302922_S17535_I118668.nii.gz"
    
    for p in patients:
        # print("Registering scans for:", p)
        for s in p.scan_paths:
            # run registration.py
            try:
                regis.main(s, os.path.join(reg_dir, p.diagnosis), ref_path)
            except KeyboardInterrupt:
                raise
            except:
                print(traceback.format_exc())
    # print("Test")
    # run skull_stripping.py
    for p in patients:
        for i, (scan_path, scan) in enumerate(zip(p.scan_paths, p.scans)):
            try:
                assert scan_path == scan.path
                dest_path = os.path.join(skull_strip_dir, p.diagnosis)
                os.makedirs(dest_path, exist_ok=True)
                output_array = skullstripping.main(scan_path, dest_path)
                # print("Test 2")
                scan.clean_data = output_array
                saved_scan = os.path.join(out_dir, p.PTID, Path((scan_path)).stem+".pkl")
                os.makedirs(os.path.join(out_dir, p.PTID), exist_ok=True)
                scan.save(saved_scan)
                p.scan_paths[i] = saved_scan
                del scan
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(str(e))

        
if __name__ == "__main__":
    main()
