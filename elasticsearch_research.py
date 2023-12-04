import os
import re
from elasticsearch_connection import connect_to_elasticsearch
from elasticsearch_credentials import CLOUD_ID, ELASTIC_PASSWORD
from elasticsearch_ri_preprocess import preprocess

def read_topics_file(request_folder_path):
    # Liste des fichiers des requêtes
    file_list = [f for f in os.listdir(request_folder_path) if os.path.isfile(os.path.join(request_folder_path, f))]
    topic_requests = []
    for filename in file_list:
        with open(os.path.join(request_folder_path, filename), 'r') as file:
            try:
                content = file.read()
                topic_requests.append(content)
            except TypeError as e:
                print(f"Erreur de lecture du contenu du fichier {filename} : {e}")

    return topic_requests


def get_requests(request_folder_path) :
    topic_pattern = re.compile(r'<top>(.*?)</top>', re.DOTALL)
    num_pattern = re.compile(r'<num>\s*Number:\s*(\d+)')
    title_pattern = re.compile(r'<title>\s*Topic:\s*(.*?)\s*\n')
    desc_pattern = re.compile(r'<desc>\s*Description:\s*(.*?)\s*<narr>', re.DOTALL)
    topic_requests= read_topics_file(request_folder_path)
    requests = []
    requests_metadata = {}

    for topic_requests_string in topic_requests:
        for topic in topic_pattern.finditer(topic_requests_string):
            topic_content = topic.group(1)

            num = num_pattern.search(topic_content)
            title = title_pattern.search(topic_content)
            desc = desc_pattern.search(topic_content)
            
            if(num) :
                requests_metadata = {
                    "num" : num.group(1) if num else None,
                    "title": title.group(1) if title else None,
                    "desc": desc.group(1).strip() if desc else None
                }
            requests.append(requests_metadata)
    # ordonner les requêtes en fonction du num
    requests = sorted(requests, key=lambda x: int(x["num"]))
    return requests


def short_query(client_es, requetes, index_name, do_preprocessing, short_request_result_file_name, run_name):
    with open(short_request_result_file_name, "w") as file:
        for requete in requetes:
            query = requete["title"]
            if do_preprocessing:
                query = preprocess(query)
                
            response = client_es.search(index=index_name, body={"query": {"match": {"text": query}}, "size": 1000})
            ranked_results = sorted(response["hits"]["hits"], key=lambda x: x["_score"], reverse=True)
            for rank, hit in enumerate(ranked_results):
                file.write(f"{int(requete['num'])} {0} {hit['_source']['doc_id']} {rank + 1} {hit['_score']} {run_name}\n")
        file.write


def long_query(client_es, requetes, index_name, do_preprocessing, long_request_result_file_name, run_name):
    with open(long_request_result_file_name, "w") as file:
        for requete in requetes:
            query = requete["title"] + requete["desc"]
            if do_preprocessing:
                query = preprocess(query)
            response = client_es.search(index=index_name, body={"query": {"match": {"text": query}}, "size": 1000})
            ranked_results = sorted(response["hits"]["hits"], key=lambda x: x["_score"], reverse=True)
            for rank, hit in enumerate(ranked_results):
                file.write(f"{int(requete['num'])} {0} {hit['_source']['doc_id']} {rank + 1} {hit['_score']} {run_name}\n")
        file.write


def research(do_preprocessing, similarity, index_name, short_request_result_file_name, long_request_result_file_name, run_name):
    try:
        # Connexion à Elasticsearch
        client_es = connect_to_elasticsearch(CLOUD_ID, ELASTIC_PASSWORD)
    except Exception as e:
        print(f"Erreur de connexion à Elasticsearch : {e}")
        return e
    
    # Chemin du dossier contenant les fichiers zip
    request_folder_path = "TREC_AP_88_90\Topics-requetes"

    requetes = get_requests(request_folder_path)
    print(f"Nombre de requests : {len(requetes)}")

    # supprimer les fichiers result_short_request et result_long_request s'ils existent
    if os.path.exists(short_request_result_file_name):
        os.remove(short_request_result_file_name)

    if os.path.exists(long_request_result_file_name):
        os.remove(long_request_result_file_name)

    print("=====>Recherche en cours.............>")
    try :
        # éxecuter la requête en fonction du titre du topic
        short_query(client_es, requetes, index_name, do_preprocessing, short_request_result_file_name, run_name)

        # éxecuter la requête en fonction du titre et de la description du topic
        long_query(client_es, requetes, index_name, do_preprocessing, long_request_result_file_name, run_name)

        print("Les résultats sont stockés dans les fichiers ", short_request_result_file_name, " et ", long_request_result_file_name)
    except Exception as e:
        print(f"Erreur lors de la recherche : {e}")
        return e