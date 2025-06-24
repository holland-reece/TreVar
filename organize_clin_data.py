"""

TREVAR: Clincal data de-identification, cleaning and organization

- SCRIPT: /trevar_clin_data_clean.py
- reads study IDs, participant names and personal numbers from a spreadsheet ('participant_info_xlsx', an XLSX file) into a pandas dataframe
- searches for matching names/personnummers in clinical data file ('raw_data_xml', an XML file)
- copies matching participants' data to a new XML file ('output_xml', an XML file); ommits patients not enrolled in TREVAR
- replaces participant names and personnummers with study IDs in output_xml
- when participants' first name, last name, or personnummer are not found in the clinical data file, writes what info was not found in participant_info_xlsx
- reformats/organizes participant clinical data from (now de-identified) output_xml in a CSV ('output_csv', a CSV file)
- RESULT: a copy of the original clinical data file containing only de-identified data of participants enrolled in the study; missing/mismatched info tracked in participant_info_xlsx

Updated 2024-09-03
Created 2024-07-04

NOTE: must have read and write permissions to the output directory you set

NOTE: for testing code, can use bash command grep -c "<personId><id>.*</id>" ./TREVAR_depression_n2_COPY.xml to see how many personal numbers are in the XML

NOTE: helpful source about parsing XML in python: https://docs.python.org/3/library/xml.etree.elementtree.html

"""
# %% Set up the script with your paths
import os
import subprocess
import numpy as np
import pandas as pd
import xml.etree as etree
import xml.etree.ElementTree as ET
from clean_clin_data import clean_clin_data

# INPUT
# group = 'S' # label of group you're trying to extract ('S', 'D', 'H', or 'I')
wkdir = os.path.join('/Users/hollandbrown/Desktop/ipsy') # path to input filess
participant_info_xlsx = os.path.join('/Users/hollandbrown/Desktop/ipsy', 'TREVAR_patient_participants_S_2023jun-dec.xlsx') # full path to participant info spreadsheet (xlsx)
raw_data_xml = os.path.join('/Volumes/P1/Holland/StodOchBehandling__soc2023_06to12/StodOchBehandling__20241001T131814.xml') # full path to clinical data file (xml)

# OUTPUT
output_directory = os.path.join('/Users/hollandbrown/Desktop/ipsy') # full path to folder where output files will go
output_xml = os.path.join(output_directory, f'TREVAR_StodOchBehandling_S_2023jun-dec.xml') # full path to new clinical data file, which will be de-identified

clean_data = clean_clin_data(participant_info_xlsx, raw_data_xml, output_directory, output_xml) # initiate class

# Parse xml file
tree = ET.parse(clean_data.outxml)
root = tree.getroot()

# %% Read output XML into python element tree (way of parsing XML files in python)
tree = ET.parse(clean_data.outxml)
root = tree.getroot()

# Exploring the XML tree (this part doesn't save anything)
for child in root.iter():
    print(f'\nCHILD: {child}')

    for grandchild in child:
        print(f'\tG1.TAG: {grandchild.tag}') # labels for the data
        print(f'\t\tG1.TEXT: {grandchild.text}')

        # See if there are deeper branches in the tree
        for grandchild2 in grandchild:
            print(f'\t\tG2.TAG: {grandchild2.tag}') 
            print(f'\t\t\tG2.TEXT: {grandchild2.text}') # print the data stored with this label (a question, an answer, a scale rating, etc.)

            for grandchild3 in grandchild2:
                print(f'\t\t\tG3.TAG: {grandchild3.tag}') 
                print(f'\t\t\t\tG3.TEXT: {grandchild3.text}') # print the data stored with this label (a question, an answer, a scale rating, etc.)

# %% Test 3 : extracts everything under 'processes' if firstName == studyID
# Define the namespace and the target firstName
namespace = {'riv': 'urn:riv:infrastructure:export:1'}
# subjID = '16389'  # Replace with the name you're searching for

# # Parse the XML file
# tree = ET.parse('your_input_file.xml')
# root = tree.getroot()

# Create a new XML tree for storing the extracted elements
new_root = ET.Element('root')  # Create a new root for the output file

# Iterate over all <processes> elements
for processes in root.findall('riv:processes', namespace):
    # Within each <processes>, find all <resident> elements
    for resident in processes.findall('riv:resident', namespace):
        # Check if the <firstName> of the resident matches the target value
        first_name = resident.find('riv:firstName', namespace)
        if first_name is not None and first_name.text == subjID:
            # Append the entire <processes> element to the new root and break out of the loop
            new_root.append(processes)
            break  # Stop checking other residents within the same <processes>

# Create a new tree and write it to a new XML file
new_tree = ET.ElementTree(new_root)
new_tree.write(f'{output_directory}/{subjID}_extracted.xml', encoding='utf-8', xml_declaration=True)

# %% Read output XML into python element tree (way of parsing XML files in python)
# Exploring the XML tree (this part doesn't save anything)
for child in new_root.iter():
    print(f'\nCHILD: {child}')

    for grandchild in child:
        print(f'\tG1.TAG: {grandchild.tag}') # labels for the data
        print(f'\t\tG1.TEXT: {grandchild.text}')

        # See if there are deeper branches in the tree
        for grandchild2 in grandchild:
            print(f'\t\tG2.TAG: {grandchild2.tag}') 
            print(f'\t\t\tG2.TEXT: {grandchild2.text}') # print the data stored with this label (a question, an answer, a scale rating, etc.)

            for grandchild3 in grandchild2:
                print(f'\t\t\tG3.TAG: {grandchild3.tag}') 
                print(f'\t\t\t\tG3.TEXT: {grandchild3.text}') # print the data stored with this label (a question, an answer, a scale rating, etc.)
# %%
