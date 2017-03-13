
# coding: utf-8

# In[64]:

import xml.etree.ElementTree as ET
import copy
import sys
import os
import xml.etree.ElementTree as ET
import fnmatch
from bs4 import BeautifulSoup


# In[68]:

ns = {'dc': 'http://purl.org/dc/elements/1.1/'}

for idx, fileTemp in enumerate(fnmatch.filter(os.listdir(sys.argv), '*.xml')):
    tei = open(sys.argv+fileTemp).read()
    print (fileTemp)
    title=BeautifulSoup(tei).find('dc:date').text[:4]+'_'+BeautifulSoup(tei).find('dc:creator').text.replace(" ", "_")+'_'+BeautifulSoup(tei).find('dc:title').text.replace(" ", "_")
    if not os.path.exists('./output/'):
        os.makedirs('./output/')
    f = open('./output/'+title+'.xml', 'w')
    f.write(tei)
    f.close()
   


# In[ ]:


