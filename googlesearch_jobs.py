from googlesearch import search
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

def authenticate_with_google_sheets(credentials_file):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
    client = gspread.authorize(creds)
    return client

def get_search_terms_from_sheet(sheet):
    search_terms = sheet.col_values(1)[1:]  # Assuming search terms are in the first column, excluding header
    return search_terms

def search_and_scrape_google(search_term, num_results=5):
    results_data = []
    # Initialize Chrome WebDriver outside the loop
    driver = webdriver.Chrome()
    
    search_results = search(search_term)  # No num_results parameter
    for idx, result in enumerate(search_results):
        if idx >= num_results:
            break
        try:
            driver.get(result)
            
            # Wait for the page to load completely
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[6]/div/div[13]/div/div[2]/div[2]/div/div/div[3]/div/div/div[1]/div/div/span/a/h3')))
            
            # Extract meta title and meta description using BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            title = driver.title.strip()
            
            # Try to extract meta description using different methods
            meta_description = None
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag:
                meta_description = meta_tag.get('content').strip()
            # Add other extraction methods here...
            
            # Extract h3 tag text using full XPath
            h3_element = driver.find_element(By.XPATH, '/html/body/div[6]/div/div[13]/div/div[2]/div[2]/div/div/div[3]/div/div/div[1]/div/div/span/a/h3')
            h3_text = h3_element.text.strip()
            
            results_data.append((title, meta_description, h3_text))
        except Exception as e:
            print(f"Error scraping {result}: {e}")
    # Quit the WebDriver after processing all URLs
    driver.quit()
    return results_data




def update_google_sheet(sheet, data):
    # Find the next available column index
    next_column_index = len(sheet.row_values(1)) + 1
    
    for row_idx, (title, meta_description, h3_texts) in enumerate(data, start=2):  # Start from row index 2
        # Write data into the next available column
        sheet.update_cell(row_idx, next_column_index, title)
        sheet.update_cell(row_idx, next_column_index + 1, meta_description)
        sheet.update_cell(row_idx, next_column_index + 2, ", ".join(h3_texts))  # Combine h3_texts into a string
        time.sleep(1)  # Add a delay of 1 second between each write request



def main(credentials_file, document_id, sheet_name):
    client = authenticate_with_google_sheets(credentials_file)
    sheet = client.open_by_key(document_id).worksheet(sheet_name)
    search_terms = get_search_terms_from_sheet(sheet)  # Pass the 'sheet' object directly
    for search_term in search_terms:
        search_results = search_and_scrape_google(search_term)
        update_google_sheet(sheet, search_results)

if __name__ == "__main__":
    # Provide the necessary credentials and document details
    credentials_file = "credentials_file.json"
    document_id = "10u5o4tZJW71cLXIL5-vsMGxnqrZNNbJ3AhTsfwMtdzs"
    sheet_name = "MTMD"
    
    # Execute the main function
    main(credentials_file, document_id, sheet_name)

