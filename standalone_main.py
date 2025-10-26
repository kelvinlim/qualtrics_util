#!/usr/bin/env python3
"""Standalone CLI entry point for qualtrics_util."""

import os
import sys

# Determine if we're running as frozen executable or from source
if getattr(sys, 'frozen', False):
    # Running as compiled executable - src/ should be in the bundle
    # PyInstaller includes everything, so we can import directly
    from qualtrics_util.cli import main as cli_main
    from qualtrics_util import __version__
else:
    # Running from source - add src to path
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    from qualtrics_util.cli import main as cli_main
    from qualtrics_util import __version__

version_history = """
2.0.10 - added IANA timezone validation for project:TIMEZONE and embedded_data:TimeZone
         with error messages including file name and line number
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
0.8.21 - increased number of characters in sms random text from 1 to 8
0.8.20 - fix bug in deleteUnsent when using --index
0.8.19 - fix when DeleteUnsent not in the embedded data, use get()
0.8.18 - changed fields used to ContactEmail, ContactSMS, ContactMethod=SMS
0.8.17 - change delete to check each contact for DeleteUnsent
0.8.16 - change verbose output
0.8.15 - ContactMethod uses string for sms, email(future), unknown
0.8.14 - added support for ContactMethod, Time1,Time2, etc.
"""


def main():
    """Main CLI entry point."""
    # Handle --history flag before calling CLI
    if '-H' in sys.argv or '--history' in sys.argv:
        # Find and remove history flags to let CLI handle the rest
        sys.argv = [arg for arg in sys.argv if arg not in ['-H', '--history']]
        print(f"qualtrics-util Version: {__version__}")
        print(version_history)
        return
    
    # Call the refactored CLI main function
    cli_main()


if __name__ == "__main__":
    main()
