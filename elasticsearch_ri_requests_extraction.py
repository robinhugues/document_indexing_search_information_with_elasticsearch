import os
import re


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