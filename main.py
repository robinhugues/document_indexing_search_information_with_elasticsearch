from elasticsearch_research import research
from elasticsearch_index_documents import index_documents
from elasticsearch_ri_documents_extraction import documents_extraction
import os
import sys
from elasticsearch_credentials import INDEX_NAME_WITH_PP, INDEX_NAME_WITHOUT_PP, CLOUD_ID, ELASTIC_PASSWORD
from elasticsearch_connection import connect_to_elasticsearch
from elasticsearch_ri_evaluation import merge_qrels_from_folder, run_trec_eval, run_evaluation, get_files_starting_by_result

# Chemin du dossier contenant les fichiers zip
documents_folder_path = "TREC_AP_88_90/AP"

do_preprocessing = True

similarities = ["dfr", "bm25", "scripted_tfidf"]

research_result_files = get_files_starting_by_result()

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

    try :
        if documents_json_file_name not in os.listdir():
            documents_extraction(documents_folder_path, do_preprocessing, documents_json_file_name, index_name)
        else:
            print("Les documents ont déjà été extraits")
    except Exception as e:
        print(f"Erreur lors de l'extraction des documents : {e}")
        sys.exit(1)

    try:
        # Connexion à Elasticsearch
        client_es = connect_to_elasticsearch(CLOUD_ID, ELASTIC_PASSWORD)
    except Exception as e:
        print(f"Erreur de connexion à Elasticsearch : {e}")
        sys.exit(1)

    try:
        # verifier si l'index existe déjà dans elasticsearch
        if client_es.indices.exists(index=index_name):
            print(f"L'index {index_name} existe déjà")
        else:
            index_documents(client_es, documents_json_file_name, index_name, similarity)
    except Exception as e:
        print(f"Erreur lors de l'indexation des documents : {e}")
        sys.exit(1)

    # Recherche  
    try:
        if(len(research_result_files) == 12):
            print("Les résultats de la recherche existent déjà")
        else:
            research(do_preprocessing, similarity, index_name, short_request_result_file_name, long_request_result_file_name, run_name)
    except Exception as e:
        print(f"Erreur lors de la recherche : {e}")
        sys.exit(1)


# Evaluation avec trec_eval
if(len(research_result_files) == 12):
    try:
        output_file = "jugements_de_pertinence.txt"
        merge_qrels_from_folder(output_file)
        run_trec_eval()
        run_evaluation(output_file)
    except Exception as e:
        print(f"Erreur lors de l'évaluation avec trec_eval : {e}")
        sys.exit(1)
else:
    print("Exécutez d'abord la recherche avant d'évaluer avec trec_eval")