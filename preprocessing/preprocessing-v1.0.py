"""
translate orientation.py, registration.py, skull_stripping.py,
and bias_correction.py to work for the project.
"""
import subprocess

# run registration.py
registration_process = subprocess.Popen(['python', 'registration.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
registration_output, registration_error = registration_process.communicate()

if registration_process.returncode == 0:
    print("registration.py executed successfully.")
else:
    print("Error running registration.py:")
    print(registration_error.decode('utf-8'))
    exit()

# run skull_stripping.py
skull_stripping_process = subprocess.Popen(['python', 'skull_stripping.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
skull_stripping_output, skull_stripping_error = skull_stripping_process.communicate()

if skull_stripping_process.returncode == 0:
    print("skull_stripping.py executed successfully.")
else:
    print("Error running skull_stripping.py:")
    print(skull_stripping_error.decode('utf-8'))
    exit()

#TODO: add bias_correction