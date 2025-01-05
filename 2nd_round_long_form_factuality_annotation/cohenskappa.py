import os
import json
from sklearn.metrics import cohen_kappa_score

# Directories where annotator files are stored
dir_sheza = "annotations_sheza"
dir_leczhang = "annotations_Xin"
# dir_leczhang = "annotations_farima"
# pair1 - sheza lechen, pair2 - lechen farima, pair3 - farima sheza

# List of models to calculate agreement for
models = ['gpt4o_mini', 'llama3.1_7b']


def load_annotations(directory):
    annotations = {}
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), 'r') as f:
                data = json.load(f)
                for entry in data:
                    model_name = entry['model_name']
                    key = (model_name, entry['instance_id'], entry['fact_id'])
                    if model_name not in annotations:
                        annotations[model_name] = {}
                    annotations[model_name][key] = {
                        'extracted_correctly': entry['extracted_correctly'],
                        'is_factual': entry['is_factual']
                    }
    return annotations


def calculate_cohens_kappa_for_model(annotations_sheza, annotations_leczhang, model):
    # Prepare data for Cohen's Kappa calculation
    extracted_correctly_sheza = []
    extracted_correctly_leczhang = []
    is_factual_sheza = []
    is_factual_leczhang = []

    for key in annotations_sheza.get(model, {}):
        if key in annotations_leczhang.get(model, {}):
            extracted_correctly_sheza.append(
                annotations_sheza[model][key]['extracted_correctly'])
            extracted_correctly_leczhang.append(
                annotations_leczhang[model][key]['extracted_correctly'])
            is_factual_sheza.append(
                annotations_sheza[model][key]['is_factual'])
            is_factual_leczhang.append(
                annotations_leczhang[model][key]['is_factual'])

    num_data_points = len(extracted_correctly_sheza)  # Count data points

    if extracted_correctly_sheza and is_factual_sheza:  # Check if there is data for the model
        return (
            cohen_kappa_score(extracted_correctly_sheza,
                              extracted_correctly_leczhang),
            cohen_kappa_score(is_factual_sheza, is_factual_leczhang),
            num_data_points  # Return number of data points
        )
    else:
        return None, None, 0


def accumulate_overall_annotations(annotations_sheza, annotations_leczhang):
    overall_extracted_correctly_sheza = []
    overall_extracted_correctly_leczhang = []
    overall_is_factual_sheza = []
    overall_is_factual_leczhang = []

    for model in models:
        for key in annotations_sheza.get(model, {}):
            if key in annotations_leczhang.get(model, {}):
                overall_extracted_correctly_sheza.append(
                    annotations_sheza[model][key]['extracted_correctly'])
                overall_extracted_correctly_leczhang.append(
                    annotations_leczhang[model][key]['extracted_correctly'])
                overall_is_factual_sheza.append(
                    annotations_sheza[model][key]['is_factual'])
                overall_is_factual_leczhang.append(
                    annotations_leczhang[model][key]['is_factual'])

    # Count overall data points
    num_data_points_overall = len(overall_extracted_correctly_sheza)

    return (
        cohen_kappa_score(overall_extracted_correctly_sheza,
                          overall_extracted_correctly_leczhang),
        cohen_kappa_score(overall_is_factual_sheza,
                          overall_is_factual_leczhang),
        num_data_points_overall  # Return overall number of data points
    )


# Load annotations for both annotators
annotations_sheza = load_annotations(dir_sheza)
annotations_leczhang = load_annotations(dir_leczhang)

# Calculate Cohen's Kappa for each model
for model in models:
    kappa_extracted_correctly, kappa_is_factual, num_data_points = calculate_cohens_kappa_for_model(
        annotations_sheza, annotations_leczhang, model)

    # Print results
    if kappa_extracted_correctly is not None:
        print(f"Model: {model}")
        print(
            f"Agreement for 'extracted_correctly': {kappa_extracted_correctly:.4f}")
        print(f"Agreement for 'is_factual': {kappa_is_factual:.4f}")
        print(f"Number of datapoints: {num_data_points}")
    else:
        print(f"No data for model: {model}")

# Calculate overall agreement
overall_kappa_extracted_correctly, overall_kappa_is_factual, overall_num_data_points = accumulate_overall_annotations(
    annotations_sheza, annotations_leczhang)

print("\nOverall Agreement Across All Models:")
print(
    f"Overall agreement for 'extracted_correctly': {overall_kappa_extracted_correctly:.4f}")
print(f"Overall agreement for 'is_factual': {overall_kappa_is_factual:.4f}")
print(f"Overall number of datapoints: {overall_num_data_points}")
