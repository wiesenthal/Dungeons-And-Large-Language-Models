from time import time
previous_time = time()
total_cost = 0

def audit_tokens(completion):
    global total_cost
    COST_MAP = {
        #Model: [prompt_token cost/1000, completion_token_cost/1000]
        "gpt-3.5-turbo": [0.002, 0.002],
        "gpt-4": [0.03, 0.06],
        "Unknown": [0.0, 0.0]
    }
    if ("gpt-3.5-turbo" in completion.model):
        model = "gpt-3.5-turbo"
    elif ("gpt-4" in completion.model):
        model = "gpt-4"
    else:
        model = "Unknown"
    cost = (completion.usage['prompt_tokens'] * COST_MAP[model][0] + completion.usage['completion_tokens'] * COST_MAP[model][1]) / 1000
    total_cost += cost
    print(f"Model: {model} | prompt: #{completion.usage['prompt_tokens']} completion: #{completion.usage['completion_tokens']} |  Cost: {cost} USD | Total Cost: {total_cost} USD")

def time_audit():
    ''' Get's the time since the last time this function was called.''' 
    global previous_time
    current_time = time()
    time_diff = current_time - previous_time
    previous_time = current_time
    return round(time_diff, 2)
