# Dungeons &amp; Large Language Models

A text-based adventure game powered by OpenAI's GPT-4 and Flask, combining the worlds of Dungeons &amp; Dragons and artificial intelligence.
It's an interactive fiction game with multimedia elements and user customization. Users can select a theme, create a character or choose a random one, and load a saved game state. The game presents a story with text, images, and audio, and allows users to interact by selecting from predefined options or entering custom ones.  
There is a blend of LLM and programatical parsing of action Options into buttons, dice rolls using random.randint, and more.

Multiple AI modules are combined to generate a world, plot, character, with unique prompting. There is also a save feature

### Note: Runs VERY SLOWLY due to the speed of api calls, is also quite expensive to run on your API key, use at the risk of your own wallet. Expect 10-60 second delays, and ~10 cents per action.

Inspired by sentdex.

## Setup
1. ```$ pip install -r requirements.txt```

2. Create a `key.txt` file in the root directory of the project and paste your OpenAI API key into it.

3. Create a `flask_key.txt` file in the root directory of the project and paste a Flask secret key (a secure, random string) into it.

## Running the Application
Run the main module with python3.
```
python main.py
```

3. Open a web browser and navigate to `http://127.0.0.1:5001/` to start your text-based AI-powered adventure!
