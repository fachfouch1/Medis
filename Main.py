from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from flask import  request,Response,jsonify
from datetime import datetime
import time
import traceback
import os
from bs4 import BeautifulSoup, Tag
from Models import Molecule
from Models import Pubmed
from Models import Pubchem
from Models import User
from Models import db
from Models import app
import requests
import random
import re
import spacy
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer,Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from sqlalchemy.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from config import *
from flask_mail import Mail, Message
from sqlalchemy.exc import SQLAlchemyError
from reportlab.lib.enums import TA_CENTER  # Import for text alignment
from selenium.common.exceptions import TimeoutException
from selenium_stealth import stealth
from selenium.common.exceptions import NoSuchElementException
import bcrypt
from flask_bcrypt import Bcrypt



bcrypt = Bcrypt(app)


#from flask import Flask
#from flask_cors import CORS

import sys
print("Python interpreter:", sys.executable)
print("Python version:", sys.version)






chrome_options = Options()
chrome_options.add_argument("--headless")


#app.config.from_object(flask_app)
app.config['MAIL_DEBUG'] = True
app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'ahmedfachfouch99@outlook.com'
app.config['MAIL_PASSWORD'] = '19982411998241Ahmed*Hassen'
app.config['MAIL_DEFAULT_SENDER'] = 'ahmedfachfouch99@outlook.com'

mail = Mail(app)

#Function for Pubchem website
def get_page(keyword):

    
# Set up the Chrome driver
    #driver=webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

# Navigate to the search page
    driver.get('https://pubchem.ncbi.nlm.nih.gov/')

# Enter the search keyword and click the search button
    search_box = driver.find_element(By.XPATH, "//div[@class='flex-grow-1 p-xsm-left p-xsm-top p-xsm-bottom b-right b-light']/input")
    search_box.send_keys(keyword)
    search_box.send_keys(Keys.RETURN)

# Wait for the search results to load
    #result_loaded = EC.presence_of_element_located((By.XPATH, '//div[@id="featured-results"]//div[@class="f-medium p-sm-top p-sm-bottom f-1125"]/a'))
    #WebDriverWait(driver, 8).until(result_loaded)
    time.sleep(6)

# Click on the best matching result
    try:
        best_match = driver.find_element(By.XPATH, "//div[@id='featured-results']//div[@class='f-medium p-sm-top p-sm-bottom f-1125']/a")
        best_match.click()
    except:
        try:
            first_result = driver.find_element(By.XPATH, '//*[@id="collection-results-container"]/div/div/div[2]/ul/li[1]/div/div/div[1]/div[2]/div[1]/a')  
            first_result.click()
            time.sleep(6)
        except:
            driver.quit()
            return "No results found."
        
# Get the height of the page
    height = driver.execute_script("return document.body.scrollHeight")

# Set the increment and delay
    increment = 500
    delay = 0.5
    time.sleep(4)

# Scroll down the page in increments
    for i in range(0, height, increment):
        driver.execute_script(f"window.scrollTo(0, {i});")
        time.sleep(delay)
    
    
# Find the name of the compound
    try:
        compound_name = driver.find_element(By.TAG_NAME, 'h1')
        compoundName = compound_name.text.strip()
    except:
        compoundName = "Compound name not found"

 # Find the Pubchem CID name of the compound
    try:
        
        PubChem_CID = driver.find_element(By.CSS_SELECTOR, '#Title-and-Summary > div > div > div > div:nth-child(1) > div.text-left.sm\:table-cell.sm\:align-middle.sm\:p-2.pb-1.pl-2')                                                   
        PubChem_CID = PubChem_CID.text.strip()
    except:
        PubChem_CID = "PubChem CID not found"

# Find the Molecular formula
    try:
        
        Molecular_form = driver.find_element(By.CSS_SELECTOR, "#Title-and-Summary > div > div > div > div:nth-child(4) > div.text-left.sm\:table-cell.sm\:align-middle.sm\:p-2.sm\:border-t.sm\:border-gray-300.dark\:sm\:border-gray-300\/20.pb-1.pl-2")
                                                    #          #main-content > div.main-width > div > div > div.summary.p-md-top.p-md-bottom > div.border.b-active.b-thick.b-radius.p-sm > table > tbody > tr:nth-child(3) > td                                       
        Molecular_form = Molecular_form.text.strip()
        Molecular_form_list = Molecular_form.split('\n')
        Molecular_form = ', '.join(Molecular_form_list)
    except:
        Molecular_form  = "Molecular formula not found"

# Find the Molecular weight
    try:
        
        Molecular_weight = driver.find_element(By.CSS_SELECTOR, "#Title-and-Summary > div > div > div > div:nth-child(6) > div.text-left.sm\:table-cell.sm\:align-middle.sm\:p-2.sm\:border-t.sm\:border-gray-300.dark\:sm\:border-gray-300\/20.pb-1.pl-2 > div > div.break-words.space-y-1")
        Molecular_weight = Molecular_weight.text.strip()
        
    except:
        Molecular_weight  = "Molecular weight not found"        

# Find CAS registration

    try:
        CAS_reg = driver.find_element(By.CSS_SELECTOR,'#CAS > div.px-1.py-3.space-y-2 > div.break-words.space-y-1')
        CAS_reg = CAS_reg.text.strip()
    except:
        CAS_reg = "CAS registration not found"

# Find ATC code
    try:
       
        ATC_Code_ref = driver.find_element(By.XPATH, '//*[@id="ATC-Code"]//button[contains(span, "WHO Anatomical Therapeutic Chemical (ATC) Classification")]')  
        ATC_Code_ref = ATC_Code_ref.text.strip()
    except:
        ATC_Code_ref = "ATC code reference not found"
    print(ATC_Code_ref)

    if ATC_Code_ref == "WHO Anatomical Therapeutic Chemical (ATC) Classification":
        try:
            ATC_Code = driver.find_element(By.XPATH,'//*[@id="ATC-Code"]//button[contains(span, "WHO Anatomical Therapeutic Chemical (ATC) Classification")]//preceding::div[1]')                                         
            ATC_Code = ATC_Code.text.strip()
            ATC_Code_list = ATC_Code.split('\n')
            ATC_Code = ' / '.join(ATC_Code_list)
        except:
            ATC_Code = "ATC Code not found"     
    else:
        try:
            ATC_Code = driver.find_element(By.CSS_SELECTOR,'#ATC-Code > div.section-content > div:nth-child(1)')                                         
            ATC_Code = ATC_Code.text.strip()
            ATC_Code_list = ATC_Code.split('\n')
            ATC_Code = ' / '.join(ATC_Code_list)
        except:

            ATC_Code = "ATC Code not found"
# Find IUPAC Name               
    try:
        iupac_name = driver.find_element(By.CSS_SELECTOR,'#IUPAC-Name > div.px-1.py-3.space-y-2 > div.break-words.space-y-1')
        iupac_name = iupac_name.text.strip()
    except:
        iupac_name = "IUPAC name not found" 
    
# Find Solubility 
    try:
       
        solubility_ref = driver.find_element(By.XPATH, '//*[@id="Solubility"]//button[contains(span, "Human Metabolome Database (HMDB)")]')  
        solubility_ref = solubility_ref.text.strip()
    except:
        solubility_ref = "Solubility reference not found"


    print(solubility_ref)
    if solubility_ref == "Human Metabolome Database (HMDB)":               
        try:
            solubility = driver.find_element(By.XPATH,'//*[@id="Solubility"]//button[contains(span, "Human Metabolome Database (HMDB)")]//preceding::div[1]')
            solubility = solubility.text.strip()
        except:
            solubility = "Solubility not found"
            
    else:
       try: 
        solubility = driver.find_element(By.CSS_SELECTOR,'#Solubility > div.section-content > div:nth-child(1) > p')
        solubility = solubility.text.strip()
       except:
        solubility = "Solubility not found"    

# Find Physical description

    try:
       
        Physical_desc_ref = driver.find_element(By.XPATH, '//*[@id="Physical-Description"]//button[contains(span, "Human Metabolome Database (HMDB)")]')  
        Physical_desc_ref = Physical_desc_ref.text.strip()
    except:
        Physical_desc_ref = "Physical description reference not found"

    print(Physical_desc_ref)    
    if solubility_ref == "Human Metabolome Database (HMDB)":
        try: 
            Physical_desc = driver.find_element(By.XPATH,'//*[@id="Physical-Description"]//button[contains(span, "Human Metabolome Database (HMDB)")]//preceding::div[1]')
            Physical_desc = Physical_desc.text.strip()
            
        except:
            Physical_desc = "Physical description not found1"
    else:
        try:
            Physical_desc = driver.find_element(By.CSS_SELECTOR,'#Physical-Description > div.section-content > div:nth-child(1)')
            Physical_desc = Physical_desc.text.strip()
            
        except:
             Physical_desc = "Physical description not found"  

# Find Melting point

    try:
       
        Melting_point_ref = driver.find_element(By.XPATH, '//*[@id="Melting-Point"]//button[contains(span, "Human Metabolome Database (HMDB)")]')  
        Melting_point_ref = Melting_point_ref.text.strip()
    except:
        Melting_point_ref = "Melting Point reference not found"

    print(Melting_point_ref)

    try:
       
        Melting_point_ref2 = driver.find_element(By.XPATH, '//*[@id="Melting-Point"]//button[contains(span, "DrugBank")]')  
        Melting_point_ref2 = Melting_point_ref2.text.strip()
    except:
        Melting_point_ref2 = "Melting Point reference 2 not found"

    print(Melting_point_ref2)    

    if Melting_point_ref == "Human Metabolome Database (HMDB)":
        try: 
            Melting_point = driver.find_element(By.XPATH,'//*[@id="Melting-Point"]//button[contains(span, "Human Metabolome Database (HMDB)")]//preceding::div[1]')
            Melting_point = Melting_point.text.strip()
        except:
            Melting_point = "Melting point not found1"
    elif Melting_point_ref2 == "DrugBank":
        try: 
            Melting_point = driver.find_element(By.XPATH,'//*[@id="Melting-Point"]//button[contains(span, "DrugBank")]//preceding::div[3]')
            Melting_point = Melting_point.text.strip()
        except:
            Melting_point = "Melting point not found"
    else:
        try:
            Melting_point = driver.find_element(By.CSS_SELECTOR,'#Melting-Point > div.section-content > div:nth-child(1)')
            Melting_point = Melting_point.text.strip()
        except:
             Melting_point = "Melting Point not found"   

# Find Decomposition               
    try:
        decomposition = driver.find_element(By.CSS_SELECTOR,'#Decomposition > div.section-content > div.section-content-item > p')
        decomposition = decomposition.text.strip()
    except:
        decomposition = "Decomposition not found" 

# Find Biological half-life               
    try:
        half_life = driver.find_element(By.CSS_SELECTOR,'#Biological-Half-Life > div.px-1.py-3.space-y-2 > div:nth-child(1) > div')
        half_life = half_life.text.strip()
    except:
        half_life = "Biological Half-life not found" 

# Find Reactivity profile               
    try:
        reactivity = driver.find_element(By.CSS_SELECTOR,'#Reactivity-Profile > div.section-content > div.section-content-item > p')
        reactivity = reactivity.text.strip()
    except:
        reactivity = "Reactivity not found"                  


 # 2D Chemical structure
    try:
        image = driver.find_element(By.XPATH, '//*[@id="Title-and-Summary"]/div/div/div/div[2]/div[2]/div/div/a/img')
        image_url = image.get_attribute('src')

    # Check if the image_url is not None before proceeding
        if image_url is not None:
        # Download the image
            image_response = requests.get(image_url, stream=True)
            if image_response.status_code == 200:
                with open(f"Image Molecule/{keyword}_image.png", 'wb') as image_file:
                    for chunk in image_response.iter_content(1024):
                        image_file.write(chunk)
                print("Image downloaded successfully")
            else:
                print("Failed to download image")
        else:
        # Handle the case where image_url is None
            print("Image URL is None, cannot download the image")

    except Exception as e:
        print('Error encountered:', e)
        image_url = None  # Set to None if image not found or an exception occurred          

# Close the driver and return the result
    driver.quit()

    return compoundName,PubChem_CID,Molecular_form,Molecular_weight,CAS_reg,ATC_Code,iupac_name,solubility,Physical_desc,Melting_point,decomposition,half_life,reactivity,image_url



# Testing
#result = get_page("paracetamol")
#print(result)

# Scraping EMC website

#def get_EMC(keyword):
    
    # Set up the Chrome driver
    driver=webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

# Navigate to the search page
    driver.get('https://www.medicines.org.uk/emc')

# Enter the search keyword and click the search button
    search_box = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="searchField"]')))
    search_box.send_keys(keyword)
    search_box.send_keys(Keys.RETURN)


# Click on the first result
    try:
        
        first_result = driver.find_element(By.XPATH, '//*[@id="search-container"]/div/div[2]/main/div[3]/div[1]/ul/li[1]/a') 
        first_result.click()
        time.sleep(4)
    except:
        driver.quit()
        print("Not found")

    time.sleep(10)

# Get the height of the page
    height = driver.execute_script("return document.body.scrollHeight")
# Set the increment and delay
    increment = 500
    delay = 0.5
    time.sleep(3)
# Scroll down the page in increments
    for i in range(0, height, increment):
        driver.execute_script(f"window.scrollTo(0, {i});")
        time.sleep(delay)
        
#click on the print info 
    print_smpc = driver.find_element(By.CSS_SELECTOR,'#product-details-content > div.smpc-header-container > div.print > a')
    print_smpc.click()

# Get the height of the page
    height1 = driver.execute_script("return document.body.scrollHeight")
# Set the increment and delay
    increment = 500
    delay = 0.5
    time.sleep(3)
# Scroll down the page in increments
    for i in range(0, height1, increment):
        driver.execute_script(f"window.scrollTo(0, {i});")
        time.sleep(delay)
    
# Find the name of the compound
    try:
        medicine_name = driver.find_element(By.CSS_SELECTOR, '#search-wrap > div > div > div > div > div > div.guideSeperator > div.spcWrapper > div:nth-child(3) > p')
        medicine_name = medicine_name.text.strip()
    except:
        medicine_name = "medicine name not found"

    return medicine_name

#CORS(app)


# Functions for Pubmed website


def get_Benefits_Risks(keyword,max_results):
    # Set up the Chrome driver
    service = Service(ChromeDriverManager().install())
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument('--headless')
    found_link = False

    driver = webdriver.Chrome(service=service,options=chrome_options)
     
# Navigate to the search page
    driver.get('https://pubmed.ncbi.nlm.nih.gov/')

    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
# Enter the search keyword and click the search button

 # Construct the search query by adding predetermined terms
    search_query = f'benefits and risks conclusion of {keyword} free full text[sb]'

    driver.get('https://pubmed.ncbi.nlm.nih.gov/?term=' + search_query)

    
    # Wait for the search results to be loaded
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#search-results")))

    full_text_links = []


    for i in range(1, max_results + 2):
        try:
             # Wait for the search results to be loaded
            
            # Construct the CSS selector for the specific search result
            result_selector = f'#search-results > section > div.search-results-chunks > div > article:nth-child({i}) a'
            search_result = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, result_selector)))
            result_url = search_result.get_attribute('href')

            # Open the result URL in a new tab
            driver.execute_script(f"window.open('{result_url}');")
            driver.switch_to.window(driver.window_handles[1])


            # (Logic to navigate to each article's page)
            try:
            # Extract the full-text link
                full_text_link_selector = '#full-view-identifiers > li:nth-child(2) > span > a'

                full_text_link = driver.find_element(By.CSS_SELECTOR, full_text_link_selector).get_attribute('href')
                full_text_links.append(full_text_link)
                found_link = True
            except Exception as e:
                
                print(f"Full text link not found for article {i}: {e}")
                
            finally:   
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        except NoSuchElementException:
            # Handle the case where the element is not found
            print(f"Full text link not found for article {i}")
        except Exception as e:
            print(f"Error processing article {i}: {e}")
            driver.switch_to.window(driver.window_handles[0])

            continue
    
    driver.quit()
   
    if not found_link:
        # Return a dictionary with a message indicating no articles found
        return {"error": "Articles not found"}
    else:
        return {link: None for link in full_text_links} if full_text_links else {"error": "Articles not found"}

def scrape_Benefits_Risks(links):
    if "error" in links:
        return links 
    # Initialize the web driver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Uncomment for headless mode
    driver = webdriver.Chrome(service=service, options=options)

    # Initialize NLP model
    nlp = spacy.load("en_core_web_sm")
    paragraph_length=500
    keywords=["conclusions","in conclusion","conclusion","benefit","risk"]
    url_to_paragraphs = {}

    for url in links:
        try:
            driver.get(url)
            last_height = driver.execute_script("return document.body.scrollHeight")
            
            while True:
                # Scroll to the bottom of the page
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Adjust sleep time as necessary

                # Wait for new content to load and check scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            # Additional processing if necessary, e.g., extracting specific elements
            # Example: Extract text and process
            paragraphs = driver.find_elements(By.TAG_NAME, 'p')
            for paragraph in paragraphs:
                text = paragraph.text.strip()
                if text:
                    doc = nlp(text)
                    current_paragraph = ''
                    for sentence in doc.sents:
                        if len(current_paragraph) < paragraph_length:
                            current_paragraph += ' ' + str(sentence)
                        else:
                            if any(keyword.lower() in current_paragraph.lower() for keyword in keywords):
                                if url not in url_to_paragraphs:
                                    url_to_paragraphs[url] = []
                                url_to_paragraphs[url].append(current_paragraph)
                            current_paragraph = str(sentence)
                    # Check for remaining paragraph
                    if current_paragraph and any(keyword.lower() in current_paragraph.lower() for keyword in keywords):
                        if url not in url_to_paragraphs:
                            url_to_paragraphs[url] = []
                        url_to_paragraphs[url].append(current_paragraph)

        except Exception as e:
            print(f"Error while processing {url}: {e}")
            continue

    driver.quit()
    return url_to_paragraphs

def get_Marketing_Experience(keyword,max_results):
    # Set up the Chrome driver
    service = Service(ChromeDriverManager().install())
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument('--headless')
    
    driver = webdriver.Chrome(service=service,options=chrome_options)
     
# Navigate to the search page
    driver.get('https://pubmed.ncbi.nlm.nih.gov/')

    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
# Enter the search keyword and click the search button

 # Construct the search query by adding predetermined terms
    search_query = f'Worldwide Marketing Experience of {keyword} free full text[sb]'

    driver.get('https://pubmed.ncbi.nlm.nih.gov/?term=' + search_query)

    
    # Wait for the search results to be loaded
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#search-results")))

    full_text_links = []


    for i in range(1, max_results + 2):
        try:
             # Wait for the search results to be loaded
            found_link = False
            # Construct the CSS selector for the specific search result
            result_selector = f'#search-results > section > div.search-results-chunks > div > article:nth-child({i}) a'
            search_result = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, result_selector)))
            result_url = search_result.get_attribute('href')

            # Open the result URL in a new tab
            driver.execute_script(f"window.open('{result_url}');")
            driver.switch_to.window(driver.window_handles[1])


            # (Logic to navigate to each article's page)
            try:
            # Extract the full-text link
                full_text_link_selector = '#full-view-identifiers > li:nth-child(2) > span > a'
                full_text_link = driver.find_element(By.CSS_SELECTOR, full_text_link_selector).get_attribute('href')
                full_text_links.append(full_text_link)
                found_link = True
            except Exception as e:
                print(f"Full text link not found for article {i}: {e}")
            finally:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        except NoSuchElementException:
            # Handle the case where the element is not found
            print(f"Full text link not found for article {i}")
        except Exception as e:
            print(f"Error processing article {i}: {e}")
            driver.switch_to.window(driver.window_handles[0])

            continue
    
    driver.quit()
    if not found_link:
        # Return a dictionary with a message indicating no articles found
        return {"error": "Articles not found"}
    else:
        return {link: None for link in full_text_links} if full_text_links else {"error": "Articles not found"}

def scrape_Marketing_Experience(links):
    if "error" in links:
        return links 
    # Initialize the web driver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Uncomment for headless mode
    driver = webdriver.Chrome(service=service, options=options)

    # Initialize NLP model
    nlp = spacy.load("en_core_web_sm")
    paragraph_length=500
    keywords=["marketing experience","marketing","world","sales","profitability","world sales","marketed"]
    url_to_paragraphs = {}

    for url in links:
        try:
            driver.get(url)
            last_height = driver.execute_script("return document.body.scrollHeight")
            
            while True:
                # Scroll to the bottom of the page
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Adjust sleep time as necessary

                # Wait for new content to load and check scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            # Additional processing if necessary, e.g., extracting specific elements
            # Example: Extract text and process
            paragraphs = driver.find_elements(By.TAG_NAME, 'p')
            for paragraph in paragraphs:
                text = paragraph.text.strip()
                if text:
                    doc = nlp(text)
                    current_paragraph = ''
                    for sentence in doc.sents:
                        if len(current_paragraph) < paragraph_length:
                            current_paragraph += ' ' + str(sentence)
                        else:
                            if any(keyword.lower() in current_paragraph.lower() for keyword in keywords):
                                if url not in url_to_paragraphs:
                                    url_to_paragraphs[url] = []
                                url_to_paragraphs[url].append(current_paragraph)
                            current_paragraph = str(sentence)
                    # Check for remaining paragraph
                    if current_paragraph and any(keyword.lower() in current_paragraph.lower() for keyword in keywords):
                        if url not in url_to_paragraphs:
                            url_to_paragraphs[url] = []
                        url_to_paragraphs[url].append(current_paragraph)

        except Exception as e:
            print(f"Error while processing {url}: {e}")
            continue

    driver.quit()
    return url_to_paragraphs

def get_Overview_of_Safety(keyword,max_results):
    # Set up the Chrome driver
    service = Service(ChromeDriverManager().install())
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument('--headless')
    
    driver = webdriver.Chrome(service=service,options=chrome_options)
     
# Navigate to the search page
    driver.get('https://pubmed.ncbi.nlm.nih.gov/')
    found_link = False
    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
# Enter the search keyword and click the search button

 # Construct the search query by adding predetermined terms
    search_query = f'overview of safety of {keyword} free full text[sb]'

    driver.get('https://pubmed.ncbi.nlm.nih.gov/?term=' + search_query)

    
    # Wait for the search results to be loaded
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#search-results")))

    full_text_links = []


    for i in range(1, max_results + 2):
        try:
             # Wait for the search results to be loaded
            
            # Construct the CSS selector for the specific search result
            result_selector = f'#search-results > section > div.search-results-chunks > div > article:nth-child({i}) a'
            search_result = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, result_selector)))
            result_url = search_result.get_attribute('href')

            # Open the result URL in a new tab
            driver.execute_script(f"window.open('{result_url}');")
            driver.switch_to.window(driver.window_handles[1])


            # (Logic to navigate to each article's page)
            try:
            # Extract the full-text link
                full_text_link_selector = '#full-view-identifiers > li:nth-child(2) > span > a'
                full_text_link = driver.find_element(By.CSS_SELECTOR, full_text_link_selector).get_attribute('href')
                full_text_links.append(full_text_link)
                found_link = True
            except Exception as e:
                print(f"Full text link not found for article {i}: {e}")
            finally:    
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        except NoSuchElementException:
            # Handle the case where the element is not found
            print(f"Full text link not found for article {i}")
        except Exception as e:
            print(f"Error processing article {i}: {e}")
            driver.switch_to.window(driver.window_handles[0])

            continue
    
    driver.quit()
    if not found_link:
        # Return a dictionary with a message indicating no articles found
        return {"error": "Articles not found"}
    else:
        return {link: None for link in full_text_links} if full_text_links else {"error": "Articles not found"}

def scrape_Overview_of_Safety(links):
    if "error" in links:
        return links 
    # Initialize the web driver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Uncomment for headless mode
    driver = webdriver.Chrome(service=service, options=options)

    # Initialize NLP model
    nlp = spacy.load("en_core_web_sm")
    paragraph_length=500
    keywords=["Overview of Safety","safety","overview of safety","Drug Safety","Side Effects","Risk Assessment","Harmful Effects","Adverse Reactions"]
    url_to_paragraphs = {}

    for url in links:
        try:
            driver.get(url)
            last_height = driver.execute_script("return document.body.scrollHeight")
            
            while True:
                # Scroll to the bottom of the page
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Adjust sleep time as necessary

                # Wait for new content to load and check scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            # Additional processing if necessary, e.g., extracting specific elements
            # Example: Extract text and process
            paragraphs = driver.find_elements(By.TAG_NAME, 'p')
            for paragraph in paragraphs:
                text = paragraph.text.strip()
                if text:
                    doc = nlp(text)
                    current_paragraph = ''
                    for sentence in doc.sents:
                        if len(current_paragraph) < paragraph_length:
                            current_paragraph += ' ' + str(sentence)
                        else:
                            if any(keyword.lower() in current_paragraph.lower() for keyword in keywords):
                                if url not in url_to_paragraphs:
                                    url_to_paragraphs[url] = []
                                url_to_paragraphs[url].append(current_paragraph)
                            current_paragraph = str(sentence)
                    # Check for remaining paragraph
                    if current_paragraph and any(keyword.lower() in current_paragraph.lower() for keyword in keywords):
                        if url not in url_to_paragraphs:
                            url_to_paragraphs[url] = []
                        url_to_paragraphs[url].append(current_paragraph)

        except Exception as e:
            print(f"Error while processing {url}: {e}")
            continue

    driver.quit()
    return url_to_paragraphs

def get_Clinical_Studies(keyword,max_results):
    # Set up the Chrome driver
    service = Service(ChromeDriverManager().install())
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument('--headless')
    found_link = False
    driver = webdriver.Chrome(service=service,options=chrome_options)
     
# Navigate to the search page
    driver.get('https://pubmed.ncbi.nlm.nih.gov/')

    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
# Enter the search keyword and click the search button

 # Construct the search query by adding predetermined terms
    search_query = f'Clinical Studies of {keyword} free full text[sb]'

    driver.get('https://pubmed.ncbi.nlm.nih.gov/?term=' + search_query)

    
    # Wait for the search results to be loaded
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#search-results")))

    full_text_links = []


    for i in range(1, max_results + 2):
        try:
             # Wait for the search results to be loaded
            
            # Construct the CSS selector for the specific search result
            result_selector = f'#search-results > section > div.search-results-chunks > div > article:nth-child({i}) a'
            search_result = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, result_selector)))
            result_url = search_result.get_attribute('href')

            # Open the result URL in a new tab
            driver.execute_script(f"window.open('{result_url}');")
            driver.switch_to.window(driver.window_handles[1])


            # (Logic to navigate to each article's page)
            try:
            # Extract the full-text link
                full_text_link_selector = '#full-view-identifiers > li:nth-child(2) > span > a'
                full_text_link = driver.find_element(By.CSS_SELECTOR, full_text_link_selector).get_attribute('href')
                full_text_links.append(full_text_link)
                found_link = True
            except Exception as e:
                print(f"Full text link not found for article {i}: {e}")
            finally:    
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        except NoSuchElementException:
            # Handle the case where the element is not found
            print(f"Full text link not found for article {i}")
        except Exception as e:
            print(f"Error processing article {i}: {e}")
            driver.switch_to.window(driver.window_handles[0])

            continue
    
    driver.quit()
    if not found_link:
        # Return a dictionary with a message indicating no articles found
        return {"error": "Articles not found"}
    else:
        return {link: None for link in full_text_links} if full_text_links else {"error": "Articles not found"}

def scrape_Clinical_Studies(links):
    if "error" in links:
        return links 
    # Initialize the web driver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Uncomment for headless mode
    driver = webdriver.Chrome(service=service, options=options)

    # Initialize NLP model
    nlp = spacy.load("en_core_web_sm")
    paragraph_length=500
    keywords=["results","studies","overview"]
    url_to_paragraphs = {}

    for url in links:
        try:
            driver.get(url)
            last_height = driver.execute_script("return document.body.scrollHeight")
            
            while True:
                # Scroll to the bottom of the page
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Adjust sleep time as necessary

                # Wait for new content to load and check scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            # Additional processing if necessary, e.g., extracting specific elements
            # Example: Extract text and process
            paragraphs = driver.find_elements(By.TAG_NAME, 'p')
            for paragraph in paragraphs:
                text = paragraph.text.strip()
                if text:
                    doc = nlp(text)
                    current_paragraph = ''
                    for sentence in doc.sents:
                        if len(current_paragraph) < paragraph_length:
                            current_paragraph += ' ' + str(sentence)
                        else:
                            if any(keyword.lower() in current_paragraph.lower() for keyword in keywords):
                                if url not in url_to_paragraphs:
                                    url_to_paragraphs[url] = []
                                url_to_paragraphs[url].append(current_paragraph)
                            current_paragraph = str(sentence)
                    # Check for remaining paragraph
                    if current_paragraph and any(keyword.lower() in current_paragraph.lower() for keyword in keywords):
                        if url not in url_to_paragraphs:
                            url_to_paragraphs[url] = []
                        url_to_paragraphs[url].append(current_paragraph)

        except Exception as e:
            print(f"Error while processing {url}: {e}")
            continue

    driver.quit()
    return url_to_paragraphs

def get_Overview_of_Efficacy(keyword,max_results):
    # Set up the Chrome driver
    service = Service(ChromeDriverManager().install())
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument('--headless')
    found_link = False
    driver = webdriver.Chrome(service=service,options=chrome_options)
     
# Navigate to the search page
    driver.get('https://pubmed.ncbi.nlm.nih.gov/')

    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
# Enter the search keyword and click the search button

 # Construct the search query by adding predetermined terms
    search_query = f' {keyword} and Overview of Efficacy free full text[sb]'

    driver.get('https://pubmed.ncbi.nlm.nih.gov/?term=' + search_query)

    
    # Wait for the search results to be loaded
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#search-results")))

    full_text_links = []


    for i in range(1, max_results + 2):
        try:
             # Wait for the search results to be loaded
            
            # Construct the CSS selector for the specific search result
            result_selector = f'#search-results > section > div.search-results-chunks > div > article:nth-child({i}) a'
            search_result = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, result_selector)))
            result_url = search_result.get_attribute('href')

            # Open the result URL in a new tab
            driver.execute_script(f"window.open('{result_url}');")
            driver.switch_to.window(driver.window_handles[1])


            # (Logic to navigate to each article's page)
            try:
            # Extract the full-text link
                full_text_link_selector = '#full-view-identifiers > li:nth-child(2) > span > a'
                full_text_link = driver.find_element(By.CSS_SELECTOR, full_text_link_selector).get_attribute('href')
                full_text_links.append(full_text_link)
                found_link = True
            except Exception as e:
                print(f"Full text link not found for article {i}: {e}")
            finally:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        except NoSuchElementException:
            # Handle the case where the element is not found
            print(f"Full text link not found for article {i}")
        except Exception as e:
            print(f"Error processing article {i}: {e}")
            driver.switch_to.window(driver.window_handles[0])

            continue
    
    driver.quit()
    if not found_link:
        # Return a dictionary with a message indicating no articles found
        return {"error": "Articles not found"}
    else:
        return {link: None for link in full_text_links} if full_text_links else {"error": "Articles not found"}

def scrape_Overview_of_Efficacy(links):
    if "error" in links:
        return links 
    # Initialize the web driver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Uncomment for headless mode
    driver = webdriver.Chrome(service=service, options=options)

    # Initialize NLP model
    nlp = spacy.load("en_core_web_sm")
    paragraph_length=500
    keywords=["Drug Performance","efficacy","efficiency","Drug Performance","Medication Effectiveness","Treatment Efficacy","Therapeutic Effectiveness","Positive Impact","Drug Response"]
    url_to_paragraphs = {}

    for url in links:
        try:
            driver.get(url)
            last_height = driver.execute_script("return document.body.scrollHeight")
            
            while True:
                # Scroll to the bottom of the page
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Adjust sleep time as necessary

                # Wait for new content to load and check scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            # Additional processing if necessary, e.g., extracting specific elements
            # Example: Extract text and process
            paragraphs = driver.find_elements(By.TAG_NAME, 'p')
            for paragraph in paragraphs:
                text = paragraph.text.strip()
                if text:
                    doc = nlp(text)
                    current_paragraph = ''
                    for sentence in doc.sents:
                        if len(current_paragraph) < paragraph_length:
                            current_paragraph += ' ' + str(sentence)
                        else:
                            if any(keyword.lower() in current_paragraph.lower() for keyword in keywords):
                                if url not in url_to_paragraphs:
                                    url_to_paragraphs[url] = []
                                url_to_paragraphs[url].append(current_paragraph)
                            current_paragraph = str(sentence)
                    # Check for remaining paragraph
                    if current_paragraph and any(keyword.lower() in current_paragraph.lower() for keyword in keywords):
                        if url not in url_to_paragraphs:
                            url_to_paragraphs[url] = []
                        url_to_paragraphs[url].append(current_paragraph)

        except Exception as e:
            print(f"Error while processing {url}: {e}")
            continue

    driver.quit()
    return url_to_paragraphs

def get_Pharmacodynamics_Drug_Interaction(keyword,max_results):
    # Set up the Chrome driver
    service = Service(ChromeDriverManager().install())
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument('--headless')
    
    driver = webdriver.Chrome(service=service,options=chrome_options)
    found_link = False 
# Navigate to the search page
    driver.get('https://pubmed.ncbi.nlm.nih.gov/')

    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
# Enter the search keyword and click the search button

 # Construct the search query by adding predetermined terms
    search_query = f'Pharmacokinetics of {keyword} free full text[sb]'

    driver.get('https://pubmed.ncbi.nlm.nih.gov/?term=' + search_query)

    
    # Wait for the search results to be loaded
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#search-results")))

    full_text_links = []


    for i in range(1, max_results + 2):
        try:
             # Wait for the search results to be loaded
            
            # Construct the CSS selector for the specific search result
            result_selector = f'#search-results > section > div.search-results-chunks > div > article:nth-child({i}) a'
                                #search-results > section > div.search-results-chunks > div > article:nth-child(2) > div.docsum-wrap > div.docsum-content > a
            search_result = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, result_selector)))
            result_url = search_result.get_attribute('href')

            # Open the result URL in a new tab
            driver.execute_script(f"window.open('{result_url}');")
            driver.switch_to.window(driver.window_handles[1])


            # (Logic to navigate to each article's page)
            try:
            # Extract the full-text link
                full_text_link_selector = '#full-view-identifiers > li:nth-child(2) > span > a'
                full_text_link = driver.find_element(By.CSS_SELECTOR, full_text_link_selector).get_attribute('href')
                full_text_links.append(full_text_link)
                found_link = True
            except Exception as e:
                print(f"Full text link not found for article {i}: {e}")
            finally:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        except NoSuchElementException:
            # Handle the case where the element is not found
            print(f"Full text link not found for article {i}")
        except Exception as e:
            print(f"Error processing article {i}: {e}")
            driver.switch_to.window(driver.window_handles[0])

            continue
    
    driver.quit()
    if not found_link:
        # Return a dictionary with a message indicating no articles found
        return {"error": "Articles not found"}
    else:
        return {link: None for link in full_text_links} if full_text_links else {"error": "Articles not found"}

def scrape_Pharmacodynamics_Drug_Interaction(links):
    if "error" in links:
        return links 
# Initialize the web driver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Uncomment for headless mode
    driver = webdriver.Chrome(service=service, options=options)

    # Initialize NLP model
    nlp = spacy.load("en_core_web_sm")
    paragraph_length=500
    keywords=["Pharmacokinetic","Pharmacokinetics","metabolism","absorption"]
    url_to_paragraphs = {}

    for url in links:
        try:
            driver.get(url)
            last_height = driver.execute_script("return document.body.scrollHeight")
            
            while True:
                # Scroll to the bottom of the page
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Adjust sleep time as necessary

                # Wait for new content to load and check scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            # Additional processing if necessary, e.g., extracting specific elements
            # Example: Extract text and process
            paragraphs = driver.find_elements(By.TAG_NAME, 'p')
            for paragraph in paragraphs:
                text = paragraph.text.strip()
                if text:
                    doc = nlp(text)
                    current_paragraph = ''
                    for sentence in doc.sents:
                        if len(current_paragraph) < paragraph_length:
                            current_paragraph += ' ' + str(sentence)
                        else:
                            if any(keyword.lower() in current_paragraph.lower() for keyword in keywords):
                                if url not in url_to_paragraphs:
                                    url_to_paragraphs[url] = []
                                url_to_paragraphs[url].append(current_paragraph)
                            current_paragraph = str(sentence)
                    # Check for remaining paragraph
                    if current_paragraph and any(keyword.lower() in current_paragraph.lower() for keyword in keywords):
                        if url not in url_to_paragraphs:
                            url_to_paragraphs[url] = []
                        url_to_paragraphs[url].append(current_paragraph)

        except Exception as e:
            print(f"Error while processing {url}: {e}")
            continue

    driver.quit()
    return url_to_paragraphs

def get_Pharmacodynamics_page(keyword,max_results):

    found_link = False
    # Set up the Chrome driver
    service = Service(ChromeDriverManager().install())
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument('--headless')
    
    driver = webdriver.Chrome(service=service,options=chrome_options)
     
# Navigate to the search page
    driver.get('https://pubmed.ncbi.nlm.nih.gov/')

    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
# Enter the search keyword and click the search button

 # Construct the search query by adding predetermined terms
    search_query = f'Pharmacodynamics of {keyword} free full text[sb]'

    driver.get('https://pubmed.ncbi.nlm.nih.gov/?term=' + search_query)

    
    # Wait for the search results to be loaded
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#search-results")))

    full_text_links = []


    for i in range(1, max_results + 2):
        try:
             # Wait for the search results to be loaded
            
            # Construct the CSS selector for the specific search result
            result_selector = f'#search-results > section > div.search-results-chunks > div > article:nth-child({i}) a'
                                #search-results > section > div.search-results-chunks > div > article:nth-child(2) > div.docsum-wrap > div.docsum-content > a
            search_result = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, result_selector)))
            result_url = search_result.get_attribute('href')

            # Open the result URL in a new tab
            driver.execute_script(f"window.open('{result_url}');")
            driver.switch_to.window(driver.window_handles[1])


            # (Logic to navigate to each article's page)
            try:
            # Extract the full-text link
                full_text_link_selector = '#full-view-identifiers > li:nth-child(2) > span > a'
                full_text_link = driver.find_element(By.CSS_SELECTOR, full_text_link_selector).get_attribute('href')
                full_text_links.append(full_text_link)
                found_link = True
            except Exception as e:
                print(f"Full text link not found for article {i}: {e}")
            finally:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        except NoSuchElementException:
            # Handle the case where the element is not found
            print(f"Full text link not found for article {i}")
        except Exception as e:
            print(f"Error processing article {i}: {e}")
            driver.switch_to.window(driver.window_handles[0])

            continue
    
    driver.quit()
    if not found_link:
        # Return a dictionary with a message indicating no articles found
        return {"error": "Articles not found"}
    else:
        return {link: None for link in full_text_links} if full_text_links else {"error": "Articles not found"}

def scrape_pharmacodynamic(links):
    if "error" in links:
        return links 
    # Initialize the web driver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Uncomment for headless mode
    driver = webdriver.Chrome(service=service, options=options)

    # Initialize NLP model
    nlp = spacy.load("en_core_web_sm")
    paragraph_length=500
    keywords=["pharmacodynamic", "Pharmacological effect", "pharmacology","pharmacological","drug efficacy", "ADME" ,"clinical pharmacology"]
    url_to_paragraphs = {}

    for url in links:
        try:
            driver.get(url)
            last_height = driver.execute_script("return document.body.scrollHeight")
            
            while True:
                # Scroll to the bottom of the page
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Adjust sleep time as necessary

                # Wait for new content to load and check scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            # Additional processing if necessary, e.g., extracting specific elements
            # Example: Extract text and process
            paragraphs = driver.find_elements(By.TAG_NAME, 'p')
            for paragraph in paragraphs:
                text = paragraph.text.strip()
                if text:
                    doc = nlp(text)
                    current_paragraph = ''
                    for sentence in doc.sents:
                        if len(current_paragraph) < paragraph_length:
                            current_paragraph += ' ' + str(sentence)
                        else:
                            if any(keyword.lower() in current_paragraph.lower() for keyword in keywords):
                                if url not in url_to_paragraphs:
                                    url_to_paragraphs[url] = []
                                url_to_paragraphs[url].append(current_paragraph)
                            current_paragraph = str(sentence)
                    # Check for remaining paragraph
                    if current_paragraph and any(keyword.lower() in current_paragraph.lower() for keyword in keywords):
                        if url not in url_to_paragraphs:
                            url_to_paragraphs[url] = []
                        url_to_paragraphs[url].append(current_paragraph)

        except Exception as e:
            print(f"Error while processing {url}: {e}")
            continue

    driver.quit()
    return url_to_paragraphs


def clean_up_text(paragraphs):

    cleaned_text = ' '.join(paragraphs)
    # Remove HTML tags
    soup = BeautifulSoup(cleaned_text, 'html.parser')
    cleaned_paragraph = soup.get_text()
    
    return cleaned_paragraph

def wait_for_page_load(driver, timeout=30):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
    except TimeoutException:
        print("Page did not load within the specified timeout")

def get_Pubmed(keyword,max_results):

    Pharmacodynamics_links = get_Pharmacodynamics_page(keyword, max_results)
    scraped_data = scrape_pharmacodynamic(Pharmacodynamics_links)
    Pharmacodynamics_str = ""

    for url, paragraphs in scraped_data.items():
        paragraphs_str = ". ".join(paragraphs)
        Pharmacodynamics_str += f"URL: {url}\n\n Paragraphs: {paragraphs_str}\n\n"
        
    Pharmacodynamics_Drug_Interaction_links = get_Pharmacodynamics_Drug_Interaction(keyword, max_results)
    scraped_data = scrape_Pharmacodynamics_Drug_Interaction(Pharmacodynamics_Drug_Interaction_links)
    Pharmacodynamics_Drug_Interaction_page_str = ""

    for url, paragraphs in scraped_data.items():
        paragraphs_str = ". ".join(paragraphs)
        Pharmacodynamics_Drug_Interaction_page_str += f"URL: {url} \n\n Paragraphs: {paragraphs_str}\n\n"
       
    Overview_of_Efficacy_links = get_Overview_of_Efficacy(keyword, max_results)
    scraped_data = scrape_Overview_of_Efficacy(Overview_of_Efficacy_links)
    Overview_of_Efficacy_str = ""

    for url, paragraphs in scraped_data.items():
        paragraphs_str = ". ".join(paragraphs)
        Overview_of_Efficacy_str += f"URL: {url} \n\n Paragraphs: {paragraphs_str}\n\n"

    Clinical_Studies_links = get_Clinical_Studies(keyword, max_results)
    scraped_data = scrape_Clinical_Studies(Clinical_Studies_links)
    Clinical_Studies_str = ""

    for url, paragraphs in scraped_data.items():
        paragraphs_str = ". ".join(paragraphs)
        Clinical_Studies_str += f"URL: {url} \n\n Paragraphs: {paragraphs_str}\n\n"

    Overview_of_Safety_links = get_Overview_of_Safety(keyword, max_results)
    scraped_data = scrape_Overview_of_Safety(Overview_of_Safety_links)
    Overview_of_Safety_str = ""

    for url, paragraphs in scraped_data.items():
        paragraphs_str = ". ".join(paragraphs)
        Overview_of_Safety_str += f"URL: {url} \n\n Paragraphs: {paragraphs_str}\n\n"
    
    Marketing_Experience_links = get_Marketing_Experience(keyword, max_results)
    scraped_data = scrape_Marketing_Experience(Marketing_Experience_links)
    Marketing_Experience_str = ""

    for url, paragraphs in scraped_data.items():
        paragraphs_str = ". ".join(paragraphs)
        Marketing_Experience_str += f"URL: {url} \n\n Paragraphs: {paragraphs_str}\n\n"
    
    Benefits_Risks_links = get_Benefits_Risks(keyword, max_results)
    scraped_data = scrape_Benefits_Risks(Benefits_Risks_links)
    Benefits_Risks_str = ""

    for url, paragraphs in scraped_data.items():
        paragraphs_str = ". ".join(paragraphs)
        Benefits_Risks_str += f"URL: {url} \n\n Paragraphs: {paragraphs_str}\n\n"
                   
    return Pharmacodynamics_str.strip(),Pharmacodynamics_Drug_Interaction_page_str.strip(),Overview_of_Efficacy_str.strip(),Clinical_Studies_str.strip(),Overview_of_Safety_str.strip(),Marketing_Experience_str.strip(),Benefits_Risks_str.strip()



#Get by id functions
def get_molecule_by_id(molecule_id):
    try:
        return Molecule.query.filter_by(id=molecule_id).one()
    except NoResultFound:
        return None
    
def get_user_by_id(user_id):
    try:
        return User.query.filter_by(id=user_id).one()
    except NoResultFound:
        return None    


#send email
def send_email_to_admin(admin_user, new_user):
    subject = 'New User Added'
    body = f'''
    Hello {admin_user.username},

    A new user has been added to the system.

    User Details:
    Username: {new_user.username}
    Email: {new_user.email}
    Role: {new_user.role}
    Phone Number: {new_user.phone_number}
    ...

    Regards,
    Medis medicale
    '''

    msg = Message(subject, recipients=[admin_user.email], body=body)
    mail.send(msg)



#URL
@app.before_request
def before_request_func():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
    else:
        response = app.response_class()
    
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response if request.method == 'OPTIONS' else None   

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response 

# Adding Scrapping results to database
@app.route('/molecule/<int:user_id>/<int:max_results>', methods=['POST'])
def molecule_data(user_id,max_results):


    try:
        data = request.get_json()
        keyword = data.get("keyword")
        results = get_page(keyword)
        results2 = get_Pubmed(keyword, max_results)

        if results == "No results found.": 
            return jsonify({"message": "No results found"}), 404

        pubchem_cid = results[1]  
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        existing_pubchem = Pubchem.query.filter_by(pubchem_cid=results[1]).first()

        if existing_pubchem:
            # Existing Pubchem found, so get its associated Molecule
            molecule = existing_pubchem.molecule
            molecule.date_of_creation = datetime.now()  # Update the timestamp
            message = "Molecule updated successfully."
        else:
            # No existing Molecule found, create new Molecule, Pubchem, and Pubmed
            molecule = Molecule(keyword=keyword, user_id=user_id, date_of_creation=datetime.now())
            db.session.add(molecule)
            db.session.flush()  # Ensures molecule gets an ID
            existing_pubchem = Pubchem(
            
                compoundname=results[0],
                pubchem_cid=results[1],
                molecular_form=results[2],
                molecular_weight=results[3],
                cas_reg=results[4],
                atc_code=results[5],
                iupac_name=results[6],
                solubility=results[7],
                physical_desc=results[8],
                melting_point=results[9],
                decomposition=results[10],
                half_life=results[11],
                reactivity=results[12],
                image_url=results[13],
                molecule_id=molecule.id  # Reference the Molecule record
                )
            message = "Molecule added successfully."

        # Update or set Pubchem data
        existing_pubchem.compoundname = results[0]
        existing_pubchem.pubchem_cid = results[1]
        existing_pubchem.molecular_form = results[2]
        existing_pubchem.molecular_weight = results[3]
        existing_pubchem.cas_reg = results[4]
        existing_pubchem.atc_code = results[5]
        existing_pubchem.iupac_name = results[6]
        existing_pubchem.solubility = results[7]
        existing_pubchem.physical_desc = results[8]
        existing_pubchem.melting_point = results[9]
        existing_pubchem.decomposition = results[10]
        existing_pubchem.half_life = results[11]
        existing_pubchem.reactivity = results[12]
        existing_pubchem.image_url = results[13]

        # Update or create Pubmed data
        existing_pubmed = Pubmed.query.filter_by(molecule_id=molecule.id).first()
        if not existing_pubmed:
            existing_pubmed = Pubmed(
        
                Pharmacodynamics=results2[0],
                Pharmacodynamics_Drug_Interaction_page=results2[1],
                Overview_of_Efficacy=results2[2],
                Clinical_Studies=results2[3],
                Overview_of_Safety=results2[4],
                Marketing_Experience=results2[5],
                Benefits_Risks=results2[6],
                molecule_id=molecule.id  # Reference the Molecule record
                )
        
        existing_pubmed.Pharmacodynamics = results2[0]
        existing_pubmed.Pharmacodynamics_Drug_Interaction_page = results2[1]
        existing_pubmed.Overview_of_Efficacy = results2[2]
        existing_pubmed.Clinical_Studies = results2[3]
        existing_pubmed.Overview_of_Safety = results2[4]
        existing_pubmed.Marketing_Experience = results2[5]
        existing_pubmed.Benefits_Risks = results2[6]

        db.session.add(existing_pubchem)
        db.session.add(existing_pubmed)
        db.session.commit()


        #print(results2)
        return jsonify({"message": message, "molecule_id": molecule.id}), 201
    
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database Error: {e}")
        return jsonify({"message": "Error storing data"}), 500

    except Exception as e:
        print(f"General Error: {e}")
        return jsonify({"message": "An error occurred"}), 500

# Adding pubmed data to database
@app.route('/pubmed/<int:molecule_id>', methods=['POST'])
def add_pubmed_data(molecule_id,max_results):

    # Check if the Molecule exists for the given ID
    molecule = Molecule.query.get(molecule_id)
    if not molecule:
        return jsonify({"message": "Molecule not found"}), 404  # HTTP status code 404 for not found

    # Now you can use the keyword from the Molecule record
    keyword = molecule.keyword

    # Call the get_Pubmed function with the keyword from the Molecule record
    results2 = get_Pubmed(keyword, max_results)

    # Check if Pubmed data already exists for the given Molecule
    pubmed = Pubmed.query.filter_by(molecule_id=molecule.id).first()
    if pubmed:
        return jsonify({"message": "Pubmed data already exists for this molecule"}), 409  # HTTP status code 409 for conflict

    #pubmed = Pubmed.query.filter_by(molecule_id=molecule.id).first()


    # If Pubmed data doesn't exist, create a new record
    try:
        pubmed = Pubmed(
            Pharmacodynamics=results2[0],
            Pharmacodynamics_Drug_Interaction_page=results2[1],
            Overview_of_Efficacy=results2[2],
            Clinical_Studies=results2[3],
            Overview_of_Safety=results2[4],
            Marketing_Experience=results2[5],
            Benefits_Risks=results2[6],
            molecule_id=molecule.id
        )
        db.session.add(pubmed)
        db.session.commit()

        return jsonify({"message": "Pubmed data stored successfully"})
    except Exception as e:
        db.session.rollback()
        print(f"Error adding pubmed data: {e}")
        return jsonify({"message": "Error adding pubmed data"}), 500  # HTTP status code 500 for internal server error  

# Adding pubchem data to database
@app.route('/pubchem/<int:molecule_id>', methods=['POST'])
def add_pubchem_data(molecule_id):
   

    # Check if the Molecule exists for the given ID
    molecule = Molecule.query.get(molecule_id)
    if not molecule:
        return jsonify({"message": "Molecule not found"}), 404  # HTTP status code 404 for not found
    
    keyword = molecule.keyword
    results = get_page(keyword)
    
    
    # Check if PubChem data already exists for the given Molecule
    pubchem = Pubchem.query.filter_by(molecule_id=molecule.id).first()
    if pubchem:
        return jsonify({"message": "PubChem data already exists for this molecule"}), 409  # HTTP status code 409 for conflict

    # If PubChem data doesn't exist, create a new record
    pubchem = Pubchem(
        compoundname=results[0],
        pubchem_cid=results[1],
        molecular_form=results[2],
        molecular_weight=results[3],
        cas_reg=results[4],
        atc_code=results[5],
        iupac_name=results[6],
        solubility=results[7],
        physical_desc=results[8],
        melting_point=results[9],
        decomposition=results[10],
        half_life=results[11],
        reactivity=results[12],
        image_url=results[13],
        molecule_id=molecule.id
        
    )
    db.session.add(pubchem)
    db.session.commit()

    return jsonify({"message": "PubChem data stored successfully"})

@app.route('/modify_pubchem/<int:molecule_id>', methods=['PUT'])
def modify_pubchem(molecule_id):
    try:
        data = request.get_json()

        # Check if the Molecule exists for the given ID
        molecule = Molecule.query.get(molecule_id)
        if not molecule:
            return jsonify({"message": "Molecule not found"}), 404

        # Check if the Pubchem record exists for the given Molecule
        pubchem = Pubchem.query.filter_by(molecule_id=molecule_id).first()
        if not pubchem:
            return jsonify({"message": "Pubchem data not found for the molecule"}), 404

        # Update Pubchem data based on the request body
        pubchem.compoundname = data.get('compoundname', pubchem.compoundname)
        pubchem.molecular_form = data.get('molecular_form', pubchem.molecular_form)
        pubchem.molecular_weight = data.get('molecular_weight', pubchem.molecular_weight)
        pubchem.cas_reg = data.get("cas_reg", pubchem.cas_reg)
        pubchem.atc_code = data.get("atc_code", pubchem.atc_code)
        pubchem.iupac_name = data.get("iupac_name", pubchem.iupac_name)
        pubchem.solubility = data.get("solubility", pubchem.solubility)
        pubchem.physical_desc = data.get("physical_desc", pubchem.physical_desc)
        pubchem.melting_point = data.get("melting_point", pubchem.melting_point)
        pubchem.decomposition = data.get("decomposition", pubchem.decomposition)
        pubchem.half_life = data.get("half_life", pubchem.half_life)
        pubchem.reactivity = data.get("reactivity", pubchem.reactivity)
        # Update other fields as needed

        # Commit changes to the database
        db.session.commit()

        return jsonify({"message": "Pubchem data modified successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Modify results in database
@app.route('/modify_molecule/<int:molecule_id>', methods=['PUT'])
def modify_molecule(molecule_id):
     # Get the existing molecule
    molecule = get_molecule_by_id(molecule_id)

    if molecule is None:
        return jsonify({"error": "Molecule not found"}), 404

    # Update molecule properties based on the request data
    data = request.get_json()
    molecule.keyword = data.get("keyword", molecule.keyword)

    # Commit the changes to the database
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "IntegrityError occurred, likely a constraint violation"}), 400

    # Update related Pubchem data if available
    if 'pubchem' in data:
        pubchem_data = data['pubchem']
        pubchem = Pubchem.query.filter_by(molecule_id=molecule_id).first()
        if pubchem:
            # Update attributes if they exist in pubchem_data
            attributes = [
                "compoundname", "pubchem_cid", "molecular_form", "molecular_weight", 
                "cas_reg", "atc_code", "iupac_name", "solubility", "physical_desc", 
                "melting_point", "decomposition", "half_life", "reactivity"
            ]
            for attr in attributes:
                if attr in pubchem_data:
                    setattr(pubchem, attr, pubchem_data[attr])

            db.session.commit()

    # Update related Pubmed data if available
    if 'pubmed' in data:
        pubmed_data = data['pubmed']
        pubmed = Pubmed.query.filter_by(molecule_id=molecule_id).first()
        if pubmed:
            # Update attributes if they exist in pubmed_data
            attributes = [
                "Pharmacodynamics", "Pharmacodynamics_Drug_Interaction_page",
                "Overview_of_Efficacy", "Clinical_Studies", "Overview_of_Safety",
                "Marketing_Experience", "Benefits_Risks"
            ]
            for attr in attributes:
                if attr in pubmed_data:
                    setattr(pubmed, attr, pubmed_data[attr])

            db.session.commit()

    return jsonify({"message": "Molecule and related data modified successfully"})

# Delete Molecule from database
@app.route('/delete_molecule/<int:molecule_id>', methods=['DELETE'])
def delete_molecule(molecule_id):
    # Check if the Molecule exists for the given ID
    molecule = Molecule.query.get(molecule_id)
    if not molecule:
        return jsonify({"message": "Molecule not found"}), 404  # HTTP status code 404 for not found

    # Delete related PubChem data
    pubchem = Pubchem.query.filter_by(molecule_id=molecule.id).first()
    if pubchem:
        db.session.delete(pubchem)

    # Delete related PubMed data
    pubmed = Pubmed.query.filter_by(molecule_id=molecule.id).first()
    if pubmed:
        db.session.delete(pubmed)

    # Delete the Molecule
    db.session.delete(molecule)
    db.session.commit()

    return jsonify({"message": "Molecule and related data deleted successfully"})

#Generate the PDF from database
@app.route('/generate_pdf/<int:molecule_id>', methods =['GET'])
def generate_pdf(molecule_id):
    try: 
    # Query data from the database for the specific molecule and its related PubChem and PubMed data
        molecule = Molecule.query.get(molecule_id)
        pubchem = Pubchem.query.filter_by(molecule_id=molecule_id).first()
        pubmed = Pubmed.query.filter_by(molecule_id=molecule_id).first()

        if molecule is None:
            return jsonify({"message": "Molecule not found"}), 404

# Specify the folder where PDFs will be stored
        pdf_folder = "PDF results"
        if not os.path.exists(pdf_folder):
            os.makedirs(pdf_folder)


    # Specify the path for the PDF file
        pdf_file_path = os.path.join(pdf_folder, f"molecule_{molecule.keyword}_output.pdf")

    # Create a PDF document
    # Create a PDF document
        doc = SimpleDocTemplate(pdf_file_path, pagesize=letter)
        story = []

    # Define a style for the PDF content
        styles = getSampleStyleSheet()
        normal_style = styles['Normal']
    # Create a stylesheet
        styles = getSampleStyleSheet()

    # Define a custom style for the heading
        heading_style = ParagraphStyle(
        name='HeadingStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,  # Adjust the font size as needed
        leading=16,  # Adjust the leading (line spacing) as needed
        textColor=colors.black,
        )
    # Add content to the PDF
 
        user = db.session.query(User).filter_by(id=molecule.user_id).first()

# Now you can access the username
        if user:
            username = user.username
        else:
            username = "User not found"

        # Add the molecule data to the PDF
        content = f"<b>Molecule ID:</b> {molecule.id}<br/><b>Keyword:</b> {molecule.keyword}<br/><b>User Name:</b> {username}<br/><b>Date of Creation:</b> {molecule.date_of_creation}<br/><br/>"
        story.append(Paragraph(content, normal_style))
        story.append(Spacer(1, 12))  # Add some space between sections

    # Add the heading for "PubChem Data"
        heading = Paragraph("<h3>PubChem</h3>", heading_style)
        story.append(heading)
        if pubchem is None:
            return jsonify({"error": "Pubchem data not found"}), 404
        # Add the PubChem data to the PDF
        content = f"<b>Compound Name:</b> {pubchem.compoundname}<br/><b>Molecular Form:</b> {pubchem.molecular_form}<br/><b>Molecular weight:</b>{pubchem.molecular_weight}<br/><b>CAS registration:</b> {pubchem.cas_reg}<br/><b>ATC code:</b> {pubchem.atc_code}<br/><b>IUPAC name:</b> {pubchem.iupac_name}<br/><b>Solubility:</b> {pubchem.solubility}<br/><b>Physical description:</b> {pubchem.physical_desc}<br/><b>Melting point:</b> {pubchem.melting_point}<br/><b>Decomposition:</b> {pubchem.decomposition}<br/><b>Half life:</b> {pubchem.half_life}<br/><b>Reactivity:</b> {pubchem.reactivity}<br/><br/>"
        story.append(Paragraph(content, normal_style))
        story.append(Spacer(1, 12))  

    # Add the heading for "PubMemd Data"
        heading = Paragraph("<h3>PubMed</h3>", heading_style)
        story.append(heading)
    # Add the PubMed data to the PDF
        if pubmed is None:
            return jsonify({"error": "Pubchem data not found"}), 404
        content = f"<b>Pharmacodynamics:</b> {pubmed.Pharmacodynamics}<br/><br/><b>Overview of Efficacy:</b> {pubmed.Overview_of_Efficacy}<br/><br/><b>Pharmacodynamics Drug Interaction:</b> {pubmed.Pharmacodynamics_Drug_Interaction_page}<br/><br/><b>Clinical Studies:</b> {pubmed.Clinical_Studies}<br/><br/><b>Overview of Safety:</b> {pubmed.Overview_of_Safety}<br/><br/><b>Marketing Experience:</b> {pubmed.Marketing_Experience}<br/><br/><b>Benefits/Risks:</b> {pubmed.Benefits_Risks}<br/><br/><br/>"
        story.append(Paragraph(content,normal_style))
        story.append(Spacer(1, 12))  

    
        image_path = f"Image Molecule/{molecule.keyword}_image.png"
        if os.path.exists(image_path):
            image = Image(image_path, width=200, height=200)
            story.append(image)
            story.append(Spacer(1, 12))  # Add some space after the image

            caption_style = ParagraphStyle(
            name='CaptionStyle',
            parent=styles['Normal'],
            alignment=TA_CENTER,  # Center alignment
            fontSize=10,  # Adjust the font size as needed
            )
            # Adding a caption for the image
            image_caption = f"Img 1: Molecule structure of {molecule.keyword} (Source: PubChem)"
            story.append(Paragraph(image_caption, caption_style))
            story.append(Spacer(1, 12))  # Additional space after the caption


    # Build the PDF document
        doc.build(story)

    # Return the PDF as a response or save it to a file
        with open(pdf_file_path, 'rb') as pdf:
            response = Response(pdf.read(), content_type='application/pdf')
            response.headers['Content-Disposition'] = 'inline; filename=output.pdf'
        return response
    except SQLAlchemyError as e:
        print(f"Database Error: {e}")
        traceback.print_exc()
        return jsonify({"message": "Database error occurred"}), 500
    except Exception as e:
        print(f"Error generating PDF: {e}")
        traceback.print_exc()
        return jsonify({"message": "Error generating PDF"}), 500

#Adding user to database
@app.route('/add_user', methods=['POST'])
def add_user():
    # Get user data from the request
    data = request.get_json()

    # Extract user details from the request data
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    role = data.get("role")
    phone_number = data.get("phone_number")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    address = data.get("address")
    status = data.get("status", False)

    # Create a new user with the extracted details
    new_user = User(
        username=username,
        password=password,
        email=email,
        role=role,
        phone_number=phone_number,
        first_name=first_name,
        last_name=last_name,
        address=address,
        status= status
    )

    # Add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    # Send email to all admin users
    admin_users = User.query.filter_by(role='ADMIN').all()
    for admin_user in admin_users:
        send_email_to_admin(admin_user, new_user)

    return 'User added successfully'

@app.route('/modify_user/<int:user_id>', methods=['PUT'])
def modify_user(user_id):

    try:
        data = request.get_json()
        print("Request Data:", data)

        user = get_user_by_id(user_id)

        if not user:
            return 'User not found', 404
        
        print("User ID:", user_id)

        print("Existing User Role:", user.role)

        # Update user details based on the request body
        user.username = data.get('username', user.username)
        data_password = data.get('password')
        if data_password:
            user.password = user._hash_password(data_password)
        user.email = data.get('email', user.email)
        user.phone_number = data.get('phone_number', user.phone_number)
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.address = data.get('address', user.address)
        data_status = data.get('status')
        if data_status is not None:
         user.status = bool(int(data_status))

        # Commit changes to the database
        db.session.commit()

        return jsonify({"message": "User modified successfully"})

    except Exception as e:
        print("Exception:", str(e))
        traceback.print_exc()
        return jsonify({"error": "An error occurred while modifying the user"}), 500

@app.route('/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user = User.query.get(user_id)

        if not user:
            return jsonify({"message": "User not found"}), 404  # HTTP status code 404 for not found

        # Delete the user
        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "User deleted successfully"})

    except Exception as e:
        print("Exception:", str(e))
        traceback.print_exc()
        return jsonify({"error": "An error occurred while deleting the user"}), 500

@app.route('/molecules', methods=['GET'])
def get_all_molecules():
    try:
        # Query all molecules
        molecules = Molecule.query.all()
        
        # Transform the SQLAlchemy objects into a list of dictionaries
        molecules_list = []
        for molecule in molecules:
            user_name = molecule.user.first_name + ' ' + molecule.user.last_name if molecule.user else 'No User'
            molecules_list.append({
                'id': molecule.id,
                'keyword': molecule.keyword,
                'user_id': molecule.user_id,
                'date_of_creation': molecule.date_of_creation.strftime("%Y-%m-%d %H:%M:%S"),  # Formatting the datetime object to string
                'User_name': user_name
            })
        
        # Return the list as JSON
        return jsonify(molecules_list), 200
    
    except Exception as e:
        # In case of any error, return an error message
        return jsonify({"error": str(e)}), 500

@app.route('/molecule_info/<int:molecule_id>', methods=['GET'])
def get_molecule_info(molecule_id):
    try:
        # Query for the Molecule by ID
        molecule = Molecule.query.get(molecule_id)
        if not molecule:
            return jsonify({"message": "Molecule not found"}), 404
        
        # Assuming the relationships are set up as discussed, 
        # you can directly access related Pubchem and Pubmed info
        pubchem_info = {}
        pubmed_info = {}
        
        if molecule.pubchem:
            pubchem_info = {
                "compoundname": molecule.pubchem.compoundname,
                "pubchem_cid": molecule.pubchem.pubchem_cid,
                "molecular_form": molecule.pubchem.molecular_form,
                "molecular_weight": molecule.pubchem.molecular_weight,
                "cas_reg": molecule.pubchem.cas_reg,
                "atc_code": molecule.pubchem.atc_code,
                "iupac_name": molecule.pubchem.iupac_name,
                "solubility": molecule.pubchem.solubility,
                "physical_desc": molecule.pubchem.physical_desc,
                "melting_point": molecule.pubchem.melting_point,
                "decomposition": molecule.pubchem.decomposition,
                "half_life": molecule.pubchem.half_life,
                "reactivity": molecule.pubchem.reactivity,
                "image_url": molecule.pubchem.image_url,
                # Add other fields as necessary
            }
        
        if molecule.pubmed:
            pubmed_info = {
                "Pharmacodynamics": molecule.pubmed.Pharmacodynamics,
                "Pharmacodynamics_Drug_Interaction_page": molecule.pubmed.Pharmacodynamics_Drug_Interaction_page,
                "Overview_of_Efficacy": molecule.pubmed.Overview_of_Efficacy,
                "Clinical_Studies": molecule.pubmed.Clinical_Studies,
                "Overview_of_Safety": molecule.pubmed.Overview_of_Safety,
                "Marketing_Experience": molecule.pubmed.Marketing_Experience,
                "Benefits_Risks": molecule.pubmed.Benefits_Risks,

                # Add other fields as necessary
            }

        # Combine all info into a single response
        response = {
            "molecule": {
                
                "keyword": molecule.keyword,
                "Date": molecule.date_of_creation,
                # Add other Molecule fields as necessary
            },
            "pubchem": pubchem_info,
            "pubmed": pubmed_info
        }
        
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password.encode('utf-8'), password.encode('utf-8')):
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role.name,
            'status': user.status,
            'phone_number': user.phone_number,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'address': user.address
        }), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401








# Specifiying port 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)





