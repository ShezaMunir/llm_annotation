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
GUIDELINES_PROMPT = """Below is an example prompt you can adapt. It provides instructions and definitions so that the LLM understands how to classify a claim as dependent or independent. You can include additional details, examples, or formatting as needed.

Prompt Template

System/Instruction Message:
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

Example Input

Context:
“John said he would drive faster tomorrow, but he didn’t mention how much faster, nor did he clarify under what road conditions he would be driving.”

Claim:
“He will drive faster.”

Example Output
	•	Classification: Dependent
	•	Dependent Type: Missing Comparison (because “faster” implies a comparison, and the basis for that comparison is not explicitly stated within the claim)
	•	Explanation: “The claim references driving ‘faster,’ but there is no mention of what it is being compared to. Hence, it needs more context about the baseline speed or situation.”

Context:
“In "Disco Elysium," one of the most interesting and satisfying skills is "Empathy," as it allows players to deeply understand and connect with the emotions of other characters, enhancing the narrative experience and enabling more nuanced interactions. This skill not only enriches the storytelling but also provides players with unique insights into the motivations and backgrounds of the game's diverse cast, making it a powerful tool for character development and emotional engagement. Conversely, "Physical Instrument" can often feel less useful in the context of the game's dialogue-heavy and cerebral gameplay, as it primarily focuses on brute strength and physicality, which may not align with the more cerebral and introspective nature of the game's core mechanics and themes.”

Claim:
“"Empathy" is a skill in "Disco Elysium".”

Example Output



Your Turn

Please classify the claim according to the definitions above.
	•	Context: [Insert the relevant context here]
	•	Claim: [Insert the extracted claim here]

Context:
Backpropagation is a supervised learning algorithm used for training artificial neural networks, enabling them to minimize the error in their predictions. It operates in two main phases: the forward pass and the backward pass. During the forward pass, input data is fed through the network layer by layer, where each neuron applies a weighted sum of its inputs followed by a non-linear activation function, ultimately producing an output. The error is then calculated by comparing the network’s output to the actual target values using a loss function. In the backward pass, backpropagation computes the gradient of the loss function with respect to each weight by applying the chain rule of calculus, propagating the error backward through the network. This involves calculating the partial derivatives of the loss with respect to the weights and biases, allowing the algorithm to determine how much each weight contributed to the error. The weights are then updated using an optimization algorithm, such as stochastic gradient descent, by subtracting a fraction of the gradient (scaled by a learning rate) to minimize the loss. This iterative process continues over multiple epochs, gradually improving the model’s accuracy by fine-tuning the weights based on the feedback received from the loss function.

Claim:
“The artificial neural network’s output is compared to the actual target values.”

Output:
	•	Reasoning: This statement could refer to multiple processes (final output vs. training loss). Without additional context, its meaning is ambiguous, so it depends on clarifying information.
	•	Label: Dependent

    


Context:
In "Disco Elysium," one of the most interesting and satisfying skills is "Empathy," as it allows players to deeply understand and connect with the emotions of other characters, enhancing the narrative experience and enabling more nuanced interactions. This skill not only enriches the storytelling but also provides players with unique insights into the motivations and backgrounds of the game's diverse cast, making it a powerful tool for character development and emotional engagement. Conversely, "Physical Instrument" can often feel less useful in the context of the game's dialogue-heavy and cerebral gameplay, as it primarily focuses on brute strength and physicality, which may not align with the more cerebral and introspective nature of the game's core mechanics and themes.

Claim:
""Empathy" is a skill in "Disco Elysium"."

Output:
	•	Reasoning: This claim mentions two specific elements ("Empathy" and "Disco Elysium"). But they are not ambiguous or specialized terms, and the claim is self-contained, requiring no further context to understand.
	•	Label: Independent

Context:
According to Section 105, a company may, by its articles, empower its board of directors to regulate the procedure for the appointment of proxies. Section 106 states that a member entitled to attend and vote at a meeting may appoint a proxy to attend and vote on his behalf. The proxy must be a member of the company or a person who is entitled to attend and vote at the meeting. Section 107 provides that a proxy must be appointed in writing and must be deposited with the company at least 48 hours before the meeting. Section 108 states that a proxy may be appointed by a member in writing, either generally or for a particular meeting, and the proxy must be authorized to vote on the member's behalf. Section 109 provides that a proxy may be revoked by the member who appointed him, either by a notice in writing to the company or by attending the meeting in person.

Claim:
"A company may, by its articles, empower its board of directors to regulate the procedure for the appointment of proxies."

Output:
	•	Reasoning: This claim refers to specific legal sections, i.e., Section 105. The interpretation of this claim depends on the legal context provided in the preceding text. It requires additional information to understand the significance of the statement.
	•	Label: Dependent

Context:
The Indian Premier League (IPL) incorporates strategic timeouts to enhance the game's dynamics and provide teams with opportunities to reassess their strategies during crucial moments. These timeouts, which occur at predetermined intervals, allow coaches and players to discuss tactics, make necessary adjustments, and regroup, thereby adding a layer of strategic depth to the match. Additionally, they serve to create a more engaging viewing experience for fans by providing breaks that can be filled with entertainment and advertisements, ultimately contributing to the commercial success of the league. By allowing teams to pause and recalibrate, strategic timeouts help maintain the competitive balance and excitement that characterize the IPL.

Claim:
"The strategic timeouts incorporated by the Indian Premier League (IPL) serve to create a more engaging viewing experience for fans."

Output:
    •	Reasoning: Though the claim stated a comparison and the comparison is missing in the claim, i.e. "more engaging viewing experience," does not mention what the comparison. But we can know that the comparison is itself, so the claim is self-contained and independent. If the implicit comparison was something mentioned in the context, it would be dependent.
    •	Label: Independent
"""

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
    context_text = data.get("response", "")  # The context for the claim
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
        user_prompt = (
            f"{GUIDELINES_PROMPT}\n\n"
            f"Context:\n{context_text}\n\n"
            f"Claim:\n\"{claim_text}\"\n\n"
        )
        
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
            if "reasoning:" in line_lower:
                # Extract everything after the colon
                reasoning_str = line.partition(":")[2].strip()
            elif "label:" in line_lower:
                label_str = line.partition(":")[2].strip()

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
            "is_independent": is_independent_val,      # True or False
            "reasoning": reasoning_str
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