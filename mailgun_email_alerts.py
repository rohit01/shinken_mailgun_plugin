#!/usr/bin/env python
#
# Utility for sending alert emails in shinken
# Author: Rohit - @rohit01
#

from optparse import OptionParser
from util.send_email import SendEmail

SHINKEN_URL = SendEmail().get_server_url()

## Shinken alert keywork mapping
ALERT_LEVEL_MAPPING = {
    # Service alert keyworks
    'ok': 'service_check',
    'recovery': 'service_check',
    'warning': 'service_check',
    'critical': 'service_check',
    'unknown': 'service_check',
    # Host alert keyworks
    'up': 'host_check',
    'flapping': 'host_check',
    'down': 'host_check',
    # unknown
    'invalid_host': 'host_check',
    'invalid_service': 'service_check',
}

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


def send_alert(hostaddress, hostname, servicename, attemptno, date, time,
               message, alertlevel):
    try:
        lower_case_alertlevel = str(alertlevel).lower()
        message_type = ALERT_LEVEL_MAPPING[lower_case_alertlevel]
    except KeyError:
        if servicename is None:
            message_type = ALERT_LEVEL_MAPPING['invalid_host']
        else:
            message_type = ALERT_LEVEL_MAPPING['invalid_service']
    remarks = 'No Remarks'
    if message_type == 'host_check':
        subject_args = (hostaddress, alertlevel, attemptno)
        body_args = (hostaddress, alertlevel, attemptno, message, remarks,
                     SHINKEN_URL, hostname, date, time)
    elif message_type == 'service_check':
        subject_args = (servicename, hostaddress, alertlevel, attemptno)
        body_args = (servicename, alertlevel, hostaddress, attemptno, message,
                     remarks, SHINKEN_URL, hostname, servicename, date, time)
    else:
        print 'Invalid message_type: %s. Aborting!'
        return
    # Send email
    email_sender = SendEmail()
    email_sender.send(message_type, subject_args=subject_args,
                      body_args=body_args)
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
    send_alert(hostaddress=hostaddress, hostname=hostname,
               servicename=servicename, attemptno=attemptno, date=date,
               time=time, message=message, alertlevel=alertlevel)


if __name__ == '__main__':
    parse_arguments_and_send_email()
