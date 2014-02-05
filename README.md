Shinken Mailgun Plugin
======================

Utility to send emails through mailgun for Shinken alerts.

**Prerequisite:**
* You have a working shinken setup installed in a server.
* Python >= 2.6 is installed on that server


## Shinken:
It is a modern open source Nagios® like tool, redesigned and rewritten from scratch in Python. Hosted in Github: https://github.com/naparuba/shinken. Website: http://www.shinken-monitoring.org/

## Mailgun:
Mailgun is a hosted service which provides easy to use HTTP APIs for emails. It can be used used for sending, receiving and tracking email effortlessly. Website: http://www.mailgun.com/

## Install Shinken Mailgun Plugin:

This plugin can be installed in 3 easy steps:

* Create a Mailgun account
* Add mailgun credentials in file: shinken_mailgun_plugin/util/email_settings.ini
* Update shinken configuration file commands.cfg with: shinken_mailgun_plugin/commands.cfg. Make necessary changes in templates.cfg for sending alerts.

