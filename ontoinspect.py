import datetime
import rdflib
from rdflib import Graph,XSD,Literal,plugin,URIRef
from rdflib.namespace import Namespace,RDFS,RDF,FOAF
from rdflib.extras.describer import Describer
from rdflib.serializer import Serializer
import ontospy
import nltk
from nltk.tag import pos_tag
import urllib.request
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from bisect import bisect_left
import urllib
from urllib.parse import urlparse
import shutil
import os
import tempfile
 
stop = stopwords.words('portuguese')
 
url = 'http://portalsaude.saude.gov.br/index.php/o-ministerio/principal/secretarias/svs/zika'
url2 = 'https://www.health.zone'
text = "O zika é uma doença viral aguda, transmitida principalmente, pelos mosquitos Ae. Aegypti e Ae. albopictus, caracterizada por exantema maculopapular pruriginoso, febre intermitente, hiperemia conjuntival não purulenta e sem prurido, artralgia, mialgia e dor de cabeça. A maior parte dos casos apresentam evolução benigna e os sintomas geralmente desaparecem espontaneamente após 3-7 dias. No entanto, observa-se a ocorrência de óbitos pelo agravo, aumento dos casos de microcefalia e de manifestações neurológicas associadas à ocorrência da doença."
text2 = "O vírus Zika é um flavivírus transmitido por mosquitos e foi, pela primeira vez, identificado em macacos, no Uganda, em 1947, através de uma rede que monitorizava a febre amarela. Foi mais tarde identificado em humanos, em 1952, no Uganda e na República Unida da Tanzânia. Foram registados surtos da doença do vírus Zika em África, nas Américas, na Ásia e no Pacífico. Entre os anos 1960 e os anos 1980, foram encontradas infecções humanas em África e na Ásia, normalmente acompanhadas de doença ligeira. O primeiro grande surto da doença causado pela infecção por Zika foi notificada na ilha de Yap (Estados Federados da Micronésia), em 2007. Em Julho de 2015, o Brasil notificou uma associação entre a infecção pelo vírus Zika e a síndrome de Guillain-Barré. Em Outubro de 2015, o Brasil notificou uma associação entre a infecção pelo vírus Zika e a microcefalia."

#Extrair o texto visivel do html
def visible_text_from_url(url):
    req = urllib.request.Request(url, headers={'User-Agent' : "Magic Browser"}) 
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read())
    [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
    return soup.getText()
 
def ie_preprocess(document):
    document = ' '.join([i for i in document.split() if i not in stop])
    sentences = nltk.sent_tokenize(document)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    #sentences = [nltk.pos_tag(sent) for sent in sentences]
    return sentences

def serialize(graph, destination=None, format="xml",base=None, encoding=None, **args):
    s = plugin.get(format,Serializer)
    serializer = s(store=graph)
    if destination is None:
        stream = BytesIO()
        serializer.serialize(stream=stream, base=base, encoding=encoding,**args)
        return stream.getvalue()
    if hasattr(destination, "write"):
        stream = destination
        serializer.serialize(stream=stream, base=base, encoding=encoding, **args)
    else:
        location = destination
        scheme, netloc, path, params, _query, fragment = urlparse(location)
        if netloc != "":
            print("WARNING: not saving as location" +"is not a local file reference")
            return
        fd, name = tempfile.mkstemp()
        stream = os.fdopen(fd, "ab")
        serializer.serialize(stream=stream, base=base, encoding=encoding, **args)
        stream.close()
        if hasattr(shutil, "move"):
            shutil.move(name, path)
        else:
            shutil.copy(name, path)
            os.remove(name)         

def get_reifications(onto):
    reifications = []
    for i in onto.classes:
        if not i.children():
            reifications.insert(len(reifications),i)
    return reifications

def get_text_sentences(text):
    sentences = nltk.sent_tokenize(' '.join([i for i in text.split()]))
    return [nltk.word_tokenize(sent) for sent in sentences]

def article_annotation(d,document,concept,authorRef,presentation,base_file):
    
    #d.rel(RDF.type,ANN.base)#De onde eu tirei isso mds?
    #d.rel(RDF.type,ANN.Annotation)


    return d

def print_graph(g):
    for s, p, o in g:
        print((s, p, o))

def gen_article_annotations(basefile,doc_ref,text,concept_dict,base,author,presentation):
    lang = 'pt'
    sentences = get_text_sentences(text)
    concepts_found = list()
    search_remaining_concepts = [nltk.word_tokenize(i) for i in concept_dict.keys()]
    
    AO = Namespace("http://smiy.sourceforge.net/ao/rdf/associationontology.owl")
    PAV = Namespace("http://cdn.rawgit.com/pav-ontology/pav/2.0/pav.owl")
    #ANN = Namespace("https://www.w3.org/2000/10/annotation-ns#annotates")
    AOF = Namespace("http://annotation-ontology.googlecode.com/svn/trunk/annotation-foaf.owl")

    graph = Graph()
    if os.path.isfile(basefile):
        graph.parse(basefile, format="xml")
        d = Describer(graph,base = "http://organizacao.com")
    else:
        print("Arquivo de anotações não encontrado ou ilegível.Outro será criado")
        d = Describer(graph,base = "http://organizacao.com")
        d.value(RDFS.comment,presentation, lang=lang)
        
    graph.bind('aof',AOF)
    graph.bind('ao',AO)
    graph.bind('pav',PAV)

    while len(search_remaining_concepts) > 0:
        biggest_concept_lenght = len(max(search_remaining_concepts,key = len))
        biggest_concept_items = [x for x in search_remaining_concepts if len(x) == biggest_concept_lenght]
        search_remaining_concepts = [x for x in search_remaining_concepts if x not in biggest_concept_items]
            
        for sentence in sentences:
            if len(sentence) >= biggest_concept_lenght:
                for k in range(0,len(sentence) - biggest_concept_lenght):
                    biggest_concept_items_cp = biggest_concept_items
                    for concept in biggest_concept_items_cp:
                        if concept not in concepts_found:
                        #Compara o conceito com os itens  de -(k + biggest_concept_lenght) até -k
                            if [i.upper() for i in concept] == [i.upper() for i in sentence[-(k + biggest_concept_lenght):-k]]:
                                concepts_found.insert(len(concepts_found),concept)
                                d.rel(RDF.type,AO.Annotation)
                                d.rel(AOF.annotatesDocument,doc_ref)
                                d.rel(AO.hasTopic,concept_dict[' '.join(concept)].uri)
                                d.rel(PAV.createdOn,Literal(datetime.datetime.now(),datatype=XSD.date))
                                d.rel(PAV.createdB,author)
                                graph.commit()
                                d = Describer(graph,base = "http://organizacao.com")
                                biggest_concept_items.remove(concept)
    return graph


onto = ontospy.Ontospy("root-ontology.owl")
web_concepts = get_reifications(onto)
concept_dict = dict()

for i in web_concepts:
    text_concept = str(i.uri).partition('#')[-1].replace('_',' ')
    concept_dict[text_concept] = i

serialize(gen_article_annotations("base.rdf",url,text,concept_dict,"www.semanticdev.com","Vitor Silva","Anotação semântica para textos jornalísticos"),format='xml', destination = 'base.rdf')


