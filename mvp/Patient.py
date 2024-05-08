import numpy as np
import Scan

# Constants
X = 250
Y = 250
Z = 250

class Patient:

    scan_paths: list
    scans: list
    PTID: str
    GMVs: np.array
    R2F: np.array
    R2SN: np.array
    RMCS: np.array
    diagnosis: str


    def __init__(self, scan_paths: list, PTID: str, diagnosis: str):
        self.scan_paths = scan_paths
        self.PTID = PTID
        self.scans = [Scan.Scan(scan_path) for scan_path in scan_paths]
        self.GMVs = np.zeros((246, 1))
        self.R2F = np.zeros((246, 47))
        self.R2SN = np.zeros((246, 246))
        self.RMCS = np.zeros((246, 1))
        self.diagnosis = diagnosis

    def __str__(self):
        return f"Patient {self.PTID} with diagnosis: {self.diagnosis}"
