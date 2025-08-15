
Run local LLM models and build AI agents

This is a seed project based on Ollama to start creating agent for your tasks. It feeds prompt to LLM, decides an action based on available actions, executes the action and feed the result back to LLM before returning an answer to the user.


Some Files:
- Modelfile -> Add Context
- model.py -> Specify the model


### Install

```
pip install -r requirements.txt
```


### Start app

```
source venv/bin/activate
python start.py
```



#### Sample queries

```
Call nabraj.com/test.json and provide me 'message' from the response.
```

```
echo hello
```
