# `bid vo`

For `bid vo`, we want to have the option to create new commercial proposal,
similare to the code fragment in `init` function below.

```python
# Create new commercial Proposal
if click.confirm("Do you want to create a new Commercial Proposal?"):
    version = click.prompt(
        "Version No, default:", default="B0", show_default=True
    )
    version = str(version).upper()
    template_folder = (
        Path(RFQ).expanduser().parent.absolute().resolve() / "@tools/resources"
    )
    template = "Template.xlsx"
    commercial_folder = new_path / "01-Commercial"
    commercial_file = folder_name + " " + str(version) + ".xlsx"
    jobcode = folder_name.split()[0]
    excelx.create_excel_from_template(
        template_folder,
        template,
        commercial_folder,
        commercial_file,
        jobcode,
        version,
    )
```

The differences to take care of are:

1. version to default to "R0"
2. version number in commercial_file to be prefixed with "NN-". E.g.
   "V1-R0".
3. jobcode to be prefix with "NN", where NN refers to VO number. So the
   string written to would be "J12789 V1"

Let us make a plan to implement this feature.
