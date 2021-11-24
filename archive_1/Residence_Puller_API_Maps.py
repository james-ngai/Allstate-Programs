import requests
import csv
import concurrent.futures
import pandas as pd

csv_name = str(input("Type in name of csv file\n"))
pd_csv = pd.read_csv(f"C:/Users/jamie/Downloads/{csv_name}.csv")

address_list = pd_csv["Address"].tolist()

row_val = 0


def add_list(address):
    global row_val
    with open(f"C:/Users/jamie/Downloads/{csv_name}.csv", "r") as csv_file:
        csv_reader_1 = csv.reader(csv_file)
        next(csv_reader_1)
        for _ in range(row_val):
            next(csv_reader_1)
        line = next(csv_reader_1)
        row_val += 1
        proper = True
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
            line.append(residence)
            return line
        else:
            residence = "Not Avaliable(DNE)"
            line.append(residence)
            return line


with open(f"C:/Users/jamie/Downloads/{csv_name}.csv", "r") as csv_file:
    csv_reader = csv.reader(csv_file)
    first_line = next(csv_reader)
    with open(
        f"C:/Users/jamie/Downloads/updated_Residency_{csv_name}.csv", "w"
    ) as new_file:
        csv_writer = csv.writer(new_file, delimiter=",", lineterminator="\n")
        first_line.append("Present Use")
        csv_writer.writerow(first_line)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for result in executor.map(add_list, address_list):
                csv_writer.writerow(result)