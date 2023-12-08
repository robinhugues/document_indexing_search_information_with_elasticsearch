import os
from elasticsearch_ri_preprocess import preprocess


def query(client_es, requetes, index_name, do_preprocessing, result_file_name, run_name, type_request):
    with open(result_file_name, "w") as file:
        for requete in requetes:
            if type_request == "short":
                query = requete["title"]
            else:
                query = requete["title"] + requete["desc"]
            
            if do_preprocessing:
                query = preprocess(query)

            body = {    
                "query": {
                    "match": {
                        "text": query
                    }
                },
                "size": 1000
            }
                
            response = client_es.search(index=index_name, body=body)
            # trier les résultats par score et par doc_id
            ranked_results = sorted(response["hits"]["hits"], key=lambda x: (x["_score"]), reverse=True)
            for rank, hit in enumerate(ranked_results):
                file.write(f"{int(requete['num'])} {0} {hit['_source']['doc_id']} {rank + 1} {hit['_score']} {run_name}\n")
        file.write


def research(requetes, client_es, do_preprocessing, index_name, request_result_file_name, run_name, type_request):
    
    # supprimer les fichiers result_short_request et result_long_request s'ils existent
    if os.path.exists(request_result_file_name):
        os.remove(request_result_file_name)

    # éxecuter les requêtes
    try :
        query(client_es, requetes, index_name, do_preprocessing, request_result_file_name, run_name, type_request)
    except Exception as e:
        print(f"Erreur lors de la recherche : {e}")
        return e