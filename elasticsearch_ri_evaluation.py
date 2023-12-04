import os
import subprocess


def merge_qrels_from_folder(output_file):
    print("=====> Récupération des jugements de pertinance.............>")
    
    # Chemin du dossier contenant les fichiers jugements de pertinence
    jugements_de_pertinence_folder_path = "TREC_AP_88_90\Jugements_de_pertinence"

    try:
        merged_content = ""
        for filename in os.listdir(jugements_de_pertinence_folder_path):
            filepath = os.path.join(jugements_de_pertinence_folder_path, filename)
            if os.path.isfile(filepath) and filename.endswith('.txt'):
                with open(filepath, 'r') as input_file:
                    merged_content += input_file.read()

        # Tri en fonction de la première colonne (assumant que c'est une colonne numérique)
        lines = merged_content.split('\n')
        sorted_lines = sorted(lines, key=lambda x: int(x.split()[0]) if x else float('inf'))

        with open(output_file, 'w') as output:
            output.write('\n'.join(sorted_lines))
            
    except Exception as e:
        print(f"Erreur lors de la fusion et du tri des fichiers de jugements : {e}")


def get_files_starting_with():
    current_folder = "."
    try:
        matching_files = [file for file in os.listdir(current_folder) if file.startswith("result") and file.endswith('.txt')]
        return matching_files
    except Exception as e:
        print(f"Erreur lors de la récupération des fichiers : {e}")
        return []
    


def run_trec_eval():
    # try:
        # Entrer dans le dossier trec_eval-9.0.7 dans TREX_AP_88_90
        os.chdir('trec_eval_9_0_7')

        # Compiler et Générer l'exécutable trec_eval
        subprocess.run(['make'])

        # Sortir du dossier trec_eval_9_0_7
        os.chdir('..')

    # except Exception as e:
    #     print(f"Erreur lors de la compilation de trec_eval : {e}")



def run_evaluation(qrels_file):
    try:
        matching_files = get_files_starting_with()
        os.chdir('trec_eval_9_0_7')
        # for results_file in matching_files[0]:
            
        command = f'./trec_eval -q ../{qrels_file} ../{matching_files[1]}'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"L'évaluation avec trec_eval a renvoyé: {result.returncode} {result.stderr}")

        # Sortir du dossier trec_eval_9_0_7
        os.chdir('..')
        
    except Exception as e:
        print(f"Erreur lors de l'évaluation avec trec_eval : {e}")   
    



run_trec_eval()
output_file = "jugements_de_pertinence.txt"
run_evaluation(output_file)



