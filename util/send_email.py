import urllib
import urllib2
import base64
import re
from configmanagement import ConfigManagement


MANDATORY_SECTIONS = ['settings', 'subject', 'body']


class SendEmail():
    def __init__(self, hosts_file=None):
        if hosts_file is None:
            path = '/'.join(__file__.split('/')[:-1])
            filename = 'email_settings.ini'
            hosts_file = '%s/%s' % (path, filename)
        self.config_management = ConfigManagement(
            hosts_file,
            mandatory_sections=MANDATORY_SECTIONS,
            list_sections=None
        )
        all_configs = self.config_management.read_file()
        self.settings = all_configs['settings']
        self.subject = all_configs['subject']
        self.body = all_configs['body']
        self.params = {
            'servername': self.settings['servername'],
            'sender': self.settings['sender'],
            'recipients': self.settings['recipients'],
        }
        self.headers = {
            'Authorization': 'Basic {0}'.format(base64.b64encode(
                             self.settings['authorization'])),
            'Content-Type': self.settings['contenttype']
        }
        self.url = self.settings['url']


    def get_server_url(self):
        try:
            return self.settings['serverurl']
        except KeyError:
            return 'unknown'


    def get_notification_email(self):
        try:
            return self.settings['notificationemail']
        except KeyError:
            return


    def send(self, message_type, subject_args=(), body_args=(),
             failover_logger=None, additional_recipients=None):
        """
        Send the email
        """
        # Check None arguments
        if subject_args is None:
            subject_args = ()
        if body_args is None:
            body_args = ()
        if (additional_recipients is not None) and \
                (additional_recipients.strip() != ''):
            self.params['recipients'] = "%s, %s" % (self.params['recipients'],
                                                    additional_recipients)
        p = re.compile('^[\s,]*$')
        if p.match(self.params['recipients'].strip()) is not None:
            print 'No recipients defined. Aborting sending alert email'
            return
        # Discard extra subject arguments
        subject = self.subject[message_type]
        args_required = subject.count('%s')
        args_count = len(subject_args)
        if args_count > args_required:
            diff = args_required - args_count
            subject = subject % (subject_args[:diff])
        elif args_count == args_required:
            subject = subject % (subject_args)
        # Get body message. Replace ';' with '\n'
        # Discard extra body_message arguments
        body_message = self.body[message_type].replace(';', '\n')
        args_required = body_message.count('%s')
        args_count = len(body_args)
        if args_count > args_required:
            diff = args_required - args_count
            body_message = body_message % (body_args[:diff])
        elif args_count == args_required:
            body_message = body_message % (body_args)
        # Get Salutation, Signature & failover logs. Replace ';' with '\n'
        salutation = self.body['salutation'].replace(';', '\n')
        signature = self.body['signature'].replace(';', '\n')
        if failover_logger is None:
            body_logs = ''
        else:
            body_logs = failover_logger.get_email_log()
        # Form the complete body
        body = ''.join([salutation, body_message, body_logs, signature])
        # Set subject & body in post parameters
        self.params['subject'] = subject
        self.params['body'] = body
        # Send an email
        print self.params
        post_data = urllib.urlencode(self.params)
        req = urllib2.Request(self.url, post_data, self.headers)
        response = urllib2.urlopen(req)
        print response
        return response
