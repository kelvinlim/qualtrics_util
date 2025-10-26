#!/usr/bin/env python3
"""Standalone CLI entry point for qualtrics_util."""

import os
import sys
import argparse

# Import from the monolithic file (which has timezone validation)
from qualtrics_util import QualtricsDist, __version__

version_history = """
2.0.11 - added datetime scheduling logic to modular src code
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
    parser = argparse.ArgumentParser(
        description="""
        Qualtrics utility tool for working with mailing lists.

        A configuration file allows customization for different projects.

        Sends out to individual via SMS or email
        """
    )

    # Determine the default config file path
    # For standalone executable, use config_qualtrics.yaml in the same directory as the executable
    # For development, use the path relative to the project root
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        exe_dir = os.path.dirname(sys.executable)
        default_config = os.path.join(exe_dir, 'config_qualtrics.yaml')
    else:
        # Running from source
        default_config = 'config/config_qualtrics.yaml'

    parser.add_argument(
        "--config",
        type=str,
        help="config file, default is config_qualtrics.yaml",
        default=default_config
    )

    parser.add_argument(
        "--cmd",
        type=str,
        help="cmd - check, delete, export, list, slist, send, update, default: list",
        default='list'
    )

    parser.add_argument(
        "--token",
        type=str,
        help="name of qualtrics token file - default qualtrics_token",
        default="qualtrics_token"
    )

    parser.add_argument(
        "--format",
        type=str,
        help="export output file format - default: json",
        default="json"
    )

    parser.add_argument(
        "--verbose",
        type=int,
        help="print diagnostic messages - 0 low, 3 high, default 1",
        default=1
    )

    parser.add_argument(
        "--index",
        type=int,
        help="index number for operations like delete",
        default=-1
    )

    parser.add_argument(
        '-V', '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )

    parser.add_argument(
        "-H", "--history",
        action="store_true",
        help="Show program history"
    )

    args = parser.parse_args()

    if args.history:
        print(f"qualtrics-util Version: {__version__}")
        print(version_history)
        return

    # Create QualtricsDist instance
    qd = QualtricsDist()
    qd.initialize(
        config_file=args.config,
        env_file=args.token,
        **vars(args)
    )

    # Execute command
    qd.work(args.cmd)


if __name__ == "__main__":
    main()
