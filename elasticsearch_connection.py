from elasticsearch import Elasticsearch

def connect_to_elasticsearch(cloud_id, elastic_password):

    client_es = Elasticsearch(
        cloud_id=cloud_id,
        basic_auth=("elastic", elastic_password)
    )

    if client_es.info():
        print('Connecté à Elasticsearch')
        return client_es
    else:
        print('Elasticsearch ne répond pas')
        return None
