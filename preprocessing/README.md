### Running registration.py and skull_stripping.py:
- Install WSL and FSL:
    - https://learn.microsoft.com/en-us/windows/wsl/install
    - https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation/Windows
- To run the programs, do the following:
    - Enter wsl in Windows command prompt 
    - Enter 'which fslreorient2std' and 'which bet' to update the FSL_BIN_DIR variable in both files. 
    - Update the data source directory and data destination directories in both files. Important: The data source directory for skull_stripping.py should be the data destination directory for the registration.py


### registration.py:
- The registration template needed to run registration.py is present in the registration-template folder. 
- Update the ref_path variable accordingly
