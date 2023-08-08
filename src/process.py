import numpy as np
import pandas as pd


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

    # create a stats dataframe with the counts and percentages for the answer column
    col_name_count = 'Number of groups'
    col_name_percentage = 'Percentage of groups'
    dset_stats = dset_melted['answer'].value_counts().to_frame(name=col_name_count)
    dset_stats[col_name_percentage] = np.round(100 * dset_stats[col_name_count] / dset.shape[0])

    # add 0 for count and percentage for option not present in dset_stats
    for opt in opts:
        if opt not in dset_stats.index:
            dset_stats.loc[opt, :] = 0

    # set the index name to the question text
    dset_stats.index.name = setup[qst]["text"]

    return dset_stats
