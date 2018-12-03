# -*- coding: utf-8 -*-
import yaml
from IPython.display import HTML
import time
import os
import numpy as np
import pandas as pd
from .base import Citable


def getName(doi):
    parts = doi.split('.')[0].split('_')
    if len(parts) > 2:
        name = '_'.join(parts[:-1])
    elif len(parts) > 1:
        name = '_'.join(parts)
    else:
        name = parts[0]
    return name


def collectionResources(project=False, formats='local'):
    """
    Return all resources for local research project.
    """
    if formats == 'local':
        if project is False:
            print("Please set project='NAME' parameter, trying to guess data path and project name...")
            dataPath = '..' + os.sep + 'data'
            project = os.getcwd().split(os.sep)[-3]
        else:
            docPath = os.path.expanduser('~') + '/ResearchCloud/Documentation'
            try:
                with open('{0}/{1}.yml'.format(docPath, project)) as file:
                    doc = yaml.load(file)
                dataPath = os.path.expanduser(doc['dataFolder'])
            except FileNotFoundError as error:
                print("Could not read 'dataFolder' key in project {0}.yml file in {1}. Does it exist?".format(self.project, self.docPath))
                raise

        dataList = []
        allFiles = os.listdir(dataPath)
        for file in allFiles:
            name = getName(file)
            if name + '_documentation.json' in allFiles:
                if name + '_metadata.json' in allFiles:
                    dataList.append(file)
        dataList = [x for x in dataList if not ('_metadata' in x or '_documentation' in x)]
        return dataList
    else:
        if formats != 'local':
            cite = Citable(project, formats=formats)
            return cite.resource()


class Credentials(object):
    """
    Create title page for notebook.
    Assumes certain folder structure.

    User metadate is stored in self.docPath. Each author has a yaml-File
    `author.yml` with the structure:

    name: Name
    firstnames: First Names
    institutions:
        - listed
        - affiliations
    email: mail@example.com
    """

    def __init__(
            self,
            authors,
            project,
            title,
            corresponding=False,
            abstract=False,
            pubDate=False
            ):

        self.authorsList = authors
        self.project = project
        self.title = title
        if pubDate:
            self.date = pubDate
        else:
            self.date = time.strftime("%d. %B %Y")
        self.corresponding = corresponding
        self.abstract = abstract
        self.docPath = os.path.expanduser('~') + '/ResearchCloud/Documentation'
        self._readAuthorInfo()

    def _readAuthorInfo(self):
        self.authors = {}
        for author in self.authorsList.split(','):
            with open('{0}/{1}.yml'.format(self.docPath, author)) as file:
                doc = yaml.load(file)
                self.authors[author] = doc

    def _readProjectInfo(self):
        with open('{0}/{1}.yml'.format(self.docPath, self.project)) as file:
            doc = yaml.load(file)
            self.projectInfo = doc

    def _readCorrespondingMails(self):
        mail = ''
        for cor in self.corresponding.split(','):
            mail += self.authors[cor]['email']
        return mail

    def titlepage(self):
        template = """
        <h1>{title}</h1>
        <h2>{authors}</h2>
        {affiliations}<br>
        """
        authorRep = ''
        instList = []

        for key in self.authors.keys():
            instList.extend(self.authors[key]['institutions'])
        instRep = {x + 1: y for x, y in enumerate(list(set(instList)))}
        revInst = {y: x for x, y in enumerate(list(set(instList)))}
        affRep = '; '.join(['{0}: {1}'.format(x, y) for x, y in instRep.items()])
        for key in self.authors.keys():
            keys = sorted([str(revInst[x] + 1) for x in self.authors[key]['institutions']])
            authTemp = self.authors[key]['firstnames'] + ' ' + self.authors[key]['name'] + '<sup>' + ','.join(keys) + '</sup>, '
            authorRep += authTemp
        output = template.format(title=self.title, authors=authorRep[:-2], affiliations=affRep)
        if self.corresponding:

            output += "Corresponding author(s): {0}<br>Date: {1}".format(self._readCorrespondingMails(), self.date)
        else:
            output += "Date: {0}".format(self.date)
        if self.abstract:
            output += "<br><h3>Abstract:</h3><p>{0}</p>".format(self.abstract)
        return HTML(output)


class Json2DF():
    """
    Convert nested dataframe to multilevel, non-nested dataframe,
    e.g. for dataframes from json via pd.read_json() method.
    """

    def __init__(self, dataframe, multiindex, level=100):
        self.dataframe = dataframe
        self.multiindex = multiindex
        self.level = level
        self.counter = 0

    def explodeDF(self, x, lst_col):
        try:
            dfNonList = x[x[lst_col].apply(type) != list]
            dfList = x[x[lst_col].apply(type) == list]
            dfExpList = pd.DataFrame({
                col: np.repeat(dfList[col].values, dfList[lst_col].str.len()) for col in dfList.columns.difference([lst_col])
            }).assign(**{lst_col: np.concatenate(dfList[lst_col].values)})[dfList.columns.tolist()]
            if dfNonList.shape[0] != 0:
                df = pd.concat([dfNonList, dfExpList], sort=False)
            else:
                df = dfExpList
        except:
            df = x
        try:
            dfNonDict = df[df[lst_col].apply(type) != dict]
            dfDict = df[df[lst_col].apply(type) == dict]
            dfExp = dfDict.drop(lst_col, 1).assign(**pd.DataFrame(dfDict[lst_col].values.tolist()))
            if dfNonDict.shape[0] != 0:
                df = pd.concat([dfNonDict, dfExp], sort=False)
            else:
                df = dfExp
        except:
            pass
        self.dataframe = df
        return

    def resolve2multi(self):
        if self.counter < self.level:
            self.counter += 1
            colTypeList = [(col, set(x for x in self.dataframe[col].apply(type).values)) for col in self.dataframe.columns]
            for col, typ in colTypeList:
                if list in typ or dict in typ:
                    self.explodeDF(self.dataframe, col)
                    return self.resolve2multi()
            return
        else:
            return

    def setLevels(self):
        self.dataframe = self.dataframe.set_index(self.multiindex).sort_index()
        self.dataframe = self.dataframe.dropna(how='all', axis=1)

    def convert(self):
        self.resolve2multi()
        self.setLevels()
        return
