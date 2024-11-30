import pandas as pd

form_details = pd.read_csv("GDG_recruitment.csv")
for i,f in enumerate(form_details.columns.tolist()):
    print(i,": ", f)
    print()
dept_pref = [
    "Department Preference - 1",
    "Department Preference - 2",
    "Department Preference - 2.1",
    "Department Preference - 2.2",
    "Department Preference - 2.3",
    "Department Preference - 2.4",
    "Department Preference - 2.5",
    "Department Preference - 2.6",
    "Department Preference - 2.7",
    "Department Preference - 2.8",
    "Department Preference - 2.9",
    "Department Preference - 2.10",
    "Department Preference - 2.11",
]

depts = form_details[dept_pref[0]].unique() # departments
questions_range = {
    "Data Science": [80,93]
}
locs = form_details[dept_pref[0]] == 'Data Science'
first_pref = locs
for pref in dept_pref:
    if pref != "Department Preference - 1":
        pass
    pref_det = (form_details[pref] == 'Data Science')
    locs = pref_det | locs

DS_dept = form_details.loc[locs][form_details.columns[1:8].tolist() + form_details.columns[80:93].tolist() + form_details.columns[180:182].tolist()] # form_details.columns[] + 
DS_questions = DS_dept.columns
DS_dept.fillna("NA", inplace=True)
DS_dept['First Pref'] = first_pref

for question in DS_questions:
    if (DS_dept[question]=="NA").all():
        DS_dept.drop(question,axis=1,inplace=True)

column_order = ["Name, "]
print(DS_dept)
DS_dept["Github profile"].to_csv("github_pref.csv")