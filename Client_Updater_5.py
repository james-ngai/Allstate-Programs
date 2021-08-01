# Author: James Ngai(Allstate "HALE INSURANCE, INC.")
# Program built solely for the use of Allstate Hale Insurance Inc
#
# Program takes prexisting client data and adds the client's
# Housing Square Footage(Potentially), Present Use, and property detail url

import requests
import csv
import concurrent.futures
from os import path
from bs4 import BeautifulSoup

# Message is to inform user about program operations
print(
    "\nOutput file will be in same folder as input file\nNew file name will be "
    "new_{file_name}.csv"
    ""
)

# Takes the PATH of the csv file
PATH = str(
    input("Insert file path\nEx: C:\\Users\\Allstate\\Downloads\\August2021.csv\n")
)

# Checks if file path exists and waits until user inputs correct one
while not path.exists(PATH):
    print("Error with file path, check it is correct and compare with example")
    PATH = str(
        input("Insert file path\nEx: C:\\Users\\Allstate\\Downloads\\August2021.csv\n")
    )

# Creates new file path for csv file that is being written
last_index = PATH.rfind("\\")
new_PATH = f"{PATH[0 : last_index + 1]}new_{PATH[last_index + 1 :]}"
# Main function that is called to determine the bar that should be set to
# maximize collection of housing square footage data
def square_call(square_bar=1980, all_info=tuple()):
    num_square_ft = square_limit(square_bar, all_info)
    if num_square_ft < 999:
        if square_limit(square_bar + 10, all_info) >= 999:
            return square_bar
        return square_call(square_bar + 10, all_info)
    else:
        if square_limit(square_bar - 10, all_info) < 999:
            return square_bar - 10
        return square_call(square_bar - 10, all_info)


# Counts the number of clients that fit within square_bar to determine bar to set to
def square_limit(square_bar, info):
    with open(PATH, "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        num_square_ft = 0
        info_index = 0
        for line, info in zip(csv_reader, all_info):
            if info[0] == True:
                present_use = info[1].lower()
                if (
                    "condo" not in present_use
                    and "apartment" not in present_use
                    and "mobile home" not in present_use
                ):
                    if int(line[8]) <= square_bar:
                        num_square_ft += 1
    return num_square_ft


# Function that threads use
def add_list(line):
    # Take address and converts to search friendly form
    # Converts spaces " " to "%20"
    address = str(line[2])
    address = address.replace(" ", "%20")
    try:
        # Takes pin_id or parcel number required to access web data and urls
        pin_id = requests.get(
            f"https://gismaps.kingcounty.gov/parcelviewer2/addSearchHandler.ashx?add={address}"
        ).json()["items"][0]["PIN"]
        # Takes present_use data Ex:"Single Family(Res)" to put in csv file
        # Creates url based off of pin_id(Parcel Number)
        # Url is not verified to avoid web visit restriction
        url = f"https://blue.kingcounty.com/Assessor/eRealProperty/Detail.aspx?ParcelNbr={pin_id}"
        source = requests.get(
            f"https://gismaps.kingcounty.gov/parcelviewer2/pvinfoquery.ashx?pin={pin_id}"
        ).json()

        taxpayer_name = source["items"][0]["TAXPAYERNAME"]
        present_use = source["items"][0]["PRESENTUSE"]
        # Parse more accurately
        if len(taxpayer_name) > 0:
            if str(line[1]).lower() not in taxpayer_name.lower():
                taxpayer_1 = taxpayer_name.replace("+", "|")
                taxpayayer_2 = taxpayer_1.replace("&", "|")
                name_list_1 = taxpayayer_2.split("|")
                for name1 in name_list_1:
                    name1 = name1.strip()
                    name_list_2 = name1.split(" ")
                    if (
                        line[1].lower() == name_list_2[0].lower()
                        and line[0].lower() == name_list_2[1].lower()
                    ):
                        taxpayer_lname = ""
                        taxpayer_fname = ""
                        break
                    else:
                        taxpayer_lname = name_list_2[0].title()
                        taxpayer_fname = name_list_2[1].title()
            else:
                taxpayer_lname = ""
                taxpayer_fname = ""
        else:
            taxpayer_lname = ""
            taxpayer_fname = ""
        # Signifies that process was successful to move onto access square footage data
        passthrough = True
    except:
        address = address.lower()
        # Dictionary that is circled through to see if search result can be recovered
        abb_dict = {
            "mt": "mountain",
            "mount": "mt",
            "woodinvl": "woodinville",
            "sunbreak": "sun break",
            "shr": "shore",
            "cntry": "country",
            "clb": "club",
            "lk": "lake",
            "shangrila": "shangri la",
            "shoreclub": "shore club",
        }
        # Means process has failed thus far unless dictionary change finds search result
        passthrough = False
        # Loops through dictionary to see if dictionary result is in address
        for abbreviation, full in abb_dict.items():
            # Sees if results is in address and will fix search result and the computer well tell computer
            if f"%20{abbreviation}%20" in address:
                address = address.replace(abbreviation, full)
                passthrough = True
        # If dictionary element changed, the program will submit another request for data to fix field
        if passthrough:
            try:
                # Takes pin_id or parcel number required to access web data and urls
                pin_id = requests.get(
                    f"https://gismaps.kingcounty.gov/parcelviewer2/addSearchHandler.ashx?add={address}"
                ).json()["items"][0]["PIN"]
                # Takes present_use data Ex:"Single Family(Res)" to put in csv file
                source = requests.get(
                    f"https://gismaps.kingcounty.gov/parcelviewer2/pvinfoquery.ashx?pin={pin_id}"
                ).json()
                taxpayer_name = source["items"][0]["TAXPAYERNAME"]
                present_use = source["items"][0]["PRESENTUSE"]
                if str(line[1]).lower() not in taxpayer_name.lower():
                    taxpayer_1 = taxpayer_name.replace("+", "|")
                    taxpayayer_2 = taxpayer_1.replace("&", "|")
                    name_list_1 = taxpayayer_2.split("|")
                    for name1 in name_list_1:
                        name1 = name1.strip()
                        name_list_2 = name1.split(" ")
                        if (
                            line[1].lower() == name_list_2[0].lower()
                            and line[0].lower() == name_list_2[1].lower()
                        ):
                            taxpayer_lname = ""
                            taxpayer_fname = ""
                            break
                        else:
                            taxpayer_lname = name_list_2[0].title()
                            taxpayer_fname = name_list_2[1].title()
                else:
                    taxpayer_lname = ""
                    taxpayer_fname = ""
                # Creates url based off of pin_id(Parcel Number)
                # Url is not verified to avoid web visit restriction
                url = f"https://blue.kingcounty.com/Assessor/eRealProperty/Detail.aspx?ParcelNbr={pin_id}"
                # Signifies that process was successful to move onto access square footage data
                passthrough = True
            except:
                add_info = (False,)
                return add_info
        else:
            add_info = (False,)
            return add_info
    # Appends previous information scraped
    add_info = (passthrough, taxpayer_fname, taxpayer_lname, present_use, url, pin_id)
    return add_info


def square_footage(all_info, line):
    global square_bar
    global error_message
    if all_info[0] == True:
        # Takes square_ft data from clients
        taxpayer_fname = all_info[1]
        taxpayer_lname = all_info[2]
        present_use = all_info[3]
        url = all_info[4]
        pin_id = all_info[5]
        present_use_lower = all_info[3].lower()
        if (
            "condo" not in present_use_lower
            and "apartment" not in present_use_lower
            and "mobile home" not in present_use_lower
        ):
            square_ft = int(line[8])
            if square_ft <= square_bar:
                try:
                    # Takes request for square footage
                    source = requests.get(
                        f"https://blue.kingcounty.com/Assessor/eRealProperty/Dashboard.aspx?ParcelNbr={pin_id}"
                    ).text
                    # Takes text element using Beautfiul Soup
                    soup = BeautifulSoup(source, "lxml")
                    # Parses through html to find correct source
                    table1 = soup.find("table", id="container")
                    table2 = table1.find("table", id="cphContent_DetailsViewPropTypeR")
                    tr_sqft = table2.find_all("tr")[1]
                    tr_yr = table2.find_all("tr")[0]
                    try:
                        header_sqft = tr_sqft.find_all("td")[0].text.lower()
                        if header_sqft == "total square footage":
                            new_square_ft = tr_sqft.find_all("td")[1].text
                        else:
                            new_square_ft = "Error"
                        header_yr = tr_yr.find_all("td")[0].text.lower()
                        if header_yr == "year built":
                            new_year_built = tr_yr.find_all("td")[1].text
                        else:
                            new_year_built = "Error"
                    except:
                        new_square_ft = "Error"
                        new_year_built = "Error"
                        # Loops through tr tags in table
                        tr = table2.find_all("tr")
                        for value in tr:
                            try:
                                header_sqft = value.find_all("td")[0].text.lower()
                                # Sees if header is correct then will append
                                if header_sqft == "total square footage":
                                    new_square_ft = value.find_all("td")[1].text
                                    break
                            except:
                                pass
                        for value in tr:
                            try:
                                header_yr = value.find_all("td")[0].text.lower()
                                if header_yr == "year built":
                                    new_year_built = value.find_all("td")[1].text
                                    break
                            except:
                                pass
                except:
                    new_square_ft = "Error"
                    new_year_built = "Error"
            else:
                # Appends dashes to maintain csv structure
                new_square_ft = ""
                new_year_built = ""
        else:
            # Appends dashes to maintain csv structure
            new_square_ft = ""
            new_year_built = ""
        line.extend(
            (
                taxpayer_fname,
                taxpayer_lname,
                new_square_ft,
                new_year_built,
                present_use,
                url,
            )
        )
        return line
    else:
        line.extend(("", "", "", "", "", error_message))
        return line


with open(PATH, "r") as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Maps function ensure the threads called first are executed first
        all_info = [line for line in executor.map(add_list, csv_reader)]
tuple(all_info)

# Calls function to get bar to set to
square_bar = square_call(square_bar=1980, all_info=all_info)

# Reminder to ensure program does not stop in execution
print("Reminder: Do not open the csv file that is being read or written!")

# The message that is sent when an error occurs
error_message = "Error — Refer to https://blue.kingcounty.com/assessor/erealproperty/ErrorDefault.htm?aspxerrorpath=/Assessor/eRealProperty/Detail.aspx"

with open(PATH, "r") as csv_file:
    csv_reader = csv.reader(csv_file)
    first_line = next(csv_reader)
    with open(new_PATH, "w") as new_file:
        csv_writer = csv.writer(new_file, delimiter=",", lineterminator="\n")
        # Adds additional elements to top row of csv data
        first_line.extend(
            (
                "Mod-Taxpayer First Name",
                "Mod-Taxpayer Last Name",
                "Mod-Real Square Footage",
                "Mod-Year Built",
                "Mod-Present Use",
                "Mod-URL",
            )
        )
        csv_writer.writerow(first_line)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Maps function ensure the threads called first are executed first
            for line in executor.map(square_footage, all_info, csv_reader):
                csv_writer.writerow(line)
print("Finished!")