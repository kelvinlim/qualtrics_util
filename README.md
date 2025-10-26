# qualtrics_utils

Code for working  with Qualtrics mailing lists using a REST api.  It supports the sending of multiple SMS text messages per day to an entry in a qualtrics mailing list.

To use the code you will need a Qualtrics API token.  To send SMS, you will need SMS tokens from Qualtrics.

The program uses two files as input.

1. .env - this contains an entry: QUALTRICS_APITOKEN=YourTokenGoesHere
2. config_qualtrics.yaml - a yaml format configuration file that specifies information about the survey, mailinglist, library, message and initial parameters.  Another file can be specified by using the --config argument.

To get help:

```
qualtrics_util --help
```

This will return:

```
usage: qualtrics_util.py [-h] [--config CONFIG] [--cmd CMD] [--verbose VERBOSE] [--index INDEX]

Qualtrics utilty tool for working with mailing lists. A configuration file allows customization for different projects. Sends out to individual via SMS or email

optional arguments:
  -h, --help         show this help message and exit
  --config CONFIG    config file
  --cmd CMD          cmd - check, delete, list, slist, send, update, default: list
  --verbose VERBOSE  print diagnostic messages - 0 low, 3 high, default 1
  --index INDEX      index number for operations like delete
```

There are several commands (we assume you are using the config_qualtrics.yaml file):

1. check - checks the validity of the qualtrics ids for survey, mailinglist, message

   ```
   qualtrics_util  --cmd check
   ```
2. delete - deletes unsent distributions for entries in the mailinglist where DeleteUnsent is set to 1. It needs the index argument for the mailinglist entry which can be obtained using the list or slist command

   ```
   qualtrics_util  --cmd delete --index 2
   ```
3. export - exports the survey data into a json file (default) or a csv file if the --format argument is set to csv

   ```
   qualtrics_util  --cmd export --format json
   ```
4. list - provides a long listing for each entry in the mailinglist

   ```
   qualtrics_util  --cmd list
   ```
5. slist - provides a short listing for each entry in the mailinglist

   ```
   qualtrics_util  --cmd slist
   ```
6. send - send the distributions for each entry in the mailinglist where SurveysSchedule=0 and UseSMS=1

   ```
   qualtrics_util  --cmd send
   ```
7. update - updates the Embedded Data fields for entries in the mailinglist

   ```
   qualtrics_util  --cmd update
   ```

## To create an executable python file that doesn't need installation of the python and packages

```
# installation
pip install pyinstaller

# create the single executable file
pyinstaller --onefile qualtrics_util.py

```

## range feature

To specify a range of times to schedule a distribution, you can give a list that provided the start and end time range to send the message.  the random.randomint function is used to provide a number in the range, converting it to a 24hour time.

```
# example timeSlots for range
[800,900], [1200,1300]

# this will schedule two surveys on the day
# The first will be scheduled between 800 to 900 and the
# second will be scheduled between 1200-1300

```

## Support for crontab

With 0.8.18, now supports crontab usage for send and delete

For RH9 (lnpiapp2), can now build the binary qualtrics_util and copy
into the target directory  /home/kolim/bin using the following command

```
make all
```

## Support for email

Starting with v 2.0.2, email support is now available.

There are two key parameters that are needed in the config file to
support email.

1. Add a MESSAGE_ID_EMAIL entry for the message id for
   your email invite.  An SMS invite will not work!!
   See below:

   ```
   # In project
   project:
   .
   .
   .
   # message_id for sms invite
   MESSAGE_ID: MS_HBhLVB5HebyavdX

   # message_id for email invite
   MESSAGE_ID_EMAIL: MS_EERJLNg8Pns2kHx
   .
   .
   .

   ```
2. Add a ContactMethod field in embedded_data with the value email

   ```
   embedded_data:
      ContactMethod: email
   ```
