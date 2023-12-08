import os
import subprocess
import sys
from elasticsearch_ri_global_functions import get_files_starting_by_result


def merge_qrels_from_folder(output_file):
    print("...... Récupération des jugements de pertinance.............")

    # supprimer le fichier s'il existe déjà
    if os.path.exists(output_file):
        os.remove(output_file)
    
    # Chemin du dossier contenant les fichiers jugements de pertinence
    jugements_de_pertinence_folder_path = "TREC_AP_88_90/Jugements_de_pertinence"

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
        sys.exit(1)
    

def run_trec_eval():
    print("...... Compilation et Génération des liens de trec_eval.............")
    try:
        # Entrer dans le dossier trec_eval-9.0.7 dans TREX_AP_88_90
        os.chdir('trec_eval_9_0_7')

        # Compiler et Générer l'exécutable trec_eval
        subprocess.run(['make'])

        # Sortir du dossier trec_eval_9_0_7
        os.chdir('..')

    except Exception as e:
        print(f"Erreur lors de la compilation de trec_eval : {e}")



def run_evaluation(qrels_file):
    print("........ Evaluation en cours.............")
    matching_files = get_files_starting_by_result()
    os.chdir('trec_eval_9_0_7')
    for results_file in matching_files:
        try:
            command = f'./trec_eval ../{qrels_file} ../{results_file}'
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                # stocker le resultat dans un fichier
                with open(f"../trec_eval_evaluation_{results_file}", 'w') as output:
                    output.write(result.stdout)
            else:
                print(f"L'évaluation avec trec_eval a renvoyé: {result.returncode} {result.stderr}")
        except Exception as e:
            print(f"Erreur lors de l'évaluation avec trec_eval : {e}") 
            sys.exit(1)

    # Sortir du dossier trec_eval_9_0_7 
    os.chdir('..')
    print("Evaluation avec trec_eval terminée avec succès")


def main():
    try:
        output_file = "jugements_de_pertinence.txt"
        merge_qrels_from_folder(output_file)
        run_trec_eval()
        run_evaluation(output_file)
    except Exception as e:
        print(f"Erreur lors de l'évaluation avec trec_eval : {e}")
        sys.exit(1)

# Lancer le programme
main()
        