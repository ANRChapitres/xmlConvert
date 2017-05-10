
# coding: utf-8

# In[74]:

import sys
import os
import fnmatch
from bs4 import BeautifulSoup as soup


# In[75]:

ns = {'dc': 'http://purl.org/dc/elements/1.1/'}

for idx, fileTemp in enumerate(fnmatch.filter(os.listdir('/home/odysseus/Bureau/ANR/testsCode/testChElem/'), '*.xml')):
    fileTemp=fileTemp.replace("/",":")
    tei = open('/home/odysseus/Bureau/ANR/testsCode/testChElem/'+fileTemp).read()
    xmlSoup = soup(tei, 'html.parser')
    for a in xmlSoup.find_all("dc:creator"):
        a.name="author"
        del a["opf:file-as"]
        del a["xmlns:dc"]
        del a["xmlns:opf"]
        del a["opf:role"]
    for a in xmlSoup.find_all("dc:date"):
        a.name="date"
        cutDate=a.string
        a.string=cutDate[:4]
        del a["xmlns:dc"]
    for a in xmlSoup.find_all("dc:subject"):
        a.name="subject"
        a.attrs.clear()
    for a in xmlSoup.find_all("dc:title"):
        a.name="title"
        del a["xmlns:dc"]
    for a in xmlSoup.find_all("hi"):
        a.attrs.clear()
        a["rend"]="italic"
    for a in xmlSoup.find_all("emph"):
        a.name="hi"
        a.attrs.clear()
        a["rend"]="italic"
    for a in xmlSoup.find_all('p'):
        del a["rend"]
        del a["xml:lang"]
    for a in xmlSoup.find_all('head'):
        a.attrs.clear()
    for a in xmlSoup.find_all('quote',{"rend" : "epigraphe"}):
        if a["rend"]=="epigraphe":
            a.name="div"
            text=""
            del a["rend"]
            if a.findChildren() : 
                for b in a.findChildren():
                    if not b.findChildren():
                        text+=b.string
            else :
                text+=a.string
            a.clear()
            a["type"]="dedication"
            newTag=xmlSoup.new_tag('epigraph')
            newTag.string=text
            a.append(newTag)
    for a in xmlSoup.find_all('div',{"type" : "section"}):
        if a["type"]=="section":
            a.attrs.clear()
            a["type"]="chapter"
            a["title"]=""
            a["id"]=""
            a["level"]=""
    for a in xmlSoup.find_all('div',{"rend" : "pindent"}):
        a.attrs.clear()
        a.name="p"
    for a in xmlSoup.find_all('div',{"rend" : "blocktextpblocktext"}):
        a.attrs.clear()
        a.name="p"
    for a in xmlSoup.find_all('div',{"rend" : "frontmatter"}):
        a.attrs.clear()
        a.name="p"
    for a in xmlSoup.find_all('div',{"rend" : "captionmatter"}):
        a.attrs.clear()
        a.name="p"
    listChap={"chapitre","Chapitre","Chapitre","I",
             "V","X","L","D","1","2","3","4","5","6","7","8","9","0"}
    listBook={"livre","Livre","LIVRE"}
    listPart={"Partie","partie","Partie"}
    for a in xmlSoup.find_all('div',{"type" : "section"}):
        for potTitle in listBook:
            if potTitle in a["n"]:
                a.name="book"
                a["type"]="book"
                a["title"]=a["n"]
                a.attrs.clear()
        for potTitle in listPart:
            if potTitle in a["n"]:
                a.name="part"
                a["type"]="part"
                a["title"]=a["n"]
                a.attrs.clear()
        for potTitle in listChap:
            if potTitle in a["n"]:
                print("ça rentre !!!!!!!!!")
                a.name="chapter"
                a["type"]="chapter"
                a["title"]=a["n"]
                a.attrs.clear()
    for a in xmlSoup.find_all('div',{"type" : "chapter"}):
        if a.findChild('head'):
            a.name="chapter"
            title=a.find('head').string
            a.attrs.clear()
            a["title"]=title
        
    for a in xmlSoup.find_all('ref',{"rend" : "renvoi"}):
        if xmlSoup.find('div', {"rend":"notecnt"}):
            elemTarg=xmlSoup.find('div', {"rend":"notecnt"})
            a.name="note"
            a.attrs.clear()
            strChild=""
            if elemTarg.findChildren:
                for child in elemTarg.findChildren():
                    strChild+=" "+child.string
            else:
                strChild=elemTarg.string
            a.string=strChild
            elemTarg.extract()
        
        
    [x.extract() for x in xmlSoup.findAll('meta')]
    [x.extract() for x in xmlSoup.findAll('dc:contributor')]
    [x.extract() for x in xmlSoup.findAll('dc:description')]
    [x.extract() for x in xmlSoup.findAll('dc:publisher')]
    [x.extract() for x in xmlSoup.findAll('dc:language')]
    [x.extract() for x in xmlSoup.findAll('dc:identifier')]
    [x.extract() for x in xmlSoup.findAll('dc:rights')]
    [x.extract() for x in xmlSoup.findAll('dc:subject')]
    [x.extract() for x in xmlSoup.findAll('graphic')]
    [x.extract() for x in xmlSoup.findAll('?xml-model')]


# In[76]:

from lxml.html.soupparser import fromstring
from lxml import etree
from lxml.etree import tostring
from collections import OrderedDict


# In[77]:

from io import StringIO, BytesIO


# In[78]:

root=str(xmlSoup.prettify())
# elem=etree.fromstring(root.encode('utf-8'))
myparser = etree.XMLParser(encoding="utf-8")
tree   = etree.parse(StringIO(root), parser=myparser)


# In[79]:

root=tree.getroot()
XHTML_NAMESPACE = "http://www.tei-c.org/ns/1.0"
ns = dict(N = "{http://www.tei-c.org/ns/1.0}")
print(tree.find('.//{http://www.tei-c.org/ns/1.0}author').text)
print(root)
print(root.getchildren()[0])
print(root.getchildren()[0].getchildren()[0])
print(root.getchildren()[0].getchildren()[0].getchildren()[0])


# In[81]:

tei= etree.Element('TEI')

teiHeader=etree.Element('teiHeader')

text=etree.Element('text')

back=etree.Element('back')
body=etree.Element('body')
front=etree.Element('front')

fileDesc=etree.Element('fileDesc')

titleStmt=etree.Element('titleStmt')
title=etree.Element('title')
title.text=tree.find('.//{http://www.tei-c.org/ns/1.0}title').text
author=etree.Element('author', 
                     attrib=OrderedDict([ \
                        ("key",""), \
                        ("name",tree.find('.//{http://www.tei-c.org/ns/1.0}author').text),\
                        ("from",tree.find('.//{http://www.tei-c.org/ns/1.0}date').text),\
                        ("to",tree.find('.//{http://www.tei-c.org/ns/1.0}date').text)]))
attEdition = {"n":""}
edition=etree.Element('edition', attrib=attEdition)

editor=etree.Element('editor',attrib=OrderedDict([("name",""),("where","")]))
titleStmt.append(title)
titleStmt.append(author)
titleStmt.append(edition)
titleStmt.append(editor)

publicationStmt=etree.Element('publicationStmt')
myattributes2 = {"when": tree.find('.//{http://www.tei-c.org/ns/1.0}date').text,
                 "type": "issued"}
myattributes1 = {"when": tree.find('.//{http://www.tei-c.org/ns/1.0}date').text,
                 "type": "created"}
date1=etree.Element('date', attrib=myattributes1)
date2=etree.Element('date', attrib=myattributes2)
publicationStmt.append(date1)
publicationStmt.append(date2)

editionStmt=etree.Element('editionStmt')
canon=""
listSubjects=tree.findall(".//{http://www.tei-c.org/ns/1.0}subject")
keywords=etree.Element('keywords')
for a in listSubjects:
    if "canonique" in a.text:
        canon="canonique"
    else:
        canon="non-canonique"
        term=etree.Element("term")
        keywords.append(term)
attProfDesc = {"type":"","tag":canon}
profileDesc=etree.Element('profileDesc', attrib=OrderedDict([("type","genre"),("tag","canon")]))
textClass=etree.Element('textClass')

textClass.append(keywords)
profileDesc.append(textClass)
editionStmt.append(profileDesc)

fileDesc.append(titleStmt)
fileDesc.append(publicationStmt)
fileDesc.append(editionStmt)

titlePage=etree.Element('titlePage')
docAuthor=etree.Element('docAuthor')
docTitle=etree.Element('docTitle')
attTitPart1={"main":title.text}
attTitPart2={"sub":""}
titlePart1=etree.Element('titlePart',attrib=attTitPart1)
titlePart2=etree.Element('titlePart',attrib=attTitPart2)
docTitle.append(titlePart1)
docTitle.append(titlePart2)
titlePage.append(docAuthor)
titlePage.append(docTitle)

attDed={"type":"dedication"}
divDed=etree.Element('div', attrib=attDed)
salute=etree.Element('salute')
epigraph=etree.Element('epigraph')
divDed.append(salute)
divDed.append(epigraph)
titlePage.append(divDed)

attPref={"type":"preface"}
divPref=etree.Element('div', attrib=attPref)
preface=""
# attention, passage à tester sur un texte à préface
listPref=tree.xpath('//div[re:test(@n, "^préface$", "i")]',
                      namespaces={"re": "http://exslt.org/regular-expressions"})
if len(listPref)==1:
    prefElem=listPref(0)
    preface=prefElem.text
elif len(listPref)>1:
    for prefElem in listPref:
        preface+=prefElem.text+" "
divPref.text=preface
titlePage.append(divPref)

front.append(titlePage)
text.append(front)

head=etree.Element('head')
# listBooks=tree.findall(".//{http://www.tei-c.org/ns/1.0}subject")
# # # book=etree.Element('div', 
# #                    attrib=OrderedDict(
#         [("type","book"),("title",""),("level","1")]))
listPart=tree.findall(".//{http://www.tei-c.org/ns/1.0}part")
if len(listPart)>0:
    for part in listPart:
        part=etree.Element('part')
        chapInPart=part.findall(".//{http://www.tei-c.org/ns/1.0}chapter")
        for chap in chapInPart:
            part.append(chap)
        body.append(part)
else :
    listChap=tree.findall(".//{http://www.tei-c.org/ns/1.0}chapter")
    for chap in listChap:
        body.append(chap)

body.append(head)
text.append(body)


text.append(back)
tei.append(teiHeader)
tei.append(text)
teiHeader.append(fileDesc)


et = etree.ElementTree(tei)
et.write("test.xml", pretty_print=True)



# In[ ]:



