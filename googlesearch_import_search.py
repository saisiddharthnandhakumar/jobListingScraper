from googlesearch import search
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time

def authenticate_with_google_sheets(credentials_file):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
    client = gspread.authorize(creds)
    return client

def get_search_terms_from_sheet(sheet):
    search_terms = sheet.col_values(1)[1:]  # Assuming search terms are in the first column, excluding header
    return search_terms

def search_and_scrape_google(search_term, num_results=3):
    results_data = []
    for result in search(search_term, num_results=num_results):
        try:
            driver.get(result)
            time.sleep(2)  # Wait for the page to load
            
            # Extract meta title and meta description
            title = driver.title.strip()
            meta_tag = driver.find_element_by_css_selector("meta[name='description']")
            meta_description = meta_tag.get_attribute('content').strip() if meta_tag else None
            results_data.append((title, meta_description))
        except Exception as e:
            print(f"Error scraping {result}: {e}")
    return results_data

def update_google_sheet(sheet, data):
    # Find the next available column index
    next_column_index = len(sheet.row_values(1)) + 1
    
    for row_idx, (title, meta_description) in enumerate(data, start=2):
        # Write data into the next available column
        sheet.update_cell(row_idx, next_column_index, title)
        sheet.update_cell(row_idx, next_column_index + 1, meta_description)
        time.sleep(1)  # Add a delay of 1 second between each write request

def main(credentials_file, document_id, sheet_name):
    client = authenticate_with_google_sheets(credentials_file)
    sheet = client.open_by_key(document_id).worksheet(sheet_name)
    search_terms = get_search_terms_from_sheet(sheet)  # Pass the 'sheet' object directly
    for search_term in search_terms:
        search_results = search_and_scrape_google(search_term)
        update_google_sheet(sheet, search_results)

if __name__ == "__main__":
    chromedriver_path = 'C:/Users/sid/OneDrive/Desktop/Meta Des Project/chromedriver-win64/chromedriver.exe'

    # Initialize Chrome WebDriver with the chromedriver executable path
    driver = webdriver.Chrome(executable_path=chromedriver_path)

    # Provide the necessary credentials and document details
    credentials_file = "credentials_file.json"
    document_id = "10u5o4tZJW71cLXIL5-vsMGxnqrZNNbJ3AhTsfwMtdzs"
    sheet_name = "MTMD"
    
    # Execute the main function
    main(credentials_file, document_id, sheet_name)
    
    # Quit the WebDriver after execution
    driver.quit()



