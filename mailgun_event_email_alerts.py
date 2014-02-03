#!/usr/bin/env python
#

from optparse import OptionParser
from util.send_email import SendEmail
import re

email_sender = SendEmail()
SHINKEN_URL = email_sender.get_server_url()
NOTIFICATION_EMAIL = email_sender.get_notification_email()

MESSAGE_TYPE = 'event_triggered'
REGEX_FILTERS = [
    ## Filter unwanted messages to be sent as an email ##
    '^Connection refused by host.*$',
    '^Connection refused or timed out.*$',
    '^Timeout while attempting connection.*$',
    '^UNKNOWN.*$',
    '^CHECK_NRPE: Error - Could not complete SSL handshake.*$',
    '^[     ]*$',
]

## Command line arguments
OPTIONS = {
    'a': 'hostaddress;Address of host server',
    'H': 'hostname;Hostname defined in shinken',
    's': 'servicename;Service description name defined in shinken',
    'n': 'attemptno;No of attempts',
    'd': 'date;Date of event',
    't': 'time;Time of event',
    'm': 'message;Message displayed by shinken',
    'l': 'alertlevel;Seriousness of alert (UP, Down, warning, critical, etc)',
}


def parse_options():
    parser = OptionParser()
    for option, description in OPTIONS.items():
        shortopt = '-%s' % (option)
        longopt = '--%s' % (description.split(';')[0])
        keyname = description.split(';')[0]
        help = ''
        if len(description.split(';')) > 1:
            help = description.split(';')[1]
        parser.add_option(shortopt, longopt, dest=keyname, help=help)
    (options, args) = parser.parse_args()
    return options


def filter_unwanted_messages(message):
    for filter_message in REGEX_FILTERS:
        p = re.compile(filter_message)
        if p.match(message) is not None:
            return True
    return False


def send_alert(hostaddress, hostname, servicename, attemptno, date, time,
               message, alertlevel):
    remarks = 'Event triggered'
    subject_args = (servicename, hostaddress, alertlevel, attemptno)
    body_args = (servicename, hostaddress, alertlevel, attemptno, message,
                 remarks, SHINKEN_URL, hostname, servicename, date, time)
    MESSAGE_TYPE
    # Send email
    global email_sender
    email_sender.send(MESSAGE_TYPE, subject_args=subject_args,
                      body_args=body_args,
                      additional_recipients=NOTIFICATION_EMAIL)
    return


def parse_arguments_and_send_email():
    arguments_passed = parse_options()
    hostaddress = str(arguments_passed.hostaddress)
    hostname = str(arguments_passed.hostname)
    servicename = str(arguments_passed.servicename)
    attemptno = str(arguments_passed.attemptno)
    date = str(arguments_passed.date)
    time = str(arguments_passed.time)
    message = str(arguments_passed.message)
    alertlevel = str(arguments_passed.alertlevel)
    if filter_unwanted_messages(message):
        return
    # Send alert
    send_alert(hostaddress=hostaddress, hostname=hostname,
               servicename=servicename, attemptno=attemptno, date=date,
               time=time, message=message, alertlevel=alertlevel)


if __name__ == '__main__':
    parse_arguments_and_send_email()
