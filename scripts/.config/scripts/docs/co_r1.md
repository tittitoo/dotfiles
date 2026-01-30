# Implement `bid co` Command

This command is for handing over of costing for a project after successful bidding.

The destination folder is in @costing folder pointed to by CO variable,
updated in bid.py.
The source folder is in @rfqs pointed to by RFQ variable. Inside @rfqs
folder, there are subfolders by year. For example,

- 2026
- 2025
- 2024

We will handle from the recent years till the year 2023 only.

Under the year folder, there are subfolders for projects. The projects
name always start with job code. This job code can be considered unique.
Example folder name is "J12795 HOS - P91 FPSO - ENT".

The source folder name needs to be requested from the user. "J12" is common
so user may also opt to put in the last 3 digits only. The program will
then search for the folder from the recent years till the year 2023.

## The candidiates folder for costing handover

Once the folder is found, it needs to look for candidates folder for
costing handover and give the list to user to choose from. The candidates
folders are:

1. The folder that is found by the job code itself. This is considered the
   main project folder. In this example, it is "J12795 HOS - P91 FPSO - ENT".
2. Any folder listed under 07-VO subfolder in the main folder.

## Things to prepare in @costing

Once the candidate is chosen:

1. Check in @costing to see the main project folder exists, e.g. "J12795
   HOS - P91 FPSO - ENT", which is always identifiable by job code. If it
   does not, create this folder.
2. If the user's choice is the main folder for handover, create 00-MAIN
   subfolder.
3. If the user's choice is a folder listed under 07-VO subfolder, create the
   subfolder with the same name as the user's choice.

User will copy and paste in selected file manually and therefore, we do not
need sync machanism.
Let us come up with a plan to implement this feature. You can ask me
questions.
