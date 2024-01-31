import datetime
import os
import re
import csv
import argparse
import sys
import pymongo

my_client = pymongo.MongoClient("mongodb://localhost:27017/")

my_database = my_client["ProjectTwo"]

my_collection_one = my_database["CollectionOne"]
my_collection_two = my_database["CollectionTwo"]

user_running_the_script = os.getlogin()
submitted_date = datetime.date.today().strftime('%Y-%m-%d')

parser = argparse.ArgumentParser()
parser.add_argument("--files", help="Baselight/Flames text files to process", nargs='+', type=str, required=True)
parser.add_argument("--xytech", help="Xytech file input", type=str, required=True)
parser.add_argument("-v", "--verbose", help="Console output on/off", action="store_true")
parser.add_argument("-o", "--output", help="Output to CSV or Database", choices=["csv", "database"], default="csv")
args = parser.parse_args()

if args.files is None:
    print("No BL/Flames files selected")
    sys.exit(2)

# Read Xytech data
with open(args.xytech, 'r') as xytech_file:
    xytech_data = xytech_file.read()
producer = re.search(r'Producer:\s+(.*)', xytech_data).group(1)
operator = re.search(r'Operator:\s+(.*)', xytech_data).group(1)
job = re.search(r'Job:\s+(.*)', xytech_data).group(1)
locations = re.findall(r'Location:\s+(.*?)\n\n', xytech_data, re.DOTALL)[0].strip().split('\n')
notes = re.search(r'Notes:\s+(.*)', xytech_data).group(1)

two_d_list = []

# Iterating over the list of files
for file_path in args.files:
    with open(file_path, 'r') as work_file:
        file_name = os.path.basename(file_path)
        file_name_without_txt = file_name[:-4]
        machine, user, date = file_name_without_txt.split("_")
        year = date[:4]
        month = date[4:6]
        day = date[6:]

        date = f"{year}-{month}-{day}"

        for line in work_file:
            line = line.strip().split()

            fixed_line = []

            if machine == "Baselight":
                path = line[0]
                nums = line[1:]
            elif machine == "Flame":
                path = line[1]
                nums = line[2:]

            # Removing <null> and <err>
            for num in nums:
                if num not in ('<null>', '<err>'):
                    fixed_line.append(int(num))

            # Putting the numbers in ranges if needed
            ranges = []
            start = end = fixed_line[0]
            for num in fixed_line[1:]:
                if num == end + 1:
                    end = num
                else:
                    if start == end:
                        ranges.append(str(start))
                    else:
                        ranges.append(str(start) + "-" + str(end))
                    start = end = num
            if start == end:
                ranges.append(str(start))
            else:
                ranges.append(str(start) + "-" + str(end))

            # Find the matching location in Xytech and Baselight/Flames
            for location in locations:
                split_location = location.split("/")
                split_path = path.split("/")
                if split_location[-2:] == split_path[-2:]:
                    path = location
                    break

            two_d_list.append([path] + ranges)

    # Exporting to database if requested
    if args.output == "database":
        document_one = {
            "User that ran the script": user_running_the_script,
            "Machine": machine,
            "Name of user on file": user,
            "Date of file": date,
            "Submitted date": submitted_date,
        }
        my_collection_one.insert_one(document_one)

        if args.verbose:
            print("Inserting document into CollectionOne:")
            print(document_one)

        document_two = {
            "Name of user on file": user,
            "Date of file": date,
            "Location/Frames to fix": [f"{line[0]},{elem}" for line in two_d_list for elem in line[1:]]
        }
        my_collection_two.insert_one(document_two)
        two_d_list = []

        if args.verbose:
            print("Inserting document into CollectionTwo:")
            print(document_two)

if args.output == "csv":
    data = [
        ['Producer', 'Operator', 'Job', 'Notes'],
        [producer, operator, job, notes],
        [],
        ['Show location', 'Frames to fix']
    ]

    for line in two_d_list:
        for element in line[1:]:
            data.append([line[0], element])

    with open('csv_output.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(data)

    # Print verbose output if requested
    if args.verbose:
        for row in data:
            print(row)
