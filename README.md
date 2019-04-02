# CI_ReportGen

Assists in generating reports for the MUN FEAS CI Program

This state of the program relies on data in Excel spreadsheets. The indicator data is stored in master lookup sheets,
which you can find/modify in the 'Indicators' folder. The grades for each assessment must be stored in formatted spreadsheets,
named in the following manner: <b>"(course) (assessment type).xlsx"</b>. An example would be "ENGI 1010 Final Exam.xlsx".
The program queries the indicator lookup sheets and determines which assessment sheet to open from the assessment type listed.

Most of the directories are not set up by default due to the gitignore, so run the Create_Directories.py script before using
the program.
