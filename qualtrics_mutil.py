#! /usr/bin/env python

import yaml
import argparse
from qualtrics_util import QualtricsDist
import os
import requests
from pprint import pprint

# Setting user Parameters
from dotenv import dotenv_values
import random

from requests.packages.urllib3.exceptions import InsecureRequestWarning



__version_info__ = ('0', '5', '0')
__version__ = '.'.join(__version_info__)


class StudySteps(QualtricsDist):
    
    def __init__(self):
        pass
    
    def initialize(self, config_file='', env_file = 'qualtrics_token', **kwargs):


        # read in the API_TOKEN from the .env file
        if os.path.exists(env_file):
            envconfig = dotenv_values(env_file)
            
            self.apiToken = envconfig.get('QUALTRICS_APITOKEN',None)
            if self.apiToken is None:
                print(f"Error: QUALTRICS_APITOKEN not found in {env_file}")
                exit(1)
        else:
            print(f"Error: need the {env_file} to read QUALTRICS_APITOKEN")
            exit(1)

        if config_file == '':
            print("Error: need config file")
            exit(1)
        else:
            self.read_config(config_file)

        self.index = kwargs.get('index')
        self.verbose = kwargs.get('verbose')
        self.format = kwargs.get('format')
        self.dataCenter = self.cfg['account']['DATA_CENTER']
        self.verify = self.cfg['account'].get('VERIFY',True)
        self.sslwarning = self.cfg['account'].get('SSLWARNING',False)
        
        # turn off ssl warning
        if self.sslwarning == False:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        # account, library_id, mailing_list_name, category_name
       
        self.directoryId = self.cfg['account']['DEFAULT_DIRECTORY']
        self.mailingListId = self.cfg['project']['MAILING_LIST_ID']
        #self.surveyId = self.cfg['project']['SURVEY_ID']
        self.libraryId = self.cfg['project'].get('LIBRARY_ID')    
        self.timeZone = self.cfg['project'].get('TIMEZONE','America/Chicago') 
        self.minutesExpire = self.cfg['project'].get('ExpireMinutes', 60)
        
        self.loadSteps()
        
        # load the contact list
        self.contactList = self.get_contact_list()
        
        self.loadSteps()
        self.loadSurveys()
        
        pass
    
    def loadSurveys(self):
        # load surveys into a dictionary for each step
        
        self.SurveyData = {}
        
        for k,v in self.steps.items():
            
            self.surveyId = v['survey']
            data = self.export_surveys(waitTime=7.5, fileFormat='json', 
                                 returnFormat='ddict', keep=True)          
            self.SurveyData[k] = data
            
            pass
        pass
        
    def loadSteps(self):
        """
        Load the steps from the config file
        """
        # create the steps dictionary
        self.steps = self.cfg.get('steps')
        

    def workSteps(self):
        
        # work through the steps
        
        for step in self.steps:
            
            self.thisStep = self.steps[step]
            # go through each of the actions
            
            for item in self.thisStep['actions']:
                
                # if action:arg format
                if ':' in item:
                    action, arg = item.split(":", 1)
                    pass
                else:
                    action = item
                    arg = None
                match action:
                    case "load":
                        self.thisStep['ddict'] = self.loadAction(self.thisStep['survey'])
                        pass
                    case "filter":
                        ddict = self.thisStep['ddict']['responses']
                        # just use values
                        newDdict = [d['values'] for d in ddict] 
                        # make sure vars exist in dict
                        addDdict = self.addVars(newDdict)              
                        filter = self.thisStep['condition']
                        filtDdict = self.filterAction(addDdict,filter)
                        pass
                    case _:
                        print(f"No case match found")
                pass
            
            pass
    
    def addVars(self,ddict):
        """
        Add vars to a dict if it doesn't exist

        Args:
            ddict (_type_): _description_
        """
        
        for index in range(len(ddict)):
            for key,value in self.thisStep['addvars'].items():
                ddict[index][key] = ddict[index].get(key,value)
                pass
            
        return ddict
                
    def filterAction(self, ddict, filter):
        """
        Filter data using provided filter and return result
        
        https://sl.bing.net/jyGiS9UoGWq
        
        """            
        
        operation = f"[d for d in ddict {filter}]"
        newDict = eval(operation)
        return newDict

        pass
    
    def loadAction(self, surveyId):
        """
        Load the survey, be default uses the ['survey']

        Args:
            surveyd_id (_type_, optional): _description_. Defaults to None.
        """
        

        self.surveyId =  surveyId           
        df = self.export_surveys(waitTime=7.5, fileFormat='json', 
                                 returnFormat='ddict', keep=True)
        return df
    
# read the mconfig file
mconfig_file = "mconfig_covid.yaml"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=
        """
        Qualtrics utilty tool for working a project involving multiple steps.

        A configuration file defines each of the steps.

        Sends out to individual via SMS or email

        """
    )

    parser.add_argument("--config", type = str,
                     help="config file, default is mconfig_qualtrics.yaml",
                     default='mconfig_qualtrics.yaml'
                     ) 
    
    parser.add_argument("--cmd", type = str,
                     help="cmd - check, delete, list, slist, send, update, default: list",
                     default='check') 

    parser.add_argument("--token", type = str,
                        help="name of qualtrics token file - default qualtrics_token",
                        default="qualtrics_token")
    
    parser.add_argument("--verbose", type = int,
                        help="print diagnostic messages -  0 low, 3 high, default 1",
                        default=1)
    
    parser.add_argument("--index", type=int,
                        help="index number for operations like delete",
                        default=-1 )

    parser.add_argument("--step", type=str,
                        help="which step to operate on, default is  all",
                        default='all' )
    
    parser.add_argument('-V', '--version', action='version', version=f'%(prog)s {__version__}')
    
    args = parser.parse_args()
    

    

    qd = StudySteps()
    qd.initialize(
            config_file = args.config,
            verbose = args.verbose,
            index = args.index,
            env_file = args.token,
            mode = 'mconfig',
            step = args.step,
            
            )
    
    pass
    qd.workSteps()
    
    pass        