# llm_annotation
Human annotation for unit extraction quality (completeness) and correctness (right label).  

## Annotation process:

### for tier 1 annotations:
1. install flask ```pip install flask```
2. run ```python app.py``` to start the server
3. go to the localhost URL (most likely: http://127.0.0.1:5000)
4. enter your name in the sign up page 
5. it will show the first default page (most likely instance_id=4 for gemini)
6. change instance id from the URL, and the model name from the drop down available at the top of the page
7. remember the name you sign up with. it will save your annotations under that directory name. annotations for the same instance_id, for different models, will be stored in the same json file. 


### for safe annotations:
1. install flask ```pip install flask```
2. run ```python app.py``` to start the server
3. go to the localhost URL (most likely: http://127.0.0.1:5000)
4. enter your name in the sign up page 
5. click radio buttons for annotations
6. use the 'go to entry' box at the bottom to jump to particular entry
7. remember your username, the csv file will be stored under a folder of that name in your local pc. 
8. you can track entries in the csv file to take a pause and come back to annotating later. 
