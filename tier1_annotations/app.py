from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import os
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

DATA_DIR = 'analysis_data_units'
MODELS = [d for d in os.listdir(
    DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]


def get_data(model_name, instance_id):
    file_path = os.path.join(DATA_DIR, model_name,
                             f'result_{instance_id}.json')
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return None


def get_instance_ids(model_name):
    folder_path = os.path.join(DATA_DIR, model_name)
    files = [f for f in os.listdir(folder_path) if f.startswith(
        'result_') and f.endswith('.json')]
    return sorted([int(f.split('_')[1].split('.')[0]) for f in files])


def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        annotator_name = request.form['annotator_name']
        session['annotator'] = annotator_name
        return redirect(url_for('first_instance'))
    return render_template('start.html')


@app.route('/first_instance')
def first_instance():
    model_name = MODELS[0] if MODELS else None
    if model_name:
        instance_ids = get_instance_ids(model_name)
        instance_id = instance_ids[0] if instance_ids else None
        if instance_id:
            return redirect(url_for('display', model_name=model_name, instance_id=instance_id))
    return 'No data available', 404


@app.route('/data/<model_name>/')
def data(model_name):
    instance_ids = get_instance_ids(model_name)
    data = [{'instance_id': id} for id in instance_ids]
    return jsonify(data)


@app.route('/display/<model_name>/<instance_id>', methods=['GET', 'POST'])
def display(model_name, instance_id):
    data = get_data(model_name, instance_id)
    if data:
        if request.method == 'POST':
            annotations = []
            annotator_name = session.get('annotator', 'unknown')

            for i, unit in enumerate(data.get('revised_fact_jsonified_all', [])):
                is_correct = request.form.get(f'is_correct_{i}')
                is_fact = request.form.get(f'is_fact_{i}')

                if is_correct is not None and is_fact is not None:
                    annotations.append({
                        'instance_id': instance_id,
                        'model_name': model_name,
                        'annotator': annotator_name,
                        'fact_id': i,
                        'extracted_correctly': is_correct == 'true',
                        'factually': is_fact == 'true'
                    })

            # Save annotations in the root directory
            annotator_name = session.get('annotator', 'unknown')
            annotations_dir = f'annotations_{annotator_name}'
            ensure_directory_exists(annotations_dir)

            # Append annotations to the existing file or create a new file
            json_file = os.path.join(
                annotations_dir, f'annotations_{instance_id}.json')
            existing_annotations = []
            if os.path.exists(json_file):
                try:
                    with open(json_file, 'r') as f:
                        existing_annotations = json.load(f)
                except Exception as e:
                    flash(f'Error reading existing annotations: {e}', 'error')

            existing_annotations.extend(annotations)

            try:
                with open(json_file, 'w') as f:
                    json.dump(existing_annotations, f, indent=4)
                flash('Annotations saved successfully!', 'success')
            except Exception as e:
                flash(f'Error saving annotations: {e}', 'error')

            return redirect(url_for('display', model_name=model_name, instance_id=instance_id))

        # Check if there are revised facts to annotate
        revised_facts = data.get('revised_fact_jsonified_all', [])
        # if not revised_facts:
        #     return render_template('display.html', data=data, model_name=model_name, instance_id=instance_id, models=MODELS, no_facts=True)

        # Include the list of models for dropdown
        return render_template('display.html', data=data, model_name=model_name, instance_id=instance_id, models=MODELS)

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
