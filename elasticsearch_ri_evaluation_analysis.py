import matplotlib.pyplot as plt
from elasticsearch_ri_global_functions import get_files_starting_by_trec_eval_evaluation_result


def plot_pr_curve(results_list):

    plt.figure()

    for results in results_list:
        for result in results:
            recall = result["recall"]
            precision = result["precision"]
            label = result["runid"]
            
            print(f"Requête : {label}")
            print(f"Rappels : {recall}")
            print(f"Précisions : {precision}")
           
            plt.plot(recall, precision, label=label)

    plt.xlabel('Rappel')
    plt.ylabel('Précision')
    plt.title("Courbe Rappel-Précision sur l'ensemble des requêtes")
    plt.legend()
    plt.show()



def parse_trec_eval_file(files_paths):

    all_results = []
    for file_path in files_paths:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        results = {}
        for line in lines:
            parts = line.split()
            if len(parts) >= 3:
                try:
                    measure, value = parts[0], float(parts[2])
                    results[measure] = value
                except ValueError:
                    pass  # Ignore les lignes qui ne peuvent pas être converties en nombre
                
                # ajouter la ligne dont la valeur est une chaine de caractères
                if parts[0] == 'runid':
                    results['runid'] = parts[2]
        
        R = ['0.00', '0.10', '0.20', '0.30', '0.40', '0.50', '0.60', '0.70', '0.80', '0.90', '1.00']
        # Initialiser precisions avec des zéros
        precisions = [0.0] * len(R)
        recalls = []

        # convertir la liste des rappels en liste de float
        rec = R.copy()
        recalls = list(map(float, rec))

        # Mise à jour des valeurs de précision et de rappel si elles sont présentes dans le dictionnaire results
        for i, r in enumerate(R):
            key = f'iprec_at_recall_{r}'
            if key in results:
                precisions[i] = results[key]

        # Ajout des valeurs de précision et de rappel à la liste des résultats
        results['precision'] = precisions
        results['recall'] = recalls

        all_results.append(results)

    return all_results


trec_eval_files = get_files_starting_by_trec_eval_evaluation_result()

# Analyse du fichier trec_eval
results_list = parse_trec_eval_file(trec_eval_files)

# Tracé de la courbe PR
plot_pr_curve([results_list])
