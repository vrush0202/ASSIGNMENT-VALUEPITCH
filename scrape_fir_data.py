import csv
import requests
from bs4 import BeautifulSoup

# Define the URL and date range for scraping
base_url = "https://citizen.mahapolice.gov.in/Citizen/MH/PublishedFIRs.aspx"
start_date = "01/01/2023"
end_date = "01/02/2023"

# Create a session to handle cookies
session = requests.Session()

# Get the initial page to extract the __VIEWSTATE value
response = session.get(base_url)
soup = BeautifulSoup(response.text, "html.parser")
viewstate = soup.find("input", {"id": "__VIEWSTATE"})["value"]

# Prepare the request data with the required parameters
data = {
    "__VIEWSTATE": viewstate,
    "ctl00$ContentPlaceHolder1$ddlDistrict": "-1",
    "ctl00$ContentPlaceHolder1$txtDate": start_date,
    "ctl00$ContentPlaceHolder1$txtToDate": end_date,
    "ctl00$ContentPlaceHolder1$ddlPage": "1",
    "ctl00$ContentPlaceHolder1$btnSearch": "Search FIR",
}

# Send a POST request with the date range
response = session.post(base_url, data=data)
soup = BeautifulSoup(response.text, "html.parser")

# Find the total number of pages for pagination
total_pages_element = soup.find("span", {"id": "ContentPlaceHolder1_lbltotalPages"})
if total_pages_element is not None:
    total_pages = int(total_pages_element.text)
else:
    total_pages = 1

# Open a CSV file for writing
csv_file = open("fir_data.csv", "w", newline="")
writer = csv.writer(csv_file)
writer.writerow(["Sr. No.", "State", "District", "Police Station", "Year", "FIR No.", "Registration Date", "Sections"])

# Loop through each page and extract the data
for page in range(1, total_pages + 1):
    data["ctl00$ContentPlaceHolder1$ddlPage"] = str(page)  # Update the page number
    response = session.post(base_url, data=data)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find the table element
    table = soup.find("table", {"id": "ContentPlaceHolder1_GridView1"})
    
    if table is not None:
        # Extract the data from each row
        rows = table.find_all("tr")
        
        if len(rows) > 1:
            for row in rows[1:]:
                cells = row.find_all("td")
                
                # Check if the row is not empty
                if len(cells) > 0:
                    sr_no = cells[0].text.strip()
                    state = cells[1].text.strip()
                    district = cells[2].text.strip()
                    police_station = cells[3].text.strip()
                    year = cells[4].text.strip()
                    fir_no = cells[5].text.strip()
                    registration_date = cells[6].text.strip()
                    sections = cells[7].text.strip()
                    
                    # Check if any column has empty or invalid data
                    if sr_no and state and district and police_station and year and fir_no and registration_date and sections:
                        # Write the data to the CSV file
                        writer.writerow([sr_no, state, district, police_station, year, fir_no, registration_date, sections])

# Close the CSV file
csv_file.close()


