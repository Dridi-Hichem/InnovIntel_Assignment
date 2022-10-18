# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 18:30:38 2022

@author: Hichem Dridi
"""
import ScrapingFunctions as sf

class MedAdvScraper():
    """
    Web scraping class for website https://www.scottishmedicines.org.uk/medicines-advice/
    Scans the published table for drug IDs, names, and web page link.
    The webpage link is then parsed to download the detailed advice pdf file.
    """
    
    def __init__(self, limit = None, path = None):
        self.__limit = limit
        self.__path = path
        
    def __repr__(self):
        return "MedicinesAdviceScraper"
        
    @property
    def limit(self):
        return self.__limit
    
    @limit.setter
    def limit(self, limit):
        self.__limit = limit
        
    @property
    def path(self):
        return self.__path
    
    @path.setter
    def path(self, path):
        self.__path = path
        
    @sf.fetch_call
    def fetch_all(self, limit = None, path = None):
        """
        Download all detailed advice pdf files. If a limit is provided, 
        the first n files will be downloaded instead.

        Parameters
        ----------
        limit : int, optional
            The number of the first n files to download. The default is None.
        path : str, optional
            The path for downloading directory. If None a default path will be used.

        Returns
        -------
        fetch_result : Tuple or None
            A tuple with the list of unretrieved files details, the downloaded files count\
                 and the path for the results directory. None if parsing method failed.

        """
        if limit == None: limit = self.__limit
        if path == None: path = self.__path
        
        # get the data from table Published
        data_dict = sf.get_table_data(limit = limit)
        
        # if the scraping method failed
        if data_dict == None: fetch_result = None
        else: fetch_result = sf.dwn_process(data_dict, limit, path)
                
        return fetch_result