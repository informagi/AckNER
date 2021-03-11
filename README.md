# AckNER

Repository with code for the paper _"This research is funded by..." Named Entity Recognition of financial information in research papers_.

This package allows to extract funding information (including funding organisations's names, contracts and grants) from pdf files.

The file acknow_mod.py contains the following 5 functions

- The first function extracts the page containing acknowledgements/funding section
- The second function extracts the sentences that contain the funding information
- the third function extracts the names of the funding organisations
- the fourth function extracts contract numbers, grant numbers and also abbreviations
- the fifth function writes the result into a csv file

# Docker


In order to run the package on docker you need to

1) build a docker image: docker build -t <image_name> .
2) run the following command on your data: docker run -v <path_to_data_folder>:/data/articles -v <path_to_output_folder>:/data/output an4

The output folder is the folder where you want to store a csv file. Note that both paths should be absolute and the data should only be in pdf format. 

# Results of the study

The repository also contains the results of the comparison of our program's output to the golden standard file where the results are stored against each other and the type of the result and the outcome is showed (tp - true positives, fp - false positives, fn - false negatives).
