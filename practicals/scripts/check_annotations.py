import matplotlib
matplotlib.use('Agg')
import re
import argparse
from datetime import datetime, timedelta, time
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import itertools
from sklearn.metrics import confusion_matrix

ANNO_LABEL_DICT = 'annotation-label-dictionary.csv'

DOHERTY2018_DICT_COL = 'label:Doherty2018'
DOHERTY2018_COLOURS = {'sleep':'blue', 
                       'sedentary': 'red',
                       'tasks-light': 'darkorange',
                       'walking': 'lightgreen',
                       'moderate': 'green'}
DOHERTY2018_LABELS = list(DOHERTY2018_COLOURS.keys())

WILLETTS2018_DICT_COL = 'label:Willetts2018'
WILLETTS2018_COLOURS = {'sleep':'blue', 
                        'sit-stand': 'red',
                        'vehicle': 'darkorange',
                        'walking': 'lightgreen',
                        'mixed': 'green',
                        'bicycling': 'purple'}
WILLETTS2018_LABELS = list(WILLETTS2018_COLOURS.keys())

WALMSLEY2020_DICT_COL = 'label:Walmsley2020'
WALMSLEY2020_COLOURS = {'sleep':'blue', 
                       'sedentary': 'red',
                       'light': 'darkorange',
                       'moderate-vigorous': 'green'}
WALMSLEY2020_LABELS = list(WALMSLEY2020_COLOURS.keys())

IMPUTED_COLOR = '#fafc6f'  # yellow
UNCODEABLE_COLOR = '#d3d3d3' # lightgray
BACKGROUND_COLOR = '#d3d3d3' # lightgray


def annotationSimilarity(anno1, anno2):
    ''' Naive sentence similarity '''
    DELIMITERS = ";|, | "
    words1 = re.split(DELIMITERS, anno1)
    words2 = re.split(DELIMITERS, anno2)
    shared_words = set(set(words1) & set(words2))
    similarity = len(shared_words) / len(words1)  # why words1 and not words2? how about averaging?
    return similarity


def nearestAnnotation(annoList, annoTarget, threshold=.8):
    similarities = [annotationSimilarity(annoTarget, _) for _ in annoList]
    if np.max(similarities) < threshold:
        print(f"No similar annotation found in dictionary for: '{annoTarget}'")
        return None
    return annoList[np.argmax(similarities)]


def buildLabelDict(labelDictCSV, labelDictCol):
    df = pd.read_csv(labelDictCSV, usecols=['annotation', labelDictCol])
    labelDict = {row['annotation']:row[labelDictCol] for i,row in df.iterrows()}
    return labelDict


def annotateTsData(tsData, annoData, labelDict):
    tsData['annotation'] = 'undefined'

    t = tsData['time'].dt.tz_localize(None)
    for i, row in annoData.iterrows():
        start, end = row['startTime'].tz_localize(None), row['endTime'].tz_localize(None)
        annotation = nearestAnnotation(list(labelDict.keys()), row['annotation'])
        label = labelDict.get(annotation, 'uncodeable')
        tsData.loc[(t > start) & (t < end), 'annotation'] = label


def gatherPredictionLabels(tsData, labels):
    tsData['prediction'] = 'undefined'
    tsData.loc[tsData['imputed'] == 1, 'prediction'] = 'imputed'
    for label in labels:
        tsData.loc[(tsData[label] > 0) & (tsData['imputed'] == 0), 'prediction'] = label


def formatXYaxes(ax, day, ymax, ymin):
    # run gridlines for each hour bar
    ax.get_xaxis().grid(True, which='major', color='grey', alpha=0.5)
    ax.get_xaxis().grid(True, which='minor', color='grey', alpha=0.25)
    # set x and y-axes
    ax.set_xlim((datetime.combine(day,time(0, 0, 0, 0)),
        datetime.combine(day + timedelta(days=1), time(0, 0, 0, 0))))
    ax.set_xticks(pd.date_range(start=datetime.combine(day,time(0, 0, 0, 0)),
        end=datetime.combine(day + timedelta(days=1), time(0, 0, 0, 0)),
        freq='4H'))
    ax.set_xticks(pd.date_range(start=datetime.combine(day,time(0, 0, 0, 0)),
        end=datetime.combine(day + timedelta(days=1), time(0, 0, 0, 0)),
        freq='1H'), minor=True)
    ax.set_ylim((ymin, ymax))
    ax.get_yaxis().set_ticks([]) # hide y-axis lables
    # make border less harsh between subplots
    ax.spines['top'].set_color(BACKGROUND_COLOR)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    # set background colour to lightgray
    ax.set_facecolor(BACKGROUND_COLOR)


def splitByTimeGap(group, seconds=30):
    subgroupIDs = (group.index.to_series().diff() > timedelta(seconds=seconds)).cumsum()
    subgroups = group.groupby(by=subgroupIDs)
    return subgroups


def confusionMatrix(tsData, labels, normalize=False, include_uncodeable_imputed=False):
    tsData = tsData.loc[tsData['annotation'] != 'undefined']
    y_true = tsData['annotation'].values
    y_pred = tsData['prediction'].values

    # Compute confusion matrix -- include 'uncodeable' & 'imputed'
    cmLabels = labels
    if include_uncodeable_imputed:
        cmLabels += ['uncodeable', 'imputed']
    cm = confusion_matrix(y_true, y_pred, labels=cmLabels)
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    return cm, cmLabels


def plotTimeSeries(tsData, labels, labelColors=None, plotFile='sample'):
    convert_date = np.vectorize(lambda day, x: matplotlib.dates.date2num(datetime.combine(day, x)))

    groups = tsData.groupby(by=tsData.index.date)

    ndays = len(groups)
    nrows = 3*ndays + 1  # ndays x (prediction + annotation + spacing) + legend
    fig = plt.figure(figsize=(10,nrows), dpi=200)
    gs = fig.add_gridspec(nrows=nrows, ncols=1, height_ratios=[2, 2, 1]*ndays+[2])
    axes = []
    for i in range(nrows):
        if (i+1) % 3 == 0: continue  # do not add the axis corresp. to the spacing
        axes.append(fig.add_subplot(gs[i]))

    if labelColors is None:
        color_cycle = itertools.cycle(plt.rcParams['axes.prop_cycle'].by_key()['color'])
        labelColors = dict(zip(labels, color_cycle))
    colors = [labelColors[l] for l in labels]

    ymin = tsData['acceleration'].min()
    ymax = tsData['acceleration'].max()

    for i, (day, group) in enumerate(groups):

        axPred, axAnno = axes[2*i], axes[2*i+1]

        # plot acceleration
        t = convert_date(day, group.index.time)
        axPred.plot(t, group['acceleration'], c='k')

        # plot predicted
        ys = [(group['prediction'] == l).astype('int') * ymax for l in labels]
        axPred.stackplot(t, ys, colors=colors, alpha=.5, edgecolor='none')
        axPred.fill_between(t, (group['prediction'] == 'imputed').astype('int') * ymax,
            facecolor=IMPUTED_COLOR)

        # plot annotated
        ys = [(group['annotation'] == l).astype('int') * ymax for l in labels]
        axAnno.stackplot(t, ys, colors=colors, alpha=.5, edgecolor='none')
        axAnno.fill_between(t, (group['annotation']=='uncodeable').astype('int') * ymax,
            facecolor=UNCODEABLE_COLOR, hatch='//')

        axPred.set_ylabel('predicted', fontsize='x-small')
        axAnno.set_ylabel('annotated', fontsize='x-small')
        formatXYaxes(axPred, day, ymax, ymin)
        formatXYaxes(axAnno, day, ymax, ymin)
        # add date to left hand side of each day's activity plot
        axPred.set_title(
            day.strftime("%A,\n%d %B"), weight='bold',
            x=-.2, y=-.3,
            horizontalalignment='left',
            verticalalignment='bottom',
            rotation='horizontal',
            transform=axPred.transAxes,
            fontsize='medium',
            color='k'
        )

    # legends
    axes[-1].axis('off')
    # create a 'patch' for each legend entry
    legend_patches = []
    legend_patches.append(mlines.Line2D([], [], color='k', label='acceleration'))
    legend_patches.append(mpatches.Patch(facecolor=IMPUTED_COLOR, label='imputed/nonwear'))
    legend_patches.append(mpatches.Patch(facecolor=UNCODEABLE_COLOR, hatch='//', label='not in dictionary'))
    # create legend entry for each label
    for label in labels:
        legend_patches.append(mpatches.Patch(facecolor=labelColors[label], label=label, alpha=0.5))
    # create overall legend
    axes[-1].legend(handles=legend_patches, bbox_to_anchor=(0., 0., 1., 1.),
        loc='center', ncol=min(4,len(legend_patches)), mode="best",
        borderaxespad=0, framealpha=0.6, frameon=True, fancybox=True)
    # remove legend border
    axes[-1].spines['left'].set_visible(False)
    axes[-1].spines['right'].set_visible(False)
    axes[-1].spines['top'].set_visible(False)
    axes[-1].spines['bottom'].set_visible(False)

    # format x-axis to show hours
    fig.autofmt_xdate()
    # add hour labels to top of plot
    hrLabels = ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00']
    axes[0].set_xticklabels(hrLabels)
    axes[0].tick_params(labelbottom=False, labeltop=True, labelleft=False)

    fig.savefig(plotFile, dpi=200, bbox_inches='tight')
    print('Timeseries plot file:', plotFile)


def plotConfusionMatrix(cm, cmLabels, title=None, plotFile='sample'):
    """ https://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html """

    fig, ax = plt.subplots()
    ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    ax.set(xticks=np.arange(cm.shape[1]),
           yticks=np.arange(cm.shape[0]),
           xticklabels=cmLabels, yticklabels=cmLabels,
           ylabel='camera annotation',
           xlabel='model prediction')
    if title is not None: ax.set_title(title)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    fmt = '.2f' if np.issubdtype(cm.dtype, np.float64) else 'd'
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], fmt),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black")
    fig.tight_layout()

    fig.savefig(plotFile, dpi=200, bbox_inches='tight')
    print('Confusion matrix plot file:', plotFile)


def date_parser(t):
    ''' Parse date a date string of the form e.g
    2020-06-14 19:01:15.123+0100 [Europe/London] '''
    # tz = re.search(r'(?<=\[).+?(?=\])', t)
    # if tz is not None:
    #     tz = tz.group()
    t = re.sub(r'\[(.*?)\]', '', t)
    # return pd.to_datetime(t, utc=True).tz_convert(tz)
    return pd.to_datetime(t, utc=True)


def main(tsFile, annoFile, labelScheme, normalize, plotFile):
    annoData = pd.read_csv(args.annoFile, parse_dates=['startTime', 'endTime'])
    tsData = pd.read_csv(args.tsFile, parse_dates=['time'], date_parser=date_parser)

    # some minor refactoring
    tsData.rename(columns={'acc':'acceleration', 'MVPA':'moderate-vigorous'}, inplace=True)
    tsData.set_index('time', drop=False, inplace=True)

    if labelScheme == 'Doherty2018':
        labelColors = DOHERTY2018_COLOURS
        labelDict = buildLabelDict(ANNO_LABEL_DICT, DOHERTY2018_DICT_COL)
        labels = DOHERTY2018_LABELS
    elif labelScheme == 'Willetts2018':
        labelColors = WILLETTS2018_COLOURS
        labelDict = buildLabelDict(ANNO_LABEL_DICT, WILLETTS2018_DICT_COL)
        labels = WILLETTS2018_LABELS
    elif labelScheme == 'Walmsley2020':
        labelColors = WALMSLEY2020_COLOURS
        labelDict = buildLabelDict(ANNO_LABEL_DICT, WALMSLEY2020_DICT_COL)
        labels = WALMSLEY2020_LABELS
    else:
        raise ValueError(f'Unrecognized label scheme {labelScheme}')

    annotateTsData(tsData, annoData, labelDict)
    gatherPredictionLabels(tsData, labels)

    # smooth acceleration
    tsData['acceleration'] = tsData['acceleration'].rolling(window=12, min_periods=1).mean()
    # drop dates without any annotation
    annotatedDates = np.unique(tsData.index.date[tsData['annotation'] != 'undefined'])
    tsData = tsData.loc[np.isin(tsData.index.date, annotatedDates)]

    plotTimeSeries(tsData, labels, labelColors, '{}_timeseries.png'.format(plotFile))

    # compute & plot confusion matrix
    cm, cmLabels = confusionMatrix(tsData, labels, normalize)
    cmFile = '{}_confusion.npz'.format(args.plotFile)
    np.savez(cmFile, cm=cm, cmLabels=cmLabels)
    print('Confusion matrix .npz file: {}'.format(cmFile))
    plotConfusionMatrix(cm, cmLabels, None, '{}_confusion.png'.format(plotFile))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('tsFile', help='time series file with predictions by the model')
    parser.add_argument('annoFile', help='camera annotation file')
    parser.add_argument('--labelScheme', default='Walmsley2020')
    parser.add_argument('--normalize', action='store_true')
    parser.add_argument('--plotFile', default='image.png')
    args = parser.parse_args()

    args.plotFile = args.plotFile.split('.')[0]  # remove any extension
    main(args.tsFile, args.annoFile, args.labelScheme, args.normalize, args.plotFile)
