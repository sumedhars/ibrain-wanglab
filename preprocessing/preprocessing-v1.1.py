"""
translate orientation.py, registration.py, skull_stripping.py,
and bias_correction.py to work for the project.
"""
import mvp.skull_stripping as skullstripping
import registration as regis
import os

def main():
        
    # run registration.py
    try:
        regis.main()
    except:
        print("An error has occurred in registration.py")

    # run skull_stripping.py
    try:
        skullstripping.main()
    except:
        print("An error has occurred in skull_stripping.py")

    #TODO: add bias_correction
        
if __name__ == "__main__":
    main()