# AckNER

Repository with code for the paper _"This research is funded by..." Named Entity Recognition of financial information in research papers_.

This package allows to extract funding information (including funding organisations's names, contracts and grants)

The file acknow_mod.py contains the following 5 functions

- The first function extracts the page containing acknowledgements/funding section
- The second function extracts the sentences that contain the funding information
- the third function extracts the names of the funding organisations
- the fourth function extracts contract numbers, grant numbers and also abbreviations
- the fifth function writes the result into a csv file
