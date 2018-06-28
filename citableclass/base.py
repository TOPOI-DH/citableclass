# -*- coding: utf-8 -*-
from matplotlib.pyplot import *
import matplotlib.pyplot as plt
from IPython.display import HTML, Image, clear_output
import ipywidgets as widgets
from plyfile import PlyData, PlyElement
import requests
import urllib.request
import csv
import codecs
import pandas as pd
import re
import json
import os


class Citableloader(object):
    """
    Load resource via a DOI which points to a Citable:
      call the function:

        - resource = Citableloader(DOI)  #for a single DOI

      apply different methods on the resource (resource.func()):
        - resource.metadata()  #the corresponding metadata
        - resource.json() #load json file
        - resource.df() #load json file as pandas dataframe
        - resource.debook() # load pdf with interactive tool 'dEbook-Viewer'
        - resource.pdf() # load PDF with standard viewer
        - resource.imageshow() # load image and show
        - resource.imagesave() # save image in local folder
        - resource.csv() # load csv file
        - resource.collection() # load overview json (each collections has its own overview json)
        - resource.docu() # a short introduction of collection & citable
        - resource.landingpage() # shows to the landing page of DOI
        - resource.filename() # returns file name
        - resource.datatype() # returns type of data (e.g. jpg or pdf)
        - resource.resource() # returns all digital resources including DOI
        - resource.getdoi() # returns DOI

      example:
        - single DOI:
          r=Citableloader('10.17171/1-3-388-1')
          r.filename()

    """
    def __init__(self, doi, types):
        self.doVerify = True
        if types == "doi":
            self.url = 'https://dx.doi.org/'+doi
            self.response0 = requests.get(self.url, verify=self.doVerify)
            if self.response0.url.split('//')[0] == 'http:':
                self.landingpage_url = re.sub('CitableHandler', 'collection', re.sub('http', 'https', self.response0.url))
        if types == "et":
            collection = re.findall('[A-Z]{4}|[A-Z]{3}', doi)[0]
            number = re.sub(collection, '', doi)
            if '/' in number:
                self.url = 'https://repository.edition-topoi.org/CitableHandler/' + collection + '/single/' + number
            else:
                self.url = 'https://repository.edition-topoi.org/CitableHandler/' + collection + '/single/' + number + '/0'
            self.landingpage_url = re.sub('CitableHandler', 'collection', self.url)
            self.response0 = requests.get(self.url, verify=self.doVerify)
        if types == "dev":
            collection = re.findall('[A-Z]{4}|[A-Z]{3}', doi)[0]
            number = re.sub(collection, '', doi)
            if '/' in number:
                self.url = 'http://repositorytest.ancient-astronomy.org/CitableHandler/' + collection + '/single/' + number
            else:
                self.url = 'http://repositorytest.ancient-astronomy.org/CitableHandler/' + collection + '/single/' + number + '/0'
            self.landingpage_url = re.sub('CitableHandler', 'collection', self.url)
            self.response0 = requests.get(self.url, verify=self.doVerify)

        self.data = requests.get(self.response0.url + '?getDigitalFormat', verify=self.doVerify)
        self.alternatives = requests.get(self.response0.url + '?getAlternatives', verify=self.doVerify)
        self.alternativefile = requests.get(self.response0.url + '?getAlternativeFile', verify=self.doVerify)
        self.doi = doi
        r = self.response0.url
        try:
            r = r.split("https://repository.edition-topoi.org/")[1]
        except:
            if types in ['doi', 'et']:
                r = r.split("http://repository.edition-topoi.org/")[1]
            elif types == 'dev':
                r = r.split("http://repositorytest.ancient-astronomy.org/")[1]
        r = r.split('/')
        try:
            self.d = re.findall("filename=(.+)", self.data.headers['Content-disposition'])[0].replace('\"', '')
            if types in ['doi', 'et']:
                self.link = "http://repository.edition-topoi.org/"+r[1]+'/Repos'+r[1]+'/'+r[1]+r[3]+'/'+self.d
            elif types == 'dev':
                self.link = "http://repositorytest.ancient-astronomy.org/"+r[1]+'/Repos'+r[1]+'/'+r[1]+r[3]+'/'+self.d
        except:
            pass

    def description(self):
        try:
            return HTML('<iframe src=https://repository.edition-topoi.org/'+self.doi[:4]+'/Service'+self.doi[:4]+'/'+self.doi+'/documentation.pdf width=1200 height=550></iframe>')
        except:
            print("No description available. Please try metadata()")

    def getdoi(self):
        return self.doi

    def response(self):
        return self.response0.url + '?getDigitalFormat'

    def json(self):
        return self.data.json()

    def df(self):
        return pd.DataFrame(self.data.json())

    def alternativefiles(self):
        return pd.DataFrame(self.alternatives.json())

    def collection(self):
        return requests.get(self.response0.url + '?getOverallJSON', verify=self.doVerify).json()

    def status(self):
        try:
            obj = requests.get(self.response0.url + '?getDigitalFormats', verify=self.doVerify).json()
            try:
                res = {
                    "Object": obj["General Information"]["Identifier"],
                    "Status": obj["General Information"]["Status"],
                    "Version": obj["General Information"]["Dev-Version"]
                    }
                return res
            except:
                print("digital resource has publication status")
        except:
            print('Can not find object.')


    def metadata(self):
        b = requests.get(self.response0.url + '?getDigitalFormats', verify=self.doVerify).json()
        c = list(b.keys())
        finallist = []
        for j in range(len(c)):
            try:
                gi = list(b[c[j]].keys())
                finallist.append((c[j].upper(), ""))
                for i in range(len(gi)):
                    finallist.append((gi[i], b[c[j]][gi[i]]))
            except:
                pass
        pd.set_option('max_colwidth', -1)
        df = pd.DataFrame(finallist)
        df.columns = [' ', '']
        df.set_index([' '], drop=True, inplace=True)
        df = df.style.set_properties(**{'text-align': 'left'})
        return df

    def filename(self):
        return self.d

    def datatype(self):
        try:
            f = requests.get(self.response0.url + '?getDigitalFormats', verify=self.doVerify).json()
            if 'Format' in f['Technical characteristics']:
                ret = f['Technical characteristics']['Format']
            elif 'Resource Type' in f['Technical characteristics']:
                ret = f['Technical characteristics']['Resource Type']
        except:
            raise ValueError("Can not determine regular format!")
        return ret

    def pdf(self):
        return HTML('<iframe src='+self.link+' width=900 height=550></iframe>')

    def debook(self):
        return HTML('<iframe src=''https://edition-topoi.org/dEbook/?pdf='+self.link+' + width=100% height=650></iframe>')

    def imageshow(self, w=500, h=500):
        data = requests.get(self.response0.url + '?getDigitalFormat', verify=self.doVerify)
        return Image(url=data.url, width=w, height=h)

    def imagesave(self, name="temp.jpg"):
        data = requests.get(self.response0.url + '?getDigitalFormat', verify=self.doVerify)
        with open(name, 'wb') as file:
            file.write(data.content)
        return name

    def digilib(self, w=1500, h=1950):
        path = self.response0.url+'#tabMode'
        path = path.replace('CitableHandler', 'collection')
        return HTML('<iframe src='+path+' + width=100% height=650></iframe>')

    def csv(self):
        text = self.data.iter_lines()
        ret = csv.reader(codecs.iterdecode(text, 'utf8'), delimiter=',')
        return ret

    def excel(self, name='./temp.xlsx'):
        data = self.data.content
        with open(name, 'wb') as file:
            file.write(data)
        return name

    def pickle(self, name='./temp.pickle'):
        data = self.data.content
        with open(name, 'wb') as file:
            file.write(data)
        return name

    def threedget(self, buttonInstance=False, filePath=False, dataTyp=False):
        files = self.alternatives.json()
        try:
            self.threedFormat
        except:
            self.threedFormat = 'ply'
        if dataTyp:
            self.threedFormat = dataTyp
        self.threedFilenames = []
        for file in files:
            ext = file['filename'].split('.')[-1]
            if ext.lower() == self.threedFormat:
                self.threedFilenames.append(file['filename'])
        if self.threedFilenames:
            for filename in self.threedFilenames:
                url = self.response0.url + '?getAlternativeFile=' + filename
                r = requests.get(url, verify=self.doVerify)
                if not filePath:
                    filePath = filename
                else:
                    filePath = os.path.join(filePath, filename)
                with open(filePath, 'wb') as w:
                    w.write(r.content)
                if buttonInstance:
                    with self.out:
                        print('Downloaded {0}'.format(filePath))
                return filePath
        else:
            print('No {0} file found.'.format(self.threedFormat))
            return None

    def threedview(self):
        path = self.response0.url+'#tabMode'
        path = path.replace('CitableHandler', 'collection')
        download = widgets.Button(
            description='Download 3D data',
            )
        self.out = widgets.Output()
        download.on_click(
            self.threedget
        )
        display(download, self.out)
        return HTML('<iframe src='+path+' + width=100% height=650></iframe>')

    def landingpage(self):
        return HTML('<iframe src='+self.landingpage_url+' + width=120% height=650></iframe>')

    def resource(self):
        resources = []
        collectiondoi = self.doi.split("-")[0]+"-"+self.doi.split("-")[1]
        self.response0 = requests.get('https://dx.doi.org/{0}'.format(collectiondoi), verify=self.doVerify)
        objectdata = requests.get(self.response0.url + '?getOverallJSON', verify=self.doVerify).json()
        objectdatakeys = list(objectdata.keys())

        def check(doi):
            val = -1
            for k in objectdatakeys:
                try:
                    if objectdata[k]['doi'] == doi:
                        val = k
                except:
                    pass
            return val

        val = check(self.doi)
        if val == -1:
            print("the current doi corresponds to a digital resource, it is not a research object!")
        if val != -1:
            try:
                resourcentypes = list(objectdata[val]["resources"].keys())
                for m in range(len(resourcentypes)):
                    try:
                        for p in range(len(list(objectdata[val]["resources"][resourcentypes[m]].keys()))):
                            key1 = list(objectdata[val]["resources"][resourcentypes[m]].keys())[p]
                            for j in range(len(objectdata[val]["resources"][resourcentypes[m]][key1]['resources'])):
                                try:
                                    formats = objectdata[val]["resources"][resourcentypes[m]][key1]['resources'][j]['metadata']['Technical characteristics']['Format']
                                except:
                                    formats = resourcentypes[m]
                                doi = objectdata[val]["resources"][resourcentypes[m]][key1]['resources'][j]['metadata']['General Information']['DOI']

                                resources.append((doi, formats))
                    except:
                        pass
            except:
                pass

        df = pd.DataFrame(resources)
        df.rename(columns={0: 'DOI', 1: 'Format'}, inplace=True)
        return df

    def digitalresource(self):
        format = self.datatype().lower()
        if format in ['ply', 'nxs', 'xyz']:
            self.threedFormat = format

        functionMap = {
            'xls': self.excel,
            'pdf': self.pdf,
            'json': self.json,
            'csv': self.csv,
            'image': self.imageshow,
            'images': self.imageshow,
            'jpg': self.imageshow,
            'ply': self.threedview,
            'xyz': self.threedview,
            'nxs': self.threedview,
            'dataset': self.resource,
            'pickle': self.pickle,
        }

        return functionMap[format]()


# Final Function
def Citable(f_arg, *argv, formats="doi"):
    """
    Load resource via a DOI which points to a Citable:
      call the function:

        - resource = Citable(DOI)  #for a single DOI
        - resource = Citable(DOI_1, DOI_2,....,DOI_n) # for more DOIs

      apply different methods on the resource (resource.func()):
        - note:
          one DOI -> resource.method()
          more DOI -> resource[i].method() with i=[0,1,...,n]

        - resource.metadata()  #the corresponding metadata
        - resource.json() #load json file
        - resource.df() #load json file as pandas dataframe
        - resource.debook() # load pdf with interactive tool 'dEbook-Viewer'
        - resource.pdf() # load PDF with standard viewer
        - resource.imageshow() # load image and show
        - resource.imagesave() # save image in local folder
        - resource.csv() # load csv file
        - resource.collection() # load overview json (each collections has its own overview json)
        - resource.docu() # a short introduction of collection & citable
        - resource.landingpage() # shows to the landing page of DOI
        - resource.filename() # returns file name
        - resource.datatype() # returns type of data (e.g. jpg or pdf)
        - resource.resource() # returns all digital resources including DOI
        - resource.getdoi() # returns DOI

      example:
        - single DOI:
          r=Citable('10.17171/1-3-388-1')
          r.filename()

        - two or more DOIs
          g=Citable('10.17171/1-1-3', '10.17171/1-1-4')
          g[1].metadata()

    """
    if type(f_arg) is pd.core.series.Series:
        lis = list(f_arg)
        liste = []
        for arg in lis:
            liste.append(Citableloader(arg, types=formats))
    if len(argv) == 0 and type(f_arg) is str:
        liste = Citableloader(f_arg, types=formats)
    if len(argv) == 0 and type(f_arg) is not str:
        liste = []
        for arg in f_arg:
            liste.append(Citableloader(arg, types=formats))
    if len(argv) != 0:
        liste = [Citableloader(f_arg, types=formats)]
        for arg in argv:
            liste.append(Citableloader(arg, types=formats))
    return liste
