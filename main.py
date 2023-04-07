# For the UI
from flask import Flask, render_template, request, session, send_file, redirect, url_for, jsonify
from flask_session import Session
from flask_wtf import CSRFProtect
import time

from audio_utils import generate_audio, get_audio
from img_utils import get_img
from text_utils import *
from dice_utils import get_dice_result

# Create a new Flask app and set the secret key
app = Flask(__name__)
# read the secret key from a file
app.secret_key = open('flask_key.txt', 'r').read()
app.config['SESSION_TYPE'] = 'filesystem'
csrf = CSRFProtect(app)
Session(app)
TITLE = "Dungeons & Large Language Models"

# Define the homepage route for the Flask app
@app.route('/play', methods=['GET', 'POST'])
def play():
    if request.method == 'GET':
        text, button_messages, button_states, message, result_message = handle_get_request()
    else:
        text, button_messages, button_states, message, result_message = handle_post_request()

    print("Generating prompt...")
    img_prompt = img_prompt_from(extract_character_sheet(session['message_history']), text)
    print(f"Generating image from prompt: {img_prompt}...")
    image_url = get_img(img_prompt)
    print("Generating audio...")
    audio_bytes = generate_audio(text)
    session['audio_bytes'] = audio_bytes
    audio_url = f'/audio?{time.time()}'

    return render_template('home.html', title=TITLE, text=text, image_url=image_url, button_messages=button_messages, button_states=button_states, message=message, result_message=result_message, audio_url=audio_url)

def handle_get_request():
    button_messages = {}
    button_states = {}

    if session.get('save_file', None):
        print("Loading from file...")
        sys_prompt = session['save_file']
    else:
        theme = session['theme']
        character_details = session['character_details']
        print(f"Generating new campaign from theme: {theme}...")
        sys_prompt = generate_campaign(theme, character_details)
    
    print("Campaign generated. Here is the system prompt:")
    print(sys_prompt)
    assistant_prompt = """You are an AI-driven interactive fantasy game master, crafting engaging and immersive story experiences for a single player. Present narrative scenarios within a fantastical world and provide 3-5 decision points as potential attempts, formatted for easy parsing and conversion into interactive buttons. For options involving ability checks, attacks, or chance, include the required die roll, relevant ability/skill in angle brackets, and character-specific modifier (e.g., 'Option 1: Attempt to pick the lock <dexterity> (1d20+2)'). In special circumstances when deserved, include advantage or disadvantage using "kh/lh" notation, such as 'Option 1: Sneak past the guard <stealth> (2d20kh1+3)'. The die roll and advantage/disadvantage will be handled programmatically. Maintain your role as a game master and avoid assistant-like behavior. When receiving custom responses (e.g., 'Custom: I cut off the vampire's head'), treat them as user attempts and continue the story with an outcome you predict with likelihood given the context. Upon understanding, reply with 'OK' and initiate the game when prompted by the user's 'begin'. During the game, focus on the story and present choices using the structure: 'Option 1:', 'Option 2:', etc. Balance creativity and conciseness while offering compelling options, and consider chance in determining the outcome of attempts when appropriate."""
    # Initialize the message history
    session['message_history'] = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": assistant_prompt},
        {"role": "assistant", "content": f"""OK"""}]
    
    # Retrieve the message history from the session
    message_history = session['message_history']

    print("Generating chat response...")
    # Generate a chat response with an initial message ("Begin")
    reply_content, message_history = chat("begin", message_history)
    text, button_messages, button_states = parse_reply_content(reply_content)

    update_session_variables(message_history, button_messages)
    
    message = ""
    result_message = ""
    return text, button_messages, button_states, message, result_message

def handle_post_request():
    button_messages = {}
    button_states = {}

    # Retrieve the message history and button messages from the session
    message_history = session['message_history']
    button_messages = session['button_messages']
    
    # Get the custom option from the form
    custom_option = request.form.get('custom_option')
    # Get the name of the button that was clicked
    if custom_option:
        message = f"Custom: {custom_option}"
    else:
        # Get the name of the button that was clicked
        button_name = request.form.get('button_name')

        # Set the state of the button to "True"
        button_states[button_name] = True

        # Get the message associated with the clicked button
        message = button_messages.get(button_name)

    print(f"Recieved user message: {message}")

    result_message = get_dice_result(message)

    print(f"Generating chat response...")
    reply_content, message_history = chat(f"{message} {result_message}", message_history)
    text, button_messages, button_states = parse_reply_content(reply_content)

    update_session_variables(message_history, button_messages)

    return text, button_messages, button_states, message, result_message

def update_session_variables(message_history, button_messages):
    # Store the updated message history and button messages in the session
    session['message_history'] = message_history
    session['button_messages'] = button_messages

@app.route('/save_campaign', methods=['POST'])
def save_campaign():
    print("Saving...")
    message_history = session['message_history']
    theme = session['theme']
    world_title = sentence_to_word(theme)

    # Set a file name for the saved chat history
    file_name = f"saves/{world_title}_{time.strftime('%Y%m%d-%H%M%S')}.txt"

    # Save the chat history to a file
    save_history(message_history, file_name)

    return jsonify({'status': 'success'})

@app.route('/audio')
def audio():
    return send_file(*get_audio(session.get('audio_bytes')))

@app.route('/character_creation', methods=['GET', 'POST'])
def character_creation():
    if request.method == 'POST':
        name = request.form['name']
        race = request.form['race']
        character_class = request.form['character_class']
        level = request.form['level']
        physical_description = request.form['physical_description']
        personality_description = request.form['personality_description']

        session['character_details'] = (name, race, character_class, level, physical_description, personality_description)

        return redirect(url_for('play'))  # Redirect to a success page or another route as needed
    else:
        return render_template('character_creation.html')
    
    
@app.route('/', methods=['GET', 'POST'])
def title_screen():
    if request.method == 'POST':
        theme = request.form['theme']
        if not theme.strip():
            theme = generate_random_theme()
        session['theme'] = theme

        if 'load_save' in request.files and request.files['load_save'].filename:
            save_file = request.files['load_save']
            save_contents = save_file.read().decode('utf-8')
            session['save_file'] = save_contents
            session['character_details'] = None
            session['theme'] = save_contents[0:20]
            return redirect(url_for('play'))
        else:
            session['save_file'] = None

        character_option = request.form['character_option']
        if character_option == 'random_character':
            session['character_details'] = generate_random_character_details()
            return redirect(url_for('play'))
        elif character_option == 'create_character':
            return redirect(url_for('character_creation'))
        
        
    else:
        return render_template('title_screen.html', title=TITLE)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=5001)
