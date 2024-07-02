from flask import Flask, render_template, request, session, redirect, jsonify
import json
import os
import csv

app = Flask(__name__)
app.secret_key = 'randomsecretkey12345'  # Change this to a random secret key

# Load the JSON files
DATA_FOLDER = 'units'
json_files = sorted([f for f in os.listdir(DATA_FOLDER) if f.endswith(
    '_units.json')], key=lambda x: int(x.split('_')[0]))

data = []
for file in json_files:
    with open(os.path.join(DATA_FOLDER, file), 'r') as f:
        entry = json.load(f)
        entry['units_and_labels'] = entry.get(
            'atomic_units_and_labels', {}).get('units_and_labels', {})
        entry['num_units'] = entry.get(
            'atomic_units_and_labels', {}).get('num_units', 0)
        data.append(entry)

dataset_length = len(data)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect('/0')
    elif 'username' in session:
        return redirect('/0')
    return render_template('login.html')


@app.route('/<int:entry_index>', methods=['GET'])
def view_entry(entry_index=0):
    if 'username' not in session:
        return redirect('/')

    if entry_index < 0:
        entry_index = 0
    elif entry_index >= len(data):
        entry_index = len(data) - 1

    entry = data[entry_index]

    return render_template('index.html', entry_index=entry_index, username=session.get('username', 'Unknown'),
                           prompt=entry['prompt'], response=entry['response'],
                           units_and_labels=entry['units_and_labels'], num_units=entry['num_units'],
                           dataset_length=dataset_length)


@app.route('/change_user', methods=['POST'])
def change_user():
    session.pop('username', None)  # Removes username from session
    return redirect('/')


@app.route('/save', methods=['POST'])
def save_annotations():
    username = session.get('username')
    if not username:
        return redirect('/')

    entry_index = request.form['entry_index']
    annotations = []
    for key in request.form:
        if key.startswith('label_assigned_'):
            index = key.split('_')[-1]
            annotations.append([entry_index, index,
                                request.form.get(f'label_assigned_{index}'),
                                request.form.get(f'independent_unit_extracted_{index}')])

    directory = os.path.join(username)
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = os.path.join(directory, 'annotations_data.csv')

    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        # Only write headers if file is new/empty
        if os.stat(file_path).st_size == 0:
            writer.writerow(
                ['cluster_id', 'sentence_id', 'correct_label', 'units_extracted'])
        writer.writerows(annotations)

    return jsonify({'message': 'Annotations saved successfully!', 'next_index': int(entry_index) + 1})


@app.route('/navigate', methods=['POST'])
def navigate():
    action = request.form['action']
    entry_index = int(request.form['entry_index'])
    if action == 'forward':
        entry_index += 1
    elif action == 'backward':
        entry_index -= 1
    elif action == 'go':
        entry_index_input = request.form['entry_index_input']
        entry_index = int(
            entry_index_input) if entry_index_input.isdigit() else entry_index
    return redirect(f'/{entry_index}')


if __name__ == '__main__':
    app.run(debug=True)
