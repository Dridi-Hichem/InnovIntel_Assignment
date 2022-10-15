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
import time
import os
from pathlib import Path

url = 'https://www.scottishmedicines.org.uk/medicines-advice/'

def get_driver(func):
    '''
    Returns a webdriver instance from selenium

    Parameters
    ----------
    func : function
        a function that returns a selenium driver object for a browser.

    Returns
    -------
    selenium.webdriver or None
        None if a the browser is not installed.

    '''
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
    '''
    Returns a selenium driver object for Chrome

    Returns
    -------
    driver : selenium.webdriver.chrome.webdriver.WebDriver

    '''
    # create selenium driver object for Chrome
    opts = webdriver.ChromeOptions()
    opts.headless = True # prevent the browser from running in the background
    
    service = ChromeService(ChromeDriverManager().install()) # Selenium requires a driver to interface with the chosen browser.
    driver = webdriver.Chrome(service = service, options=opts)
    return driver

@get_driver
def get_FirefoxDriver():
    '''
    Returns a selenium driver object for Firefox

    Returns
    -------
    driver : selenium.webdriver.firefox.webdriver.WebDriver

    '''
    opts = webdriver.FirefoxOptions()
    opts.headless = True
    
    service = FirefoxService(GeckoDriverManager().install())
    driver = webdriver.Firefox(service = service, options=opts)
    return driver

@get_driver
def get_EdgeDriver():
    '''
    Returns a selenium driver object for Edge

    Returns
    -------
    driver : selenium.webdriver.Edge.webdriver.WebDriver

    '''
    opts = webdriver.EdgeOptions()
    opts.headless = True
    
    service = EdgeService(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service = service, options=opts)
    return driver

def parse_url(func):
    '''
    Function to parse a webpage using selenium webdriver.

    Parameters
    ----------
    func : function
        The function with instructions for scraping a given website .

    Returns
    -------
    dictionnary or None
        Dictionnary of data retrieved or None if the scrapping method failed.

    '''
    @functools.wraps(func)
    def wrapper_parse_url(*args, **kwargs):
        # instantiate the webdriver object
        for getDriver in [get_ChromeDriver(), get_FirefoxDriver(), get_EdgeDriver()]:
            driver = getDriver
            if driver != None: break

        assert driver != None, "This program requires Chrome, Edge or Firefox \
            to run. Please ensure that at least one of these browsers is installed."
        
        try:
            data_dict = func(driver, *args, **kwargs)
        except NoSuchElementException:
            # returns None if the scraping failed
            data_dict = None
            
        return data_dict     
    return wrapper_parse_url

@parse_url
def get_table_data(driver):
    '''
    A function to parse the 'Medecines advice' webpage to retrieve medication IDs,\
    names and links to the medication webpage from the 'Published' table.

    Parameters
    ----------
    driver : selenium webdriver object, Optional
        generated automatically.

    Returns
    -------
    data_dict : dict
        A JSON like dictionnary with lists of medication IDs, names and links.

    '''
    driver.get(url) # send the GET request
    assert driver.title == "Medicines advice", "Unable to retrieve web page, try later."
    
    # close cookies popup
    wait(driver, 10).until(EC.element_to_be_clickable((By.ID, "ccc-dismiss-button"))).click()
    
    # get the number of pages i.e. the number of times to click on the button load more
    totalPages = driver.find_element(By.ID, "max-page-0").get_attribute("value")
    
    # click the button "load more" to load all the rows in the table
    for i in range(totalPages):
        wait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btn-more-0"]'))).click()
        time.sleep(3)
    
    # get IDs, names and links to medicine webpage in a JSON like dictionnary
    # get the table Published
    table_published = driver.find_element(By.CLASS_NAME, "tabs__content").find_element(By.TAG_NAME, "table")
    
    data_dict = {
        "IDs": [ID_element.text.strip() for ID_element in table_published.\
                find_elements(By.CLASS_NAME, "medicine-advice-table__id-row")],
        "Names": [medecine_element.find_element(By.CLASS_NAME, "medicine-advice-table__link").text.strip() 
                  for medecine_element in table_published.\
                      find_elements(By.CLASS_NAME, "medicine-row")],
        "Links": [link_element.find_element(By.TAG_NAME, 'a').get_attribute("href") \
                  for link_element in table_published.find_elements(By.CLASS_NAME, "medicine-advice-table__link-row")]
        }
    
    return data_dict
     
@parse_url
def get_file_link(driver, file_id, file_name, file_url):
    '''
    A function to parse the url of a given drug to retrieve the link \
    to the detailed advice pdf file.

    Parameters
    ----------
    driver : selenium webdriver object, Optional
        generated automatically.
    file_id : str
        The medicine SMC ID.
    file_name : str
        The medicine name.
    file_url : str
        The link to the detailed advice pdf file.

    Returns
    -------
    dict
        A dictionnary with the medication ID, name and pdf file link.

    '''
    
    driver.get(file_url) # send the GET request
    # get the link the detailed advice pdf file
    section_element = driver.find_element(By.XPATH, "/html/body/div/section")
    file_link = section_element.find_elements(By.TAG_NAME, "a")[0].get_attribute("href")
    
    return {"ID": file_id, "Name": file_name, "File link": file_link}


def folder_path(path, name):
    '''
    Returns the path to the existed/created folder in the given path.

    Parameters
    ----------
    path : str
        The path to the check the existance of the folder or created it.
    name : str
        the folder name.

    Returns
    -------
    final_path : str
        The final path to the folder.

    '''
    final_path = str(os.path.join(path, name))
    if not os.path.exists(final_path): os.mkdir(final_path)
    return final_path
    
def get_downloading_path(path = None):
    '''
    Create a folder called 'Medicines advice' in the specified path otherwise in \
    the 'Downloads' folder or create 'Downloads' then 'Medicines advice' if 'Downloads' does not exist

    Parameters
    ----------
    path : str
        A path to save downloaded files.

    Returns
    -------
    medicines_folder_path : str
        The path to the created folder 'Medicines advice'.

    '''
    
    downloads_path = folder_path(Path.home(), "Downloads")
    medicines_folder_path = folder_path(downloads_path, "Medicines advice")
    
    if path == None:
        print("Downloading the file in -> ", medicines_folder_path)
    
    elif not os.path.exists(path): # if the given path is wrong
        print(f"The entered path: {path} is not valid!")
        print("Downloading the file in -> ", medicines_folder_path)
        
    else:
        medicines_folder_path = folder_path(downloads_path, "Medicines advice")
        
    return medicines_folder_path


def fetch_all(limit, path = None):
    data_dict = get_table_data()
    
    if data_dict == None:
        print(", ".join(["Unable to retrieve data from https://www.scottishmedicines.org.uk/medicines-advice/",
                        "The website may not be found or its desing has been changed!"]))
        pass
    
    downloads_path = get_downloading_path(path)
    pass
        

def fetch(by_id = None, by_name = None):
    pass
