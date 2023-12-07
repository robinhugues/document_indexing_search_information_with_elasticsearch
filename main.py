import os
import sys
from dotenv import load_dotenv
# Chargement des variables d'environnement depuis le fichier .env
load_dotenv()
from elasticsearch_ri_global_variables import INDEX_NAME_WITH_PP, INDEX_NAME_WITHOUT_PP, SIMILARITIES
from elasticsearch_ri_research import research
from elasticsearch_ri_documents_indexing import index_documents
from elasticsearch_ri_documents_extraction import documents_extraction
from elasticsearch_connection import connect_to_elasticsearch
from elasticsearch_ri_requests_extraction import get_requests
from elasticsearch_ri_evaluation import merge_qrels_from_folder, run_trec_eval, run_evaluation, get_files_starting_by_result


elastic_password = os.environ.get("ELASTIC_PASSWORD")
cloud_id = os.environ.get("CLOUD_ID")

# Chemin du dossier contenant les fichiers zip
documents_folder_path = "TREC_AP_88_90/AP"

# Chemin du dossier contenant les fichiers zip
request_folder_path = "TREC_AP_88_90/Topics-requetes"

try:
    requetes = get_requests(request_folder_path)
    print(f"Les {len(requetes)} requêtes ont été récupérées")
except Exception as e:
    print(f"Erreur lors de la récupération des requêtes : {e}")
    sys.exit(1)

do_preprocessing = False

research_result_files = get_files_starting_by_result()

# Connexion à Elasticsearch
try:
    client_es = connect_to_elasticsearch(cloud_id, elastic_password)
except Exception as e:
    print(f"Erreur de connexion à Elasticsearch : {e}")
    sys.exit(1)

for similarity in SIMILARITIES:

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

    # Extraction des documents
    try :
        if documents_json_file_name not in os.listdir():
            documents_extraction(documents_folder_path, do_preprocessing, documents_json_file_name, index_name)
        else:
            print("Les documents ont déjà été extraits dans le fichier json : ", documents_json_file_name)
    except Exception as e:
        print(f"Erreur lors de l'extraction des documents : {e}")
        sys.exit(1)

    # verifier si l'index existe déjà dans elasticsearch
    try:
        if not client_es.indices.exists(index=index_name):
            index_documents(client_es, documents_json_file_name, index_name, similarity)
    except Exception as e:
        print(f"Erreur lors de l'indexation des documents : {e}")
        sys.exit(1)

    # Recherche d'information
    try:
        print("....... Recherche d'information sur les documents de l'index : ", index_name, " .............")
        if(len(research_result_files) == 12):
            print("Les résultats de la recherche existent déjà")
        else:
            requests_types = ["short", "long"]
            for type_request in requests_types:
                if type_request == "short":
                    request_result_file_name = short_request_result_file_name
                else:
                    request_result_file_name = long_request_result_file_name

                research(requetes, client_es, do_preprocessing, index_name, request_result_file_name, run_name, type_request)
            print("Les requêtes sur les documents de l'index :", index_name ," ont été exécutées avec succès")
    except Exception as e:
        print(f"Erreur lors de la recherche : {e}")
        sys.exit(1)

    print("\n")
print("Fin de l'indexation et de la recherche d'information")


# déconnexion de Elasticsearch
try:
    client_es.transport.close()
    print("Déconnexion de Elasticsearch")
except Exception as e:
    print(f"Erreur lors de la déconnexion de Elasticsearch : {e}")
    sys.exit(1)


print("\n")

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
    print("Exécutez d'abord toutes les requêtes avant de faire l'évaluation avec trec_eval")