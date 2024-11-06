import requests
from bs4 import BeautifulSoup
import numpy as np 
import pandas as pd
import pymysql
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Code to scrape the website
data = []
for i in range(9):
    url = "https://researchops.web.illinois.edu/?page=" + str(i)
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')  
        table_rows = soup.find_all('tr') 

        for row in table_rows:
            columns = row.find_all('td')
            row_data = [column.text.strip() for column in columns]
            if row_data:  
                data.append(row_data)

df = pd.DataFrame(data, columns=["Description", "Research Area", "Timing", "Deadline"])

# Function to clean and format the 'Deadline' column
def clean_deadline(deadline_str):
    try:
        # Remove non-date text (e.g., "Anticipated") and extract the date part
        cleaned = deadline_str.split()[-1]
        # Convert the date to the format YYYY-MM-DD
        return datetime.strptime(cleaned, "%m/%d/%y").strftime("%Y-%m-%d")
    except Exception:
        # If parsing fails, return None or a default date
        return None

# Apply the function to the 'Deadline' column
df['Deadline'] = df['Deadline'].apply(clean_deadline)

# Database connection setup
timeout = 10
connection = pymysql.connect(
  charset="utf8mb4",
  connect_timeout=timeout,
  cursorclass=pymysql.cursors.DictCursor,
  db="defaultdb",
  host=os.getenv("db_host"),
  password=os.getenv("db_password"),
  read_timeout=timeout,
  port=int(os.getenv("db_port")),
  user=os.getenv("db_user"),
  write_timeout=timeout,
)

try:
  cursor = connection.cursor()
  #cursor.execute("DROP TABLE IF EXISTS ResearchOpp")
  
  # Create the table with 'ID' as the auto-incrementing primary key
  cursor.execute("""
    CREATE TABLE ResearchOpp (
      ID INT AUTO_INCREMENT PRIMARY KEY,
      Description VARCHAR(100),
      Research_area VARCHAR(300),
      Timing VARCHAR(100),
      Deadline DATE
    )
  """)
  
  # Insert data into the table
  for i in df.index:
    description = df["Description"][i][:100]  # Ensure the description doesn't exceed 100 characters
    cursor.execute("""INSERT INTO ResearchOpp (Description, Research_area, Timing, Deadline)
                      VALUES (%s, %s, %s, %s)""", 
                   (description, df["Research Area"][i], df["Timing"][i], df["Deadline"][i]))
  
  # Fetch and print data from the table
  cursor.execute("SELECT * FROM ResearchOpp")
  print(cursor.fetchall())
  
finally:
  connection.close()
