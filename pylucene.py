import logging, sys
logging.disable(sys.maxsize)

import lucene
import os
import simplejson as json #Used to parse json files
from org.apache.lucene.store import MMapDirectory, SimpleFSDirectory, NIOFSDirectory
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader
from org.apache.lucene.search import IndexSearcher, BoostQuery, Query
from org.apache.lucene.search.similarities import BM25Similarity
from org.apache.lucene.index import Term
from org.apache.lucene.search import WildcardQuery
from org.apache.lucene.queryparser.classic import MultiFieldQueryParser
from java.util import ArrayList

def create_index(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)
    store = SimpleFSDirectory(Paths.get(dir))
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)
    config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
    writer = IndexWriter(store, config)

    metaType = FieldType()
    metaType.setStored(True)
    metaType.setTokenized(False)

    contextType = FieldType()
    contextType.setStored(True)
    contextType.setTokenized(True)
    contextType.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)


    location = 'data'  #Directory with JSONL files 

    #go through all jsonl files
    for filename in os.listdir(location):
        if filename.endswith('.jsonl'):
            file_path = os.path.join(location, filename)
            
            with open(file_path, 'r') as file:
                #Read from file
                lines = file.readlines()
                
                #Parse each line 
                for line in lines:
                    json_data = json.loads(line)
                    
                    #attributes in the JSON data
                    id = json_data['id']
                    title = json_data['title']
                    body = json_data['body']
                    username = json_data['username']
                    upvotes = json_data['upvotes']
                    permalink = json_data['permalink']
                    comments = json_data['comments']

                    doc = Document()
                    doc.add(Field('id', str(id), metaType))
                    doc.add(Field('title', str(title), contextType))
                    doc.add(Field('body', str(body), contextType))
                    doc.add(Field('username', str(username), metaType))
                    doc.add(Field('upvotes', str(upvotes), metaType))
                    doc.add(Field('permalink', str(permalink), metaType))                    
                    writer.addDocument(doc)

    writer.close()

def retrieve(storedir, query):
    searchDir = NIOFSDirectory(Paths.get(storedir))
    searcher = IndexSearcher(DirectoryReader.open(searchDir))
    
    parser = QueryParser('title', StandardAnalyzer())
    parsed_query = parser.parse(query)
    
    # Define the fields to search over
    # fields_to_search = ['title', 'username', 'body']
    # parser = MultiFieldQueryParser(fields_to_search, StandardAnalyzer())
    # query_terms = ArrayList()
    # query_terms.add(query)  # add your query string to the list
    # parsed_query = parser.parse(query_terms)  # pass the list to the parse method 
    # print(parsed_query)

    topDocs = searcher.search(parsed_query, 10).scoreDocs
    topkdocs = []
    for hit in topDocs:
        print(hit.score)
        doc = searcher.doc(hit.doc)
        topkdocs.append({
            "score": hit.score,
            "username": doc.get("username"),
            "title": doc.get("title"),
            "upvotes": doc.get("upvotes"),
            "text": doc.get("body")
        })
    
    print(topkdocs)

def createCustomAnalyzer():
    # Create individual analyzers for each field
    titleAnalyzer = StandardAnalyzer()
    bodyAnalyzer = KeywordAnalyzer()

    # Create a map of field names to analyzers
    fieldAnalyzers = {
        "title": titleAnalyzer,
        "body": bodyAnalyzer
    }

    # Create the per-field analyzer wrapper
    perFieldAnalyzer = PerFieldAnalyzerWrapper(StandardAnalyzer(), fieldAnalyzers)

    return perFieldAnalyzer


lucene.initVM(vmargs=['-Djava.awt.headless=true'])
retrieve('food', 'how can i purposely get clumps in my')
