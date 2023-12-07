# import matplotlib
# matplotlib.use('TkAgg')  # 'TkAgg' ou 'Qt5Agg' selon ton environnement
import matplotlib.pyplot as plt

def plot_pr_curve(results):
    recalls = []
    precisions = []

    for result in results:
        recall = result["recall"]
        precision = result["precision"]
        recalls.append(recall)
        precisions.append(precision)

    plt.plot(recalls, precisions, label='PR Curve')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve')
    plt.legend()
    plt.show()


def parse_trec_eval_file(file_path):
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

    # Choisis une mesure de précision appropriée (par exemple, P_5 ou P_10)
    precision_measure = 'P_5'

    # Calcul des valeurs de rappel et de précision pour la courbe PR
    num_rel = results.get('num_rel', 0)
    num_ret = results.get('num_ret', 1)
    precisions = results.get(precision_measure, 0) / num_ret if num_ret > 0 else 0
    recalls = results.get('num_rel_ret', 0) / num_rel if num_rel > 0 else 0

    results['precision'] = precisions
    results['recall'] = recalls

    return results

# Exemple d'utilisation
# trec_eval_file_path = 'trec_eval_evaluation_result_long_request_bm25.txt'
trec_eval_file_path = 'trec_eval_evaluation_result_long_request_dfr.txt'
# trec_eval_file_path = 'trec_eval_evaluation_result_long_request_scripted_tfidf.txt'
# trec_eval_file_path = 'trec_eval_evaluation_result_short_request_bm25.txt'
# trec_eval_file_path = 'trec_eval_evaluation_result_short_request_dfr.txt'
# trec_eval_file_path = 'trec_eval_evaluation_result_short_request_scripted_tfidf.txt'

# Analyse du fichier trec_eval
results = parse_trec_eval_file(trec_eval_file_path)

# Affichage des résultats
for measure, value in results.items():
    print(f"{measure}: {value}")

# Tracé de la courbe PR
plot_pr_curve([results])
