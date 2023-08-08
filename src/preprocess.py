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
