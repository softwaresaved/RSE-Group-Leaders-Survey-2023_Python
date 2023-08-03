""" Utility functions for data processing. """

import json
import pandas as pd


def read_setup_and_data(path='../data/raw/',
                        fname_setup='survey_setup',
                        fname_data='rse_group_survey_2023_responses'):
    """ Read in the setup and data files.
    Args:
        path (str): path to the setup and data files
        fname_setup (str): name of the setup file
        fname_data (str): name of the data file
    Returns: 
        setup (dict): setup dictionary
        dset (pd.DataFrame): data frame of the survey responses
    """
    dset = pd.read_csv(f"{path}{fname_data}.csv", index_col=0)
    setup = json.load(open(f"{path}{fname_setup}.json", "r"))

    return setup, dset


def validate_setup_and_data(setup, dset):
    """ Validate the setup and data files.
    Args:
        setup (dict): setup dictionary
        dset (pd.DataFrame): data frame of the survey responses
    Returns:
        validated (bool): True if setup and data are valid
    """
    validated = True

    # Check that the setup and data have the same number of questions
    if len(setup.keys()) != dset.shape[1]:
        validated = False
        print("ERROR: setup and data files do not have the same number of questions.")

    for iqst, qst in enumerate(dset.columns):
        if qst != setup[f"q{iqst+1}"]["text"]:
            validated = False
            print(f" ERROR: question {iqst+1} in setup and data files do not match.")

    return validated
