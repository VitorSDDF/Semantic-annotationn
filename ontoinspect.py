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
 
url = 'http://portalsaude.saude.gov.br/index.php/o-ministerio/principal/secretarias/svs/zika'
 
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
 
#sentences = ie_preprocess(soup.getText())
sentences = ' '.join([i for i in soup.getText().split()])
sentences = nltk.sent_tokenize(sentences)
sentences = [nltk.word_tokenize(sent) for sent in sentences]

onto = ontospy.Ontospy("root-ontology.owl")

l = set(onto.classes)

reifications = []
for i in onto.classes:
    if not i.children():
        reifications.insert(len(reifications),i)

reifications = [str(i).partition('#')[-1].rpartition('*')[0].replace('_',' ') for i in reifications]
reifications = [nltk.word_tokenize(sent) for sent in reifications]

a = list()

print("Anotações:")
while len(reifications) > 0:
    biggest_concept_lenght = len(max(reifications,key = len))
    biggest_concept_items = [x for x in reifications if len(x) == biggest_concept_lenght]

    reifications = [x for x in reifications if x not in biggest_concept_items]
    for sentence in sentences:
        if len(sentence) >= biggest_concept_lenght:
            for k in range(0,len(sentence) - biggest_concept_lenght):
                biggest_concept_items_cp = biggest_concept_items
                for concept in biggest_concept_items_cp:
                    if concept not in a:
                        #Compara o conceito com os itens  de -(k + biggest_concept_lenght) até -k
                        if [i.upper() for i in concept] == [i.upper() for i in sentence[-(k + biggest_concept_lenght):-k]]:
                            a.insert(len(a),concept)
                            print('<' + url + ',' + "predicado" + ',' + str(concept) + '>')
                            biggest_concept_items.remove(concept)

