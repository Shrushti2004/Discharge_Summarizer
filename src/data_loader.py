import pandas as pd
import os

BASE_PATH = r"C:\Users\Shrushti Modak\OneDrive\Desktop\Discharge_Summarizer\data\raw"

def load_csv(filename):
    """
    Handles both:
    1. data/raw/patients.csv
    2. data/raw/patients.csv/patients.csv
    """

    # First try normal file path
    normal_path = os.path.join(BASE_PATH, filename)

    # If it's a file → load directly
    if os.path.isfile(normal_path):
        print(f"Loading file: {normal_path}")
        return pd.read_csv(normal_path)

    # If it's a directory → go inside and find actual csv
    elif os.path.isdir(normal_path):
        nested_file = os.path.join(normal_path, filename)
        if os.path.isfile(nested_file):
            print(f"Loading nested file: {nested_file}")
            return pd.read_csv(nested_file)
        else:
            raise FileNotFoundError(f"CSV file not found inside folder: {normal_path}")

    else:
        raise FileNotFoundError(f"File or folder not found: {normal_path}")


# Load all datasets
patients = load_csv("patients.csv")
admissions = load_csv("admissions.csv")
diagnoses = load_csv("diagnoses_icd.csv")
labs = load_csv("labevents.csv")
labs_items = load_csv("d_labitems.csv")
prescriptions = load_csv("prescriptions.csv")

print("\nAll datasets loaded successfully ✅")