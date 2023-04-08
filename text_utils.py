import openai
import re

from audit import audit_tokens

openai.api_key = open("key.txt", "r").read().strip("\n")

DEFAULT_MODEL = "gpt-4"
DEFAULT_MODEL_CHEAP = "gpt-3.5-turbo"
CAMPAIGN_SPLIT_STRING = "~~~The previous are both private notes to you and as the DM you should make sure you keep them secret from the players, and let them discover the world and plot as they play.~~~"
CHARACTER_SHEET_SPLIT_STRING = "Here is the players initial character sheet: "
ACTION_HISTORY_SPLIT_STRING = "Here are your notes on the players actions from the pervious session: "


def generate_campaign(theme, character_details):
    print("Generating world...")
    world = generate_world(theme)
    print("Generating plot...")
    plot = generate_plot(world)
    print("Generating character sheet...")
    character_sheet = generate_character_sheet(*character_details)
    return (f"Here are your notes about the world: {world}\nHere are your notes about the plot: {plot}\n{CAMPAIGN_SPLIT_STRING}\n{CHARACTER_SHEET_SPLIT_STRING}{character_sheet}\n ")

def generate_world(theme):
    prompt = f"""You are a Dungeon Master (DM) who is creating a campaign. Focus on content creation, not on presentation, because these will be your personal notes so you don't have to hide any secrets from yourself. It doesn't have to be pretty, just functional and organized for your reference. 
    You are given a theme, and you must create a campaign world based on that theme. 
    Write notes about the world including factions, influential characters, locations, magic systems, races, creatures, political forces, and more.
    Don't worry about the plot yet, just focus on the world. Use your imagination and creativity to create a world that is interesting and fun to play in, with lots of depth and karmic interactions, and that will be fun to explore.
    Include a brief outline of the history of the world, and a description of the world's geography, climate, and culture.
    The world is brimming with energy and potential for change.
    The theme is: {theme}"""
    completion = openai.ChatCompletion.create(
        model=DEFAULT_MODEL_CHEAP,
        messages=[{"role": "system", "content": prompt}],
    )
    audit_tokens(completion)
    reply_content = completion.choices[0].message.content
    return reply_content

def generate_plot(world):
    prompt = f"""You are a Dungeon Master (DM) who is creating a plot for one player. You have already written notes on the world, and will create a story that takes place in that world.
    Write brief notes/an outline about the plot allowing for lots of player freedom. Be concise and use quick bullet points.
    Use this space to involve secrets and twists, and the player's choices should have a significant impact on the plot, allowing for a wide variety of outcomes, decisions, and consequences.
    The player can pick sides and choose their own paths, and the plot will progress based on their choices.
    Your world notes are following:
    {world}"""
    completion = openai.ChatCompletion.create(
        model=DEFAULT_MODEL_CHEAP,
        messages=[{"role": "system", "content": prompt}],
    )
    audit_tokens(completion)
    reply_content = completion.choices[0].message.content
    return reply_content

def generate_character_sheet(name, race, character_class, level, physical_description, personality_description):
    prompt = f"""Create a very concise and organized character description sheet for a character with the following details:
    Name: {name}
    Race: {race}
    Class: {character_class}
    Level: {level}
    Physical Description: {physical_description}
    Personality Description: {personality_description}

    Please include the following information:
    - Phyiscal and personality notes 
    - Alignment
    - Stats
    - Proficiencies and languages
    - Special abilities, features, and traits
    - Inventory
    - Spellcasting/Magic
    """

    completion = openai.ChatCompletion.create(
        model=DEFAULT_MODEL_CHEAP,
        messages=[{"role": "system", "content": prompt}],
    )
    audit_tokens(completion)
    reply_content = completion.choices[0].message.content
    return reply_content

def generate_random_character_details():
    prompt = """Generate a random character with Name, Race, Class, Level, Physical Description, and Personality Description. Format the output as follows:
        Name: <Name>
        Race: <Race>
        Class: <Class>
        Level: <Level>
        Physical Description: <Physical Description>
        Personality Description: <Personality Description>"""
    completion = openai.ChatCompletion.create(
        model=DEFAULT_MODEL_CHEAP,
        messages=[{"role": "system", "content": prompt}],
    )
    audit_tokens(completion)
    reply_content = completion.choices[0].message.content
    # Extract the character details from the response
    pattern = r"Name: (.*?)\nRace: (.*?)\nClass: (.*?)\nLevel: (\d+)\nPhysical Description: (.*?)\nPersonality Description: (.*?)$"
    match = re.search(pattern, reply_content, re.MULTILINE)

    if match:
        character_data = [
            match.group(1),
            match.group(2),
            match.group(3),
            match.group(4),
            match.group(5),
            match.group(6)
        ]
    else:
        print(f"Character generation failed. input: {reply_content}. Please try again.")
        exit()

    return character_data

def save_character(message_history):
    character_sheet = extract_character_sheet(message_history)
    prompt = f"You are an AI-driven interactive fantasy game master, responsible for maintaining and updating a concise record of the character sheet from ongoing sessions. Please output just the character sheet. Be sure to level up the character if you deem it worthy based on their achievements in the session. Update their inventory with any items obtained. The session has ended, so your goal is to create a clear and organized record that can be easily reviewed and referenced for future sessions, ensuring the continuity and consistency of the game experience. Here is their current character sheet: {character_sheet}"
    completion = openai.ChatCompletion.create(
        model=DEFAULT_MODEL_CHEAP,
        messages= message_history[1:] + [{"role": "system", "content": prompt}]
    )
    audit_tokens(completion)
    reply_content = completion.choices[0].message.content
    return reply_content

def save_actions(message_history):
    prompt = "You are an AI-driven interactive fantasy game master, responsible for maintaining and updating a concise record of the message history from ongoing sessions. The session has ended, so compress the message history while preserving essential information. Use brief notes summarizing the player's actions during the session, their current location and relationships, and any important outcomes or consequences of their decisions. Your goal is to create a clear and organized record that can be easily reviewed and referenced for future sessions, ensuring the continuity and consistency of the game experience."
    completion = openai.ChatCompletion.create(
        model=DEFAULT_MODEL_CHEAP,
        messages= message_history + [{"role": "system", "content": prompt}]
    )
    audit_tokens(completion)
    reply_content = completion.choices[0].message.content
    return reply_content

def extract_campaign(message_history):
    sys_message = message_history[0]["content"]
    return sys_message.split(CAMPAIGN_SPLIT_STRING)[0]

def extract_character_sheet(message_history):
    sys_message = message_history[0]["content"]
    return sys_message.split(CHARACTER_SHEET_SPLIT_STRING)[1]

def save_history(message_history, filename):
    campaign = extract_campaign(message_history)
    print("Saving character...")
    character_sheet = save_character(message_history)
    print("Saving actions...")
    actions = save_actions(message_history)
    save_string = f"{campaign}{CAMPAIGN_SPLIT_STRING}\n{CHARACTER_SHEET_SPLIT_STRING}{character_sheet}{ACTION_HISTORY_SPLIT_STRING}{actions}"
    
    with open(filename, "w") as f:
        f.write(save_string)

def generate_random_theme():
    prompt = """Generate a creative, random theme for a fun world. The theme should be a 1-2 sentences."""
    completion = openai.ChatCompletion.create(
        model=DEFAULT_MODEL_CHEAP,
        messages=[{"role": "system", "content": prompt}],
    )
    audit_tokens(completion)
    reply_content = completion.choices[0].message.content
    return reply_content

def img_prompt_from(character, text):
    prompt = f"Craft a 10-20 word visual description to depict this DnD scene. Because the recipient has no context, include visual descriptions of characters and locations: {text}"
    completion = openai.ChatCompletion.create(
        model=DEFAULT_MODEL_CHEAP,
        messages=[{"role": "system", "content": f"{CHARACTER_SHEET_SPLIT_STRING}{character}"}, {"role": "system", "content": prompt}],
    )
    audit_tokens(completion)
    reply_content = completion.choices[0].message.content
    return reply_content

def sentence_to_word(sentence):
    prompt = f"Distill the following sentence into exactly one word: {sentence}"
    completion = openai.ChatCompletion.create(
        model=DEFAULT_MODEL_CHEAP,
        messages=[{"role": "system", "content": prompt}],
    )
    audit_tokens(completion)
    reply_content = completion.choices[0].message.content
    return reply_content

# Extract the important context from the message history, to be given to the more expensive model
def extract_context(message_history):
    context_prompt = "Given the previous conversation in a DnD game, extract the important context that will be necessary for the next response. Be concise and extract all relevant information (such as player location, status, relationships, and any items they have acquired) into bullet points."
    completion = openai.ChatCompletion.create(
        model=DEFAULT_MODEL_CHEAP,
        messages=message_history + [{"role": "system", "content": context_prompt}],
        max_tokens=150
    )
    audit_tokens(completion)
    # Grab the generated summary from the API response
    context_summary = completion.choices[0].message.content.strip()

    return context_summary

# Define a function to generate a chat response using the OpenAI API
def chat(inp, message_history, role="user"):
    message_history.append({"role": role, "content": f"{inp}"})
    important_details = extract_context(message_history)
    print(f"Extracted context: {important_details}")
    prompt = """You are an AI game master for a single-player fantasy adventure. Present concise but immersive narratives and 3-5 decision points, formatted for easy parsing and button conversion (e.g. 'Option 1: Travel to the tavern for information'). For those options with checks, attacks, or chance, include relevant ability/skill, die roll, and modifier (e.g., 'Option 2: Pick the lock <dexterity> (1d20+2)'). In special cases, add advantage/disadvantage using "kh/lh" notation (e.g., 'Option 3: Sneak past guard <stealth> (2d20kh1+3)'). Die rolls and advantage/disadvantage are handled programmatically. Maintain your game master role, avoiding assistant-like behavior. Treat custom responses (e.g., 'Custom: I cut off the vampire's head') as user attempts and predict outcomes based on context. Present choices as 'Option 1:', 'Option 2:', etc., balancing creativity and conciseness. Consider chance in determining outcomes.

You're in an ongoing game without full message history. After this instruction is the player's character sheet, followed by world and session context notes. The user has just taken action."""
    charcater_sheet = extract_character_sheet(message_history)
    compressed_message_history = [{"role": "system", "content": prompt}, {"role": "system", "content": f"{CHARACTER_SHEET_SPLIT_STRING}{charcater_sheet}"}, {"role": "system", "content": important_details}, {"role": "user", "content": inp}]
    # Generate a chat response using the OpenAI API
    completion = openai.ChatCompletion.create(
        model=DEFAULT_MODEL,
        messages=compressed_message_history,
        max_tokens=250
    )
    audit_tokens(completion)
    # Grab just the text from the API completion response
    reply_content = completion.choices[0].message.content

    # Append the generated response to the message history
    message_history.append({"role": "assistant", "content": f"{reply_content}"})

    # Return the generated response and the updated message history
    return reply_content, message_history

# Chat with full context, used for first message
def chat_full(inp, message_history, role="user"):
    message_history.append({"role": role, "content": f"{inp}"})

    # Generate a chat response using the OpenAI API
    completion = openai.ChatCompletion.create(
        model=DEFAULT_MODEL,
        messages=message_history
    )
    audit_tokens(completion)
    reply_content = completion.choices[0].message.content

    message_history.append({"role": "assistant", "content": f"{reply_content}"})
    return reply_content, message_history

def parse_reply_content(reply_content):
    # Extract the text and options from the response
    text = reply_content.split("Option 1")[0]
    options = re.findall(r"Option \d:.*", reply_content)

    # Update the button messages and states
    button_messages = {}
    button_states = {}
    for i, option in enumerate(options):
        button_messages[f"button{i+1}"] = option
    for button_name in button_messages.keys():
        button_states[button_name] = False
    return text, button_messages, button_states

def save_sys_prompt(prompt, filename):
    with open(filename, "w") as f:
        f.write(prompt)

def count_total_words(message_history):
    word_count = 0
    for message in message_history:
        word_count += len(message["content"].split())
    return word_count