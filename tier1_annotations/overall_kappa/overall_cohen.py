import re


def parse_file(filename):
    with open(filename, 'r') as file:
        data = file.read()
    pattern = r"Model: (.*?)\nAgreement for 'extracted_correctly': (.*?)\nAgreement for 'is_factual': (.*?)\nNumber of datapoints: (\d+)"
    parsed_data = re.findall(pattern, data, re.DOTALL)

    models_data = []
    for model, extracted_correctly, is_factual, num_datapoints in parsed_data:
        models_data.append({
            'model': model.strip(),
            'extracted_correctly': float(extracted_correctly.strip()),
            'is_factual': float(is_factual.strip()),
            'num_datapoints': int(num_datapoints.strip())
        })
    return models_data


def calculate_weighted_average(data, key):
    total_weighted_value = sum(d[key] * d['num_datapoints'] for d in data)
    total_datapoints = sum(d['num_datapoints'] for d in data)
    return total_weighted_value / total_datapoints, total_datapoints


def combine_data(files):
    combined_data = {}
    overall_data = []

    for file in files:
        file_data = parse_file(file)
        for entry in file_data:
            model = entry['model']
            if model not in combined_data:
                combined_data[model] = []
            combined_data[model].append(entry)
            overall_data.append(entry)

    return combined_data, overall_data


def calculate_combined_kappa(combined_data):
    combined_kappa = {}
    for model, data in combined_data.items():
        avg_extracted_correctly, _ = calculate_weighted_average(
            data, 'extracted_correctly')
        avg_is_factual, _ = calculate_weighted_average(data, 'is_factual')
        combined_kappa[model] = {
            'extracted_correctly': avg_extracted_correctly,
            'is_factual': avg_is_factual,
        }
    return combined_kappa


# Files to read data from
files = ['Pair1.txt', 'Pair2.txt', 'Pair3.txt']

# Combine data from all files
combined_data, overall_data = combine_data(files)

# Calculate combined Cohen's Kappa for each model
combined_kappa = calculate_combined_kappa(combined_data)

# Calculate overall combined Cohen's Kappa
overall_extracted_correctly, overall_num_datapoints_extracted = calculate_weighted_average(
    overall_data, 'extracted_correctly')
overall_is_factual, overall_num_datapoints_factual = calculate_weighted_average(
    overall_data, 'is_factual')

# Print results for each model
for model, kappa_values in combined_kappa.items():
    print(f"Model: {model}")
    print(
        f"Combined Agreement for 'extracted_correctly': {kappa_values['extracted_correctly']:.4f}")
    print(
        f"Combined Agreement for 'is_factual': {kappa_values['is_factual']:.4f}")
    print()

# Print overall results
print("Overall Combined Agreement Across All Models:")
print(
    f"Overall combined agreement for 'extracted_correctly': {overall_extracted_correctly:.4f}")
print(f"Overall combined agreement for 'is_factual': {overall_is_factual:.4f}")
print(
    f"Overall number of datapoints for 'extracted_correctly': {overall_num_datapoints_extracted}")
print(
    f"Overall number of datapoints for 'is_factual': {overall_num_datapoints_factual}")
