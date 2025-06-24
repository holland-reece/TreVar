"""

TREVAR: Clincal data de-identification, cleaning and organization

Updated 2024-10-04
Created 2024-07-04

Holland Brown (holland.brown@ki.se)

NOTE: must have read and write permissions to the output directory you set

NOTE: for testing code, can use bash command grep -c "<personId><id>.*</id>" ./TREVAR_depression_n2_COPY.xml to see how many personal numbers are in the XML

"""
# %% Set up the script with your paths
import os
import subprocess
import numpy as np
import pandas as pd
from clean_clin_data import clean_clin_data # my module file


# USER OPTIONS

# INPUT
group = 'I' # label of group you're trying to extract ('S', 'D', 'H', or 'I')
wkdir = os.path.join('/Users/hollandbrown/Desktop/ipsy') # path to input filess
participant_info_xlsx = os.path.join('/Users/hollandbrown/Desktop/ipsy', 'TREVAR_patient_participants_I_2023jun-dec.xlsx') # full path to participant info spreadsheet (xlsx)
raw_data_xml = os.path.join('/Volumes/P1/Holland/StodOchBehandling_ins2023_06to12/StodOchBehandling__20241001T132539.xml') # full path to clinical data file (xml)

# OUTPUT
output_directory = os.path.join('/Users/hollandbrown/Desktop/ipsy') # full path to folder where output files will go
output_xml = os.path.join(output_directory, f'TREVAR_StodOchBehandling_I_2023jun-dec.xml') # full path to new clinical data file, which will be de-identified

clean_data = clean_clin_data(participant_info_xlsx, raw_data_xml, output_directory, output_xml) # initiate class

# Search and replace identifiers in the XML and track mismatched data in the study spreadsheet
clean_data.deidentify()
print(clean_data.pptinfo)  

# %% Extract only subjects that are in our study

# create list of subject IDs in this patient group
ids_to_extract = []
for sub in clean_data.pptinfo.index:
    if clean_data.pptinfo.loc[sub]['Group'] == group:
        # if clean_data.pptinfo.loc[sub]['firstName mismatch with clinic data'] != 'Mismatch':
        #     if clean_data.pptinfo.loc[sub]['lastName mismatch with clinic data'] != 'Mismatch':
        #         if clean_data.pptinfo.loc[sub]['PNR mismatch with clinic data'] != 'Mismatch':
        # print(sub)
        ids_to_extract.append(str(sub))

print(f'Number of subjects to extract: {len(ids_to_extract)}')
name_space = {'riv': 'urn:riv:infrastructure:export:1'} # string (XML name space)
clean_data.extract_by_ids(ids_to_extract, name_space, group)

# %%
