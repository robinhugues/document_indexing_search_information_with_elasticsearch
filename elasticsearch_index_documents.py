from elasticsearch import helpers
import json


def extract_documents_from_json(documents_json_file_name):
    try:
        with open(documents_json_file_name, 'r') as file:
            data = json.load(file)

        # Vérifie si le fichier JSON est une liste de documents
        if isinstance(data, list):
            documents = data
            return documents
        else:
            print("Le fichier JSON ne contient pas une liste de documents.")
            return None

    except json.JSONDecodeError:
        print(f"Erreur lors du décodage JSON dans le fichier {documents_json_file_name}.")
        return None


def index_documents(client_es, documents_json_file_name, index_name, similarity):
 
    # lire dans le fichier json des documents et récupérer les documents
    documents = extract_documents_from_json(documents_json_file_name)
    print(f"=====> Nombre de documents à indexer : {len(documents)} .............>")

    # Créer un tableau contenant les différents types de similarité
    similarities  = {
        "dfr" : {
            "dfr" : {
                "type": "DFR",
                "basic_model": "g",
                "after_effect": "l",
                "normalization": "h2",
                "normalization.h2.c": "3.0"    
            }
        }, 
        "bm25" : {
            "default": {
                "type": "BM25",
                "b": 0.75,
                "k1": 1.2
            }
        },
        "scripted_tfidf" : {
            "scripted_tfidf": {
                "type": "scripted",
                "script": {
                    "source": "double tf = Math.sqrt(doc.freq); double idf = Math.log((field.docCount+1.0)/(term.docFreq+1.0)) + 1.0; double norm = 1/Math.sqrt(doc.length); return query.boost * tf * idf * norm;"
                }
            }
        }
    }

    body = {
        "mappings": {
            "properties": {
                "language": {"type": "keyword"},
                "id": {"type": "keyword"},
                "title": {"type": "text"},
                "passage": {"type": "text"},
                "passage_embedding": {
                    "type": "dense_vector",
                    "dims": 768,
                    "index": "true",
                    "similarity": "cosine"
                }
            }
        },
        "settings" : {
            "number_of_shards": 1,
            "similarity": similarities[similarity]
        }
    }

    # Création de l'index
    try:
        client_es.indices.create(index=index_name, body=body)
        print(f"=====> Index {index_name} créé avec succès .............>")
    except Exception as e:
        print(f"Erreur lors de la création de l'index {index_name} : {e}")
        return e

    try:
        print(f"=====> Indexation des documents dans l'index {index_name}.............>")
        # indexer les documents JSON dans Elasticsearch
        helpers.bulk(client_es, documents)
        response = client_es.search(index=index_name, body={"query": {"match_all": {}}})
        print(f"Nombre de documents indexés : {response['hits']['total']['value']}")

    except Exception as e:
        print(f"Erreur lors de l'indexation des documents : {e}")
        return e

    # fermer la connexion à Elasticsearch
    client_es.transport.close()