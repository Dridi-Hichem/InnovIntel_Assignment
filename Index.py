# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 14:06:41 2022

@author: Hichem
"""

import functools
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.common.exceptions import SessionNotCreatedException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
import os
from pathlib import Path
import time

url = 'https://www.scottishmedicines.org.uk/medicines-advice/'

def get_driver(func):
    @functools.wraps(func)
    def wrapper_get_driver():
        try:
            driver = func()
        except SessionNotCreatedException:
            driver = None
        return driver
    return wrapper_get_driver

@get_driver
def get_ChromeDriver():
    # create selenium driver object for Chrome
    opts = webdriver.ChromeOptions()
    opts.headless = True # prevent the browser from running in the background
    
    service = ChromeService(ChromeDriverManager().install()) # Selenium requires a driver to interface with the chosen browser.
    driver = webdriver.Chrome(service = service, options=opts)
    return driver

@get_driver
def get_FirefoxDriver():
    opts = webdriver.FirefoxOptions()
    opts.headless = True
    
    service = FirefoxService(GeckoDriverManager().install())
    driver = webdriver.Firefox(service = service, options=opts)
    return driver

@get_driver
def get_EdgeDriver():
    opts = webdriver.EdgeOptions()
    opts.headless = True
    
    service = EdgeService(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service = service, options=opts)
    return driver

def parse_url(func):
    @functools.wraps(func)
    def wrapper_parse_url(*args, **kwargs):
        for getDriver in [get_ChromeDriver(), get_FirefoxDriver(), get_EdgeDriver()]:
            driver = getDriver
            if driver != None: break

        assert driver != None, "This program requires Chrome, Edge or Firefox \
            to run. Please ensure that at least one of these browsers is installed."
        
        try:
            data_dict = func(driver, *args, **kwargs)
        except NoSuchElementException:
            data_dict = None
            
        return data_dict     
    return wrapper_parse_url

@parse_url
def get_table_data(driver):
    driver.get(url)
    assert driver.title == "Medicines advice", "Unable to retrieve web page, try later."
    
    # create "load more" button object
    #loadMore = driver.find_element(By.ID, "btn-more-0")
    # or 
    #loadMore = wait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Load more']")))
    
    # get the number of pages
    #totalPages = driver.find_element(By.ID, "max-page-0").get_attribute("value")
    
    # click the button "load more" to load all the rows in the table
    #for i in range(totalPages):
    #    loadMore.click()
    
    # get a list of medecine IDs elements and a list of medecine links elements
    
    data_dict = {
        "IDs": [ID_element.text.strip() for ID_element in driver.find_elements(By.CLASS_NAME, "medicine-advice-table__id-row")],
        "Names": [medecine_element.text.strip() for medecine_element in driver.find_elements(By.CLASS_NAME, "medicine-advice-table__link")],
        "Links": [link_element.find_element(By.TAG_NAME, 'a').get_attribute("href") for link_element in driver.find_elements(By.CLASS_NAME, "medicine-advice-table__link-row")]
        }
    
    return data_dict
     
@parse_url
def get_file_link(driver, file_id, file_name, file_url):
    driver.get(file_url)
    section_element = driver.find_element(By.XPATH, "/html/body/div/section")
    file_link = section_element.find_elements(By.TAG_NAME, "a")[0].get_attribute("href")
    return {"ID": file_id, "Name": file_name, "File link": file_link}
    
def fetch_all(limit, path = None):
    data_dict = get_table_data()
    
    if data_dict == None:
        print(", ".join(["Unable to retrieve data from https://www.scottishmedicines.org.uk/medicines-advice/",
                        "The website may not be found or its desing has been changed!"]))
        pass
    
    if path == None:
        downloads_path = str(os.path.join(Path.home(), "Downloads", "Medicines advice"))
        print("Downloading the file in ", str(os.path.join(downloads_path, "Downloads")))
    
    elif not os.path.exists(path):
        downloads_path = str(os.path.join(Path.home(), "Downloads", "Medicines advice"))
        print(f"The entered path: {path} is not valid!")
        print("Downloading the file in ", str(os.path.join(downloads_path, "Downloads")))
        
    elif os.path.isdir(str(path, "Medicines advice")):
        print(". ".join(["The current path contains a folder called 'Medicines advice'",
                         ]))
        

def fetch(by_id = None, by_name = None):
    pass

res = get_table_data()
print(res['IDs'])
print(res['Names'])
print(res['Links'])