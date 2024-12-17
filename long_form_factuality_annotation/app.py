from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import os
import json
import markdown

app = Flask(__name__)
app.secret_key = 'xxx'

DATA_DIR = 'analysis_data_for_annotation'
MODELS = [d for d in os.listdir(
    DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]


def get_data(model_name, instance_id):
    file_path = os.path.join(DATA_DIR, model_name,
                             f'result_{instance_id}.json')
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            data["response"] = markdown.markdown(data["response"], extensions=[
                                                 'extra', 'fenced_code', 'nl2br'])
            return data
    return None


def get_instance_ids(model_name):
    folder_path = os.path.join(DATA_DIR, model_name)
    files = [f for f in os.listdir(folder_path) if f.startswith(
        'result_') and f.endswith('.json')]
    return sorted([int(f.split('_')[1].split('.')[0]) for f in files])

def get_next_instance_id(model_name, curr_id):
    curr_id = int(curr_id)
    instance_ids = get_instance_ids(model_name)
    if curr_id in instance_ids:
        curr_id_index = instance_ids.index(curr_id)
        if curr_id_index + 1 < len(instance_ids):
            return instance_ids[curr_id_index + 1]
    return curr_id


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

            # Collect global "Missing Relationship" and comments
            is_missing_relationship = request.form.get('is_missing_relationship')
            global_comments = request.form.get('global_comments')

            # Collect "Is Independent?" annotations for each revised unit
            for i, unit in enumerate(data.get('revised_fact_jsonified_all', [])):
                is_independent = request.form.get(f'is_independent{i}')
                if is_independent is not None:
                    annotations.append({
                        'instance_id': instance_id,
                        'model_name': model_name,
                        'annotator': annotator_name,
                        'fact_id': i,
                        'is_independent': is_independent == 'true',
                    })

            # Add global Missing Relationship and Comments to annotations
            annotations.append({
                'instance_id': instance_id,
                'model_name': model_name,
                'annotator': annotator_name,
                'is_missing_relationship': is_missing_relationship == 'true',
                'global_comments': global_comments
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
                return redirect(url_for('display', model_name=model_name, instance_id=str(get_next_instance_id(model_name, instance_id))))
            except Exception as e:
                flash(f'Error saving annotations: {e}', 'error')

            return redirect(url_for('display', model_name=model_name, instance_id=instance_id))

        # Include the list of models for dropdown
        return render_template('display.html', data=data, model_name=model_name, instance_id=instance_id, models=MODELS, instance_id_list=list(map(str, get_instance_ids(model_name))))

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=False)
