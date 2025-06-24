import os
import subprocess
import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET
# from typing import List, Union

class clean_clin_data:

    def __init__(self, participant_info_xlsx: str, raw_data_xml: str, output_directory: str, output_xml: str):
        self.rawxml = raw_data_xml
        self.outdir = output_directory
        self.outxml = output_xml

        # Read study IDs, participant names and personal numbers from the participant info XLSX into a pandas dataframe
        self.pptinfo_path = participant_info_xlsx
        self.pptinfo = pd.read_excel(participant_info_xlsx, index_col=0)

        # append columns to pptinfo to track mismatches between pptinfo and the XML file
        tmp_list = [''] * len(self.pptinfo) # init empty string list to add empty columns to pptinfo
        if ("firstName mismatch with clinic data" in self.pptinfo.columns) == False:
            self.pptinfo.insert(7, "firstName mismatch with clinic data", tmp_list, True)
        if ("lastName mismatch with clinic data" in self.pptinfo.columns) == False:
            self.pptinfo.insert(8, "lastName mismatch with clinic data", tmp_list, True)
        if ("PNR mismatch with clinic data" in self.pptinfo.columns) == False:
            self.pptinfo.insert(9, "PNR mismatch with clinic data", tmp_list, True)

        print(f'Number of Rows (Participants): {self.pptinfo.shape[0]}')
        # print(f'Number of Columns: {self.pptinfo.shape[1]}\n')
        # print('First 3 rows:\n')
        # print(self.pptinfo.head(3)) # print first 10 rows of dataframe to see that spreadsheet was read correctly

        # If output dir does not exist, create new dir
        if os.path.isdir(self.outdir) == False:
            subprocess.run(f"mkdir {self.outdir}", shell=True, executable='/bin/bash')

        # If file does not exist, create copy of raw data XML in output dir
        if os.path.isfile(self.outxml) == False:
            print('Copying raw XML file to output dir...')
            subprocess.run(f"cp {self.rawxml} {self.outxml}", shell=True, executable='/bin/bash')

    # Read participant's identifiers and studyID from the study spreadsheet, self.pptinfo, into a dictionary
    def deID_read_ppt_info(self, study_id):
        row = self.pptinfo.loc[study_id] # one participant's row of dataframe

        # Get first and last name from Excel spreadsheet
        # NOTE: only works if participants only have two names; else third name will remain in XLM file
        name = row.loc['Name']
        n = name.split(' ') # split string where space is between the names
        first_name = n[0]
        last_name = n[1]

        # Get the personnummer from the spreadsheet
        person_id = row.loc['PNR']

        # print(f'ID: {study_id}\nFirst Name: {first_name}\nLast Name: {last_name}\nPersonal Number: {person_id}\n\n') # TEST

        info = {'studyID': study_id, 'firstName': first_name, 'lastName': last_name, 'personID': person_id}

        # print(f'ID: {info['studyID']}\nFirst Name: {info['firstName']}\nLast Name: {info['lastName']}\nPersonal Number: {info['personID']}\n\n') # TEST

        return info # return participant's identifiers in a dictionary
    
    # Takes note of participants in the spreadsheet whose data don't match the clinical data file
    def deID_track_mismatch(self, study_id, out1, out2, out3):
        # df = self.pptinfo # make a copy of participant info pandas dataframe
        # if out1 != "b'first name found\n'":
        if out1 == "b''":
            self.pptinfo.loc[study_id, 'firstName mismatch with clinic data'] = 'Mismatch'
        if out2 == "b''":
            self.pptinfo.loc[study_id, 'lastName mismatch with clinic data'] = 'Mismatch'
        if out3 == "b''":
            self.pptinfo.loc[study_id, 'PNR mismatch with clinic data'] = 'Mismatch'
        

    # Replace participant names and personnummers with study IDs in new file (de-identification)
    def deID_replace_identifiers(self, identifiers):
        pnr_string = 'XXXXXX-XXXX'
        
        # Tracking mismatched info and editing XML to remove identifiers
        out = subprocess.run(f"""if grep -qF "{identifiers['firstName']}" {self.outxml}; then echo -e "first name found" && sed -i.bu 's;{identifiers['firstName']};{identifiers['studyID']};g' {self.outxml}; fi""", shell=True, executable='/bin/bash', stdout=subprocess.PIPE) # replace first name with study ID
        output1 = str(out.stdout)
        out = subprocess.run(f"""if grep -qF "{identifiers['lastName']}" {self.outxml}; then echo -e "last name found" && sed -i.bu 's;{identifiers['lastName']};{identifiers['studyID']};g' {self.outxml}; fi""", shell=True, executable='/bin/bash', stdout=subprocess.PIPE) # replace first name with study ID
        output2 = str(out.stdout)
        out = subprocess.run(f"""if grep -qF "{identifiers['personID']}" {self.outxml}; then echo -e "personal number found" && sed -i.bu 's;{identifiers['personID']};{pnr_string};g' {self.outxml}; fi""", shell=True, executable='/bin/bash', stdout=subprocess.PIPE) # replace first name with study ID
        output3 = str(out.stdout)

        clean_clin_data.deID_track_mismatch(self, identifiers['studyID'], output1, output2, output3)

    # (1) Search for matching names/personnummers in clinical data file and copy matches to the new file (ommits patients not enrolled in TREVAR)
    def deidentify(self):
        # for i in range(len(self.pptinfo.index)): # loop through rows of pptinfo (i.e. loop through study participants)
        for study_id in (self.pptinfo.index): # loop through rows of pptinfo (i.e. loop through study participants)
            identifiers = clean_clin_data.deID_read_ppt_info(self, study_id) # Read participant's identifiers and studyID from the study spreadsheet
            clean_clin_data.deID_replace_identifiers(self, identifiers) # Replaces identifers with studyID in the output XML file

        # self.pptinfo['studyID'] = self.pptinfo.index # convert pandas dataframe index (study IDs) back to column before saving as XLSX
        self.pptinfo.to_excel(self.pptinfo_path, sheet_name='sheet1', index=True) # overwrites old xlsx with this pandas dataframe

    def extract_by_ids(self, ids, namespace, grouplabel):
        perID_str = 'XXXXXX-XXXX'

        # Parse the original XML file
        tree = ET.parse(self.outxml)
        root = tree.getroot()

        for subjID in ids:
            # # Iterate over all <processes> elements
            # for processes in root.findall('riv:processes', namespace):

            #     # Within each <processes>, find all <resident> elements
            #     for resident in processes.findall('riv:resident', namespace):

            #         # Check if the <firstName> of the resident matches the target value
            #         first_name = resident.find('riv:firstName', namespace)
            #         if first_name is not None and first_name.text == subjID:
            #         # perID = resident.find('riv:personId', namespace)
            #         # if perID is not None and perID_str in perID.text:
            #         #     print ('TEST')

            #             # Append the entire <processes> element to the new root and break out of the loop
            #             # Create a new XML tree for storing the extracted elements
            #             new_root = ET.Element('root')  # Create a new root for the output file
            #             new_root.append(processes)
            #             # break  # Stop checking other residents within the same <processes>

            new_root = ET.Element('root')  # Create a new root for the output file

            # Iterate over all <processes> elements
            for processes in root.findall('riv:processes', namespace):
                # Within each <processes>, find all <resident> elements
                for resident in processes.findall('riv:resident', namespace):
                    # Check if the <firstName> of the resident matches the target value
                    first_name = resident.find('riv:firstName', namespace)
                    # print(first_name.text) # TEST
                    if first_name is not None and first_name.text == subjID:
                        # Append the entire <processes> element to the new root and break out of the loop
                        new_root.append(processes)
                        # break  # Stop checking other residents within the same <processes>


                        # Create a new tree and write it to a new XML file
                        new_tree = ET.ElementTree(new_root)
                        new_tree.write(f'/Users/hollandbrown/Desktop/ipsy/{subjID}_{grouplabel}_2023jun-dec.xml', encoding='utf-8', xml_declaration=True)
