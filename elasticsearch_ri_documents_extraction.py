import os
import gzip
import re
import json
from elasticsearch_ri_preprocess import preprocess
import enlighten
import time

manager = enlighten.get_manager()
pbar = manager.counter(desc='Basic', unit='ticks')

def read_zip_file(documents_folder_path):
    # Liste des fichiers à extraire
    file_list = [f for f in os.listdir(documents_folder_path) if os.path.isfile(os.path.join(documents_folder_path, f))]
    blocs = []
    for filename in file_list:
        with gzip.open(os.path.join(documents_folder_path, filename), 'rt') as file:
            try:
                content = file.read()
                blocs.append(content)
            except TypeError as e:
                print(f"Erreur de lecture du contenu du fichier {filename} : {e}")

    return blocs


def documents_extraction(documents_folder_path, do_preprocessing, documents_file_name, index) :
    print("=====> Extraction des documents ..........")
    doc_pattern = re.compile(r'<DOC>(.*?)</DOC>', re.DOTALL)
    docno_pattern = re.compile(r'<DOCNO>\s*(.*?)\s*</DOCNO>')
    head_pattern = re.compile(r'<HEAD>\s*(.*?)\s*</HEAD>')
    text_pattern = re.compile(r'<TEXT>\s*(.*?)\s*</TEXT>', re.DOTALL)
  
    documents = []
    documents_metadata = {}

    try:
        blocs = read_zip_file(documents_folder_path)
    except Exception as e:
        print(f"Erreur lors de la lecture des fichiers zip : {e}")
        return e

    # Iterating over each matched DOC block
    for doc_string in blocs:
        time.sleep(0.1) 
        pbar.update()
        for doc in doc_pattern.finditer(doc_string):
            doc_content = doc.group(1)
            # Extracting individual elements
            doc_id = docno_pattern.search(doc_content).group(1)
            head_elem = head_pattern.search(doc_content)
            text_elem = text_pattern.search(doc_content)

            title = head_elem.group(1) if head_elem else ""
            text = text_elem.group(1) if text_elem else ""
        
            if do_preprocessing:
                title = preprocess(title)
                text = preprocess(text)
            
            # Populating the dictionary
            documents_metadata = {
                "_index": index,
                "doc_id": doc_id,
                "title": title,
                "text": text
            }

            documents.append(documents_metadata)

    # Save the list of metadata dictionaries to a JSON file
    try:
        with open(documents_file_name, 'w') as json_file:
            json.dump(documents, json_file)
        print(f"Nombre de documents extraits et enregistrés : {len(documents)}")
    except Exception as e:
        print(f"Erreur lors de l'extraction des documents : {e}")
        return e


  
