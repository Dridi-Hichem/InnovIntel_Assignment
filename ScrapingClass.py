# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 18:30:38 2022

@author: Hichem Dridi
"""
import ScrapingFunctions as sf
import sys

class MedAdvScraper():
    """
    Web scraping class for website https://www.scottishmedicines.org.uk/medicines-advice/
    Scans the published table for drug IDs, names, and web page link.
    The webpage link is then parsed to download the detailed advice pdf file.
    """
    
    def __init__(self, IDs_list = None, names_list = None, limit = None, path = None):
        self.__IDs_list = IDs_list
        self.__names_list = names_list
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
    def fetch_byIDs(self, IDs_list = None, path = None):
        """
        Download The detailed advice pdf files for the medicine Identifiers provided.

        Parameters
        ----------
        IDs_list : list
            A list of medicines SMC identifiers .
        path : str, optional
            The path for downloading directory. If None a default path will be used.

        Returns
        -------
        fetch_result : Tuple or None
            A tuple with the list of unretrieved files details, the downloaded files count\
                 and the path for the results directory. None if parsing method failed.

        """
        if IDs_list == None: IDs_list = self.__IDs_list
        
        # ensure that IDs_list is a of type list
        if not isinstance(IDs_list, list):
            raise TypeError(f"A list of IDs is required, got a {type(IDs_list)} instead!")
            sys.exit()
            
        # get the data from table Published
        data_dict = sf.get_table_data()
        
        # if the scraping method failed
        if data_dict == None: fetch_result = None
        else: 
            # limit the data dictionary to only medicines whose identifiers are provided in IDs_list
            new_data_dict = {
                "IDs": [ID for ID in data_dict['IDs'] if ID in IDs_list],
                "Names": [name for ID, name in zip(data_dict['IDs'], data_dict['Names']) if ID in IDs_list],
                "Links": [link for ID, link in zip(data_dict['IDs'], data_dict['Links']) if ID in IDs_list]
                }
            
            # flag bad IDs
            bad_IDs = list(set(IDs_list) - set(new_data_dict['IDs']))
            if bad_IDs:
                print("Bad or not found IDs:")
                print("\n".join(bad_IDs))
                
                
            fetch_result = sf.dwn_process(new_data_dict, path)
                
        return fetch_result
    
    @sf.fetch_call
    def fetch_byNames(self, names_list = None, path = None):
        """
        Download The detailed advice pdf files for the medicine Identifiers provided.

        Parameters
        ----------
        names_list : list
            A list of medicines names .
        path : str, optional
            The path for downloading directory. If None a default path will be used.

        Returns
        -------
        fetch_result : Tuple or None
            A tuple with the list of unretrieved files details, the downloaded files count\
                 and the path for the results directory. None if parsing method failed.

        """
        if names_list == None: names_list = self.__names_list
        
        # ensure that names_list is a of type list
        if not isinstance(names_list, list):
            raise TypeError(f"A list of namess is required, got a {type(names_list)} instead!")
            sys.exit()
            
        # get the data from table Published
        data_dict = sf.get_table_data()
        
        # if the scraping method failed
        if data_dict == None: fetch_result = None
        else: 
            # limit the data dictionary to only medicines whose names are provided in names_list
            new_data_dict = {
                "IDs": [ID for ID, name in zip(data_dict['IDs'], data_dict['Names']) if name in names_list],
                "Names": [name for name in data_dict['Names'] if name in names_list],
                "Links": [link for link, name in zip(data_dict['Links'], data_dict['Names']) if name in names_list]
                }
            
            # flag bad names
            bad_names = list(set(names_list) - set(new_data_dict['Names']))
            if bad_names:
                print("wrong or missing names:")
                print("\n".join(bad_names))
                
                
            fetch_result = sf.dwn_process(new_data_dict, path)
                
        return fetch_result
        
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