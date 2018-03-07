import pandas as pd
import re
import difflib


class CorpusTextSearch():
    """
    This class is initialized with a searchstring, the name of the column,
    which contains the textstrings, and a path to a pickled dataframe.
    Optionally, a path to an excel file containing metadata can be provided.

    For other import formats change read_pickle and read_excel accordingly.

    Example:
            >>> search1 = SearchPhrases(
                            '[Ss]ol','text,'/path/to/kepler/dataframe'
                            )
            True
    """

    def __init__(
            self, pathDF,
            dataType='pickle', dataIndex='multi', colname='text',
            searchstring=False, pathMeta=False
            ):

        self.datatype = dataType

        if self.datatype == 'pickle':
            self.dataframe = pd.read_pickle(pathDF)
        elif self.datatype == 'excel':
            self.dataframe = pd.read_excel(pathDF)
        elif self.datatype == 'csv':
            self.dataframe = pd.read_csv(pathDF)
        elif self.datatype == 'json':
            self.dataframe = pd.read_json(pathDF)
        else:
            raise ValueError(
                'Please provide data in pickle,excel,csv or json format'
                )

        self.extData = ''

        self.dataindex = dataIndex

        self.levelValues = {}

        if searchstring:
            self.Kstr = searchstring
            self.result = self.dataframe[
                            self.dataframe[self.column].str.contains(self.Kstr)
                            ]
        else:
            self.Kstr = ''
            self.result = ''

        if pathMeta:
            self.metaData = pd.read_excel(pathMeta)
        else:
            self.metaData = ''

    def resetColWidth(self):
        """ Reset pandas display option for max_colwidth"""
        pd.reset_option('display.max_colwidth')
        return

    def reduce(self, level, value):
        """ Return reduced dataframe for search tuple (level/column,value):
            a) as cross-section for multi-index dataframe:
               df.xs(value,level=level)
            b) as sub-dataframe for single-index dataframe:
               df[df.column == value]

            Result is in self.result, to be able to chain reductions.
            To view result use self.results()
        """
        if self.dataindex == 'multi':
            if level in ['part', 'volume']:
                if level not in self.levelValues.keys():
                    self.levelValues[level] = self.dataframe.index.get_level_values(level).unique()
                else:
                    pass
                if value not in self.levelValues[level]:
                    closestMatch = difflib.get_close_matches(value, self.levelValues[level],1)
                    if closestMatch:
                        searchValue = closestMatch[0]
                    else:
                        raise ValueError(
                            'Could not find matching expression to search.'
                            )
                else:
                    searchValue = value
                if type(self.result) == str:
                    self.result = self.dataframe.xs(searchValue, level=level)
                else:
                    self.result = self.result.xs(searchValue, level=level)
            else:
                if type(self.result) == str:
                    self.result = self.dataframe.xs(value, level=level)
                else:
                    self.result = self.dataframe.xs(value, level=level)
            return self

    def results(self):
        """Returns the search result as a single-index dataframe."""
        if self.dataindex == 'multi':
            self.indexLevels = list(self.result.index.names)
            formatedResult = self.result.reset_index(level=self.indexLevels)
        pd.set_option('display.max_colwidth', -1)
        return formatedResult

    def extResults(self, level):
        """
        Returns the search result as a single-index dataframe, extend with
        metadata on the desired level. The metadata is calculated for all other
        levels of multi-indexed dataframe.
        """
        self.extData = pd.merge(left=self.results(), right=self._metaData(level), on=level)
        cols = [x for x in self.extData.columns if x != self.column]
        cols = cols + [self.column]
        self.extData = self.extData[cols]
        pd.set_option('display.max_colwidth', -1)
        return self.extData

    def _countWords(self, level, value):
        """Helper function to count words on a given level."""
        text = ' '.join(self.dataframe.xs(value, level=level).text.tolist())
        numWords = len(re.findall('\w+', text))
        return numWords

    def _getStatistics(self, level):
        """Helper function to return statistics on given level."""
        retDict = {}
        subLevels = self.indexLevels.copy()
        try:
            subLevels.remove(level)
        except ValueError:
            print('{0} not in index'.format(level))

        for part in self.dataframe.index.get_level_values(level).unique():
            partDict = {}
            for subLevel in subLevels:
                num = len(self.dataframe.xs(part, level=level).index.get_level_values(subLevel).unique())
                if num > 1:
                    partDict['Num_' + subLevel] = num
            partDict['words'] = self._countWords(level, part)
            retDict[part] = partDict
        return retDict

    def _metaData(self, level):
        """Helper function to generate dataframe from statistics."""
        resDict = self._getStatistics(level)
        self.metaDataFrame = pd.DataFrame(resDict).fillna('1').astype('int').transpose().reset_index().rename({'index': level}, axis=1)
        return self.metaDataFrame
