import datetime
import time
from bs4 import BeautifulSoup

"""
Simple script to scrape the curse points per project and day from an html download of 
the rewards page. Outputs into a .csv file to load into excel and similar
"""


def get_key(dictionary, index):
    """
    Convenience method to get a key at an index in a dict

    :param dictionary: The dict to operate on
    :param index: The wanted key index
    :return: The key at that index in the dict
    """
    return list(dictionary.keys())[index]


# Load the file and parse it into a soup
points_html = open("points.html")
soup = BeautifulSoup(points_html.read(), "html.parser")

date_to_transaction = {}

# Iterate all transactions and load their affected projects and respective points into a dict
for transaction in soup.findAll("div", {"class": "transactions"}):

    # Parse the epoch timestamp in the html
    localtime = time.strftime('%Y-%m-%d', time.localtime(int(transaction.find("abbr")["data-epoch"])))

    # Iterate all rewards in this transaction
    for reward in transaction.findAll("li"):
        points = float(reward.find("b").text)
        project = reward.find("a").text

        # Get the current sub-dict for this day or an empty one if this is the first reward
        day_data = date_to_transaction.get(localtime, {})
        day_data[project] = points
        date_to_transaction[localtime] = day_data

# Get the most recent transaction as that one is most likely to contain entries
# for every project that will appear in any of the following transactions
mostRecentTransaction = date_to_transaction[get_key(date_to_transaction, 0)]

# The first column is empty, the dates don't need a header
output = ","
project_names = []

# Prepare the first row in our csv with the names for every project
for project in mostRecentTransaction:
    output += project + ","
    project_names.append(project)

output += "\n"

# Extract the oldest and newest dates to iterate
pointer_date = datetime.datetime.strptime(get_key(date_to_transaction, -1), '%Y-%m-%d').date()
target_date = datetime.datetime.strptime(get_key(date_to_transaction, 0), '%Y-%m-%d').date()

timedelta = datetime.timedelta(days=1)

# Iterate from the oldest to the newest date to find any possible days that have been missed
while pointer_date <= target_date:

    date = str(pointer_date)
    output += date + ","

    # Check if there is a transaction for this day
    if date in date_to_transaction:
        # Iterate all projects we know of and add an empty cell
        # for padding if there is no reward for it in this transaction
        for project in project_names:
            if project in date_to_transaction[date]:
                output += str(date_to_transaction[date][project]) + ","
            else:
                output += ","

    output += "\n"
    pointer_date += timedelta

# Write the output file
output_file = open("output.csv", "w")
output_file.write(output)
output_file.close()
