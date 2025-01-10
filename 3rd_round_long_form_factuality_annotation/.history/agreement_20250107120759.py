import json
import os

annotation_folders = [
        folder for folder in os.listdir('./')
        if os.path.isdir(os.path.join('./', folder)) and folder.startswith("annotations_")
    ]

models = ['gpt4o_mini', 'llama3.1_7b']
independent_data = {} # [model][instance_id][fact_id][annotator] = value
for model in models:
    independent_data[model] = {}
    for folder in annotation_folders:
        for file in os.listdir(folder):
            instance_id = file
            if instance_id == "annotations_272.json":
                continue
            if instance_id not in independent_data[model]:
                independent_data[model][instance_id] = {}
            with open(os.path.join(folder, file), 'r') as f:
                file_data = json.load(f)
                for instance in file_data:
                    if instance['model_name'] == model:
                        if 'fact_id' not in instance:
                            continue
                        fact_id = instance['fact_id']
                        annotator = instance['annotator'].replace('Yiyang Gu', 'Yiyang')
                        # # or annotator == "Xin" or annotator == "Yiyang" or annotator == "sheza" or annotator == "leczhang"
                        # if annotator == "test" or annotator == "Yiyang" or annotator == "gpt-4o" or annotator == "gpt-4o-mini":
                        #     continue
                        if fact_id not in independent_data[model][instance_id]:
                            independent_data[model][instance_id][fact_id] = {}
                        independent_data[model][instance_id][fact_id][annotator] = instance['error_type']
                        print(model, instance_id, fact_id, annotator, instance['error_type'])

# calculate agreement
agreement = []
for model in models:
    for instance_id in independent_data[model]:
        for fact_id in independent_data[model][instance_id]:
            if len(independent_data[model][instance_id][fact_id]) >= 2:
                # agreement.append(independent_data[model][instance_id][fact_id]['Xin'] == independent_data[model][instance_id][fact_id]['sheza'])
                # if independent_data[model][instance_id][fact_id]['Xin'] != independent_data[model][instance_id][fact_id]['sheza']:
                #     print(model, instance_id, fact_id, independent_data[model][instance_id][fact_id])
                
                # if all annotators agree
                if all([independent_data[model][instance_id][fact_id][annotator] == independent_data[model][instance_id][fact_id]['sheza_2'] for annotator in independent_data[model][instance_id][fact_id]]):
                    agreement.append(1)
                else:
                    agreement.append(0)

print(len(agreement))
print(sum(agreement))
print(sum(agreement) / len(agreement))


# missing_relationship_data = {}
# for model in models:
#     missing_relationship_data[model] = {}
#     for folder in annotation_folders:
#         for file in os.listdir(folder):
#             instance_id = file
#             if instance_id not in missing_relationship_data[model]:
#                 missing_relationship_data[model][instance_id] = {}
#             with open(os.path.join(folder, file), 'r') as f:
#                 file_data = json.load(f)
#                 missing_relationship_instance = file_data[-1]
#                 annotator = missing_relationship_instance['annotator'].replace('Yiyang Gu', 'Yiyang')
#                 missing_relationship_data[model][instance_id][annotator] = missing_relationship_instance['global_comments']

# # print(missing_relationship_data)
# relation2importance = {}
# for model in models:
#     for instance_id in missing_relationship_data[model]:
#         for annotator in missing_relationship_data[model][instance_id]:
#             if annotator == "Xin":
#                 continue
#             if missing_relationship_data[model][instance_id][annotator] == "":
#                 continue
#             # print(missing_relationship_data[model][instance_id][annotator])
#             missing_relationships = missing_relationship_data[model][instance_id][annotator].split('\r\n')
#             for missing_relationship in missing_relationships:
#                 if missing_relationship == "":
#                     continue
#                 relation_l1 = missing_relationship.split('|')[0].split('.')[0].strip()
#                 importance = missing_relationship.split('|')[2].strip()
#                 if relation_l1 not in relation2importance:
#                     relation2importance[relation_l1] = []
#                 relation2importance[relation_l1].append(importance)
#                 if importance == "important" and relation_l1 == "Comparison":
#                     print(model, instance_id, annotator, missing_relationship)

# for relation in relation2importance:
#     print(relation)
#     print(sum([importance == "important" for importance in relation2importance[relation]]) / len(relation2importance[relation]))
#     # print(sum([int(importance) for importance in relation2importance[relation]]) / len(relation2importance[relation]))