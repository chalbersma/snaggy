#!/usr/bin/env python3

'''
Read Configuration with Optional Defaults
'''

import time
import configparser
import ast

def read_config(configfile=False, configstring=False, default_population=False):

    # Read Config File and Return Dict of Info
    now_time=int(time.time())
    defaults= { "time" : str(now_time) }

    try:
        # Read Our INI with our data collection rules
        config = configparser.ConfigParser(defaults)
        #config = ConfigParser()
        if configfile != False :
            # Configuration File Given
            config.read(configfile)
        elif configstring != False :
            # Configuration String Given
            config.read_string(configstring)
        else :
            # Both are False I've recieved neither
            raise Exception("No Configuration Given")
    except Exception as e: # pylint: disable=broad-except, invalid-name
        sys.exit('Bad configuration file {}'.format(e))

    # DB Config Items
    config_dict=dict()
    for section in config:
        config_dict[section]=dict()
        if default_population != False and type(default_population) is dict :
            # Add the Default Items to the document
            for default_top_populate in default_population.keys():
                config_dict[section][default_top_populate] = default_population[default_top_populate]

        for item in config[section]:
            config_dict[section][item] = ast.literal_eval(config[section][item])

    #print(config_dict)

    return config_dict
