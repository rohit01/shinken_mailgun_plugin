import logging
from ConfigParser import ConfigParser
from ConfigParser import NoOptionError
from ConfigParser import NoSectionError
from ConfigParser import Error
from logging.handlers import SysLogHandler


TOTAL_KEY = '_total'
PREFIX_KEY = '_prefix'
POSTFIX_KEY = '_postfix'


def get_logger(facility=None):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if facility:
        syslog = SysLogHandler(address='/dev/log', facility=facility)
        formatter = logging.Formatter('%(name)s: %(levelname)s %(message)r')
        syslog.setFormatter(formatter)
        logger.addHandler(syslog)
    return logger


class ConfigManagement(object):
    def __init__(self, filename, mandatory_sections=['master', 'slave'],
                 list_sections=['slave'], section_schema=None, logger=None):
        if logger is not None:
            self.logger = logger
        else:
            self.logger = get_logger()
        self.logger.info("Logger initialized in __init__()")
        self.hosts_file = filename
        if mandatory_sections is None:
            self.mandatory_sections = []
        else:
            self.mandatory_sections = mandatory_sections
        if list_sections is None:
            self.list_sections = []
        else:
            self.list_sections = list_sections
        self.section_schema = section_schema
        self.prefix_store = {}
        self.postfix_store = {}

    def validate_config(self):
        config = ConfigParser()
        config.read(self.hosts_file)
        sections = config.sections()
        self.logger.debug("Validating mandatory sections")
        for section_name in self.mandatory_sections:
            if section_name not in sections:
                raise NoSectionError(section_name)
        self.logger.debug("Validating sections to be extracted as list")
        for section_name in self.list_sections:
            if section_name in sections:
                try:
                    count = config.getint(section_name, TOTAL_KEY)
                except NoOptionError:
                    self.logger.error("'%s' option not specified in mandatory"
                                      " list section '%s'" % (TOTAL_KEY,
                                                              section_name))
                    raise NoOptionError(TOTAL_KEY, section_name)
                try:
                    prefix = config.get(section_name, PREFIX_KEY)
                except NoOptionError:
                    prefix = section_name
                self.prefix_store[section_name] = prefix
                try:
                    postfix = config.get(section_name, POSTFIX_KEY)
                except NoOptionError:
                    postfix = ''
                self.postfix_store[section_name] = postfix
                for index in range(count):
                    index = index + 1
                    child_section = '%s%s%s' % (prefix, index, postfix)
                    try:
                        config.items(child_section)
                    except NoSectionError:
                        self.logger.error("'%s' section not specified for"
                                          " parent section '%s'. '%s' is a"
                                          " list section with count '%s'."
                                          % (child_section, section_name,
                                             section_name, count))
                        raise NoSectionError("'%s' section not specified for"
                                             " parent section '%s'. '%s' is a"
                                             " list section with count '%s'."
                                             % (child_section, section_name,
                                                section_name, count))
                    sections.remove(child_section)
                sections.remove(section_name)
        self.logger.debug("Validating sections are within ths section_schema,"
                          " if specified")
        if self.section_schema is not None:
            for section_name in self.section_schema:
                try:
                    sections.remove(section_name)
                except ValueError:
                    pass
            if len(sections) != 0:
                self.logger.error("'Invalid sections added. %s" % (sections))
                raise Error('Invalid sections added. %s' % (sections))

    def read_file(self):
        self.validate_config()
        config = ConfigParser()
        config.read(self.hosts_file)
        sections = config.sections()
        host_store = {}
        self.logger.debug("Extracting all List sections if mandatory, and"
                          " store it in host_store as a List with key value as"
                          " list section_name")
        for section_name in self.list_sections:
            if section_name in sections:
                count = config.getint(section_name, TOTAL_KEY)
                try:
                    prefix = config.get(section_name, PREFIX_KEY)
                except NoOptionError:
                    prefix = section_name
                try:
                    postfix = config.get(section_name, POSTFIX_KEY)
                except NoOptionError:
                    postfix = ''
                host_store[section_name] = []
                for index in range(count):
                    index = index + 1
                    child_section = '%s%s%s' % (prefix, index, postfix)
                    items = config.items(child_section)
                    host_store[section_name].append(dict(items))
                    sections.remove(child_section)
                sections.remove(section_name)
        self.logger.debug("Extracting all other configurations from file and "
                          "store it as a dictionary with key value as"
                          " section_name")
        for section_name in sections:
            items = config.items(section_name)
            host_store[section_name] = dict(items)
        return host_store

    def update_file(self, updated_host_store):
        host_store = updated_host_store.copy()
        config = ConfigParser()
        self.logger.debug("verifying mandatory_sections")
        all_sections = host_store.keys()
        for section_name in self.mandatory_sections:
            if section_name not in all_sections:
                self.logger.error("mandatory section '%s' not present."
                                  % (section_name))
                raise KeyError
        del all_sections
        self.logger.debug("Parsing list_sections")
        for section_name in self.list_sections:
            if section_name in host_store:
                config.add_section(section_name)
                count = len(host_store[section_name])
                config.set(section_name, TOTAL_KEY, count)
                try:
                    prefix = self.prefix_store[section_name]
                    config.set(section_name, PREFIX_KEY, prefix)
                except KeyError:
                    prefix = section_name
                try:
                    postfix = self.postfix_store[section_name]
                    config.set(section_name, POSTFIX_KEY, postfix)
                except KeyError:
                    postfix = section_name
                index = 1
                for child_section in host_store[section_name]:
                    child_section_name = '%s%s%s' % (prefix, index, postfix)
                    config.add_section(child_section_name)
                    for item_key in child_section.keys():
                        value = child_section[item_key]
                        config.set(child_section_name, str(item_key), value)
                    index = index + 1
                host_store.pop(section_name)
        self.logger.debug("Add non list sections to dictionary")
        for section_name in host_store.keys():
            config.add_section(section_name)
            section = host_store[section_name]
            for item_key in section.keys():
                value = section[item_key]
                config.set(section_name, str(item_key), value)
        self.logger.debug("Update config to file: '%s'" % (self.hosts_file))
        try:
            with open(self.hosts_file, 'wb') as configfile:
                self.logger.debug("File sucessfully opened: '%s'"
                                  % (self.hosts_file))
                config.write(configfile)
                self.logger.info("Config file sucessfully updated: '%s'"
                                 % (self.hosts_file))
        except:
            self.logger.exception("Exception in updating config to file: '%s'"
                                  % (self.hosts_file))
