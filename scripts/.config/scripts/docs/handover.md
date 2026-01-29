# Implement `bid ho` Command

This command is for handing over of a project after successful bidding.

The destination folder is in @handover folder pointed to by HO variable.
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

## The candidiates folder for handover

Once the folder is found, it needs to look for candidates folder for
handover and give the list to user to choose from. The candidates folders
are:

1. The folder that is found by the job code itself. This is considered the
   main project folder. In this example, it is "J12795 HOS - P91 FPSO - ENT".
2. Any folder listed under 07-VO subfolder in the main folder.

## Things to prepare in @handover

Once the candidate is chosen:

1. Check in @handover to see the main project folder exists, e.g. "J12795
   HOS - P91 FPSO - ENT", which is always identifiable by job code. If it
   does not, create this folder.
2. If the user's choice is the main folder for handover, create 00-MAIN
   subfolder.
3. If the user's choice is a folder listed under 07-VO subfolder, create the
   subfolder with the same name as the user's choice.
4. In these subfolders, the followng actions are to be performed.

| Action | From @rfqs   | To @handover | Remark                                 |
| :----- | :----------- | :----------- | :------------------------------------- |
| sync   | 00-ITB       | 00-ITB       |                                        |
| sync   | 06-PO        | 01-PO        |                                        |
| sync   | 02-Technical | 02-Technical |                                        |
| sync   | 03-Supplier  | 03-Supplier  |                                        |
| sync   | 04-Datasheet | 04-Datasheet |                                        |
| create |              | 05-Cost      |                                        |
| sync   | 05-Drawing   | 06-Drawing   | Only if 05-Drawing folder is not empty |

> [!NOTE]
> **Only non-empty folders are to be sync**

For syncing machanism, we can consider dirsync or pyrsync2 library. It is
important that the code needs to be compatible with both Windows and Mac
OS.

If there are any updates to the source folder, the command may be run again
to perfom the sync.

Let us come up with a plan to implement this feature. You can ask me
questions.
