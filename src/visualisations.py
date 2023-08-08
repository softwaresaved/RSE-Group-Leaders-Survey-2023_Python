
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from IPython.display import display, Markdown

FIGURE_BGCOLOR = 'white'
BARS_COLOUR = 'tab:blue'
SCATTER_COLOUR = 'tab:blue'

# set the precision for printing datasets
pd.set_option('precision', 0)


def build_title(qst, setup):
    """ Build the title for the visualisations.

    Args:
        qst (str): question number
        setup (dict): setup dictionary

    Returns:
        title (str): title for the visualisation
    """

    return f"{qst.upper()}: {setup[qst]['text'].replace(':', '')}"


def plot_hbarchart(dset,
                   stat='count',
                   xlabel="",
                   title=""
                   ):
    """ Plot a horizontal bar chart of counts or percentages.

    Args:
        dset (pd.DataFrame): data frame to plot,
                             assumes first column is a count, second column is a percentage
        stat (str): stat type to plot, default 'count'
        ylabel (str): y-axis label, default ""
        title (str): barchart title, default ""
    """

    if stat == 'count':
        y = dset.columns[0]
    else:
        y = dset.columns[1]

    dset.plot.barh(y=y,
                   color=BARS_COLOUR,
                   title=title,
                   legend=False
                   )
    plt.ylabel(xlabel)
    plt.xlabel(y)
    plt.tick_params(axis="both", which="major", length=0)
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.gcf().set_facecolor(FIGURE_BGCOLOR)
    if stat != 'count':
        plt.xlim(0, 100)
    plt.show()


def plot_hsbarchart(dset,
                    xlabel="",
                    title=""
                    ):
    """ Plot a stacked horizontal bar chart .

    Args:
        dset (pd.DataFrame): data frame to plot,
                             assumes first column is a count, second column is a percentage
        stat (str): stat type to plot, default 'count'
        ylabel (str): y-axis label, default ""
        title (str): barchart title, default ""
    """

    dset.plot.barh(title=title,
                   stacked=True,
                   )
    plt.ylabel(xlabel)
    plt.tick_params(axis="both", which="major", length=0)
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.gcf().set_facecolor(FIGURE_BGCOLOR)
    plt.gcf().set_size_inches(10, 10)
    plt.legend(bbox_to_anchor=(0.5, 1.1), loc='upper center', ncol=3)

    plt.show()


def plot_scatter(dset, setup, columns, title=""):
    # plot scatter plot of sorted values
    qst = columns[1]
    dset2plot = dset[columns].copy()
    dset2plot = dset2plot.sort_values(by=qst)
    dset2plot = dset2plot.dropna(subset=[qst])
    dset2plot.plot.scatter(x=qst,
                           y=columns[0],
                           xlabel="",
                           ylabel="",
                           color=SCATTER_COLOUR,
                           title=f"{title} (N = {dset2plot.shape[0]})")
    plt.gcf().set_size_inches(10, 10)
    plt.tick_params(axis="both", which="major", length=0)
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.gcf().set_facecolor(FIGURE_BGCOLOR)
    plt.show()

    dset2plot.columns = [setup[col]["text"] for col in columns]
    dset2plot.set_index(dset2plot.columns[0], inplace=True)

    return dset2plot


def print_answers(dset, setup, columns):
    # print the values in the qst column
    dset2print = dset[columns].copy()
    dset2print = dset2print.fillna('')
    dset2print.set_index(columns[0], inplace=True)

    dset2print.index.name = setup[dset2print.index.name]["text"]
    dset2print.columns = [setup[dset2print.columns[0]]["text"]]
    display(Markdown(dset2print.to_markdown(tablefmt="github")))

    return dset2print
