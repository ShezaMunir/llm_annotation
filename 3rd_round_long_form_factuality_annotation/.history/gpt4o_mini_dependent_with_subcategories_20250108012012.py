import os
import json
import glob
import openai

###############################################################################
# 1. Configuration for the Azure OpenAI Service
###############################################################################
# Replace these placeholders with your actual Azure OpenAI settings.
openai.api_type = "azure"
openai.api_base = "https://xin-openai-service-us2.openai.azure.com/"
openai.api_version = "2024-02-01"  # adjust to the version your resource supports
openai.api_key = "8W8gxX6zC8T0Y6hNBFUmpxRPHIS7VtOyrv4x2YrmHTwg8a3l5oNYJQQJ99AJACHYHv6XJ3w3AAABACOG2GnX"

# This is the name (or deployment ID) of the ChatGPT model you deployed on Azure.
# Example: "gpt4o-mini" or "gpt-35-turbo" deployment name
DEPLOYMENT_NAME = "gpt-4o-mini"
ROOT_DIR = "./analysis_data_for_annotation"

###############################################################################
# 2. The labeling guidelines prompt
###############################################################################
# This is the prompt you provided. You can store it as a multi-line string.
GUIDELINES_PROMPT = """System/Instruction Message:
You are given:
	1.	A context (a passage or statement).
	2.	A claim extracted from that context.

Your task:
	1.	Determine whether the claim is Dependent or Independent based on the definitions below.
	2.	If the claim is Dependent, identify which type of dependency applies:
	•	Ambiguous Concepts/Pronouns: The claim contains ambiguous references or pronouns that require additional context for clarity.
	•	Missing Comparison: The claim implies or states a comparison (e.g., “more,” “harder,” etc.) but does not include the object or basis of that comparison.
	•	Lack of Condition/Sources: The claim lacks necessary conditions or references (e.g., hypothetical scenarios, quoted sources, or attributions) that are essential for clarity.

Definitions:
	•	Dependent: The claim relies on additional context or conditions to be understood or to make sense. It either has ambiguous references, lacks a necessary comparison, or lacks a condition/source to be clear.
	•	Independent: The claim is self-contained and can be understood without needing extra clarifications, conditions, or references from the context.

Step-by-step Instructions:
	1.	Read the context to understand any background information.
	2.	Examine the claim and see if it can stand alone or if it is missing critical information from the context.
	3.	If the claim requires the context to clarify ambiguous references, comparisons, or conditions, label it “Dependent.” Then specify which of the three types best describes the missing or ambiguous element.
	4.	If the claim does not require additional context and is clear on its own, label it “Independent.”
	5.	Provide a brief explanation of your reasoning.

Example Input/Output:

Context:
“John said he would drive faster tomorrow, but he didn’t mention how much faster, nor did he clarify under what road conditions he would be driving.”

Claim:
“He will drive faster.”

Output
	•	Classification: Dependent
	•	Dependent Type: Missing Comparison (because “faster” implies a comparison, and the basis for that comparison is not explicitly stated within the claim)
	•	Explanation: “The claim references driving ‘faster,’ but there is no mention of what it is being compared to. Hence, it needs more context about the baseline speed or situation.”

Context:
“Fine-tuning in the context of deep learning refers to the process of taking a pre-trained model—typically one that has been trained on a large dataset—and making small adjustments to its weights and parameters to adapt it for a specific task or dataset. This approach leverages the knowledge the model has already acquired, allowing it to achieve better performance on the new task with less data and training time compared to training a model from scratch. Fine-tuning usually involves freezing some of the earlier layers of the model, which capture general features, while allowing the later layers to be retrained to capture task-specific features. This technique is particularly effective in transfer learning scenarios, where the pre-trained model serves as a strong starting point for various applications, such as image classification, natural language processing, and more.”

Claim:
“Training a model being trained from scratch requires more data.”

Output
	•	Classification: Dependent
	•	Dependent Type: Missing Comparison
	•	Explanation: “The claim states that training a model from scratch requires more data, but it does not specify what it requires more data than. It needs a comparison point to be clear.”

Context:
“Decarbonizing civil flight companies is a pressing concern as the aviation industry accounts for approximately 2.5% of global greenhouse gas emissions (ICAO, 2020). To mitigate this impact, several strategies can be employed. Firstly, the adoption of more fuel-efficient aircraft, such as the Airbus A320neo and Boeing 787 Dreamliner, can significantly reduce fuel consumption and emissions (Schipper et al., 2015). Additionally, the use of sustainable aviation fuels (SAF) can decrease emissions by up to 80% compared to traditional fossil fuels (ICCT, 2020). SAF can be produced from waste biomass, algae, or agricultural waste, providing a carbon-neutral alternative to traditional fuels. Furthermore, optimizing flight routes and altitudes can also reduce fuel consumption and emissions (Lee et al., 2010). For instance, flying at higher altitudes can take advantage of more efficient engine performance and reduce air resistance. Finally, implementing carbon offsetting programs, such as the Carbon Offset and Reduction Scheme for International Aviation (CORSIA), can provide a financial incentive for airlines to reduce their emissions (ICAO, 2020). By implementing these strategies, civil flight companies can significantly reduce their carbon footprint and contribute to a more sustainable aviation industry.\n\nReferences:\nICAO (2020). Carbon Offset and Reduction Scheme for International Aviation (CORSIA). International Civil Aviation Organization.\n\nICCT (2020). Sustainable Aviation Fuels: A Review of the Current State of the Industry. International Council on Clean Transportation.\n\nLee, D. S., et al. (2010). Aviation and the Global Atmosphere. Cambridge University Press.\n\nSchipper, L., et al. (2015). The Future of Aviation: A Review of the Literature. Energy Policy, 87, 1-12.", "response": "Decarbonizing civil flight companies is a pressing concern** as **the aviation industry accounts for approximately 2.5% of global greenhouse gas emissions** (ICAO, 2020)**. **To mitigate **this impact**, **several strategies can be employed. **Firstly, the adoption o**f more fuel-efficient aircraft**, such as the Airbus A320neo and Boeing 787 Dreamliner**, can significantly reduce fuel consumption** and emissions (Schipper et al., 2015)**. **Additionally, **the use of sustainable aviation fuels (SAF) can decrease emissions by up to 80% compared to traditional fossil fuels** (ICCT, 2020)**. SAF can be produced from waste biomass**, algae, or **agricultural waste**, providin**g a carbon-neutral alternative to traditional fuels. **Furthermore, **optimizing flight routes **and altitudes can als**o reduce fuel consumption** and emissions (Lee et al., 2010)**. **For instance, **flying at higher altitudes can take advantage of more efficient engine performance **and reduce air resistance**. **Finally**, implement**ing carbon offsetting programs, such as **the Carbon Offset and Reduction Scheme for International Aviation (CORSIA)**, can provide a financial incentive for airlines to reduce their emissions (ICAO, 2020)**. **By implementing these strategies, civil flight companies can significantl**y reduce their carbon footprint** an**d contribute to a more sustainable aviation industry. **References:\nICAO (2020)**. Carbon Offset and Reduction Scheme for International Aviation **(CORSIA)**. ICCT **(2020)**. **(2010)**. Aviation and the **Global Atmosphere**. **(2015**). Energy Policy**, 87**, 1-12.”

Claim:
“The publication by Schipper et al. (2015) was in the format of 1-12.”

Output:
    •	Classification: Dependent
    •	Dependent Type: Ambiguous Concepts/Pronouns
    •	Explanation: “The claim references a publication by Schipper et al. (2015) in the format of 1-12, but it is unclear what the format refers to. It requires more context or clarification to be understood.”

    
Context:
“Fine-tuning in the context of deep learning refers to the process of taking a pre-trained model—typically one that has been trained on a large dataset—and making small adjustments to its weights and parameters to adapt it for a specific task or dataset. This approach leverages the knowledge the model has already acquired, allowing it to achieve better performance on the new task with less data and training time compared to training a model from scratch. Fine-tuning usually involves freezing some of the earlier layers of the model, which capture general features, while allowing the later layers to be retrained to capture task-specific features. This technique is particularly effective in transfer learning scenarios, where the pre-trained model serves as a strong starting point for various applications, such as image classification, natural language processing, and more.”

Your Turn

Please classify the claim according to the definitions above.
	•	Context: [Insert the relevant context here]
	•	Claim: [Insert the extracted claim here]

Output:
    •	Classification: """

###############################################################################
# 3. Main script logic
###############################################################################

def label_facts_in_file(result_filepath):
    """
    Reads a single result_X.json file, calls the Azure OpenAI chat for each
    'revised_fact_jsonified_all' entry, and saves the output in annotations_X.json
    """
    
    # Load the data from the results file
    with open(result_filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Example: parse out the "response" (the context) and the array of facts
    # Adjust these if your JSON structure is different.
    context_text = data.get("orig_response", "")  # The context for the claim
    revised_facts = data.get("revised_fact_jsonified_all", [])

    # Extract the "X" from "result_X.json" to use as instance_id
    # e.g., if result_filepath is "/path/to/result_58.json", instance_id="58"
    filename = os.path.basename(result_filepath)
    # For example, "result_58.json" -> "58"
    instance_id = filename.replace("result_", "").replace(".json", "")

    # We can also extract the model name from the directory or any other naming convention
    # For example, if the path is "llama3.1_7b/result_58.json"
    model_name = os.path.basename(os.path.dirname(result_filepath))

    # We'll store the annotation results in a list
    annotations = []

    # For each fact in revised_fact_jsonified_all, we do one chat request
    for fact_idx, fact_data in enumerate(revised_facts):
        
        # The claim we want to evaluate
        claim_text = fact_data.get("revised_unit", "").strip()
        if claim_text == "":
            annotations.append({
                "instance_id": instance_id,
                "model_name": model_name,
                "annotator": DEPLOYMENT_NAME,
                "fact_id": fact_idx,
                "is_independent": True,
                "reasoning": "Empty claim"
            })
            continue

        # Build the actual prompt we send to the model:
        #  - Provide the "GUIDELINES_PROMPT"
        #  - Then show the context + claim
        #  - Instruct the model to output reasoning + label in your requested format
        context_text = context_text.replace("**", "")
        user_prompt = GUIDELINES_PROMPT.replace("[Insert the relevant context here]", context_text).replace("[Insert the extracted claim here]", claim_text)
        
        # Call the Azure OpenAI ChatCompletion
        try:
            response = openai.ChatCompletion.create(
                engine=DEPLOYMENT_NAME,  # or deployment_id=...
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                temperature=0.0,  # for more deterministic output
            )
        except Exception as e:
            print(f"Error calling Azure OpenAI API for file {filename}, fact {fact_idx}: {e}")
            continue
        
        # Extract the model's reply
        # The typical structure for ChatCompletion is:
        # response["choices"][0]["message"]["content"]
        model_content = response["choices"][0]["message"]["content"].strip()

        # Now, we expect the content to include something like:
        #    Reasoning: ...
        #    Label: Dependent (or Independent)
        # You need to parse that from the text. If your format is consistent,
        # you can do it via some simple string operations. If the model might vary,
        # you may want to do more robust parsing.

        # For example:
        reasoning_str = ""
        label_str = ""

        # A very simple approach: search line by line
        lines = model_content.splitlines()
        for line in lines:
            line_lower = line.lower().strip()
            if "explanation:" in line_lower:
                # Extract everything after the colon
                reasoning_str = line.partition(":")[2].strip()
            elif "classification:" in line_lower:
                label_str = line.partition(":")[2].strip()
            elif "dependent type:" in line_lower:
                dependent_type_str = line.partition(":")[2].strip()

        # Determine the boolean is_independent from the label
        # If label_str says "Independent", set True; if "Dependent", set False.
        is_independent_val = False
        if "independent" in label_str.lower():
            is_independent_val = True

        # Build the annotation object
        annotation_obj = {
            "instance_id": instance_id,                # e.g. "58"
            "model_name": model_name,                  # e.g. "llama3.1_7b"
            "annotator": DEPLOYMENT_NAME,              # e.g. "gpt4o-mini"
            "fact_id": fact_idx,                       # index in the array
            "error_type": "none" if is_independent_val else "dependent",
            "dependent_type": dependent_type_str,
            "explanation": reasoning_str,              
        }
        
        annotations.append(annotation_obj)

    # Once we've processed all facts, we'll write out annotations_X.json
    # matching the "X" from "result_X.json"
    annotations_filename = f"annotations_{instance_id}.json"
    if not os.path.exists(os.path.join(f"annotations_gpt4omini_{model_name}")):
        os.makedirs(os.path.join(f"annotations_gpt4omini_{model_name}"))
    annotations_path = os.path.join(f"annotations_gpt4omini_{model_name}", annotations_filename)

    with open(annotations_path, 'w', encoding='utf-8') as out_f:
        json.dump(annotations, out_f, indent=4, ensure_ascii=False)
    
    # print(f"Saved annotations to {annotations_path}")
    # exit()

def main():
    # Example: Suppose your directory structure is:
    #   <model>/result_X.json
    #   e.g. "llama3.1_7b/result_58.json"
    # You might want to process all "result_*.json" in all subfolders.

    # Adjust this root directory as needed
    root_dir = ROOT_DIR

    # Recursively find all "result_*.json" files
    all_result_files = glob.glob(os.path.join(root_dir, "**", "result_*.json"), recursive=True)

    for result_file in all_result_files:
        print(f"Processing {result_file} ...")
        label_facts_in_file(result_file)

if __name__ == "__main__":
    main()