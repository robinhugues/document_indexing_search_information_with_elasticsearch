from elasticsearch_research import research
from elasticsearch_index_documents import index_documents
from elasticsearch_ri_documents_extraction import documents_extraction
import os
from elasticsearch_credentials import INDEX_NAME_WITH_PP, INDEX_NAME_WITHOUT_PP, CLOUD_ID, ELASTIC_PASSWORD
from elasticsearch_connection import connect_to_elasticsearch
from elasticsearch_ri_evaluation import merge_qrels_from_folder, run_trec_eval, run_evaluation

# Chemin du dossier contenant les fichiers zip
documents_folder_path = "TREC_AP_88_90\AP"

do_preprocessing = False

similarities = ["dfr", "bm25", "scripted_tfidf"]

for similarity in similarities:

    if do_preprocessing:
        documents_json_file_name = "documents_with_preprocessing.json" if similarity == "cosine" else "documents_with_preprocessing_" + similarity + ".json"
        short_request_result_file_name = "result_short_request_preproced_" + similarity + ".txt"
        long_request_result_file_name = "result_long_request_preproced_" + similarity + ".txt"
        run_name = "ELasticsearch_RI_with_preprocessing_" + similarity
        index_name = INDEX_NAME_WITH_PP if similarity == "cosine" else INDEX_NAME_WITH_PP + "_" + similarity
    else:
        documents_json_file_name = "documents_without_preprocessing.json" if similarity == "cosine" else "documents_without_preprocessing_" + similarity + ".json"
        short_request_result_file_name = "result_short_request_" + similarity + ".txt"
        long_request_result_file_name = "result_long_request_" + similarity + ".txt"
        run_name = "ELasticsearch_RI_without_preprocessing_" + similarity
        index_name = INDEX_NAME_WITHOUT_PP if similarity == "cosine" else INDEX_NAME_WITHOUT_PP + "_" + similarity


    if documents_json_file_name not in os.listdir():
        print("Extraction des documents...")
        documents_extraction(documents_folder_path, do_preprocessing, documents_json_file_name, index_name)
    else:
        print("Les documents ont déjà été extraits")

    try:
        # Connexion à Elasticsearch
        client_es = connect_to_elasticsearch(CLOUD_ID, ELASTIC_PASSWORD)
    except Exception as e:
        print(f"Erreur de connexion à Elasticsearch : {e}")

    try:
        # verifier si l'index existe déjà dans elasticsearch
        if client_es.indices.exists(index=index_name):
            print(f"L'index {index_name} existe déjà")
        else:
            index_documents(client_es, documents_json_file_name, index_name, similarity)
    except Exception as e:
        print(f"Erreur lors de l'indexation des documents : {e}")
        
    try:
        # Recherche
        research(do_preprocessing, similarity, index_name, short_request_result_file_name, long_request_result_file_name, run_name)
    except Exception as e:
        print(f"Erreur lors de la recherche : {e}")

output_file = "jugements_de_pertinence.txt"
merge_qrels_from_folder(output_file)

print("=====> Evaluation en cours.............>")

run_trec_eval()
output_file = "jugements_de_pertinence.txt"
run_evaluation(output_file)



