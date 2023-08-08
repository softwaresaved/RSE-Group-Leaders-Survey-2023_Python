""" Utility functions for I/O """

import json
import pandas as pd


def read_setup_and_data(fname_responses='survey_responses',
                        fname_setup='survey_setup',
                        path='../data/raw/',
                        index_col=0,
                        verbose=False
                        ):
    """ Read in the setup and data files.
    Args:
        fname_responses (str): name of the responses file, default 'survey_responses'
        fname_setup (str): name of the setup file, default 'survey_setup'
        path (str): path to the setup and data files, default '../data/raw/'
        index_col (int): index column, default 0
        verbose (bool): default False
    Returns:
        setup (dict): setup dictionary
        dset (pd.DataFrame): data frame of the survey responses
    """
    rfname = f"{path}{fname_responses}.csv"
    sfname = f"{path}{fname_setup}.json"

    dset = pd.read_csv(rfname, index_col=index_col)
    setup = json.load(open(sfname, "r"))

    if verbose:
        print(f"Read survey responses from {rfname}")
        print(f"Read survey setup from {sfname}")

    return setup, dset


def read_group_names(fname,
                     path='../data/raw/',
                     verbose=False):
    """ Read in the group names.
    Args:
        fname (str): name of the group names file
        path (str): path to the setup and data files
        verbose (bool): default False
    Returns:
        dset (pd.DataFrame): data frame of the group names
    """
    fname = f"{path}{fname}.csv"
    dset = pd.read_csv(fname)
    if verbose:
        print(f"Read group names from {fname}")

    return dset


def save_dataset(dset,
                 fname='survey_responses_processed',
                 path='../data/processed/',
                 verbose=False):
    """ Save the data frame of the survey responses.
    Args:
        dset (pd.DataFrame): data frame of the survey responses
        path (str): path to the setup and data files
        fname (str): name of the data file
    """
    fname = f"{path}{fname}.csv"
    dset.to_csv(fname)
    if verbose:
        print(f"Saved processed survey responses to {fname}")


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
