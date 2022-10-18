# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 14:06:41 2022

@author: Hichem Dridi
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
from selenium.common.exceptions import SessionNotCreatedException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
import sys
import time
import os
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import re

url = 'https://www.scottishmedicines.org.uk/medicines-advice/'

def get_WebDriver(func):
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
        driver = None
        try:
            driver = func()
        except SessionNotCreatedException as e:
            print('Fail! Code: {}, {}'.format(type(e).__name__, str(e)))
        except SessionNotCreatedException as e:
            print('Fail! Code: {}, {}'.format(type(e).__name__, str(e)))
        
        return driver
    return wrapper_get_driver

@get_WebDriver
def get_ChromeDriver():
    '''
    Returns a selenium driver object for Chrome

    Returns
    -------
    driver : selenium.webdriver.chrome.webdriver.WebDriver

    '''
    print("Trying to install a driver for Chrome. Please wait...")
    
    # create selenium driver object for Chrome
    opts = webdriver.ChromeOptions()
    opts.headless = True # prevent the browser from running in the background
    
    service = ChromeService(ChromeDriverManager().install()) # Selenium requires a driver to interface with the chosen browser.
    driver = webdriver.Chrome(service = service, options=opts)
    
    return driver

@get_WebDriver
def get_FirefoxDriver():
    '''
    Returns a selenium driver object for Firefox

    Returns
    -------
    driver : selenium.webdriver.firefox.webdriver.WebDriver

    '''
    print("Trying to install a driver for Firefox. Please wait...")
    
    opts = webdriver.FirefoxOptions()
    opts.headless = True
    
    service = FirefoxService(GeckoDriverManager().install())
    driver = webdriver.Firefox(service = service, options=opts)
    return driver

@get_WebDriver
def get_EdgeDriver():
    '''
    Returns a selenium driver object for Edge

    Returns
    -------
    driver : selenium.webdriver.Edge.webdriver.WebDriver

    '''
    print("Trying to install a driver for Edge. Please wait...")
    
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
        
        # exit if the none of the browsers are found
        try:
            assert driver != None
        except AssertionError:
            error_msg = ". ".join(["This program requires Chrome, Edge or Firefox to run",
                             "Please ensure that at least one of these browsers is installed."])
            print('Fail! Code: SessionNotCreatedException, Message: ' + error_msg)
            sys.exit()
        
        # scrap the webpage
        try:
            data_dict = func(driver, *args, **kwargs)
        except NoSuchElementException:
            # returns None if the scraping failed
            data_dict = None
        
        driver.quit() # end The WebDriver session
        return data_dict     
    return wrapper_parse_url               

@parse_url
def get_table_data(driver, limit = None):
    '''
    A function to parse the 'Medecines advice' webpage to retrieve medication IDs,\
    names and links to the medication webpage from the 'Published' table.

    Parameters
    ----------
    driver : selenium webdriver object, Optional
        generated automatically.
    limit : int, Optional
        the number of rows to retrieve from Published table.

    Returns
    -------
    data_dict : dict
        A JSON like dictionnary with lists of medication IDs, names and links.

    '''
    print('Collecting data from ' + url)
    
    driver.get(url) # send the GET request
    
    # exit if the page for "Medicines advice" is not rtrieved
    try:
        assert driver.title == "Medicines advice"
    except AssertionError as e:
        error_msg = "Unable to rertieve data from "+ url + ". Try later!"
        print('Fail! Code: {}, Message: {}'.format(type(e).__name__, error_msg))
        sys.exit()
        
    # close cookies popup
    wait(driver, 10).until(EC.element_to_be_clickable((By.ID, "ccc-dismiss-button"))).click()
    
    # get the number of pages i.e. the number of times to click on the button load more
    totalPages = driver.find_element(By.ID, "max-page-0").get_attribute("value")
    
    # click the button "load more" to the rows in the table
    rows_count = 20 # the table has 20 rows initially
    for i in range(int(totalPages) - 1):
        # stop clicking the button 'Load more' if the desired number of rows is attained
        if (limit != None) & (rows_count >= limit): break
        wait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btn-more-0"]'))).click()
        time.sleep(3)
        # increase the rows count by 20 after each click
        rows_count += 20
    
    # get IDs, names and links to medicine webpage in a JSON like dictionnary
    # get the table Published
    table_published = driver.find_element(By.CLASS_NAME, "tabs__content").find_element(By.TAG_NAME, "table")
    
    data_dict = {
        "IDs": [ID_element.text.strip() for ID_element in table_published.\
                find_elements(By.CLASS_NAME, "medicine-advice-table__id-row")],
        "Names": [medecine_element.find_element(By.CLASS_NAME, "medicine-advice-table__link").text.strip() 
                  for medecine_element in table_published.\
                      find_elements(By.CLASS_NAME, "medicine-advice-table__medicine-row")],
        "Links": [link_element.find_element(By.TAG_NAME, 'a').get_attribute("href") \
                  for link_element in table_published.find_elements(By.CLASS_NAME, "medicine-advice-table__link-row")]
        }
    
    return data_dict
     
def get_file_link(file_id, file_name, file_url):
    """
    Scrap the webpage for a given medicine and return the detailed advice pdf link.
    Return None for failure

    Parameters
    ----------
    file_id : str
        medicine SMC ID.
    file_name : str
        medicine name.
    file_url : str
        medicine webpage.

    Returns
    -------
    dict
        a dictionnary with the medicine ID, name and pdf downloading link.

    """
    
    try:
        response = requests.get(file_url) # send the GET request
        soup = BeautifulSoup(response.content, 'html.parser') # soup object
        
        # for inaccessible or erroneous web page
        success_conditions = (response.status_code == requests.codes.ok) &\
                            (soup.title.string.strip() == file_name)                      
        if not success_conditions: return None
        
        # get the link the detailed advice pdf file and ignore public summary file if exist
        base_url = re.findall('(^https.*)/medicines', url)[0]
        pdf_link = base_url + soup.find('a', {'href': re.compile('.*for-website\.pdf.*')}).get('href')
        
        return {"ID": file_id, "Name": file_name, "File link": pdf_link}
        
    except:
        return None


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
    # join the path and the folder name
    final_path = str(os.path.join(path, name))
    # if the folder does not exist create it
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
        print("Download path is set to ->", medicines_folder_path)
    
    elif not os.path.exists(path): # if the given path is wrong
        print(f"The entered path: {path} is not valid!")
        print("Download path is set to -> ", medicines_folder_path)
        
    else:
        medicines_folder_path = folder_path(path, "Medicines advice")
     
    time.sleep(2)
    return medicines_folder_path

def dwn_pdf_file(ID, name, pdf_link, dwn_path):
    """
    Download the detailed advice pdf file. Return None on successful download.

    Parameters
    ----------
    ID : str
        The medicine SMC ID.
    name : str
        The medicine name.
    pdf_link : str
        The pdf file link.
    dwn_path : str
        The directory path to store the file.

    Returns
    -------
    ID : str
        The medicine SMC ID.
    name : str
        The medicine name.
    message: str
        error message.

    """
    try:
        res = requests.get(pdf_link) # send GET request for the pdf file link
    
        # check status code
        if res.status_code != requests.codes.ok: return (ID, name, "Inaccessible link for pdf file")
        # set downloading path
        dwn_path = str(os.path.join(dwn_path, pdf_link.split('/')[-1]))
        
        with open(dwn_path, mode = 'wb') as fh:
            fh.write(res.content)
        
        return None
    except:
        return (ID, name, "Incorrect link for pdf file")
    
def dwn_process(data_dict, limit = None, path = None):
    """
    Download detailed advice pdf files from drug web pages in a default path if not provided.
    Files not retrieved and number of successful downloads will be returned.

    Parameters
    ----------
    data_dict : dict
        A dictionnary of medicines IDs, names and web pages links.
    limit : int, optional
        the number of files to download. The default is None.
    path : str, optional
        The path for downloading directory. If None a default path will be used.

    Returns
    -------
    unretrieved_list : list
        Contains ID, name and short message tuples for undownloaded files.
    counter : int
        Number of successful downloads.
    downloads_path : str
        Location for downloaded files.

    """
    # set the directory for downloading
    downloads_path = get_downloading_path(path)
    # get the medicines data
    IDs_list, names_list, links_list = data_dict['IDs'], data_dict['Names'], data_dict['Links']
    
    unretrieved_list = [] # for unretrieved files
    counter = 0 # count the number of files succefully downloaded
    print('Downloading files...')
    for ID, name, link in zip(IDs_list, names_list, links_list):
        # get the link to the detailed advice pdf file
        med_data = get_file_link(file_id = ID, file_name = name, file_url = link)
        
        # if there is no link to the pdf file
        if med_data == None:
            unretrieved_list.append((ID, name, "Inaccessible or incorrect web page"))
            continue
            
        pdf_link = med_data['File link'] # the pdf link
        # download the file
        dwn_result = dwn_pdf_file(ID, name, pdf_link, downloads_path)
        # store the ID and name for undowloaded file
        if dwn_result != None: unretrieved_list.append(dwn_result)
           
        counter += 1
        if counter == limit: break # if the limit is reached
    
    return (unretrieved_list, counter, downloads_path)

def fetch_call(func):
    @functools.wraps(func)
    def wrapper_fetch_call(*args, **kwargs):
        # print the function signature
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        print(f"Calling {func.__name__}({signature})")
        
        # get the fetching result
        fetch_result =  func(*args, **kwargs)
        
        # quit if data retrieving failed
        if fetch_result == None:
            error_msg = ". ".join(["Unable to retrieve data from " + url,
                            "The website may not be found or its design has changed!"])
            print('Fail! Message: ' + error_msg)
            sys.exit()
        else:
            unretrieved_list, counter, downloads_path = fetch_result
            # print final message
            print(". ".join([f'The process ends with {counter} files downloaded successfully', 
                      f'Please see the following path for the results: {downloads_path}']))
            if unretrieved_list:
                print('Failed to retrieve data for the following:')
                for ID, name, message in unretrieved_list: print(ID, name, message)
    
    return wrapper_fetch_call
