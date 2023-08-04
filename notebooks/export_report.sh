rm -rd report.md
rm -rf report_files
jupyter nbconvert --to markdown --no-input PRODUCE_report.ipynb --output report.md 