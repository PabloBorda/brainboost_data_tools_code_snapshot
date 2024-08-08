

Tech Reporter
=============

Given a user name it clones github repositories that belong to that user and it generates a report of all technologies used. 
(External library imports), in this way we can compare the real user experience to a given job spec. 



sudo python3 tech_report.py PabloBorda --compress=0 --amount-of-chunks=10



Source Code Scanner
==================

Description
The command:



sudo -E python3 list_source_code_directories.py --start-path /media/golden/Expansion1/ --output-path ./list_of_directories_that_have_source_code.txt
What it does:


sudo -E: Runs the command with elevated privileges, preserving the user's environment variables. This is necessary if the script needs access to directories that require root permissions.
python3: Specifies that the script should be run using Python 3.
list_source_code_directories.py: This is the script being executed. It traverses the directory structure starting from a given path, identifying directories containing source code files.
Arguments:

--start-path /media/golden/Expansion1/: Specifies the starting directory for the scan. The script will begin looking for directories containing source code files from this path and continue through all subdirectories.
--output-path ./list_of_directories_that_have_source_code.txt: Specifies the file where the paths of directories containing source code files will be saved. Each time a directory with relevant files is found, its path is appended to this output file.
Script Behavior:

Scanning: The script recursively scans all directories starting from the specified --start-path.
Detection: It checks each file in the directories for specific extensions associated with source code (e.g., .py, .js, .cpp).
Logging: If a directory contains at least one file with a recognized source code extension, the directory path is printed and appended to the specified --output-path file.
Output: The output file (list_of_directories_that_have_source_code.txt) contains a list of directories, each on a new line, where source code files were found. This file is continuously updated during the scan.
Use Case
This command is useful for quickly identifying directories that contain source code files within a large file system or backup drive. It can help developers, system administrators, or data analysts locate and catalog source code for analysis, migration, or backup purposes.





Context Generator
=================

Correct Command to Run the Script
To use the default output folder:

python3 generate_context.py \
  --root_dir /home/golden/Desktop/brainboost_data/data_tools/brainboost_data_tools_code_snapshot/source_code_for_analysis/SmartBandS \
  --output_file ./smartbands.context \
  --additional-avoid-folders env,__pycache__ \
  --compress 1 \
  --amount-of-chunks 10


To specify a custom output folder:

python3 generate_context.py \
  --root_dir /home/golden/Desktop/brainboost_data/data_tools/brainboost_data_tools_code_snapshot/source_code_for_analysis/SmartBandS \
  --output_file ./smartbands.context \
  --output_folder /path/to/custom/output \
  --additional-avoid-folders env,__pycache__ \
  --compress 1 \
  --amount-of-chunks 10
