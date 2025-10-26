#! /usr/bin/env python

from datetime import datetime

from pprint import pprint
import argparse
import yaml
import requests
import json
from time import gmtime, strftime
from datetime import date, timezone
import datetime
import sys
import os
import pandas as pd
import random
import string
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import dateutil.parser
import zipfile
import json
import io, os
import sys
import time
import tempfile
import glob
import shutil
import textwrap


# Setting user Parameters
from dotenv import dotenv_values
import random

from requests.packages.urllib3.exceptions import InsecureRequestWarning



__version_info__ = ('2', '0', '9')
__version__ = '.'.join(__version_info__)
__version_history__ = \
"""
2.0.9 - fix bug to determine sms vs. email from config for calling
        either get_distribution_sms or get_distribution_email
2.0.8 - implemnted the delete_unset for email distributions
2.0.7 - fixed bug in conversion of StartDate to a datetime.date object by yaml, which
        prevented it from being converted to json again.
2.0.6 - cleaned up the email vs. sms selection, only need the following 
        embedded fields:
        
        ContactMethod
        SurveysScheduled
        StartDate
        NumDays
        TimeSlots
        TimeZone
        ExpireMinutes
        DeleteUnsent
        LogData

2.0.5  - enhance the help
2.0.4  - fixed bug contact['embeddedData'].get('UseSMS','0')
2.0.3  - added support for using timeZone in embeded data
2.0.2  - added random text to email message text to prevent duplicate message error
2.0.1  - First of version 2
0.8.23 - in check_send, check for numDays > 0
0.8.22 - for cmd slist, added surveys sent, start date and method
0.8.21 - increased number of characters in sms random text from 1 to 8 to reduce failure rate due to
        message text being identical. This increases number of possibilities from
        52 to 1977060966400
0.8.20 - fix bug in deleteUnsent when using --index
0.8.19 - fix when DeleteUnsent not in the embedded data, use get(); fix in logData for embedded Data; 
        check on timeSlots to skip iteration; removed contactLookupId from send_sms(), pass directly from send_multiple_sms
0.8.18 - changed fields used to ContactEmail, ContactSMS, ContactMethod=SMS
0.8.17 - change delete to check each contact for DeleteUnsent
0.8.16 - change verbose output
0.8.15 - ContactMethod uses string for sms, email(future), unknown
0.8.14 - added support for ContactMethod, Time1,Time2, etc. for covid ema study which uses
        workflows to update the contact list

"""


class VersionHistoryAction(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, nargs=0, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        print("Version History:",end='')
        print(__version_history__)
        parser.exit()

class QualtricsDist:

    """
    Class for handing qualtrics distributions

    """
    def __init__(self):
        pass

    def initialize(self, config_file='', env_file = 'qualtrics_token', **kwargs):


        # read in the API_TOKEN from the .env file
        if os.path.exists(env_file):
            envconfig = dotenv_values(env_file)
            
            self.apiToken = envconfig.get('QUALTRICS_APITOKEN',None)
            if self.apiToken is None:
                print(f"Error: QUALTRICS_APITOKEN not found in {env_file}")
                sys.exit('Exiting program')
        else:
            print(f"Error: need the {env_file} to read QUALTRICS_APITOKEN")
            sys.exit('Exiting program')

        if config_file == '':
            print("Error: need config file")
            sys.exit('Exiting program')
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
        self.surveyId = self.cfg['project']['SURVEY_ID']
        self.libraryId = self.cfg['account'].get('LIBRARY_ID')    
        self.messageId = self.cfg['project']['MESSAGE_ID']    
        self.messageIdEmail = self.cfg['project'].get('MESSAGE_ID_EMAIL','unknown')   
        self.timeZone = self.cfg['project'].get('TIMEZONE','America/Chicago') 
        self.minutesExpire = self.cfg['project'].get('MINUTES_EXP', 60)
        
        pass

    def work(self, cmd):
        """
        Do work based on cmd
        """
        
        if cmd == 'send':
            self.check_for_send(self.mailingListId)
            pass
        elif cmd == 'check':
            # check that ids are correct
            # check if we can get contactList
            
            print(f"Checking for mailingListId {self.mailingListId}...")
            try: 
                contactList = self.get_contact_list()
                if len(contactList) > 0: print(f"mailingListId {self.mailingListId} found")
            except Exception as e:
                print(f"{e}")


            # check the surveyId
            print(f"Checking for surveyId {self.surveyId}...")
            # is this for email or sms?
            if self.cfg['embedded_data'].get('ContactMethod','').lower() == 'sms' or \
                self.cfg['embedded_data'].get('UseSMS',0) == 1:
                distributions = self.get_distribution_sms(self.surveyId)
            else:
                # assume email
                distributions = self.get_distribution_email()
                
            if len(distributions) >= 0: print(f"surveyId {self.surveyId} found")

            # check messageId
            print(f"Checking for messageId {self.messageId}...")
            
            message = self.getLibraryMessage(self.libraryId, self.messageId)
            if len(message) >= 0: print(f"messageId {self.messageId} found")

            pass
        elif cmd == 'delete':
            self.delete_unsent(self.index)
        elif cmd == 'export':
            self.export_surveys(fileFormat=self.format)
        elif cmd == 'list':
            # update the EmbeddedData before list
            self.update_contact_list()

            contactList = self.get_contact_list()
            # print the list
            self.print_contact_list(contactList, format='long')
        elif cmd == 'slist':
            # short listing
            # update the EmbeddedData before list
            self.update_contact_list()
            contactList = self.get_contact_list()
            # print the list
            self.print_contact_list(contactList, format='short')
        elif cmd == 'update':
            # update the embeddedData in the contactList
            contactList = self.get_contact_list()
            for contact in contactList:
                self.update_embedded(contact['contactId'])
        else:
            print(f"Error: {cmd} is an unknown command")
            
    def read_config(self,config_file):
        "read in the yaml config file"
        try:
            # Try to find config file in multiple locations
            actual_path = self._find_config_file(config_file)
            if actual_path is None:
                raise FileNotFoundError(f"Config file not found: {config_file}")
            
            with open(actual_path, 'r') as fp:
            #try:
                file_lines = fp.readlines()
                fp.seek(0)  # Reset file pointer
                self.cfg = yaml.safe_load(fp)
                
                # Store file info for error reporting
                self._config_file_path = actual_path
                self._config_file_lines = file_lines
                
                # if StartDate is datetime.date, then convert to a string like 2025-03-03
                if isinstance(self.cfg['embedded_data']['StartDate'], date):
                    self.cfg['embedded_data']['StartDate'] = self.cfg['embedded_data']['StartDate'].strftime("%Y-%m-%d")
                
                # Validate timezones with file context
                self._validate_timezone(self.cfg.get('project', {}).get('TIMEZONE'), 'project:TIMEZONE', 'TIMEZONE')
                self._validate_timezone(self.cfg.get('embedded_data', {}).get('TimeZone'), 'embedded_data:TimeZone', 'TimeZone')
        except Exception as e:
            print(f"Error: {e}")
            sys.exit('Exiting program')
        pass
    
    def _validate_timezone(self, timezone_str, field_name, key_name):
        """
        Validate that a timezone string is a valid IANA timezone.
        
        Args:
            timezone_str: The timezone string to validate
            field_name: The field name for error reporting
            key_name: The key name to search for in the config file
        
        Raises:
            ValueError: If timezone is invalid
        """
        if timezone_str is None:
            return  # Skip validation if timezone is not specified
        
        try:
            # Try to create a ZoneInfo object with the timezone string
            ZoneInfo(timezone_str)
        except (ValueError, Exception) as e:
            # Find the line number in the config file
            line_num = self._find_line_number(key_name)
            file_info = f" in {self._config_file_path}" if hasattr(self, '_config_file_path') else ""
            line_info = f" on line {line_num}" if line_num > 0 else ""
            
            # Catch both ValueError and ZoneInfoNotFoundError
            raise ValueError(
                f"Invalid timezone '{timezone_str}' in {field_name}{line_info}{file_info}. "
                f"It must be a valid IANA timezone name (e.g., 'America/New_York', 'Europe/London'). "
                f"Error: {e}"
            )
    
    def _find_line_number(self, key_name):
        """Find the line number of a key in the config file."""
        if not hasattr(self, '_config_file_lines'):
            return 0
        
        for i, line in enumerate(self._config_file_lines, start=1):
            if key_name in line:
                return i
        return 0
    
    def _find_config_file(self, config_file):
        """Find config file in multiple locations for backward compatibility."""
        # Check if it's an absolute path
        if os.path.isabs(config_file) or '/' in config_file:
            if os.path.exists(config_file):
                return config_file
        
        # Try current directory
        if os.path.exists(config_file):
            return config_file
        
        # Try config/ directory
        config_in_config_dir = os.path.join('config', config_file)
        if os.path.exists(config_in_config_dir):
            return config_in_config_dir
        
        # Try config/ directory with just filename
        filename = os.path.basename(config_file)
        config_in_config_dir = os.path.join('config', filename)
        if os.path.exists(config_in_config_dir):
            return config_in_config_dir
        
        return None

    def print_contact_list(self, contactList, format='long'):
        """
        Print the contact list
        """
        index = 1
        if contactList is not None:
            for contact in contactList:

                if format == 'long':
                    print("======================")
                    print(f"contact index: {index} {contact['lastName']},{contact['firstName']}")
                    print("======================")
                    pprint(contact)
                    index += 1
                else:
                    print("index:{}\tNumSched:{}\tMethod:{}\tDate:{} name:{},{} {} email:{} phone:{} extRef:{}  ".format(
                            index,
                            contact['embeddedData'].get('SurveysScheduled',0),
                            contact['embeddedData'].get('ContactMethod',"contact unknown"),                            
                            contact['embeddedData'].get('StartDate',"None"),
                            contact['lastName'],
                            contact['firstName'],
                            contact['contactId'],
                            contact['email'],
                            contact['phone'],
                            contact['extRef'],
                        )
                    )
                    # print("index:{}\tname:{},{}\t{}\temail:{}\tphone:{}\textRef:{}".format(
                    #         index,
                    #         contact['lastName'],
                    #         contact['firstName'],
                    #         contact['contactId'],
                    #         contact['email'],
                    #         contact['phone'],
                    #         contact['extRef'],
                    #         contact['embeddedData']['StartDate'],
                    #         contact['embeddedData']['SurveysScheduled'],
                    #         contact['embeddedData'].get('ContactMethod',"contact unknown")
                    #     )
                    
                    index += 1

    def export_surveys(self, waitTime=7.5, fileFormat='json', 
                       returnFormat = 'df', keep=True):
        """
        export surveys to a file and also return a df
    
        https://api.qualtrics.com/u9e5lh4172v0v-survey-response-export-guide
        
        """

# Setting user Parameters



        apiToken = self.apiToken
        surveyId = self.surveyId
        dataCenter = self.dataCenter

        # Setting static parameters
        requestCheckProgress = 0.0
        progressStatus = "inProgress"
        url = "https://{0}.qualtrics.com/API/v3/surveys/{1}/export-responses/".format(dataCenter, surveyId)
        headers = {
            "content-type": "application/json",
            "x-api-token": apiToken,
            }

        # Step 1: Creating Data Export
        data = {
                "format": fileFormat,
                #"seenUnansweredRecode": 2
            }

        downloadRequestResponse = requests.request("POST", url, json=data, headers=headers,verify=self.verify)
        # print(downloadRequestResponse.json())

        try:
            progressId = downloadRequestResponse.json()["result"]["progressId"]
        except KeyError:
            print(downloadRequestResponse.json())
            sys.exit(2)
            
        isFile = None

        max_retries = 5
        retry_count = 0

        # Step 2: Checking on Data Export Progress and waiting until export is ready
        while progressStatus != "complete" and progressStatus != "failed" and isFile is None:
            if isFile is None:
                print("File not ready")
            else:
                print("ProgressStatus=", progressStatus)
            
            requestCheckUrl = url + progressId
            requestCheckResponse = requests.request("GET", requestCheckUrl, headers=headers,verify=self.verify)
            
            try:
                isFile = requestCheckResponse.json()["result"]["fileId"]
            except KeyError:
                1==1

            #print(requestCheckResponse.json())
            requestCheckProgress = requestCheckResponse.json()["result"]["percentComplete"]
            print("Download is " + str(requestCheckProgress) + " complete")
            progressStatus = requestCheckResponse.json()["result"]["status"]

            if progressStatus not in ["complete", "failed"]:
                # Implement exponential backoff with a maximum number of retries
                retry_count += 1
                if retry_count > max_retries:
                    print("Exceeded maximum retries. Exiting.")
                    sys.exit('Exiting program')
                
                # Calculate the next sleep interval using exponential backoff (The first retry will occur after 200 seconds, the second after 400 seconds, the third after 600 seconds, and so on, until the max_retries limit is reached)
                sleep_interval = waitTime * ( 2 ** (retry_count-1))
                print(f"Retrying in {sleep_interval} seconds...")
                time.sleep(sleep_interval)

        # Step 3: Downloading file
        requestDownloadUrl = url + isFile + '/file'
        requestDownload = requests.request("GET", requestDownloadUrl, headers=headers, stream=True,verify=self.verify)

        # Step 4: Unzipping the file
        # create temp_dir
        with tempfile.TemporaryDirectory() as temp_dir:

            zipfile.ZipFile(io.BytesIO(requestDownload.content)).extractall(temp_dir)
            # get the expected single file
            tmpPath = glob.glob(os.path.join(temp_dir, f"*{fileFormat}"))[0]
            baseName = os.path.basename(tmpPath)
            # clean up baseName
            cleanBaseName = baseName.replace(" ","_").replace(":","")
            localDir = os.getcwd()
            newPath = os.path.join(localDir, cleanBaseName)
            
            if fileFormat == 'csv':
                # copy the file
                shutil.copy(tmpPath, newPath)
                # skip the 0 index rows 1 and 2
                df = pd.read_csv(tmpPath, skiprows=[ 1, 2])
                pass
            elif fileFormat == 'json':
                # make copy of the json file with indent output
                with open(tmpPath) as fp:
                    ddict = json.load(fp)
                # add source key
                ddict['source'] = 'qualtrics'
                # write out file with indent
                with open(newPath,'w') as fp:
                    json.dump(ddict, fp, indent=4)
                # read into df
                df = pd.DataFrame(ddict['responses'])
                pass
            
            print(f'Complete: data written to {newPath}') 
            
        if returnFormat =='df':   
            return df
        else:
            return ddict
        
        
    def get_contact_list(self, embedded = True):
        """Returns mailing list's contact list """
    
        baseUrl = "https://{0}.qualtrics.com/API/v3/directories/{1}/mailinglists/{2}/contacts".format(
              self.dataCenter, 
              self.directoryId, 
              self.mailingListId)
        
        if embedded == True:
            baseUrl = baseUrl + "?includeEmbedded=true"

        headers = {
            "x-api-token": self.apiToken,
        }

        try:
            response = requests.get(baseUrl, headers=headers, verify=self.verify)
            response.raise_for_status()
        except Exception as e:
            print(f"Error contact_list: {e}")
            d = None
            sys.exit('Exiting program')
        else:
            d = json.loads(response.text)['result']['elements']
            self.contactList = d
        return d

    def get_distribution_email(self, sendStartDate=None, distributionRequestType='Invite'):
        """
        
        https://yul1.qualtrics.com/API/v3/distributions

          --url 'https://yul1.qualtrics.com/API/v3/distributions?mailingListId=CG_2XpNxso87o1O548&surveyId=SV_8eMxLSXymY6lW6y&distributionRequestType=Invite&useNewPaginationScheme=true' \

        """

        if self.verbose > 0:
            print("Getting distribution...", end="")

        baseUrl = "https://{0}.qualtrics.com/API/v3/distributions/?mailingListId={1}&surveyId={2}&distributionRequestType={3}&useNewPaginationScheme=true".format(
              self.dataCenter, 
              self.mailingListId,
              self.surveyId,
              distributionRequestType,
        )
        
        if sendStartDate is not None:
            # add start date argument
            baseurl = baseUrl + f"&sendStartDate={sendStartDate}"

        headers = {
            "x-api-token": self.apiToken,
            "Content-Type": "application/json"
        }

        # TODO try
        response = requests.get(baseUrl, headers=headers, verify=self.verify)
    
        dataElements = []  

        d = json.loads(response.text)

        status = d['meta']['httpStatus']
        nextPage = 'OK'  # initialize to something not null

        # loop over multiple pages if needed
        while '200' in status:
            # get the data and append to dataElements
            dataElements = dataElements + d['result']['elements']

            if d['result']['nextPage'] is not None:
                # more pages so get next page
                response = requests.get(d['result']['nextPage'], headers=headers,verify=self.verify)
                d = json.loads(response.text)
                status = d['meta']['httpStatus']
            else:
                # no more pages so can break out of while
                break

        if self.verbose > 0:
            print(f"Done {len(dataElements)} retrieved")
            
        return dataElements

    def get_distribution_sms(self, surveyId):
        """
        Get sms distributions for a surveyId


        https://yul1.qualtrics.com/API/v3/distributions/sms

        https://api.qualtrics.com/2c09bb20f50cc-list-sms-distribution


        """

        if self.verbose > 0:
            print("Getting sms distribution...", end="")

        baseUrl = "https://{0}.qualtrics.com/API/v3/distributions/sms?surveyId={1}".format(
              self.dataCenter, 
              self.surveyId,
        )
        
        headers = {
            "x-api-token": self.apiToken,
            "Content-Type": "application/json"
        }

        # try
        response = requests.get(baseUrl, headers=headers,verify=self.verify)
    
        dataElements = []  

        d = json.loads(response.text)

        status = d['meta']['httpStatus']
        nextPage = 'OK'  # initialize to something not null

        # loop over multiple pages if needed
        while '200' in status:
            # get the data and append to dataElements
            dataElements = dataElements + d['result']['elements']

            if d['result']['nextPage'] is not None:
                # more pages so get next page
                response = requests.get(d['result']['nextPage'], headers=headers,verify=self.verify)
                d = json.loads(response.text)
                status = d['meta']['httpStatus']
            else:
                # no more pages so can break out of while
                break

        if self.verbose > 0:
            print(f"Done {len(dataElements)} retrieved")
            
        return dataElements

    def delete_unsent(self, index):
        """
        Delete unsent distributions
        """

        if index < 0:
            contacts = self.get_contact_list()
        else:
            # get the contact information for the index
            contacts = self.get_contact_list()
            # reduce list down to one based on index
            contacts = [ contacts[index-1]]
            
        for contact in contacts:
            
            if contact['embeddedData'].get('DeleteUnsent','0') =='1':
                # get the contactLookupId
                contactLookupId = self.getContactLookupId( self.mailingListId, contact['contactId'])
                # check if sms or email
                if (contact['embeddedData'].get('UseSMS','0')=='1') or (contact['embeddedData'].get('ContactMethod','SMS').upper()=='SMS'):
                    # sms
                    distributions = self.get_distribution_sms(self.surveyId)
                    # bring contactId to top level of hierarchy
                    for i in range(len(distributions)):
                        distributions[i]['contactLookupId'] = distributions[i]['recipients']['contactId']

                    dt_now = datetime.now()
                    # convert to UTC
                    dt_now_utc = dt_now.astimezone(timezone.utc)
                    dt_now_str = dt_now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
                    df = pd.DataFrame(distributions)
                    # filter for contactLookupId and sendDate
                    df.query(f"contactLookupId == '{contactLookupId}'", inplace=True)
                    df.query(f"sendDate > '{dt_now_str}'", inplace=True)

                    if self.verbose >= 1: print(f"Found {len(df)} unsent messages for {contact['lastName']}")
                    
                    if len(df) > 0:
                        # iterate over rows
                        count = 1
                        for index, row in df.iterrows():
                            if self.verbose >= 1: print(f"Deleting {count} of {len(df)}...", end="")
                            # delete a single distribution
                            res = self.delete_sms_distribution(row.id, self.surveyId)
                            count+=1
                    # update the contact embedded data
                    # comment this out because of of limits on embedded data size
                    # TODO just save most recent with datetime
                    # response = self.update_embedded(contact['contactId'], updateFields={"LogData": {"action":"delete_unsent"}})
                    # update the contact list for DeleteUnsent to 0
                    response = self.update_embedded(contact['contactId'], {"DeleteUnsent": 0})
                    pass
                else:
                    # email
                    # get all the distributions for this survey
                    distributions = self.get_distribution_email()
                    # bring contactId to top level of hierarchy
                    for i in range(len(distributions)):
                        distributions[i]['contactLookupId'] = distributions[i]['recipients']['contactId']

                    dt_now = datetime.now()
                    # convert to UTC
                    dt_now_utc = dt_now.astimezone(timezone.utc)
                    dt_now_str = dt_now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
                    df = pd.DataFrame(distributions)
                    # filter for contactLookupId and sendDate
                    df.query(f"contactLookupId == '{contactLookupId}'", inplace=True)
                    df.query(f"sendDate > '{dt_now_str}'", inplace=True)

                    if self.verbose >= 1: print(f"Found {len(df)} unsent messages for {contact['lastName']}")
                    
                    if len(df) > 0:
                        # iterate over rows
                        count = 1
                        for index, row in df.iterrows():
                            if self.verbose >= 1: print(f"Deleting {count} of {len(df)}...", end="")
                            # delete a single distribution
                            res = self.delete_email_distribution(row.id)
                            count+=1
                    # update the contact list
                    response = self.update_embedded(contact['contactId'], updateFields={"LogData": {"action":"delete_unsent"}})
                    # update the contact list for DeleteUnsent to 0
                    response = self.update_embedded(contact['contactId'], {"DeleteUnsent": 0})
                                      
                    pass
                pass
            pass


    def delete_sms_distribution(self, smsDistributionId, surveyId):
        """
        Delete an sms distribution

        https://api.qualtrics.com/e0bbc91f396f4-delete-sms-distribution

        https://yul1.qualtrics.com/API/v3/distributions/sms/{smsDistributionId}
        
        """
        if self.verbose > 0:
            print(f"Deleting sms distribution {smsDistributionId}...", end="")

        baseUrl = "https://{0}.qualtrics.com/API/v3/distributions/sms/{1}?surveyId={2}".format(
              self.dataCenter, 
              smsDistributionId,
              surveyId
            )
        
        
        headers = {
            "x-api-token": self.apiToken,
            "Content-Type": "application/json"
        }

        # try
        response = requests.delete(baseUrl, headers=headers,verify=self.verify)

        d = json.loads(response.text)

        status = d['meta']['httpStatus']
        nextPage = 'OK'  # initialize to something not null

        if self.verbose > 0:
            if '200' in status:
                if self.verbose>0: print(f"Success")
                return True
            else:
                if self.verbose>0: print(f"Failed")
                return False
            
    def delete_email_distribution(self, distributionId):
        """
        Delete an email distribution

        https://api.qualtrics.com/b76130e1af452-delete-distribution

        https://yul1.qualtrics.com/API/v3/distributions/{distributionId}
        
        """
        if self.verbose > 1:
            print(f"Deleting email distribution {distributionId}...", end="")

        baseUrl = "https://{0}.qualtrics.com/API/v3/distributions/{1}".format(
              self.dataCenter, 
              distributionId
            )
        
        
        headers = {
            "x-api-token": self.apiToken,
            "Content-Type": "application/json"
        }

        # try
        response = requests.delete(baseUrl, headers=headers,verify=self.verify)

        d = json.loads(response.text)

        status = d['meta']['httpStatus']
        nextPage = 'OK'  # initialize to something not null

        if self.verbose > 0:
            if '200' in status:
                if self.verbose>0: print(f"Success")
                return True
            else:
                if self.verbose>0: print(f"Failed")
                return False
            

    def reorg_distribution_list(self, dataElements):
        """
        reorganize the distribution list so that the stats section is
        at the top level so that vars such as sent can be queried in the
        dataframe
        """
        df = pd.DataFrame(dataElements)

        # loop through each row creating new column sent
        sent = []
        contactLookupId = []
        for item in dataElements:
            sent.append(item['stats']['sent'])
            contactLookupId.append(item['recipients']['contactId'])

        # add to dataframe
        df['sent'] = sent
        df['contactLookupId'] = contactLookupId
        
        return df
    

    def print_contact_list_(self,):

        index = 0
        for contact in self.contactList:
            print("======================")
            print(f"contactnum: {index}")
            print("======================")
            pprint(contact)
            index += 1

    def update_contact_list(self):
        """
        Update the contact list with the embedded fields
        """

        # update the EmbeddedData
        contactList = self.get_contact_list()
        if contactList is not None:
            for contact in contactList:
                self.update_embedded(contact['contactId'])

    def embedded_flat2nested(self, embData:dict, sep='__')-> dict:
        """
        take embedded data with label__start: 0 and
        convert it into a nested dictionary
        data[label]['start'] = 0

        Can handle just one level data[label]['start]
        not label__label2__start
        data[label][label2]['start']
        
        Args:
            emData (_type_): _description_
        """
        
        newDict = {}  # hold converts
        
        for key, value in embData.items():
            if sep in key:
                # make it nested
                key1 = key.split(sep)[0]
                key2 = key.split(sep)[1]
                # check if key1 exists
                if key1 in newDict.keys():
                    if type(newDict[key1]) == dict:
                        newDict[key1][key2] = value
                    else:
                        # error
                        if self.verbose: print(f"Error in nested embedded data {key}")
                        exit(2)
                else:
                    # create a new dict
                    newDict[key1] = {}
                    newDict[key1][key2] = value
            else:
                # not nested key
                newDict[key] = value
                
        
        testDict = self.embedded_nested2flat(newDict)
        return newDict   

    def embedded_nested2flat(self, embData:dict, sep='__')-> dict:
        """
        take embedded data in nested format
        and convert to flat.
        
        So data['label']['start'] = 0
        becomes label__start: 0 

        Can handle just one level data[label], not
        data[label][label2]
        
        Args:
            emData (_type_): _description_
        """
        
        newDict = {}  # hold converts
        
        for key, value in embData.items():
            if type(value) == dict:
                # this is a dict
                # unpack the dict to flat
                # get the keys in the value dict
                for key1, value1 in value.items():
                    # create new key
                    nestedKey = f"{key}__{key1}"
                    newDict[nestedKey] = value1
            else:
                # not nested 
                newDict[key]=value
                
        return newDict    
                    
    def update_contact(self, index, **kwargs):
        """ 
        
        update the specified contact by index 

        individual elements can be added or changed
        
        https://api.qualtrics.com/d98216303e054-update-contact-in-mailing-list

        https://api.qualtrics.com/80eaf8928a31f-managing-contacts-in-mailing-lists-for-xm-directory#update-contact-in-mailing-list
        
        """
    
        baseUrl = "https://{0}.qualtrics.com/API/v3/directories/{1}/mailinglists/{2}/contacts/{3}".format(
            self.dataCenter, 
            self.directoryId, 
            self.mailingListId,
            self.contactList[index]['contactId'] #contactId
        )
        headers = {
            "x-api-token": self.apiToken,
            "Content-Type": "application/json"
        }

        # get the original data
        # data = self.contactList[index]
        data = {}

        # remove ContactId key if it exists, need to remove this to avoid error
        if data.get('contactId') is not None:
            del data['contactId']
        
        # use the kwargs 
        # if begins with edata__ then belongs in embedded data
        for key, value in kwargs.items():
            if self.verbose == 3: print("%s == %s" % (key, value))
            if 'edata__' in key:
                # create the key
                data['embeddedData'] = {}
                # add or replace field in embeddedData
                newKey = key.split('edata__')[1] # extract the newKey
                data['embeddedData'][newKey] = value
            else:
                data[key] = value

        response = requests.put(baseUrl, json=data, headers=headers)

        d = json.loads(response.text)

        status = d['meta']['httpStatus']

        return status, response


    def update_embedded(self, contactId, updateFields={}):
        """ 
        
        updateFields is a dictionary of items in the embeddedData that you want to change.
        
        To add an entry to LogData
        {"LogData":{"action":"update"}}
        
        To change another entry such as SendStatus and NumDays
        {"SendStatus": 8, "NumDays": 10}
        
        Initialize and update standard embeddedData elements needed for supporting distribution
        
        https://api.qualtrics.com/d98216303e054-update-contact-in-mailing-list

        https://api.qualtrics.com/80eaf8928a31f-managing-contacts-in-mailing-lists-for-xm-directory#update-contact-in-mailing-list
        
        20240416 - erratic bug observed, with embeddedData
        

        """
    
    
        # lookup the contact using the contactId and get the data
        for item in self.contactList:
            if item['contactId'] == contactId:
                data = item.copy()
        
        baseUrl = "https://{0}.qualtrics.com/API/v3/directories/{1}/mailinglists/{2}/contacts/{3}".format(
            self.dataCenter, 
            self.directoryId, 
            self.mailingListId,
            contactId, # self.contactList[index]['contactId'] #contactId
        )
        headers = {
            "x-api-token": self.apiToken,
            "Content-Type": "application/json"
        }

        # read default values from config file
        embeddedFields = self.cfg['embedded_data']
        # update the values
        for key, value in updateFields.items():
            embeddedFields[key] = value

        # remove ContactId key, need to remove this to avoid error
        del data['contactId']

        # set language to en if None then set to en
        if data['language'] is None:
            data['language'] = "en"
        
        if self.verbose > 2: print(f"*** {data['lastName']} {data['firstName']}")    
        # check if entry embeddedData exists so don't erase existing data
        for key, value in embeddedFields.items():
            
            if key not in data['embeddedData']:
                # key is not in current embeddedData so initialize
                # check if it is a dictionary, then convert to json
                if type(value) == dict:
                    data['embeddedData'][key] = json.dumps(value)
                else:
                    data['embeddedData'][key] = value
            else:
                # field exists so update it if it is in updatedFields
                if key in updateFields:
                    
                    if key == 'LogData':
                        
                        # convert original json data into dict
                        origLogData = json.loads(data['embeddedData'][key])
                        # check if a dict, then convert to a list
                        if type(origLogData) == dict:
                            LogData = list()
                            LogData.append(origLogData)
                        else:
                            LogData = origLogData
                            
                        # then a list of json, so read in and append the new data
                        # logList = json.loads(updateFields[key])
                        # append new data to origLogData
                        LogData.append(updateFields[key])
                        # convert back to json to store in embeddedData
                        data['embeddedData'][key] = json.dumps(LogData)
                        pass
                    #elif 
                    else:
                        data['embeddedData'][key] = updateFields[key]
                
            if self.verbose > 2: print("%s: %s" % (key, value))
            pass

            # test nested emb data
            newDict = self.embedded_flat2nested(data['embeddedData'])  
            pass
              
        response = requests.put(baseUrl, json=data, headers=headers,verify=self.verify)

        d = json.loads(response.text)

        status = d['meta']['httpStatus']
        if '200' not in status:
            print(f"Error: {d['meta']['error']['errorMessage']}")
        return status, response

    def initialize_all_embedded(self):
        """
        Initialize the embedded fields for all the contacts in the contact list

        """
        index = 0
        for contact in self.contactList:
            # check if embeddedData is empty
            # if not contact['embeddedData']:
            self.update_embedded(index)
            index += 1
            pass



    def getContactLookupId(self, mailingListId, contactId):
        """
        gets the ContactLookupId for a specific contactId in a mailingListId
        
        The ContactLookupId begins with "CGC_" and is a required parameter when
        sending out a distribution from  a mailing list to an  individual.
        
        
        API/v3/directories/{directoryId}/mailinglists/{mailingListId}/contacts/{contactId}
 
        """
        
        """
        # this call resulted in an error (20240328)
        
        Error: getContactLookupId 404
        (b'{"meta":{"requestId":"b6212545-7444-4861-9a92-e05649f886af","httpStatus":"40'
        b'4 - Not Found","error":{"errorCode":"GET_CONTACT_FROM_LIST_NOT_FOUND","error'
        b'Message":"The request to get the contact(CID_cI256zBhPiwJkeq) from mailing-l'
        b'ist(CG_3NxJ3cmg6jRvqUd) in directory(POOL_3fAZGWRVfLKuxe3) was unable to fin'
        b'd the mailing list or directory."}}}')
 
        baseUrl = "https://{0}.qualtrics.com/API/v3/directories/{1}/mailinglists/{2}/contacts/{3}"\
            .format(self.dataCenter, self.directoryId, mailingListId, contactId)
        
        Use a different call https://api.qualtrics.com/dd105bd826317-get-directory-contact
        
        https://yul1.qualtrics.com/API/v3/directories/{directoryId}/contacts/{contactId}
        
        """
        
        baseUrl = "https://{0}.qualtrics.com/API/v3/directories/{1}/contacts/{2}"\
            .format(self.dataCenter, self.directoryId, contactId)
        
        headers = {
            "x-api-token": self.apiToken,
            }

        response = requests.get(baseUrl, headers=headers, verify=self.verify)
        
        # if OK
        if response.status_code == 200:
            # retrieve the CGC
            # convert to dict
            ddict = json.loads(response.text)
            # get the contactLookupId
            try:
                contactLookupId = ddict['result']['mailingListMembership'][mailingListId]['contactLookupId']
            except Exception as e:
                print(f"Error in getContactLookupId {e}")
                sys.exit('Exiting program')
                
            return contactLookupId
        else:
            print(f"Error: getContactLookupId {response.status_code}")
            pprint(response.content)
            sys.exit('Exiting program')
            return None   
        

    def getLibraryMessage(self, libraryId, messageId):
        """
        Get a library message
        
        https://api.qualtrics.com/b41dc5c6eac64-get-library-message
        https://yul1.qualtrics.com/API/v3/libraries/{libraryId}/messages/{messageId}
        
        """
        
        baseUrl = "https://{0}.qualtrics.com/API/v3/libraries/{1}/messages/{2}".format(
            self.dataCenter, 
            libraryId, 
            messageId,
        )
        headers = {
            "x-api-token": self.apiToken,
            "Content-Type": "application/json"
        }

        response = requests.get(baseUrl, headers=headers,verify=self.verify)

        d = json.loads(response.text)

        status = d['meta']['httpStatus']
        
        if status == '200 - OK':
            message = d['result']['messages']['en']
        else:
            message = None
            print(f"Error in get LibraryMessage {response.text} for messageId {messageId}")
            sys.exit('Exiting program')
        
        return message       
    
    def check_for_send(self, mailingListId, sendFlag=True):
        """
        check a mailing list for cases which need invitations to be sent
        """
        contactList = self.get_contact_list()
        # for mailing list
        for contact in contactList:
            # load values
            useSMS = int(contact['embeddedData'].get('UseSMS', 0))
            contactMethod = contact['embeddedData'].get('ContactMethod', 'unknown').upper()
            surveysScheduled = int(contact['embeddedData'].get('SurveysScheduled', 0))
            numDays = int(contact['embeddedData'].get('NumDays', 0))
            
            # get TimeSlots
            check_TimeSlots = contact['embeddedData'].get('TimeSlots', 'NotPresent')
            
            if self.verbose > 0:
                print(f"checking {contact['email']}")
            
            
            # check if SurveysSchedule == 0 and numDays > 0
            if surveysScheduled == 0 and numDays>0:
            # if surveysScheduled == 0 and ( useSMS == 1 or contactMethod == 'SMS') and numDays>0:

                # get the time slots, depends on format TimeSlots or TimeX mode
                if check_TimeSlots != 'NotPresent':                
                    # use eval to convert the timeSlots into a list
                    timeSlots = eval(f"[{contact['embeddedData'].get('TimeSlots')}]")
                    pass
                else:
                    # expect to have TimeX, load Time1, Time2, etc into timeSlots
                    # developed this for the long covid study since qualtrics can't create lists
                    # in the embedded data.
                    timeSlots = []  # initialize
                    keys = contact['embeddedData'].keys()
                    timeList = []
                    for key in keys:
                        # ignore TimeZone
                        if key.startswith('Time') and 'TimeZone' not in key:
                            timeList.append(key)
                    timeList.sort()  # sort in place
                    
                    for time in timeList:
                        timeSlots.append(int(contact['embeddedData'][time]))
                    pass
                
                # if timeSlots is empty then skip current iteration and move to next one (contact)
                if len(timeSlots) == 0:
                    continue
                           
                # get expiration time in minutes
                ExpireMinutes = int(contact['embeddedData'].get('ExpireMinutes', self.minutesExpire))

                # prepare parameters for schedule_multiple_xxxx
                sendParams={}

                # get the contactLookupId
                sendParams['contactId'] = contact['contactId']
                sendParams['contactLookupId'] = self.getContactLookupId(mailingListId, contact['contactId'])
                # set timezone
                # see  if in the embeddedData
                if contact['embeddedData'].get('TimeZone') is not None:
                    timeZone = contact['embeddedData']['TimeZone']
                else:
                    # use the default TimeZone
                    timeZone = self.timeZone
                    
                sendParams['timeZone'] = timeZone
                
                sendParams['startDate'] = contact['embeddedData']['StartDate']
                sendParams['timeSlots'] = timeSlots
                sendParams['numDays'] = numDays
                sendParams['contactInfo'] = contact
                sendParams['ExpireMinutes'] = ExpireMinutes

                # check for EMAIL first
                if contactMethod == 'EMAIL':
                    # do the stuff for email
                    if sendFlag:
                        # send to scheduler
                        resp = self.schedule_multiple_email(sendParams)
                    
                    pass
                # order is important for check contactMethod first
                elif  contactMethod == 'SMS' or useSMS == 1:

                    if sendFlag:
                        # send to scheduler
                        resp = self.schedule_multiple_sms(sendParams)
                        # TODO check ok
                        # response = self.update_embedded(sendParams['contactId'], updateFields={"LogData": {"action":"send"}})
                    else:
                        pprint.pprint(contact)

                else:
                    # error not match for contactMethod
                    print(f"Error no contact method match {contactMethod} for {contact}")
                    pass
            pass    
        pass
    
    def schedule_multiple_email(self, params={}):
        """
        Schedule multiple email for a case 
        
        calls: send_email(contactId, sendDate,  method='Invite')
        
        sendDate is of form strftime('%Y-%m-%dT%H:%M:%SZ', gmtime())
        
        Sample code for converting from one timezone to another
        
        from datetime import datetime
        from zoneinfo import ZoneInfo

        # Create a datetime object in the 'America/Chicago' time zone
        chicago_time = datetime(2023, 10, 25, 12, 0, 0, tzinfo=ZoneInfo("America/Chicago"))

        # Convert 'chicago_time' to UTC
        utc_time = chicago_time.astimezone(ZoneInfo("UTC"))

        print("Chicago Time:", chicago_time)
        print("UTC Time:", utc_time)
        """
        # prep parameters
        # Date time
        
        pass
        # loop for each invite
        
            # schedule invite
            
            # update the mailinglist entry for SurveysScheduled
            
        # after all done  set SendStatus to 1
            # loop for days and times
        invite_count = 1
        
        # check the timeSlots
        if self.check_time_slots(params['timeSlots']) == False:
            print(f"Error in  format of timeSlots {params['timeSlots']}")
            return -1
            
        total_count = params['numDays'] * len(params['timeSlots'])
        emailAddress =params['contactInfo']['email']
        if self.verbose: print(f"Sending {total_count} surveys to {emailAddress}")
        for day in range(params['numDays']):
            pass
            for raw_time in params['timeSlots']:  
                
                time = self.get_time(raw_time)                
                #TODO - adjust if there is a time zone difference between 
                
                # create datetime object for recipient
                # dobj = datetime.strptime(params['startDate'], '%Y-%m-%d')
                dobj = dateutil.parser.parse(params['startDate'])
                hour = int(time)//100
                min = int(time)%100
                
                start_recipient_time = datetime(dobj.year, dobj.month, dobj.day,hour,min, 0, 
                                          tzinfo=ZoneInfo(params['timeZone']))
                # add the day delta
                recipient_time = start_recipient_time + timedelta(days=day)
                # convert to utc
                recipient_time_utc = recipient_time.astimezone(ZoneInfo("UTC"))
                
                ExpireMinutes = params.get('ExpireMinutes',self.minutesExpire)
                
                expiration_time_utc = recipient_time.astimezone(ZoneInfo("UTC")) \
                                        + timedelta(minutes=ExpireMinutes)                
                # don't schedule if now is > recipient_time
                
                response = self.send_email(params['contactLookupId'], recipient_time_utc, expiration_time_utc )

                # if OK
                if response.status_code == 200:
                    if self.verbose: print(f"Scheduled {invite_count} of {total_count} surveys to {emailAddress}")                
                    # update the SurveysScheduled entry for this contact
                    response = self.update_embedded(params['contactId'], updateFields={"SurveysScheduled": invite_count})
                    invite_count += 1
                else:
                    print(f"Error: {response.status_code}")
                    #pprint.pprint(response.content) 
                    print(response.content) 
                    sys.exit('Exiting program')


        return 1

    def send_email(self, contactLookupId, sendDate, expDate, method='Invite'):

        """
        Schedules sending of an email to an individual
        
        index - index in the contactList
        """
        headers = {
        "x-api-token": self.apiToken,
        "Content-Type": "application/json"
        }

        url='https://{0}.qualtrics.com/API/v3/distributions'.format(self.dataCenter)
        # url = "https://{0}.qualtrics.com/API/v3/distributions/sms".format(self.dataCenter)

        recipients = {}
        recipients['mailingListId'] = self.mailingListId
        # passß the contactLookupId
        # contactLookupId = self.getContactLookupId( self.mailingListId, contactId)
        recipients['contactId'] = contactLookupId

        message = {}
        
        # don't use the original message since we need to make it different to prevent
        # duplicate message errors
        #message['messageId']= self.messageIdEmail
        #message['libraryId']= self.libraryId
        
        # retrieve the original message
        self.getLibraryMessages(self.libraryId)
        origMessageText = self.getLibraryMessage(
            self.libraryId, self.messageIdEmail
        )
        
        # add random text to end of messageText to get around problem of 
        # qualtrics rule of only sending one SMS per day.
        # six random characters + 2 random digits to increase possible randomness
        # 52**6 * 10**2 = 1977060966400
        randText = '\n['
        randText += f"{random.choice(string.ascii_letters)}"
        randText += f"{random.choice(string.ascii_letters)}"
        randText += f"{random.choice(string.digits)}"
        randText += f"{random.choice(string.ascii_letters)}"
        randText += f"{random.choice(string.ascii_letters)}"
        randText += f"{random.choice(string.digits)}"
        randText += f"{random.choice(string.ascii_letters)}"
        randText += f"{random.choice(string.ascii_letters)}"
        randText += "]"
       
        newMessageText = origMessageText + '\n' + '&nbsp;' +'\n' + randText + '\n'
        # use modified message
        message['messageText'] = newMessageText

        # email header info
        # TODO - customize to entries in config
        header = {}
        header['fromEmail'] = "noreply@qualtrics.com"
        header['fromName'] = "UMN Qualtrics"
        header['replyToEmail'] = "noreply@qualtrics.com"
        # make every subject header different to allow multiple emails/day - necessary?
        header['subject'] = f"UMN Survey"
               
        surveyLink={}
        surveyLink['surveyId'] = self.surveyId
        surveyLink['type'] = "Individual"
        surveyLink["expirationDate"] = expDate.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        data = {}
        data['header'] = header  
        data['surveyLink'] = surveyLink      
        data['sendDate'] = sendDate.strftime('%Y-%m-%dT%H:%M:%SZ')
        #data['method'] = method
        #data['surveyId'] = self.surveyId
        #data['name'] = "EMAIL message"
        data['recipients'] = recipients
        data['message'] = message



        if self.verbose > 2:
            pprint(data)

        response = requests.post(url, json=data, headers=headers,verify=self.verify)
        # response = requests.post(url, json=data, headers=headers,verify=self.verify)
        if self.verbose > 1: pprint(response.text)

        if response.status_code != 200 and self.verbose > 2:
            print(f"Error: {response.status_code}")
            #pprint.pprint(response.content) 
            print(response.content) 
        
        return response    

    def schedule_multiple_sms(self, params={}):
        """
        Schedule multiple sms for a case 
        
        calls: send_sms(contactId, sendDate,  method='Invite')
        
        sendDate is of form strftime('%Y-%m-%dT%H:%M:%SZ', gmtime())
        
        Sample code for converting from one timezone to another
        
        from datetime import datetime
        from zoneinfo import ZoneInfo

        # Create a datetime object in the 'America/Chicago' time zone
        chicago_time = datetime(2023, 10, 25, 12, 0, 0, tzinfo=ZoneInfo("America/Chicago"))

        # Convert 'chicago_time' to UTC
        utc_time = chicago_time.astimezone(ZoneInfo("UTC"))

        print("Chicago Time:", chicago_time)
        print("UTC Time:", utc_time)
        """
        # prep parameters
        # Date time
        
        pass
        # loop for each invite
        
            # schedule invite
            
            # update the mailinglist entry for SurveysScheduled
            
        # after all done  set SendStatus to 1
            # loop for days and times
        invite_count = 1
        
        # check the timeSlots
        if self.check_time_slots(params['timeSlots']) == False:
            print(f"Error in  format of timeSlots {params['timeSlots']}")
            return -1
            
        total_count = params['numDays'] * len(params['timeSlots'])
        phoneNumber=params['contactInfo']['phone']
        if self.verbose: print(f"Sending {total_count} surveys to {phoneNumber}")
        for day in range(params['numDays']):
            pass
            for raw_time in params['timeSlots']:  
                
                time = self.get_time(raw_time)                
                #TODO - adjust if there is a time zone difference between 
                
                # create datetime object for recipient
                # dobj = datetime.strptime(params['startDate'], '%Y-%m-%d')
                dobj = dateutil.parser.parse(params['startDate'])
                hour = int(time)//100
                # need to check time, for correct e.g. 2366
                min = int(time)%100
                
                start_recipient_time = datetime(dobj.year, dobj.month, dobj.day,hour,min, 0, 
                                          tzinfo=ZoneInfo(params['timeZone']))
                # add the day delta
                recipient_time = start_recipient_time + timedelta(days=day)
                # convert to utc
                recipient_time_utc = recipient_time.astimezone(ZoneInfo("UTC"))
                
                ExpireMinutes = params.get('ExpireMinutes',self.minutesExpire)
                
                expiration_time_utc = recipient_time.astimezone(ZoneInfo("UTC")) \
                                        + timedelta(minutes=ExpireMinutes)                
                # don't schedule if now is > recipient_time
                
                response = self.send_sms(params['contactLookupId'], recipient_time_utc, expiration_time_utc )

                # if OK
                if response.status_code == 200:
                    if self.verbose: print(f"Sent {invite_count} of {total_count} surveys to {phoneNumber}")                
                    # update the SurveysScheduled entry for this contact
                    response = self.update_embedded(params['contactId'], updateFields={"SurveysScheduled": invite_count})
                    invite_count += 1
                else:
                    print(f"Error: {response.status_code}")
                    #pprint.pprint(response.content) 
                    print(response.content) 
                    sys.exit('Exiting program')


        return 1

    def send_sms(self, contactLookupId, sendDate, expDate, method='Invite'):

        """
        Schedules sending of an sms to an individual
        
        index - index in the contactList
        """
        headers = {
        "x-api-token": self.apiToken,
        "Content-Type": "application/json"
        }


        url = "https://{0}.qualtrics.com/API/v3/distributions/sms".format(self.dataCenter)

        recipients = {}
        recipients['mailingListId'] = self.mailingListId
        # passß the contactLookupId
        # contactLookupId = self.getContactLookupId( self.mailingListId, contactId)
        recipients['contactId'] = contactLookupId

        message = {}
        # retrieve the original message
        # message['messageId']= self.messageId
        # message['libraryId']= self.libraryId
        origMessageText = self.getLibraryMessage(
            self.libraryId, self.messageId
        )
        
        # add random text to end of messageText to get around problem of 
        # qualtrics rule of only sending one SMS per day.
        # six random characters + 2 random digits to increase possible randomness
        # 52**6 * 10**2 = 1977060966400
        randText = '\n['
        randText += f"{random.choice(string.ascii_letters)}"
        randText += f"{random.choice(string.ascii_letters)}"
        randText += f"{random.choice(string.digits)}"
        randText += f"{random.choice(string.ascii_letters)}"
        randText += f"{random.choice(string.ascii_letters)}"
        randText += f"{random.choice(string.digits)}"
        randText += f"{random.choice(string.ascii_letters)}"
        randText += f"{random.choice(string.ascii_letters)}"
        randText += "]"
       
        newMessageText = origMessageText + '\n' + '&nbsp;' +'\n' + randText + '\n'
        message['messageText'] = newMessageText
        
        data = {}
        data['sendDate'] = sendDate.strftime('%Y-%m-%dT%H:%M:%SZ')
        data['surveyLinkExpirationDate'] = expDate.strftime('%Y-%m-%dT%H:%M:%SZ')
        data['method'] = method
        data['surveyId'] = self.surveyId
        data['name'] = "SMS message"
        data['recipients'] = recipients
        data['message'] = message

        if self.verbose > 2:
            pprint(data)

        response = requests.post(url, json=data, headers=headers,verify=self.verify)
        if self.verbose > 1: pprint(response.text)
        
        return response    

    def send_sms_(self, contactId, sendDate, expDate, method='Invite'):

        """
        Schedules sending of an sms to an individual
        
        index - index in the contactList
        """
        headers = {
        "x-api-token": self.apiToken,
        "Content-Type": "application/json"
        }


        url = "https://{0}.qualtrics.com/API/v3/distributions/sms".format(self.dataCenter)

        recipients = {}
        recipients['mailingListId'] = self.mailingListId
        # get the contactLookupId
        contactLookupId = self.getContactLookupId( self.mailingListId, contactId)
        recipients['contactId'] = contactLookupId

        message = {}
        # retrieve the original message
        # message['messageId']= self.messageId
        # message['libraryId']= self.libraryId
        origMessageText = self.getLibraryMessage(
            self.libraryId, self.messageId
        )
        
        # add random text to end of messageText to get around problem of 
        # qualtrics rule of only sending one SMS per day.
        randText = f"[{random.choice(string.ascii_letters)}]"
        newMessageText = origMessageText + '\n' + '&nbsp;' +'\n' + randText + '\n'
        message['messageText'] = newMessageText
        
        data = {}
        data['sendDate'] = sendDate.strftime('%Y-%m-%dT%H:%M:%SZ')
        data['surveyLinkExpirationDate'] = expDate.strftime('%Y-%m-%dT%H:%M:%SZ')
        data['method'] = method
        data['surveyId'] = self.surveyId
        data['name'] = "SMS message"
        data['recipients'] = recipients
        data['message'] = message

        print(data)

        response = requests.post(url, json=data, headers=headers,verify=self.verify)
        if self.verbose > 1: print(response.text)
        
        return response    
    
    def check_time_slots(self, parts: list):
        """
        Args:
            parts (list): time slots examples [800,1200,1600,2000]
        """
    
        
        count = len(parts)
        result = False  # init to False
        
        # check each part
        for part in parts:
            
            if type(part) is list:

                try:
                    if len(part)==2:

                        for number in part:
                            try:
                                if type(number) is not int:
                                    raise Exception("Not an int")
                            except Exception as e:
                                return False
                            else:
                                result = True
                    else:
                        return False
                except Exception as e:
                    return False

                result=True
            else:
                # check is it a number
                try:
                    if type(part) is not int:
                        raise Exception("Not an int")
                    pass
                except Exception as e:
                    return False
                else:
                    result = True
            
        # everything OK!     
        return result
    
    def get_time(self, slot) -> int:
        """ check the entry and return a time as a number.
        For the [800:900] entry, returns a time between the two
        numbers, e.g. 815

        Args:
            slot : time slot 800 or [800:900]

        Returns:
            int: time as a number in 24 hour notation
        """
        
        try:
            time = int(slot)
        except:
            # is a list [2050,2110]
            #  TODO  how to deal with [2350,0010]!!
            # convert hourm inute to hours.float
            time0 = slot[0]//100 + (slot[0] - slot[0]//100*100)/60.0
            time1 = slot[1]//100 + (slot[1] - slot[1]//100*100)/60.0
            
            time_raw = random.uniform(time0, time1)
            # convert time_raw such that 830 is 8 for hours and 30/60 for minutes
            # is 8.5
            hours = time_raw//1 
            minutes_percentage = (time_raw - hours)
            minutes = minutes_percentage * 60
            # convert back to hhmm
            time = int(hours*100 + minutes)
            
        return time

    def getLibraryMessages(self, libraryId):
        """
        Given a libraryId , return the message id and names

        Args:
            libraryId (_type_): _description_

        Get a library message
        
        https://api.qualtrics.com/b41dc5c6eac64-get-library-message
        https://yul1.qualtrics.com/API/v3/libraries/{libraryId}/messages/{messageId}
        
        """
        
        baseUrl = "https://{0}.qualtrics.com/API/v3/libraries/{1}/messages".format(
            self.dataCenter, 
            libraryId, 
        )
        headers = {
            "x-api-token": self.apiToken,
            "Content-Type": "application/json"
        }

        response = requests.get(baseUrl, headers=headers,verify=self.verify)

        # if OK
        if response.status_code == 200:
            messages = response.json().get('result', {}).get('elements', [])
            if self.verbose > 2:
                pprint(messages)
            return messages
                
        else:
            print(f"Error: {response.status_code}")
            #pprint.pprint(response.content) 
            print(response.content) 
            sys.exit('Exiting program')
  
        # d = json.loads(response.text)

        # status = d['meta']['httpStatus']
        
        # if status == '200 - OK':
        #     message = d['result']['messages']['en']
        # else:
        #     message = None
        #     print(f"Error in get LibraryMessage {response.text} ")
        #     sys.exit('Exiting program')
        
        # return message          
        
            
if __name__ == "__main__":
    
    # provide a description of the program with format control
    description = textwrap.dedent('''\
    This program provides several commands for interacting with Qualtrics.
    
    Account information is read from the qualtrics_token file which contains the 
    QUALTRICS_APITOKEN.
    
    A yaml configs file contains the required qualtrics ids and configuration information.
    Below is a sample configuration file. 
    You will need to create your own config_qualtrics.yaml file 
    with the parameters  set for your project.  
    
    We recommend that you create a config file for each project.
    For example, for a tbi study, you could create a config_tbi.yaml file.
    
    ===== begin config_qualtrics.yaml =====
    # account info
    account:
        DATA_CENTER: ca1
        DEFAULT_DIRECTORY: POOL_3fAZGWRVfLKuxe3
        # place your group library id here
        LIBRARY_ID: GR_eRwfaL8bcG2pimO
        
        # default is True for ssl check
        # set to False for VA
        VERIFY: True

    # project info
    project:
        # Study 355
        # survey id
        SURVEY_ID: SV_8i6LlPpza6mQHvU
        # message_id for sms invite
        MESSAGE_ID: MS_wcuiwtCPHQh4MeI
        # message_id for email invite
        MESSAGE_ID_EMAIL: MS_7We9SXRJ1igELB1
        # 355_mailing_list
        MAILING_LIST_ID: CG_3NxJ3cmg6jRvqUd
        TIMEZONE: America/Chicago
        MINUTES_EXPIRE: 60

    # default embedded data
    embedded_data:
        # ContactMethod - options sms, email
        ContactMethod: sms
        # Internal counter of number of surveys scheduled
        # Set this to 0 to schedule surveys
        # When the program completes, it updates this value
        SurveysScheduled: 0
        # Start date of the survey
        StartDate: 2025-02-11
        # number of days to send surveys
        NumDays: 1
        # times during day to send surveys, use military time
        TimeSlots: 800,1200,1600,2000
        # time zone
        TimeZone: America/Chicago
        # survey expiration time in minutes
        ExpireMinutes: 60
        # flag to delete unsent surveys, set to 1 to delete
        # then use the delete command
        DeleteUnsent: 0
        # bookkeeping log data of operations
        LogData: '[{"action":"init"}]'
    
    ===== end config_qualtrics.yaml =====
    
  
    
    Here are some examples of using the command. Text following the $ is
    the command that is entered at the command line in a terminal window.
    
    $ qualtrics_util --config config_qualtrics.yaml --cmd list
    Prints the entries for the specified mailing_list
    
    $ qualtrics_util --config config_qualtrics.yaml --cmd send
    Schedules the sending of invitations for the specified mailing_list, for 
    all contacts with SurveysScheduled == 0 and NumDays > 0.
    
    $ qualtrics_util --config config_qualtrics.yaml --cmd delete
    Deletes all unsent invitations for the specified mailing_list
     
    ''')
    
    parser = argparse.ArgumentParser(
        description=description, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--config", type = str,
                     help="config file, default is config/config_qualtrics.yaml",
                     default='config/config_qualtrics.yaml'
                     #default='study_298/s298_config.yaml',
                     ) 
    
    parser.add_argument("--cmd", type = str,
                     help="cmd - check, delete, export, list, slist, send, update, default: list",
                     default='list') 

    parser.add_argument("--token", type = str,
                        help="name of qualtrics token file - default qualtrics_token",
                        default="qualtrics_token")

    parser.add_argument("--format", type = str,
                        help="export output file format- default: json ",
                        default="json")

    parser.add_argument("-H", "--history", action="store_true", help="Show program history")
        
    parser.add_argument("--verbose", type = int,
                        help="print diagnostic messages -  0 low, 3 high, default 1",
                        default=1)
    
    parser.add_argument("--index", type=int,
                        help="index number for operations like delete",
                        default=-1 )
    
    parser.add_argument('-V', '--version', action='version', version=f'%(prog)s {__version__}')

   
    args = parser.parse_args()
    
    if args.history:
        print(f"{os.path.basename(__file__) } Version: {__version__}")
        print(__version_history__)
        sys.exit(0)
        
    test = False

    if test:

        config_file = 'config_va.yaml' # 'config_covid_ema.yaml'
        config_file = 'config_covid_ema_test.yaml'
        qd = QualtricsDist()
        qd.initialize(config_file = config_file,
                          verbose = 3)
        args.cmd = 'get_distribution_test' 
        args.cmd = 'list'
        args.cmd = 'initialize_all_test'
        
        qd.get_contact_list()

        if args.cmd == 'list':
            qd.get_contact_list()
            qd.print_contact_list()
        elif args.cmd == 'update_test':
            qd.get_contact_list()
            status, response = qd.update_contact(
                1, # index of contact
                edata__StartDate = '2023-08-20',
                firstName = 'Kelvin O.',
            )
            status, response = qd.update_contact(
                1, # index of contact
                
            )
        elif args.cmd == 'initialize_test':
            status, response = qd.update_embedded(
                1
            )
        elif args.cmd == 'initialize_all_test':
            status = qd.initialize_all_embedded()
        elif args.cmd == 'get_distribution_test':
            dataElements = qd.get_distribution()
            # 'stats' column contains a dict with 'sent' 
            df = qd.reorg_distribution_list(dataElements)
            # to get the distribution not sent and the contactLookupId

            # get all distributions for a specific contact
            # df.query("contactLookupId=='CGC_EE7O5AMAjhtmOYq'")['sendDate']
            newdf = df.query("sent==0")
            passed = False
        elif args.mode =='getMessage':
            status, response = qd.getLibraryMessage(
                                qd.cfg['project']['LIBRARY_ID'],
                                qd.cfg['project']['MESSAGE_ID']
                                )
        elif args.mode == 'sendSMS':
            response = qd.send_sms(
                    'CID_30jbzCtFodRMAEP',
                    strftime('%Y-%m-%dT%H:%M:%SZ', gmtime()),        
                )
        pass
                    
    else:

        qd = QualtricsDist()
        qd.initialize(
                config_file = args.config,
                #verbose = args.verbose,
                #index = args.index,
                env_file = args.token,
                **vars(args)
                )
        qd.work(args.cmd)
        
        pass        