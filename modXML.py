
# coding: utf-8

# In[771]:

import sys
import os
import fnmatch
from bs4 import BeautifulSoup as soup
from bs4 import Comment


# In[772]:

def divRend(soup, listAtt, name):
    for att in listAtt:
        for a in soup.find_all('div',{"rend" : att}):
            a.attrs.clear()
            a.name=name


# In[773]:

def defChap():
    for a in xmlSoup.find_all('div',{"type" : "section"},{"n":True}):
        check=False
        sectionTitle=a["n"]
        for potBook in listBook:
            if potBook in sectionTitle:
                a.attrs.clear()
                a.name="book"
                a["type"]="book"
                a["title"]=sectionTitle
                check=True
        for potPart in listPart:
            if potPart in sectionTitle:
                a.attrs.clear()
                a.name="part"
                a["type"]="part"
                a["title"]=sectionTitle
                check=True
        for potChap in listChap:
            if potChap in sectionTitle:
                a.attrs.clear()
                a.name="chapter"
                a["type"]="chapter"
                a["title"]=sectionTitle
                check=True
        if check==False:
            a.attrs.clear()
            a.name="UndefinedSection"
            a["type"]="section"
            a["title"]=sectionTitle
    for a in xmlSoup.find_all('div',{"type" : "chapter"}):
        a.attrs.clear()
        if a.findChild('head'):
            a.name="chapter"
            title=a.find('head').string
            if (title==None):
                a.extract()
            else:
                for book in listBook:
                    if book in title:
                        a.name="book"
                a.attrs.clear()
                a["title"]=title


# In[774]:

def elemExtract(elems):
    for elem in elems:
        [x.extract() for x in xmlSoup.findAll(elem)]


# In[775]:

def quote(soup,listVerse,att):
    for verse in listVerse:
        for a in soup.find_all('div',{"rend" : verse}):
            txt=a.text
            a.attrs.clear()
            a.name=att
            a.string=txt


# In[776]:

ns = {'dc': 'http://purl.org/dc/elements/1.1/'}
rends={'pindent','blocktextpblocktext','frontmatter',
         'captionmatter','realspc',
         'calibre','calibrecalibre','sepetoile','chapter',
         'titlechapter','pcbr','calibretitpartl','titpartl',
        'titlesection','part','chapn','schap','dev','pre',
        'pagecopyright','subtitlechapter','pindentinverse','pc'}
salutes={'dedicace','indentdedicaces'}
quotes={'cita','citation',
        'poetrypoetryintfigureadvertisementfigureadvertisement'}
verses={'poetrypoetryintcalibrestropint','citastroplg',
        'poetrycontainerpoetrystanza','poemstanza',
        'poetrycontainerpoetrystanza','poetrypoetryintstropstrop',
        'poem'}
toRem={'meta','dc:contributor','dc:description','dc:publisher',
      'dc:language','dc:identifier','dc:rights','dc:subjects',
      'graphic','?xml-model'}
listChap={"chapitre","Chapitre","Chapitre","I","V","X","D",
              "1","2","3","4","5","6","7","8","9","0"}
listBook={"livre","Livre","LIVRE"}
listPart={"Partie","partie","Partie"}


# In[777]:

# Parcours des fichiers
for idx, fileTemp in enumerate(fnmatch.filter(os.listdir('/home/odysseus/Bureau/ANR/testsCode/testChElem/'), '*.xml')):
    fileTemp=fileTemp.replace("/",":")
    tei = open('/home/odysseus/Bureau/ANR/testsCode/testChElem/'+fileTemp).read()
    xmlSoup = soup(tei, 'html.parser')
    for element in xmlSoup(text=lambda text: isinstance(text, Comment)):
        element.extract()

# Nettoyage des dublin core :
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

# italiques
    for a in xmlSoup.find_all("hi"):
        a.attrs.clear()
        a["rend"]="italic"
    for a in xmlSoup.find_all("emph"):
        a.name="hi"
        a.attrs.clear()
        a["rend"]="italic"

# dedication
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

# clear <p>s
    for a in xmlSoup.find_all('p'):
        a.attrs.clear()
        a.name="p"

# quotes, citations
    quote(xmlSoup,quotes,"quotecit")
    quote(xmlSoup,verses,"quoteverse")
    
            
# nettoyer balise head   
    for a in xmlSoup.find_all('head'):
        a.attrs.clear()
    for a in xmlSoup.find_all('head'):
        test=a.text
        if "À propos de cette édition numérique" in test:
            a.extract()

# nettoyer les div rend
    divRend(xmlSoup,rends,"p")
    quote(xmlSoup,salutes,"salute")
    
    for a in xmlSoup.find_all('div',{"rend" : "letter"}):
        a.attrs.clear()
        a.name="q"
        a["type"]="letter"

# chapitres, parties, livres
    defChap()

# inclassables
    for a in xmlSoup.find_all('div',{"type" : "section"}):
        test=a["n"]
        if "START: FULL LICENSE" or "propos de cette édition numérique" in test:
            a.extract()
        
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
        
# suppressions    
    elemExtract(toRem)
    [x.extract() for x in xmlSoup.findAll('div',{'rend':"som"})]
    [x.extract() for x in xmlSoup.findAll('div', {"rend":"illustypeimage"})]
    [x.extract() for x in xmlSoup.findAll('div', {"rend":"realspc"})]
    [x.extract() for x in xmlSoup.findAll('div', {"rend":"pblanc"})]


# In[778]:

from lxml.html.soupparser import fromstring
from lxml import etree, objectify
from lxml.etree import tostring
from lxml.etree import QName
from collections import OrderedDict
import re


# In[779]:

from io import StringIO, BytesIO


# In[780]:

root=str(xmlSoup)
myparser = etree.XMLParser(remove_blank_text=True)
tree   = etree.parse(StringIO(root), parser=myparser)


# In[781]:

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
listSalutes=tree.findall(".//{http://www.tei-c.org/ns/1.0}salute")
for salute in listSalutes:
    newSal=etree.Element('salute')
    tmpSal=salute.text.strip()
    newSal.text=tmpSal
    divDed.append(newSal)
listDedications=tree.findall(".//{http://www.tei-c.org/ns/1.0}dedication")
for dedication in listDedications:
    divDed.append(dedication)
if divDed.getchildren():
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
if divPref.getchildren():
    titlePage.append(divPref)

front.append(titlePage)
text.append(front)

head=etree.Element('head')
listQuotes=tree.findall(".//{http://www.tei-c.org/ns/1.0}quotecit")
for quote in listQuotes:
    quote.name="quote"
    if quote.text and quote.getchildren()==False:
        parag=etree.Element('p')
        tmp=re.sub(r'(\s+)', ' ', quote.text).strip()
        parag.text=tmp
        quote.text=""
        quote.append(parag)
listVerse=tree.findall(".//{http://www.tei-c.org/ns/1.0}quoteverse")
for quote in listVerse:
        
    if quote.getchildren():
        for element in quote.getchildren():
            element.tag="q"
    else:
        parag=etree.Element('q')
        tmp=re.sub(r'(\s+)', ' ', quote.text).strip()
        parag.text=tmp
        quote.text=""
        quote.append(parag)
    quote.tag="quote"
    
listBooks=tree.findall(".//{http://www.tei-c.org/ns/1.0}subject")
book=etree.Element('div', 
                   attrib=OrderedDict(
        [("type","book"),("title",""),("level","1")]))
listBook=tree.findall(".//{http://www.tei-c.org/ns/1.0}book")
listPart=tree.findall(".//{http://www.tei-c.org/ns/1.0}part")
if len(listPart)>0:
    for part in listPart:
        part=etree.Element('part')
        chapInPart=part.findall(".//{http://www.tei-c.org/ns/1.0}chapter")
        for chap in chapInPart:
            part.append(chap)
        body.append(part)
if len(listBook)>0:
    for book in listBook:
        part=etree.Element('book')
        chapInPart=part.findall(".//{http://www.tei-c.org/ns/1.0}chapter")
        if len(chapInPart)>0:
            for chap in chapInPart:
                part.append(chap)
        else:
            part=book
        body.append(part)
else :
    listChap=tree.findall(".//{http://www.tei-c.org/ns/1.0}chapter")
    for chap in listChap:
        body.append(chap)
    if len(listChap)<1:
        listSect=tree.findall(".//{http://www.tei-c.org/ns/1.0}UndefinedSection")
        for sect in listSect:
            body.append(sect)
body.append(head)
text.append(body)

text.append(back)
tei.append(teiHeader)
tei.append(text)
teiHeader.append(fileDesc)

for element in tei.iter():
    element.tail = None

final=str(etree.tostring(tei, pretty_print=True,encoding = "unicode"))
final = re.sub(r'ns[0-9]+:', '', final)
final= final.replace("&#10;","")
final=re.sub(r'xmlns:ns[0-9]+=\"http://www.tei-c.org/ns/1.0\" ',"",final)
f = open('test.xml', 'w')
f.write(final)
f.close()

