from rdflib import Graph
import ontospy
from rdflib import URIRef
import nltk
import rdflib
from nltk.tag import pos_tag   
import re
import urllib.request
from bs4 import BeautifulSoup
#from newspaper import Article
from nltk.corpus import stopwords
from bisect import bisect_left
import urllib
 
stop = stopwords.words('portuguese')
 
url = 'http://www.minhavida.com.br/saude/temas/zika-virus'
 
#Extrair o texto visivel do html
def visible_text_from_html(url):
    html = urlopen(url)
    soup = BeautifulSoup(html)
    [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
    return(soup.getText())
 
def ie_preprocess(document):
    document = ' '.join([i for i in document.split() if i not in stop])
    sentences = nltk.sent_tokenize(document)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    #sentences = [nltk.pos_tag(sent) for sent in sentences]
    return sentences
 
req = urllib.request.Request(url, headers={'User-Agent' : "Magic Browser"}) 
con = urllib.request.urlopen(req)
soup = BeautifulSoup(con.read())
[s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
 

sentences = ie_preprocess(soup.getText())
graph = rdflib.Graph()


onto = ontospy.Ontospy("root-ontology.owl")
#onto.printClassTree()
l = set(onto.classes)

a = []
print("Anotações:")
for sentence in sentences:
    for token in sentence:
        for i in l:
            s = str(i).partition('#')[-1].rpartition('*')[0].replace('_',' ')
            if sentence[0] == s:
                if s not in a:
                    a.insert(len(a),s)
                    print('<' + url + ',' + str(i) + ',' + token + '>')
 
