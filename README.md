# TREVAR
### Scripts for cleaning, organizing, and analyzing TREVAR study data from Swedish population registry and InternetPsykiatri psychiatry records

Updated 2024-10-04
Created 2024-07-04

Holland Brown

### Clincal data de-identification, cleaning and organization
- SCRIPT: /trevar_clin_data_clean.py
- reads study IDs, participant names and personal numbers from a spreadsheet
- creates a copy of the clinical data file
- searches for matching names/personnummers in clinical data files and copies matches to the new file (ommits patients not enrolled in TREVAR)
- replaces participant names and personnummers with study IDs in new file (de-identifies)
- takes note of participants in the spreadsheet whose data don't match the clinical data file
- if participant is not found in the clinical data file, marks in spreadsheet whether name, personnummer, or neither were found
- RESULT: a copy of the original clinical data file containing only de-identified data of participants enrolled in the study

### Dependencies
- Python 3.13
- os
- subprocess
- numpy
- pandas
- xml.etree.ElementTree

### Scripts
- use RUN_clean_clin_data.py to set variables and run (other scripts are classes)
