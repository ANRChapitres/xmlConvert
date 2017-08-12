
# coding: utf-8

# In[73]:

import sys
import os
import fnmatch
from bs4 import BeautifulSoup as soup
from bs4 import Comment
from lxml.html.soupparser import fromstring
from lxml import etree
from lxml.etree import tostring
from collections import OrderedDict
import re
from io import StringIO, BytesIO


# In[ ]:

ns = {'dc': 'http://purl.org/dc/elements/1.1/'}

for idx, fileTemp in enumerate(fnmatch.filter(os.listdir('/home/odysseus/Bureau/Bureau/ANR/testsCode/output/'), '*.xml')):
    fileTemp=fileTemp.replace("/",":")
    tei = open('/home/odysseus/Bureau/Bureau/ANR/testsCode/output/'+fileTemp).read()
    print(fileTemp)
    xmlSoup = soup(tei, 'html.parser')
    for element in xmlSoup(text=lambda text: isinstance(text, Comment)):
        element.extract()
    
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
#         print(a.text)
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
#     for a in xmlSoup.find_all('div',{"type" : "section"}):
#         if a["type"]=="section":
#             a.attrs.clear()
#             a["type"]="chapter"
#             a["title"]=""
#             a["id"]=""
#             a["level"]=""
    for a in xmlSoup.find_all('p'):
        a.attrs.clear()
        a.name="p"
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
    for a in xmlSoup.find_all('div',{"rend" : "realspc"}):
        a.extract()
    for a in xmlSoup.find_all('div',{"rend" : "cita"}):
        a.attrs.clear()
        a.name="quotecit"
    for a in xmlSoup.find_all('div',{"rend" : "poetrypoetryintfigureadvertisementfigureadvertisement"}):
        a.attrs.clear()
        a.name="quoteverse"
    for a in xmlSoup.find_all('div',{"rend" : "poemstanza"}):
        a.attrs.clear()
        a.name="quoteverse"
    for a in xmlSoup.find_all('div',{"rend" : "poetrycontainerpoetrystanza"}):
        a.attrs.clear()
        a.name="quoteverse"
    listChap={"chapitre","Chapitre","CHAPITRE","1","2","3","4","5","6","7","8","9","0"}
    listBook={"livre","Livre","LIVRE"}
    listPart={"Partie","partie","PARTIE"}
    for a in xmlSoup.find_all('div',{"type" : "section"},{"n":True}):
        check=False
        sectionTitle=a["n"]
        sectionTitle=sectionTitle.replace(u'\xa0', ' ').encode('utf-8')
        wordsInTitle=sectionTitle.decode().split(" ")
        if len(set(wordsInTitle).intersection(set(listBook)))>0:
            a.attrs.clear()
            a.name="book"
            a["type"]="book"
            a["title"]=sectionTitle.decode("utf-8")
        elif len(set(wordsInTitle).intersection(set(listPart)))>0:
            a.attrs.clear()
            a.name="part"
            a["type"]="part"
            a["title"]=sectionTitle.decode("utf-8")
        elif len(set(wordsInTitle).intersection(set(listChap)))>0:
            a.attrs.clear()
            a.name="chapter"
            a["type"]="chapter"
            a["title"]=sectionTitle.decode("utf-8")
        else:
            a.attrs.clear()
            a.name="UndefinedSection"
            a["type"]="section"
            a["title"]=sectionTitle.decode("utf-8")

    for a in xmlSoup.find_all('div',{"type" : "chapter"}):
#         print(a.text)
        if a.findChild('head'):
            a.name="chapter"
            title=a.find('head').string
            if (title==None):
                a.extract()
            else:
                for book in listBook:
                    if book in title:
#                         print(title)
                        a.name="book"
                a.attrs.clear()
#                 print(title)
                a["title"]=title
    
    invalid_tags = ['hi', 'ref']
    
    for a in xmlSoup.find_all('ref',{"rend" : "renvoi"}):
        if xmlSoup.find('div', {"rend":"notecnt"}):
            elemTarg=xmlSoup.find('div', {"rend":"notecnt"})
            a.name="note"
            a.attrs.clear()
            for tag in invalid_tags: 
                for match in elemTarg.findAll(tag):
                    match.replaceWithChildren()
            a.string=elemTarg.text
            elemTarg.extract()
        
        
    [x.extract() for x in xmlSoup.findAll('meta')]
    [x.extract() for x in xmlSoup.findAll('dc:contributor')]
    [x.extract() for x in xmlSoup.findAll('dc:description')]
    [x.extract() for x in xmlSoup.findAll('dc:publisher')]
    [x.extract() for x in xmlSoup.findAll('dc:language')]
    [x.extract() for x in xmlSoup.findAll('dc:identifier')]
    [x.extract() for x in xmlSoup.findAll('dc:rights')]
    [x.extract() for x in xmlSoup.findAll('dc:subject')]
    [x.extract() for x in xmlSoup.findAll('opf:meta')]
    [x.extract() for x in xmlSoup.findAll('graphic')]
    [x.extract() for x in xmlSoup.findAll('?xml-model')]
    [x.extract() for x in xmlSoup.findAll('div', {"rend":"illustypeimage"})]

    root=str(xmlSoup)
    
#     if "Chandernagor" in fileTemp:
#         print(xmlSoup)
    
    root=root.replace("xmlns=\"http://www.tei-c.org/ns/1.0\"","xmlns:tei=\"http://www.tei-c.org/ns/1.0\"")
    root=root.replace("xmlns=\"http://www.idpf.org/2007/opf\"","xmlns:idpf=\"http://www.idpf.org/2007/opf\"")

# print (root)
# elem=etree.fromstring(root.encode('utf-8'))
    myparser = etree.XMLParser(remove_blank_text=True)
    tree   = etree.parse(StringIO(root), parser=myparser)
    root=tree.getroot()
    tei= etree.Element('TEI')

    teiHeader=etree.Element('teiHeader')

    text=etree.Element('text')

    back=etree.Element('back')
    body=etree.Element('body')
    front=etree.Element('front')

    fileDesc=etree.Element('fileDesc')

    titleStmt=etree.Element('titleStmt')
    title=etree.Element('title')
    title.text=tree.find('.//title',root.nsmap).text
    author=etree.Element('author', 
                     attrib=OrderedDict([ \
                        ("key",""), \
                        ("name",tree.find('.//author',root.nsmap).text),\
                        ("from",tree.find('.//date',root.nsmap).text),\
                        ("to",tree.find('.//date',root.nsmap).text)]))
    attEdition = {"n":""}
    edition=etree.Element('edition', attrib=attEdition)

    editor=etree.Element('editor',attrib=OrderedDict([("name",""),("where","")]))
    titleStmt.append(title)
    titleStmt.append(author)
    titleStmt.append(edition)
    titleStmt.append(editor)

    publicationStmt=etree.Element('publicationStmt')
    myattributes2 = {"when": tree.find('.//date',root.nsmap).text,
                 "type": "issued"}
    myattributes1 = {"when": tree.find('.//date',root.nsmap).text,
                 "type": "created"}
    date1=etree.Element('date', attrib=myattributes1)
    date2=etree.Element('date', attrib=myattributes2)
    publicationStmt.append(date1)
    publicationStmt.append(date2)

    editionStmt=etree.Element('editionStmt')
    canon=""
    listSubjects=tree.findall(".//subject",root.nsmap)
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
    listQuotes=tree.findall(".//quotecit",root.nsmap)
    for quote in listQuotes:
        parag=etree.Element('p')
        quote.append(parag)
        quote.tag="quote"
        quote.text=""
    listVerse=tree.findall(".//quoteverse",root.nsmap)
    for quote in listVerse:
        parag=etree.Element('q')
        if quote.iterdescendants():
            subChildren=quote.iterdescendants()
            for element in subChildren:
                if element.tag=="l":
                    element.tag="q"
                parag.append(element)
    
        quote.tag="quote"
        quote.append(parag)
        quote.text=""
    listBooks=tree.findall(".//subject",root.nsmap)
    book=etree.Element('div', 
                   attrib=OrderedDict(
        [("type","book"),("title",""),("level","1")]))
    listBook=tree.findall(".//book",root.nsmap)
    listPart=tree.findall(".//part",root.nsmap)
    if len(listPart)>0:
        for part in listPart:
            part=etree.Element('part')
            chapInPart=part.findall(".//chapter",root.nsmap)
            for chap in chapInPart:
                part.append(chap)
            body.append(part)
    if len(listBook)>0:
        for book in listBook:
            part=etree.Element('book')
            chapInPart=part.findall(".//chapter",root.nsmap)
            if len(chapInPart)>0:
                for chap in chapInPart:
                    part.append(chap)
            else:
                part=book
            body.append(part)
            
    else :
        listChap=tree.findall(".//chapter",root.nsmap)
        for chap in listChap:
            body.append(chap)
#             if "Chandernagor" in fileTemp:
#                 print(etree.tostring(chap))
#         if len(listChap)<1:
        listSect=tree.findall(".//UndefinedSection",root.nsmap)
        for sect in listSect:
            body.append(sect)
    body.append(head)
#     if "Chandernagor" in fileTemp:
#         print(etree.tostring(body))
    text.append(body)

    text.append(back)
    tei.append(teiHeader)
    tei.append(text)
    teiHeader.append(fileDesc)

#     for element in tei.iter():
#         element.tail = None

    final=str(etree.tostring(tei, pretty_print=True,encoding = "unicode"))
    final = re.sub(r'ns[0-9]+:', '', final)
    final= final.replace("&#10;","")
# final = re.sub(r"(\s)+",' ',final)
# et = etree.ElementTree(tei)
# et.write("test.xml", pretty_print=True)
    f = open('./tests/'+fileTemp, 'w')
    f.write(final)
    f.close()
#     print(final)


# In[ ]:



