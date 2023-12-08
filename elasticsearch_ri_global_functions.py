import os


def get_files_starting_by_result():
    current_folder = "."
    try:
        matching_files = [file for file in os.listdir(current_folder) if file.startswith("result") and file.endswith('.txt')]
        return matching_files
    except Exception as e:
        print(f"Erreur lors de la récupération des fichiers : {e}")
        return []
    
def get_files_starting_by_trec_eval_evaluation_result():
    current_folder = "."
    try:
        matching_files = [file for file in os.listdir(current_folder) if file.startswith("trec_eval_evaluation_result") and file.endswith('.txt')]
        return matching_files
    except Exception as e:
        print(f"Erreur lors de la récupération des fichiers : {e}")
        return []