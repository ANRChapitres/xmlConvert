
# coding: utf-8

# In[1]:


import os
import glob
import argparse
import sys
import fnmatch
from time import perf_counter


# In[2]:


from bs4 import BeautifulSoup


# In[3]:


import re
from collections import OrderedDict
import regex


# In[4]:


from io import StringIO


# In[5]:


from lxml import etree as ET
import lxml.html


# In[6]:


def strip_ns_prefix(tree):
    query = "descendant-or-self::*[namespace-uri()!='']"
    for element in tree.xpath(query):
        element.tag = ET.QName(element).localname
    return tree


# In[7]:


def recursive_xml(root):
    if root.getchildren() is not None:
        for child in root.getchildren():
            if child.text is None and child.getchildren() is None:
                root.remove(child)
            else:
                recursive_xml(child)


# In[8]:


def parse_from_unicode(unicode_str):
    s = unicode_str.encode('utf-8')
    return ET.fromstring(s, parser=utf8_parser)


# In[36]:


def remove_tags(html, invalid_tags):
    soup = BeautifulSoup(html, "xml")
    for tag in invalid_tags: 
        for match in soup.findAll(tag):
            match.replaceWithChildren()
    cleaned_text=str(soup)
    return cleaned_text


# In[40]:


print('This software cleans XML files from Debook (credits Frédéric Glorieux) \nusage: --src path/to/your/source/dir --trg path/to/your/target/directory')
parser = argparse.ArgumentParser()
parser.add_argument('--src', help= '/your/directory/to/tagged/files/')
parser.add_argument('--trg', help= '/your/directory/to/your/files/')
args = parser.parse_args()


if len(sys.argv) == 1:
    sys.exit()


argssrc= os.path.join(args.src, '')
argstrg= os.path.join(args.trg, '')
logf = open(argstrg+"/errors.log", "w")
t1_start = perf_counter()

source_dir=argssrc
target_dir=argstrg
files= glob.iglob(source_dir+'/*.xml', recursive=True)
#print(files)

# Parsing
nb_files=0
for filename in files :
    #print(filename)
    try:
        basename=(filename[:-4])
        infos=re.split("_",basename[basename.rfind("/")+1:])
        print(infos)

        text=""

        with open(filename, 'r') as reader:
            text=reader.read()
        #if "bibebook" in text or "Bibebook" in text:
            #print("Texte Bibebook : "+filename)

        text=re.sub('\s*xml:id=\"[A-Za-z0-9\-_:]+\"', '', text)
        text=re.sub('<meta xml:id=\"[A-Za-z\-: 0-9_]*\"\s*(content=")*[A-Za-z\s,\'.(0-9\-)&;:{}]*("/>)*\n','',text)
        text=re.sub('<meta xml:id="[A-Za-z\-: 0-9_]*"/>\n', '', text)
        text=re.sub('xsi:type="[A-Za-z0-9:]*"', '', text)
        text=re.sub(' xml:id=\"[a-zA-Z0-9]*\"','',text)
        text=re.sub("(\n*\s*<seg>\n*\s*)q(\n*\s*</seg>\n*\s*)","",text)

        #pattern = re.compile("((\n*\s*<hi rend=\"italic\">\n*\s*)*(\n*\s*<seg>\n*\s*))([B-Z])((\n*\s*</seg>\n*\s*)(\n*\s*</hi>\n*\s*)*)")
        #results = pattern.findall(text)
        '''
        if results is not None:
            for result in results:
                print(results)
                print(result[1])
                #print(result)
                print("".join(result))
                text=re.sub("".join(result),result[1],text)
        print(text)
        '''

        text=remove_tags(text, ["seg","hi"])
        #print(repr(text))
        text=re.sub("(?!>)(\n)+","",text)
        text=re.sub("\s{2,}"," ",text)

        pattern=re.compile("(\s)([B-Z])(\s)([A-ZÈÉ]+)")
        results=pattern.findall(text)
        if results is not None:
            for result in results:
                #print(results)
                text=re.sub("".join(result),result[1]+result[3],text)

        #print(text)

        utf8_parser = ET.XMLParser(encoding='utf-8',remove_blank_text=True, resolve_entities=False, ns_clean=True, dtd_validation=False)
        tree=parse_from_unicode(text)

        tree=strip_ns_prefix(tree)

        ps = tree.findall(".//p")
        hs = tree.findall(".//head")
        cs = tree.xpath('//comment()')
        divs = tree.findall('.//div')
        header = tree.find ('.//teiHeader')
        body = tree.find('.//body')
        notes = tree.findall('.//note')
        parent=body.getparent()
        front=ET.Element("front")
        back=ET.Element("back")
        titlePage=ET.Element("titlePage")
        titlePage.append(ET.Element("docAuthor"))
        docTitle=ET.Element("docTitle")    

        if tree.find('.//front'):
            front=tree.find('.//front')
        else:
            front.append(titlePage)
            docTitle.append(ET.Element('titlePart',attrib=OrderedDict([("main","")])))
            docTitle.append(ET.Element('titlePart',attrib=OrderedDict([("sub","")])))
            titlePage.append(docTitle)
        parent.insert(parent.index(body)-1,front)

        if tree.find ('.//back'):
            back=tree.find('.//back')
        parent.insert(parent.index(body)+1,back)        

    # Nettoyage du texte

        for p in ps:
            rawtext= lxml.html.tostring(p, method="text", encoding="utf8")
            rawtext=rawtext.decode("utf8")

            pattern="[mle]{2,}\n*\s*(</[seghi]+>)*"
            if re.search(pattern,rawtext):
                rawtext=re.sub("\n\s+"," ",rawtext)
                rawtext=re.sub("M\s","M",rawtext)

            if rawtext!=None:
                raw_p=ET.Element("p")
                raw_p.text=rawtext
                p.addnext(raw_p)
                p.getparent().remove(p)

        for h in hs:
            rawtext= lxml.html.tostring(h, method="text", encoding="utf8")
            if rawtext!=None:
                raw_h=ET.Element("head")
                raw_h.text=h.text
                h.addnext(raw_h)
                h.getparent().remove(h)
        for c in cs :
            if c.getparent() is not None:
                c.getparent().remove(c)
        for note in notes :
            if note.getparent() is not None:
                note.getparent().remove(note)

        for div in divs:
            ET.strip_attributes(div,'rend')
            if 'type' in div.attrib:
                if div.attrib['type']=='section':
                    div.attrib['type']='chapter'
                if "n" in div.attrib :
                    div.attrib['title']=div.attrib['n']
                    del div.attrib['n']


    # Reconstitution du Header  

        fileDesc=ET.Element('fileDesc')
        titleStmt=ET.Element('titleStmt')
        title=ET.Element('title')

        if len(tree.xpath('.//title/text()'))>0 :
            title.text=tree.xpath('.//title/text()')[0]
        else:
            title.text=re.sub("-"," ",infos[2])

        if len(tree.xpath('.//author/text()'))>0 :
            name = tree.xpath('.//author/text()')[0]
        else:
            name=infos[1]
        if len(tree.xpath('.//date/text()'))>0:
            date = tree.xpath('.//date/text()')[0]
        else:
            date=infos[0]

        if len(tree.xpath(".//author[@name]"))>0:
            author=tree.find(".//author")      
        else :
            author=ET.Element('author', 
                             attrib=OrderedDict([ \
                                ("key",""), \
                                ("name",name),\
                                ("from",date),\
                                ("to",date)]))

        if tree.xpath(".//edition[@n]"):
            #print(tree.xpath(".//edition[@n]"))
            edition=tree.find(".//edition")
        else:
            attEdition = {"n":""}
            edition=ET.Element('edition', attrib=attEdition)

        if tree.xpath(".//editor[@name]"):
            editor=tree.find(".//editor")
        else:
            editor=ET.Element('editor',attrib=OrderedDict([("name",""),("where","")]))

        titleStmt.append(title)
        titleStmt.append(author)
        titleStmt.append(edition)
        titleStmt.append(editor)

        if tree.find(".//publicationStmt"):
            publicationStmt=tree.find(".//publicationStmt")
        else:
            publicationStmt=ET.Element('publicationStmt')
            myattributes2 = {"when": date,
                         "type": "issued"}
            myattributes1 = {"when": date,
                         "type": "created"}
            date1=ET.Element('date', attrib=myattributes1)
            date2=ET.Element('date', attrib=myattributes2)
            publicationStmt.append(date1)
            publicationStmt.append(date2)

        if tree.find(".//editionStmt"):
            editionStmt=tree.find(".//editionStmt")
        else:
            editionStmt=ET.Element('editionStmt')
            canon=""
            listSubjects=tree.findall(".//subject")
            keywords=ET.Element('keywords')
            for a in listSubjects:
                if "canonique" in a.text:
                    canon="canonique"
                else:
                    canon="non-canonique"
                    term=ET.Element("term")
                    keywords.append(term)
            attProfDesc = {"type":"","tag":canon}
            profileDesc=ET.Element('profileDesc', attrib=OrderedDict([("type","genre"),("tag","canon")]))
            textClass=ET.Element('textClass')

            textClass.append(keywords)
            profileDesc.append(textClass)
            editionStmt.append(profileDesc)

        fileDesc.append(titleStmt)
        fileDesc.append(publicationStmt)
        fileDesc.append(editionStmt)

        #noises = header.getchildren()
        if header is not None:
            noises = header.getchildren()
            for noise in noises:
                noise.getparent().remove(noise)

        header.append(fileDesc)

        #tree.write(filename[:-4]+'_remastered.xml', pretty_print=True, encoding='utf8')
        base=tree.getroottree()
        base.write(target_dir+"/"+basename[basename.rfind("/")+1:]+".xml", pretty_print=True, encoding='utf8')
        nb_files+=1
        
    except (ValueError,TypeError,etree.XMLSyntaxError,AttributeError,IndexError,KeyError,StopIteration,NameError,ZeroDivisionError) as e:
        logf.write("Problème avec le fichier : "+file+"\n")
        logf.write("Erreur : "+str(e)+"\n")
        print("!!!!!!!!!!!!!!!!!!!!!!!Problème avec le fichier : "+file)

    if nb_files % 10 == 0:
        print("++++++++++++++++++++++Nombre de fichiers traités : "+str(nb_files))
        t1_stop = perf_counter()
        print("Elapsed time:", int(t1_stop-t1_start))

logf.close()
    

