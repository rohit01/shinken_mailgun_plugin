Shinken Mailgun Plugin
======================

Utility to send emails through mailgun for Shinken alerts.

###### Prerequisite:
- A working shinken setup installed in a server.
- Python >= 2.6 is installed on that server

### Shinken:
It is a modern open source Nagios® like tool, redesigned and rewritten from scratch in Python. Hosted in Github: https://github.com/naparuba/shinken. Website: http://www.shinken-monitoring.org/

### Mailgun:
Mailgun is a hosted service which provides easy to use HTTP APIs for emails. It can be used used for sending, receiving and tracking email effortlessly. Website: http://www.mailgun.com/

---

### Install Shinken Mailgun Plugin in 3 easy steps:
###### 1. Create a Mailgun account:
- Sign up: https://mailgun.com/signup

###### 2. Update file: shinken_mailgun_plugin/util/email_settings.ini
In 'settings' section, update the following variables:
- servername: Enter sandbox name (See image below)
- sender: Desired monitoring email ID
- recipients: Destination email ids separated by comma
- authorization: Mailgun API key (See image below)
- serverurl: Update this with your shinken http url. It helps in generating the exact host/service link in alert mails.

![Mailgun credentials help](http://raw2.github.com/rohit01/shinken_mailgun_plugin/master/images/mailgun_credentials.jpg)

###### 3. Update shinken configuration:
- **commands.cfg** - */usr/local/shinken/etc/commands.cfg*
    - Update this file with contents from shinken_mailgun_plugin/commands.cfg
    - Add python virtualenv location in resource.cfg. For example:
        - $PYTHON_VENV$=/usr/src/python_env
    - Add location details of nrpe plugin files. For example:
        - $PLUGINSDIR$=/usr/local/nagios/libexec
    - Update the <event_command_name> as instructed in comments.
- **templates.cfg** - */usr/local/shinken/etc/templates.cfg*
    - Update notification command details in this file. Set the following as:
        - host_notification_commands           host_email_alerts
        - service_notification_commands        service_email_alerts

Once configurations files are updated, restart shinken-arbiter to apply settings:

    # /etc/init.d/shinken-arbiter restart
    Restarting arbiter
    Doing config check
    . ok
    . ok
    #

---

### Sample service check email alert:

###### Service check alert for nginx crash in server: rohit.io. To customize message, edit file: email_settings.ini

![Sample service check email alert](http://raw2.github.com/rohit01/shinken_mailgun_plugin/master/images/sample_email.png)

**And as always, Thanks for reading :)**
