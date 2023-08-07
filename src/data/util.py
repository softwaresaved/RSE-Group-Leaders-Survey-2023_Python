""" Utility functions for data processing. """

import json
import numpy as np
import pandas as pd


def read_setup_and_data(path='../data/raw/',
                        fname_setup='survey_setup',
                        fname_data='rse_group_survey_2023_responses',
                        fname_group_names='renaming_for_groups'
                        ):
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

    dset_gnames = pd.read_csv(f"{path}{fname_group_names}.csv")

    return setup, dset, dset_gnames


def rename_groups(dset, dset_gnames):
    """ Rename the groups in the data frame of the survey responses
        to resolve ambiguities.
    Args:
        dset (pd.DataFrame): data frame of the survey responses
        dset_gnames (pd.DataFrame): data frame of the group names
    Returns:
        dset (pd.DataFrame): data frame of the survey responses with renamed groups
    """

    # original column order
    cols = list(dset.columns)

    # process the updated group names
    col = 'What is the name of your group?'
    dset_gnames = dset_gnames.drop(columns=[col, 'Is your group:'])
    dset_gnames = dset_gnames.rename(columns={'New name of group': col})

    # update the group names in the original dataset
    dset = dset.drop(columns=[col])
    dset = dset.reset_index().merge(dset_gnames, on='Name', how='left')
    dset = dset.set_index('Timestamp')

    # restore original column order
    dset = dset[cols]

    return dset


def save_dataset(dset,
                 fname='rse_group_survey_2023_responses_processed',
                 path='../data/processed/'):
    """ Save the data frame of the survey responses.
    Args:
        dset (pd.DataFrame): data frame of the survey responses
        path (str): path to the setup and data files
        fname (str): name of the data file
    """
    dset.to_csv(f"{path}{fname}.csv")


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


def preprocess_text(dset, setup, verbose=False):
    """ Process the text responses.
    Args:
        dset (pd.DataFrame): data frame of the survey responses
        setup (dict): setup dictionary
        verbose (bool): print the preprocessing steps, default False
    Returns:
        dset (pd.DataFrame): data frame of the survey responses

    """

    if verbose:
        print("\nPreprocessing text responses to")
        print("- fill empty cells with ''")
        print("- replace new line characters with spaces")

    for qst in setup.keys():
        if setup[qst]["type"] != "text":
            continue

        # fill the empty cells with ""
        dset[qst] = dset[qst].fillna("")
        # replace the new line characters with spaces
        dset[qst] = dset[qst].str.replace("\n", " ", regex=True)

    return dset


def preprocess_checkboxes(dset, setup, verbose=False):
    """ Process the checkbox responses.
    Args:
        dset (pd.DataFrame): data frame of the survey responses
        setup (dict): setup dictionary
    Returns:
        dset (pd.DataFrame): data frame of the survey responses
    """

    if verbose:
        print("\nPreprocessing checkbox responses to")
        print("- fill empty cells with ''")
        print("- replace ( with - and ) with ''")
        print("- create extra columns for each option, including Other if it exists")

    for qst in setup.keys():
        if setup[qst]["type"] != "checkbox":
            continue

        # fill the empty cells with ""
        dset[qst] = dset[qst].fillna("")

        # get the options and number of options
        opts = setup[qst]["options"]
        nopts = len(opts)

        # replace ( with - and ) with ""
        dset[qst] = dset[qst].str.replace("(", "- ", regex=True)
        dset[qst] = dset[qst].str.replace(")", "", regex=True)

        # check if none of the options are in the response and append "Other"
        dset[qst] = dset[qst].apply(lambda x: "Other, " + x
                                    if all(opt not in x for opt in opts)
                                    else x)

        # create extra columns for each option
        extra_cols = [f"{qst}_option_{iopt+1}" for iopt in range(nopts)]
        dset[extra_cols] = False
        for iopt, opt in enumerate(opts):
            dset.loc[dset[qst].str.contains(opt),
                     f"{qst}_option_{iopt+1}"] = True  # opt

        # if we have Other responses, create a new column and populate it
        # with the given other responses
        nother = dset[qst].str.contains("Other,").sum()
        if nother > 0:
            extra_column = f"{qst}_option_other"
            dset[extra_column] = ""
            dset.loc[dset[qst].str.contains("Other"), extra_column] = \
                dset.loc[dset[qst].str.contains("Other"), qst]
            dset.loc[:, extra_column] = dset.loc[:, extra_column].str.replace("Other, ", "")

    return dset


def derive_checkbox_stats(dset, setup, qst):
    """ Display the statistics for the checkbox responses.
    Args:
        dset (pd.DataFrame): data frame of the survey responses
        setup (dict): setup dictionary
        qst (str): question number
    """
    cols = [col for col in dset.columns if qst in col][1:]
    opts = setup[qst]["options"]

    # create a new dataframe with the melted values of these columns
    dset_melted = pd.melt(dset.reset_index(),
                          id_vars=['Timestamp'],
                          value_vars=cols,
                          var_name='answer')
    dset_melted = dset_melted[dset_melted['value'] == True]
    dset_melted = dset_melted.drop(columns=['value'])
    dset_melted = dset_melted.set_index('Timestamp')

    # replace the answer column with the option name
    dset_melted["answer"].replace(f"{qst}_option_", "", regex=True, inplace=True)
    dset_melted['answer'] = dset_melted['answer'].apply(lambda x: opts[int(x) - 1])

    # create a stats dataframe with the counts for the answer column
    dset_stats = dset_melted['answer'].value_counts().to_frame(name='count')
    dset_stats['percentage'] = np.round(100 * dset_stats['count'] / dset.shape[0])

    # add 0 for count and percentage for option not present in dset_stats
    for opt in opts:
        if opt not in dset_stats.index:
            dset_stats.loc[opt, :] = 0

    return dset_stats
