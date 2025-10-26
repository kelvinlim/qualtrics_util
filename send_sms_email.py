#! /usr/bin/env python
"""
https://api.qualtrics.com/595f1f2975dc9-send-survey-as-sms-message-or-email#sending-the-sms

"""

import requests
import json
from time import gmtime, strftime
from datetime import date
import datetime
import sys
import os
from dotenv import load_dotenv, dotenv_values
from random import seed
from random import randint
from zoneinfo import ZoneInfo

# seed random number generator
seed(int(datetime.datetime.now().timestamp()))

config = dotenv_values('.env')

directoryId = "POOL_3fAZGWRVfLKuxe3"
# "CG_3phdg4O3eUKWWSa"  covidema_dist_support
mailingListId = 'CG_2XpNxso87o1O548' # CG_2XpNxso87o1O548 covid ema 2023023
messageId = 'MS_EERJLNg8Pns2kHq'
libraryId = 'GR_cCk7JYSBpnnz6Rg'
surveyId = 'SV_8eMxLSXymY6lW6y'  # long covid ema SV_8eMxLSXymY6lW6y
# lim.kelvino@gmail.com
contactId = 'CID_30jbzCtFodRMAEP'
contactLookupId = 'CGC_EeOcLGz28opYoY3'
# contactId = 'CID_1IuEHgOYzf4uBqY'
# contactLookupId = 'CGC_a6NF0PbZk9M0sXm'

# def get_contact_in_mailing_list( mailing_list=None, contactId=None):
#     """
#     Returns the contactLookupId needed to send an individual distribution
#     to contactId from mailing_list 

#     :param mailing_list: Your mailing list id that you are interested in getting information on.
#     :type mailing_list: str
#     :param contactId: The contactId you are querying
#     :return: A Pandas DataFrame
#     """
#     assert mailing_list != None, 'Hey there! The mailing_list parameter cannot be None. You need to pass in a Mailing List ID as a string into the mailing_list parameter.'
#     assert isinstance(mailing_list, str) == True, 'Hey there! The mailing_list parameter must be of type string.'
#     assert len(mailing_list) == 18, 'Hey, the parameter for "mailing_list" that was passed is the wrong length. It should have 18 characters.'
#     assert mailing_list[:3] == 'CG_', 'Hey there! It looks like your Mailing List ID is incorrect. You can find the Mailing List ID on the Qualtrics site under your account settings. It will begin with "CG_". Please try again.'
    
#     assert len(contactId) == 19, 'Hey, the parameter for "contactId" that was passed is the wrong length. It should have 19 characters.'
#     assert contactId[:4] == 'CID_', 'Hey there! It looks like your ContactId is incorrect. It will begin with "CID_". Please try again.'

#     headers, base_url = self.header_setup(xm=True)
#     url = f"{base_url}/mailinglists/{mailing_list}/contacts/{contactId}"
#     request = r.get(url, headers=headers)
#     response = request.json()
#     try:
#         list_info = {
#                     "contactId": response['result']['contactId'],
#                     "creationDate": response['result']['creationDate'],
#                     #"lastModifiedDate": response['result']['lastModifiedDate'],
#                     "firstName": response['result']['firstName'],
#                     "lastName": response['result']['lastName'],
#                     "email": response['result']['email'],
#                     "emailDomain": response['result']['emailDomain'],
#                     "contactLookupId": response['result']['contactLookupId'],
#         }
#         df = pd.DataFrame.from_dict(list_info, orient='index').transpose()
#         df['creationDate'] = pd.to_datetime(df['creationDate'], unit='ms')
#         #df['lastModifiedDate'] = pd.to_datetime(df['lastModifiedDate'], unit='ms')
#         return df, list_info
#     except:
#         print(f"ServerError: {response['meta']['httpStatus']}\nError Code: {response['meta']['error']['errorCode']}\nError Message: {response['meta']['error']['errorMessage']}")

def sms(apiToken, dataCenter, method):

    headers = {
    "x-api-token": apiToken,
    "Content-Type": "application/json"
    }


    url = "https://{0}.qualtrics.com/API/v3/distributions/sms".format(dataCenter)

    recipients = {}
    recipients['mailingListId'] = mailingListId
    recipients['contactId'] = contactLookupId

    message = {}
    message['messageId']= messageId
    message['libraryId']=libraryId

    data = {}
    data['sendDate'] = strftime('%Y-%m-%dT%H:%M:%SZ', gmtime())
    data['method'] = method
    data['surveyId'] = surveyId
    
    # create random number
    value = randint(0, 100)
    data['name'] = f"Customer Satisfaction Survey  {value}"
    data['recipients'] = recipients
    data['message'] = message

    print(data)

    response = requests.post(url, json=data, headers=headers)
    print(response.text)
    
def sms_customMessageText(apiToken, dataCenter, method):
    """
    Uses MessageText instead of messageId

    Args:
        apiToken (_type_): _description_
        dataCenter (_type_): _description_
        method (_type_): _description_
    """
    headers = {
    "x-api-token": apiToken,
    "Content-Type": "application/json"
    }


    url = "https://{0}.qualtrics.com/API/v3/distributions/sms".format(dataCenter)

    recipients = {}
    recipients['mailingListId'] = mailingListId
    recipients['contactId'] = contactLookupId

    # create random number
    value = randint(0, 100)
    
    message = {}
    # message['messageId']= messageId
    # message['libraryId']=libraryId
    message['messageText']= f"A custom message {value}"

    data = {}
    data['sendDate'] = strftime('%Y-%m-%dT%H:%M:%SZ', gmtime())
    data['method'] = method
    data['surveyId'] = surveyId
    
    # create random number
    value = randint(0, 100)
    data['name'] = f"Customer Satisfaction Survey  {value}"
    data['recipients'] = recipients
    data['message'] = message

    print(data)

    response = requests.post(url, json=data, headers=headers)
    print(response.text)

def email(apiToken, dataCenter):
   
    headers = {
    "x-api-token": apiToken,
    "Content-Type": "application/json"
    }

    # create random number
    value = randint(0, 100)

    header = {}
    header['fromEmail'] = "noreply@qualtrics.com"
    header['fromName'] = "Qualtrics"
    header['replyToEmail'] = "noreply@qualtrics.com"
    # make every subject header different to allow multiple emails/day
    header['subject'] = f"Survey Distribution {value}"

    surveyLink={}
    surveyLink['surveyId'] = surveyId
    surveyLink['type'] = "Individual"
    dt_now = datetime.datetime.now()
    dt_exp = dt_now + datetime.timedelta(minutes=60)
    
    # https://stackoverflow.com/questions/7986776/how-do-you-convert-a-naive-datetime-to-dst-aware-datetime-in-python/64484063#64484063
    # switch to UTC
    utc_dt_exp = dt_exp.astimezone(ZoneInfo("UTC"))
    # expDate in utc
    expDate = utc_dt_exp.strftime('%Y-%m-%dT%H:%M:%SZ')
    surveyLink["expirationDate"]= expDate

    message = {}
    message["libraryId"] = libraryId
    message["messageId"] = messageId

    recipients={}
    recipients["mailingListId"] = mailingListId
    recipients['contactId'] = contactLookupId

    data = {}
    data['header'] = header
    data['surveyLink'] = surveyLink
    data['recipients'] = recipients
    data['sendDate'] = strftime('%Y-%m-%dT%H:%M:%SZ', gmtime())
    data['message'] = message

    print(data)

    url='https://{0}.qualtrics.com/API/v3/distributions'.format(dataCenter)
    response = requests.post(url, json=data, headers=headers)
    print(response.text)
    pass

def main(cmd='email'):
    try:
        operation  = cmd
        if operation == "sms":
           distribution = 'Invite'
    except IndexError:
        print ("usage: %s -i <operation> 'email' or 'sms Invite' or sms Interactive")
        sys.exit(2) 

    try:
        apiToken = config['APITOKEN']
        dataCenter = config['DATACENTER']
    except KeyError:
        print("set environment variables APIKEY and DATACENTER")
        sys.exit(2) 
    
    if operation == 'email':
       email(apiToken, dataCenter)
    if operation == 'sms':
       #sms(apiToken, dataCenter, distribution) 
       sms_customMessageText(apiToken, dataCenter, distribution) 

if __name__ == "__main__":
    main()
