import requests
import csv
import concurrent.futures
import pandas as pd

csv_name = str(input("Type in name of csv file\n"))
csv_data = pd.read_csv(csv_name)
address_column = csv_data[2].tolist()
# Currently does not have return statement
def add_list(address):
    proper = True
    # Needs to be updated to work with more query searches
    address = address.replace(" ", "%20")
    try:
        source1 = requests.get(
            f"https://gismaps.kingcounty.gov/parcelviewer2/addSearchHandler.ashx?add={address}"
        )
        pin_id = source1.json()["items"][0]["PIN"]

        source2 = requests.get(
            f"https://gismaps.kingcounty.gov/parcelviewer2/pvinfoquery.ashx?pin={pin_id}"
        )
    except:
        proper = False
    if proper:
        residence = str(source2.json()["items"][0]["PRESENTUSE"])
        if residence == "":
            residence = "Not Avaliable(Empty)"
        print(line)
        line.append(residence)
        return line
    else:
        print(line)
        line.append("Not Avaliable(DNE)")
        return line


with open(f"C:/Users/jamie/Downloads/{csv_name}.csv", "r") as csv_file:
    csv_reader = csv.reader(csv_file)
    first_line = next(csv_reader)
    with open(f"C:/Users/jamie/Downloads/updated_{csv_name}.csv", "w") as new_file:
        csv_writer = csv.writer(new_file, delimiter=",", lineterminator="\n")
        first_line.append("Present Use")
        csv_writer.writerow(first_line)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            csv_writer.writerow(executor.map(add_list, address_column))

# Check if residential status is mixed with

# Implement multiprocessing for when adding to list
