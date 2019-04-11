"""DEPRECATED

Sets up the directories for Grades spreadsheets

Results:
    Creates a folder hierarchy in Grades which creates folders for each
    program and folders for core and co-op.
"""

def Create_Directories():
    # Imports
    import os

    # Create the subdirectories starting from Grades
    os.makedirs("Grades/Core", exist_ok=True)
    os.makedirs("Grades/Co-op", exist_ok=True)
    os.makedirs("Grades/ENCM", exist_ok=True)
    os.makedirs("Grades/ENCV", exist_ok=True)
    os.makedirs("Grades/ENEL", exist_ok=True)
    os.makedirs("Grades/ENMC", exist_ok=True)
    os.makedirs("Grades/ENPR", exist_ok=True)
    os.makedirs("Grades/ONAE", exist_ok=True)
    os.makedirs("Grades/ENUD", exist_ok=True)

    # Add the histograms folder
    os.makedirs("Histograms", exist_ok=True)
