import json
import os
from sklearn.metrics import cohen_kappa_score

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
                        # if annotator == "Xin" or annotator == "sheza_2":
                        #     continue
                        # # or annotator == "Xin" or annotator == "Yiyang" or annotator == "sheza" or annotator == "leczhang"
                        # if annotator == "test" or annotator == "Yiyang" or annotator == "gpt-4o" or annotator == "gpt-4o":
                        #     continue
                        if annotator == "gpt-4o-mini" or annotator == "gpt-4o":
                            continue
                        if fact_id not in independent_data[model][instance_id]:
                            independent_data[model][instance_id][fact_id] = {}
                        # if instance['error_type'] == "self—duplicated" or instance['error_type'] == "hallucinated" or instance['error_type'] == "dependent":
                        if instance['error_type'] == "self—duplicated" or instance['error_type'] == "hallucinated":
                            instance['error_type'] = 'none'
                        independent_data[model][instance_id][fact_id][annotator] = instance['error_type']
                        # print(model, instance_id, fact_id, annotator, instance['error_type'])

# calculate agreement
agreement = []
type2count = {}
for model in models:
    for instance_id in independent_data[model]:
        for fact_id in independent_data[model][instance_id]:
            if len(independent_data[model][instance_id][fact_id]) >= 2:
                # agreement.append(independent_data[model][instance_id][fact_id]['Xin'] == independent_data[model][instance_id][fact_id]['sheza'])
                # if independent_data[model][instance_id][fact_id]['Xin'] != independent_data[model][instance_id][fact_id]['sheza']:
                #     print(model, instance_id, fact_id, independent_data[model][instance_id][fact_id])
                
                # if all annotators agree
                if all([independent_data[model][instance_id][fact_id][annotator] == independent_data[model][instance_id][fact_id]['Yiyang'] for annotator in independent_data[model][instance_id][fact_id]]):
                    agreement.append(1)
                else:
                    agreement.append(0)
                    print(model, instance_id, fact_id, independent_data[model][instance_id][fact_id])
                
                for annotator in independent_data[model][instance_id][fact_id]:
                    if independent_data[model][instance_id][fact_id][annotator] not in type2count:
                        type2count[independent_data[model][instance_id][fact_id][annotator]] = 0
                    type2count[independent_data[model][instance_id][fact_id][annotator]] += 1
                    

print(len(agreement))
print(sum(agreement))
print(sum(agreement) / len(agreement))
print(type2count)

# cohen_kappa_score agreement
annotations_sheza = []
annotations_leczhang = []
annotations_yiyang = []
annotations_gpt4o_mini = []
for model in models:
    for instance_id in independent_data[model]:
        for fact_id in independent_data[model][instance_id]:
            annotations_sheza.append(independent_data[model][instance_id][fact_id]['sheza_2'])
            annotations_leczhang.append(independent_data[model][instance_id][fact_id]['leczhang'])
            annotations_yiyang.append(independent_data[model][instance_id][fact_id]['Yiyang'])
            annotations_gpt4o_mini.append(independent_data[model][instance_id][fact_id]['gpt-4o'])

def raw_agreement(annotation1, annotation2):
    assert len(annotation1) == len(annotation2)
    return sum([annotation1[i] == annotation2[i] for i in range(len(annotation1))]) / len(annotation1)

print(cohen_kappa_score(annotations_sheza, annotations_leczhang))
print(cohen_kappa_score(annotations_sheza, annotations_yiyang))
print(cohen_kappa_score(annotations_leczhang, annotations_yiyang))
print(cohen_kappa_score(annotations_yiyang, annotations_gpt4o_mini))
print(cohen_kappa_score(annotations_sheza, annotations_gpt4o_mini))
print(cohen_kappa_score(annotations_leczhang, annotations_gpt4o_mini))
print('raw agreement')
print(raw_agreement(annotations_sheza, annotations_leczhang))
print(raw_agreement(annotations_sheza, annotations_yiyang))
print(raw_agreement(annotations_leczhang, annotations_yiyang))
print(raw_agreement(annotations_yiyang, annotations_gpt4o_mini))
print(annotations_sheza)
print(annotations_leczhang)
# print(annotations_sheza)
# print(annotations_leczhang)

# print("=====================================")
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
#                 for missing_relationship_instance in file_data:
#                     if 'span' not in missing_relationship_instance:
#                         continue
#                     span = missing_relationship_instance['span']
#                     annotator = missing_relationship_instance['annotator'].replace('Yiyang Gu', 'Yiyang')
#                     # if annotator == "Xin" or annotator == "leczhang":
#                     #     continue
#                     if span not in missing_relationship_data[model][instance_id]:
#                         missing_relationship_data[model][instance_id][span] = {}
#                     if missing_relationship_instance['missing_relationship'] == "not_missing":
#                         missing_relationship_instance['missing_relationship'] = "none"
#                     missing_relationship_data[model][instance_id][span][annotator] = missing_relationship_instance['missing_relationship']

# # print(missing_relationship_data)
# agreement = []
# for model in models:
#     for instance_id in missing_relationship_data[model]:
#         for span in missing_relationship_data[model][instance_id]:
#             # if all annotators agree
#             if all([missing_relationship_data[model][instance_id][span][annotator] == missing_relationship_data[model][instance_id][span]['sheza_2'] for annotator in missing_relationship_data[model][instance_id][span]]):
#                 agreement.append(1)
#                 # print(model, instance_id, span, missing_relationship_data[model][instance_id][span])
#             else:
#                 agreement.append(0)
#                 # print(model, instance_id, span, missing_relationship_data[model][instance_id][span])

# # print(len(agreement))
# # print(sum(agreement))
# # print(sum(agreement) / len(agreement))

# # cohen_kappa_score agreement

# annotations_sheza = []
# annotations_leczhang = []
# annotations_yiyang = []
# for model in models:
#     for instance_id in missing_relationship_data[model]:
#         for span in missing_relationship_data[model][instance_id]:
#             annotations_sheza.append(missing_relationship_data[model][instance_id][span]['sheza_2'])
#             annotations_leczhang.append(missing_relationship_data[model][instance_id][span]['leczhang'])
#             annotations_yiyang.append(missing_relationship_data[model][instance_id][span]['Yiyang'])

# print(cohen_kappa_score(annotations_sheza, annotations_leczhang))
# print(cohen_kappa_score(annotations_sheza, annotations_yiyang))
# print(cohen_kappa_score(annotations_leczhang, annotations_yiyang))
# print('raw agreement')
# print(raw_agreement(annotations_sheza, annotations_leczhang))
# print(raw_agreement(annotations_sheza, annotations_yiyang))
# print(raw_agreement(annotations_leczhang, annotations_yiyang))



# dependent_type_data = {} # [model][instance_id][fact_id][annotator] = value
# for model in models:
#     dependent_type_data[model] = {}
#     for folder in annotation_folders:
#         for file in os.listdir(folder):
#             instance_id = file
#             if instance_id not in dependent_type_data[model]:
#                 dependent_type_data[model][instance_id] = {}
#             with open(os.path.join(folder, file), 'r') as f:
#                 file_data = json.load(f)
#                 for instance in file_data:
#                     if instance['model_name'] == model:
#                         if 'fact_id' not in instance:
#                             continue
#                         fact_id = instance['fact_id']
#                         annotator = instance['annotator'].replace('Yiyang Gu', 'Yiyang')
#                         # if annotator == "Xin" or annotator == "sheza_2":
#                         #     continue
#                         # # or annotator == "Xin" or annotator == "Yiyang" or annotator == "sheza" or annotator == "leczhang"
#                         # if annotator == "test" or annotator == "Yiyang" or annotator == "gpt-4o" or annotator == "gpt-4o":
#                         #     continue
#                         if fact_id not in dependent_type_data[model][instance_id]:
#                             dependent_type_data[model][instance_id][fact_id] = {}
#                         # if instance['error_type'] == "self—duplicated" or instance['error_type'] == "hallucinated" or instance['error_type'] == "dependent":
#                         # if annotator == "gpt-4o" or annotator == "gpt-4o":
#                         #     continue
#                         if instance['dependent_type'] is None:
#                             instance['dependent_type'] = 'none'
#                         # if instance['dependent_type'] == "lack_condition" or instance['dependent_type'] == "missing_comparison":
#                         #     instance['dependent_type'] = 'Non-sense'
#                         dependent_type_data[model][instance_id][fact_id][annotator] = instance['dependent_type']
#                         # print(model, instance_id, fact_id, annotator, instance['error_type'])

# # cohen_kappa_score agreement
# annotations_sheza = []
# annotations_leczhang = []
# annotations_yiyang = []
# instance_info_list = []
# for model in models:
#     for instance_id in dependent_type_data[model]:
#         for fact_id in dependent_type_data[model][instance_id]:
#             annotations_sheza.append(dependent_type_data[model][instance_id][fact_id]['sheza_2'])
#             annotations_leczhang.append(dependent_type_data[model][instance_id][fact_id]['leczhang'])
#             annotations_yiyang.append(dependent_type_data[model][instance_id][fact_id]['Yiyang'])
#             instance_info_list.append(" ".join([model, instance_id, str(fact_id)]))

# print("-----------------------------")
# temp_annotations_sheza = []
# temp_annotations_leczhang = []
# temp_instances_info = []
# for i in range(len(annotations_sheza)):
#     if annotations_sheza[i] != 'none' and annotations_leczhang[i] != 'none':
#         temp_annotations_sheza.append(annotations_sheza[i])
#         temp_annotations_leczhang.append(annotations_leczhang[i])
#         temp_instances_info.append(instance_info_list[i])
# print(cohen_kappa_score(temp_annotations_sheza, temp_annotations_leczhang))
# print(len(temp_annotations_sheza))
# print(temp_annotations_sheza)
# print(temp_annotations_leczhang)
# print(temp_instances_info)

# temp_annotations_sheza = []
# temp_annotations_yiyang = []
# temp_instances_info = []
# for i in range(len(annotations_sheza)):
#     if annotations_sheza[i] != 'none' and annotations_yiyang[i] != 'none':
#         temp_annotations_sheza.append(annotations_sheza[i])
#         temp_annotations_yiyang.append(annotations_yiyang[i])
#         temp_instances_info.append(instance_info_list[i])
# print(cohen_kappa_score(temp_annotations_sheza, temp_annotations_yiyang))
# print(len(temp_annotations_sheza))
# print(temp_annotations_sheza)
# print(temp_annotations_yiyang)
# print(temp_instances_info)

# temp_annotations_leczhang = []
# temp_annotations_yiyang = []
# temp_instances_info = []
# for i in range(len(annotations_leczhang)):
#     if annotations_leczhang[i] != 'none' and annotations_yiyang[i] != 'none':
#         temp_annotations_leczhang.append(annotations_leczhang[i])
#         temp_annotations_yiyang.append(annotations_yiyang[i])
#         temp_instances_info.append(instance_info_list[i])
# print(cohen_kappa_score(temp_annotations_leczhang, temp_annotations_yiyang))
# print(len(temp_annotations_leczhang))
# print(temp_annotations_leczhang)
# print(temp_annotations_yiyang)
# print(temp_instances_info)