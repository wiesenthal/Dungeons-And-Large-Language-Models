# For the UI
from flask import Flask, render_template, request, session, send_file, redirect, url_for, jsonify, flash
from flask_session import Session
from flask_wtf import CSRFProtect
import time

from audio_utils import generate_audio, get_audio
from img_utils import get_img
from text_utils import *
from dice_utils import get_dice_result
from audit import time_audit, get_audit

# Create a new Flask app and set the secret key
app = Flask(__name__)
# read the secret key from a file
app.secret_key = open('flask_key.txt', 'r').read()
app.config['SESSION_TYPE'] = 'filesystem'
csrf = CSRFProtect(app)
Session(app)
TITLE = "Dungeons & Large Language Models"
WORD_THRESHOLD = 2400

# Define the homepage route for the Flask app
@app.route('/play', methods=['GET', 'POST'])
def play():
    if count_total_words(session['message_history']) > WORD_THRESHOLD:
            # Trigger the auto save using JavaScript
            return render_template('auto_save.html')
    time_audit()
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
    print(f"Chat response generation took {time_audit()}s")
    cost_diff, last_time_diff = get_audit()
    session['total_cost'] = session['total_cost'] + cost_diff
    audit_str = f"Last response took: {round(last_time_diff, 2)}s | Total Cost: ${round(session['total_cost'], 2)} "

    return render_template('home.html', title=TITLE, text=text, image_url=image_url, button_messages=button_messages, button_states=button_states, message=message, result_message=result_message, audio_url=audio_url, audit_str=audit_str)

def handle_get_request():
    button_messages = {}
    button_states = {}
    loaded_game = False
    if session.get('save_file', None):
        print("Loading from file...")
        sys_prompt = session['save_file']
        if LAST_MESSAGE_SPLIT_STRING in sys_prompt:
            loaded_game = True
    else:
        theme = session['theme']
        character_details = session['character_details']
        print(f"Generating new campaign from theme: {theme}...")
        time_audit()
        sys_prompt = generate_campaign(theme, character_details)
        print(f"Campaign generation took {time_audit()}s")
        save_sys_prompt(sys_prompt, f"saves/init_{time.strftime('%Y%m%d-%H%M%S')}.txt")
    
    print("Campaign generated.")

    if not loaded_game:
        print("Generating chat response...")
        reply_content, message_history = chat_begin(sys_prompt)
    else:
        print("Loading chat from save.")
        sys_prompt, reply_content = sys_prompt.split(LAST_MESSAGE_SPLIT_STRING)
        message_history = [
            {"role": "system", "content": sys_prompt},
            {"role": "assistant", "content": reply_content}]

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
    time_audit()
    message_history = session['message_history']
    theme = session['theme']
    world_title = sentence_to_word(theme)

    # Set a file name for the saved chat history
    file_name = f"saves/{world_title}_{time.strftime('%Y%m%d-%H%M%S')}.txt"

    # Save the chat history to a file
    save_history(message_history, file_name)
    print(f"Saving took {time_audit()}s")

    return jsonify({'status': 'success', 'filename': file_name})

@app.route('/auto_save_campaign', methods=['POST'])
def auto_save_campaign():
    print("Auto-saving...")
    filename = save_campaign().json['filename']
    # open the file and read the contents
    with open(filename, 'r') as file:
        data = file.read()
    session['save_file'] = data
    session['message_history'] = []
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
        
        session['total_cost'] = 0

        if 'load_save' in request.files and request.files['load_save'].filename:
            save_file = request.files['load_save']
            save_contents = save_file.read().decode('utf-8')
            session['save_file'] = save_contents
            session['character_details'] = None
            session['theme'] = save_contents[0:20]
            session['message_history'] = []
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
