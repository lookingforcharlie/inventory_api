# For large and complex project, configparser and .ini file combination will be a good approach
# How to use: 'from config import config' in the main.py allows you access the variables in .ini file
# will parse the database.ini and will return everything there in the form of dictionary
# so main.py will read value in database.ini from here

from configparser import ConfigParser


def config(filename='database.ini', section='postgresql') -> dict:
    # create a parser
    parser = ConfigParser()
    # read database.ini file
    parser.read(filename)
    db = {}
    # section is the first line inside database.ini file
    if parser.has_section(section):
        # iterate over the file, return a list of tuple contains key-value pairs
        params = parser.items(section)
        # print(f'params is {params}, \n type of params is {type(params)}')
        for param in params:
            # assign each ele inside database.ini inside the db dict
            db[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} is not found in the {filename}')
    # print(f'db dict is {db}')
    return db


# config()
