from matplotlib.pyplot import *
import matplotlib.pyplot as plt
import webbrowser
from IPython.display import HTML, Image
from plyfile import PlyData, PlyElement
import requests
import urllib.request
import csv
import pandas as pd
import re
import json

class Citableloader:
    def __init__(self, doi):
        self.url = 'http://dx.doi.org/'+doi
        self.response0 = requests.get(self.url)
        self.data = requests.get(self.response0.url + '?getDigitalFormat')
        self.alternatives=requests.get(self.response0.url + '?getAlternatives')
        self.alternativefile=requests.get(self.response0.url + '?getAlternativeFile')
        self.doi=doi
        r=self.response0.url
        r=r.split("http://repository.edition-topoi.org/")[1]
        r=r.split('/')
        try:
            self.d= re.findall("filename=(.+)", self.data.headers['Content-disposition'])[0].replace('\"','')
            self.link="http://repository.edition-topoi.org/"+r[1]+'/Repos'+r[1]+'/'+r[1]+r[3]+'/'+self.d
        except:
            webbrowser.open(self.url)
    def description(self):
        return HTML('<iframe src=http://repositorytest.ancient-astronomy.org/MAPD/RoMAPD/documentation.pdf width=1200 height=550></iframe>')
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
        return requests.get(self.response0.url + '?getOverallJSON').json()
    def metadata(self):
        b=requests.get(self.response0.url + '?getDigitalFormats').json()
        c=list(b.keys())
        finallist=[]
        for j in range(len(c)):
            try:
                gi=list(b[c[j]].keys())
                finallist.append(( c[j].upper(), ""))
                for i in range(len(gi)):
                    finallist.append((gi[i], b[c[j]][gi[i]]))
            except:
                pass
        pd.set_option('max_colwidth',-1)
        df=pd.DataFrame(finallist)
        df.columns = [' ', '']
        df.set_index([' '],drop=True,inplace=True)
        df=df.style.set_properties(**{'text-align': 'left'})
        return df
    def filename(self):
        return self.d;
    def datatype(self):
        f=requests.get(self.response0.url + '?getDigitalFormats').json()
        return f['Technical characteristics']['Format']
    def pdf(self):
        return HTML('<iframe src='+self.link+' width=900 height=550></iframe>')
    def debook(self):
        return HTML('<iframe src=''http://edition-topoi.org/dEbook/?pdf='+self.link+' + width=100% height=650></iframe>')
    def imageshow(self, w=500, h=500):
        data = requests.get(self.response0.url + '?getDigitalFormat')
        urllib.request.urlretrieve(data.url, "image.jpg");
        return Image(filename='image.jpg', width=w, height=h) 
    def imagesave(self, name="temp.jpg"):
        data = requests.get(self.response0.url + '?getDigitalFormat')
        urllib.request.urlretrieve(data.url, name);
        return;
    def digilib(self, w=1500, h=1950):
        path = self.response0.url+'#tabMode'
        path=path.replace('CitableHandler', 'collection')
        return HTML('<iframe src='+path+' + width=100% height=650></iframe>')
    def csv(self):
        urllib.request.urlretrieve(self.response0.url + '?getDigitalFormat', "temp.csv")
        return pd.read_csv("temp.csv")
    def excel(self):
        urllib.request.urlretrieve(self.response0.url + '?getDigitalFormat', "temp.xls")
        df = pd.read_excel('temp.xls')
        return df
    def ply(self):
        temppath =self.alternatives.json()
        for m in range(len(temppath)):
            if temppath[m]['format'] in ["PLY", "ply"]:
                temppath=temppath[m]['filename']
        path=self.response0.url + '?getAlternativeFile='+temppath.format(temppath)
        r = requests.get(path)
        with open(temppath,'wb') as w:
            w.write(r.content)
        return print("file saved as: "+temppath)
    def xyz(self):
        temppath =self.alternatives.json()
        for m in range(len(temppath)):
            if temppath[m]['format'] in ["XYZ", "xyz"]:
                temppath=temppath[m]['filename']
        path=self.response0.url + '?getAlternativeFile='+temppath.format(temppath)
        r = requests.get(path)
        with open(temppath,'wb') as w:
            w.write(r.content)
        return temppath
    def threedview(self):
        path = self.response0.url+'#tabMode'
        path=path.replace('CitableHandler', 'collection')
        return HTML('<iframe src='+path+' + width=100% height=650></iframe>')
    def landingpage(self):
        return HTML('<iframe src='+self.url+' + width=120% height=650></iframe>')
    def citableclass(self):
        return HTML('<iframe src=http://141.20.159.91/files/documentation/_build/html/topoi.html + width=100% height=650></iframe>')
    def resource(self):
        resources=[]
        with open("../ancientsundials/data/BSDP_objects.cite", encoding="iso-8859-15" ) as data_file:    
            objectdata= json.load(data_file)
            objectdatakeys= list(objectdata.keys())
        def check(doi):
            val=-1
            for k in objectdatakeys:
                try:
                    if objectdata[k]['doi']==doi:
                        val=k
                except:
                    pass
            return val;
        val=check(self.doi)
        if val==-1:
            print("the current doi corresponds to a digital resource, it is not a research object!")
        if val!=-1:
            try:
                resourcentypes=list(objectdata[val]["resources"].keys())
                for m in range(len(resourcentypes)):
                    try:
                        for p in range(len(list(objectdata[val]["resources"][resourcentypes[m]].keys()))):
                            key1=list(objectdata[val]["resources"][resourcentypes[m]].keys())[p]
                            for j in range(len(objectdata[val]["resources"][resourcentypes[m]][key1]['resources'])):
                                doi=objectdata[val]["resources"][resourcentypes[m]][key1]['resources'][j]['metadata']['General Information']['DOI']
                                formats=objectdata[val]["resources"][resourcentypes[m]][key1]['resources'][j]['metadata']['Technical characteristics']['Format']
                                resources.append((doi, formats))
                    except:
                        pass
            except:
                pass
       
        df=pd.DataFrame(resources)
        df.rename(columns={0: 'DOI',1: 'Format'}, inplace=True)
        return df;
    def digitalresource(self):
        try:
            f=requests.get(self.response0.url + '?getDigitalFormats').json()
            if 'Format' in f['Technical characteristics']:
                if f['Technical characteristics']['Format'] in ["XLS", "xls"]:
                    return self.excel()
                if f['Technical characteristics']['Format'] in ["PDF", "pdf"]:
                    return self.pdf()
                if f['Technical characteristics']['Format'] in ["JSON", "json"]:
                    return self.df()
                if f['Technical characteristics']['Format'] in ["CSV", "csv"]:
                    return self.csv()
                if f['Technical characteristics']['Format'] in ["Image", "image", "Images", "images"]: 
                    return self.imageshow()
                if f['Technical characteristics']['Format'] in ["Ply", "ply", "PLY","xyz", "XYZ", "NXS", "nxs"]: 
                    return self.threedview()
                if f['Technical characteristics']['Format'] in ["Dataset"]: 
                    print('You have selected a research object which contains normally more than one digital resource')
                    return self.resource()
            if 'Resource Type' in f['Technical characteristics']:
                if f['Technical characteristics']['Resource Type'] in ["XLS", 'xls']:
                    return self.excel()
                if f['Technical characteristics']['Resource Type'] in ["PDF", "pdf"]:
                    return self.pdf()
                if f['Technical characteristics']['Resource Type'] in ["JSON", "json"]:
                    return self.df()
                if f['Technical characteristics']['Resource Type'] in ["CSV", "csv"]:
                    return self.csv()
                if f['Technical characteristics']['Resource Type'] in ["Image", "image", "Images", "images"]: 
                    return self.imageshow()
                if f['Technical characteristics']['Resource Type'] in ["Ply", "ply", "PLY","xyz", "XYZ", "NXS", "nxs"]: 
                    return self.threedview()
                if f['Technical characteristics']['Resource Type'] in ["Dataset"]: 
                    print('You have selected a research object which contains normally more than one digital resource')
                    return self.resource()
        except:
            print("no regular format!")
# Final Function 
def Citable(f_arg, *argv):
    """
    Load resource via a DOI which points to a Citable:
      call the function:
      
        - resource = CitableLoader(DOI)  #for a single DOI
        - resource = CitableLoader(DOI_1, DOI_2,....,DOI_n) # for more DOIs
        
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
          r=CitableLoader('10.17171/1-3-388-1')
          r.filename()
          
        - two or more DOIs
          g=CitableLoader('10.17171/1-1-3', '10.17171/1-1-4')
          g[1].metadata()
        
    """
   
    if type(f_arg) is pd.core.series.Series:
        lis = list(f_arg)
        liste=[]
        for arg in lis:
            liste.append(Citableloader(arg))
    if len(argv)==0 and type(f_arg) is str:
        liste=Citableloader(f_arg)
    if len(argv)==0 and type(f_arg) is not str:
        liste=[]
        for arg in f_arg:
            liste.append(Citableloader(arg))
    if len(argv)!=0:
        liste=[Citableloader(f_arg)]
        for arg in argv:
            liste.append(Citableloader(arg))
    return liste;

