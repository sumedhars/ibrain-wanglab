"""
translate orientation.py, registration.py, skull_stripping.py,
and bias_correction.py to work for the project.
"""
import skull_stripping as skullstripping
import registration as regis
import os


def preprocess_main(reg_input_image_path, reg_dir, skull_strip_image_path, skull_strip_dir, ref_path):
    try:
        regis.main(reg_input_image_path, reg_dir, ref_path)
    except Exception as e:
        print(f"An error occurred in registration: {e}")

    try:
        output_array = skullstripping.main(skull_strip_image_path, skull_strip_dir)
        return output_array
    except Exception as e:
        print(f"An error occurred in skull stripping: {e}")
        return None

        
if __name__ == "__main__":
    main()
