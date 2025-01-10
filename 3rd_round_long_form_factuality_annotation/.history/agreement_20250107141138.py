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
                        if annotator == "Xin" or annotator == "sheza_2":
                            continue
                        # # or annotator == "Xin" or annotator == "Yiyang" or annotator == "sheza" or annotator == "leczhang"
                        # if annotator == "test" or annotator == "Yiyang" or annotator == "gpt-4o" or annotator == "gpt-4o-mini":
                        #     continue
                        if fact_id not in independent_data[model][instance_id]:
                            independent_data[model][instance_id][fact_id] = {}
                        # if instance['error_type'] == "self—duplicated" or instance['error_type'] == "hallucinated" or instance['error_type'] == "dependent":
                        if instance['error_type'] == "hallucinated" or instance['error_type'] == "dependent":
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
                    print(model, instance_id, fact_id, independent_data[model][instance_id][fact_id])
                else:
                    agreement.append(0)
                
                for annotator in independent_data[model][instance_id][fact_id]:
                    if independent_data[model][instance_id][fact_id][annotator] not in type2count:
                        type2count[independent_data[model][instance_id][fact_id][annotator]] = 0
                    type2count[independent_data[model][instance_id][fact_id][annotator]] += 1
                    

print(len(agreement))
print(sum(agreement))
print(sum(agreement) / len(agreement))
print(type2count)


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
#                 print(model, instance_id, span, missing_relationship_data[model][instance_id][span])

# print(len(agreement))
# print(sum(agreement))
# print(sum(agreement) / len(agreement))