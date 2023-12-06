import matplotlib.pyplot as plt
import numpy as np

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


def parse_trec_eval_output(output):
    results = {}
    lines = output.strip().split('\n')

    for line in lines:
        parts = line.split()
        measure, value = parts[0], float(parts[2])
        results[measure] = value

    # Calcul des valeurs de rappel et de précision pour la courbe PR
    num_rel = results.get('num_rel', 0)
    num_ret = results.get('num_ret', 1)
    precisions = results.get('P_1', 0) / num_ret  # Exemple avec P@1, à ajuster selon tes besoins
    recalls = results.get('num_rel_ret', 0) / num_rel if num_rel > 0 else 0

    results['precision'] = precisions
    results['recall'] = recalls

    return results


# Exemple d'utilisation
trec_eval_output = """
runid                   all     ELasticsearch_RI_with_preprocessing_bm25
num_q                   all     150
num_ret                 all     142106
num_rel                 all     25539
num_rel_ret             all     9638
map                     all     0.1488
gm_map                  all     0.0282
Rprec                   all     0.1937
bpref                   all     0.2547
recip_rank              all     0.5053
iprec_at_recall_0.00    all     0.5426
iprec_at_recall_0.10    all     0.3011
iprec_at_recall_0.20    all     0.2430
iprec_at_recall_0.30    all     0.2099
iprec_at_recall_0.40    all     0.1704
iprec_at_recall_0.50    all     0.1421
iprec_at_recall_0.60    all     0.1087
iprec_at_recall_0.70    all     0.0742
iprec_at_recall_0.80    all     0.0507
iprec_at_recall_0.90    all     0.0302
iprec_at_recall_1.00    all     0.0115
P_5                     all     0.3253
P_10                    all     0.2900
P_15                    all     0.2684
P_20                    all     0.2563
P_30                    all     0.2429
P_100                   all     0.1889
P_200                   all     0.1488
P_500                   all     0.0958
P_1000                  all     0.0643
"""

# Analyse de la sortie de trec_eval
results = parse_trec_eval_output(trec_eval_output)

# Affichage des résultats
for measure, value in results.items():
    print(f"{measure}: {value}")

# Tracé de la courbe PR
plot_pr_curve([results])
