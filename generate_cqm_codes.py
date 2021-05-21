import pandas as pd
import csv
import os
import shutil
from time import sleep
import argparse
from pprint import pprint

parser = argparse.ArgumentParser(description="Generate CSV files containing valid codes for use in CQM extractions")
required_args = parser.add_argument_group("required arguments")
required_args.add_argument('--source', help="The file to extract codes from")
parser.add_argument('--clean', help="Purges the output directory before writing new files", action="store_true")
parser.add_argument('-o', help="Location to write the output files", default='./')
args = parser.parse_args()

cqm_section = 'Diagnostic Study'
excel_file = args.source
output_dir = args.o + "Codesets/"
clean_output_dir = args.clean

valid_measures = ["CMS2v10", "CMS69v9", "CMS75v9", "CMS117v9", "CMS136v10", "CMS138v9", "CMS146v9", "CMS147v10", "CMS153v9", "CMS154v9", "CMS155v9"]

try:
    os.stat(output_dir)
except:
    os.mkdir(output_dir)

data = pd.read_excel(excel_file, sheet_name=None, skiprows=[0], engine='openpyxl')
print(list(data.keys()))

def purge_output_dir(clean):
    if (clean) :
        shutil.rmtree(output_dir)
        try:
            os.stat(output_dir)
        except:
            os.mkdir(output_dir)

def parse_file(data):
    for sheet in data:
        df = data[sheet]
        print(f"[INFO] Parsing {sheet} sheet")
        print(f"[INFO] Rows: {df.shape[0]}, Columns: {df.shape[1]}")

        sheet_dir = sheet.replace(" ", "_") + "/"
        file_location = output_dir + sheet_dir

        sheet_data = get_codes(df)
        write_code_csvs(sheet_data, file_location)

def get_codes(data):
    code_dict = {}
    code_types = data['Code System'].unique()
    for i in code_types:
        codes = data.loc[(data['Code System'] == i), ['Code','CMS ID']]
        code_dict[i] = []
        for j in codes.values:
            if j[1] in valid_measures:
                code_dict[i].append(j[0])
        if len(code_dict[i]) <= 0:
            del code_dict[i]
    return code_dict

def write_code_csvs(data, location="./"):
    try:
        os.stat(location)
    except:
        os.mkdir(location)

    for i in data:
        filename = i.replace(" ", "_") + ".csv"
        path = location + filename
        print(f"[INFO] Writing {location}")
        with open(path, mode='w', newline="") as outfile:
            fieldnames = ['code']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for code in data[i]:
                writer.writerow({"code": code})

        

if __name__ == "__main__":
    purge_output_dir(clean_output_dir)
    parse_file(data)