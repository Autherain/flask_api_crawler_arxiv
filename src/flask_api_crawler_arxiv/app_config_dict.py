""" Load configuration parameters from files and environnement variables.

Notes
-----
Data is loaded from '.env.default' file, the '.env' file. 
If a variable is already in a previous file, it's overwritten. 
If a file does'nt exist, no exception is raised.


Attributes
------
app_config : dict
    The dictionnary with the parameters to use.
"""

from dotenv import dotenv_values, find_dotenv

app_config = {**dotenv_values(find_dotenv())}
