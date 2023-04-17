from time import time
previous_time = time()
total_cost = 0
prev_total_cost = 0
last_time_diff = 0

def audit_tokens(completion, trace=True):
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
    cost = round(cost, 2)
    print(f"Model: {model} | prompt: #{completion.usage['prompt_tokens']} completion: #{completion.usage['completion_tokens']} |  Cost: {cost} USD | Total Cost: {round(total_cost, 2)} USD")

def time_audit():
    global last_time_diff
    ''' Get's the time since the last time this function was called.''' 
    global previous_time
    current_time = time()
    time_diff = current_time - previous_time
    previous_time = current_time
    last_time_diff = time_diff
    return round(time_diff, 2)

def get_audit():
    global prev_total_cost, total_cost, last_time_diff
    cost_diff = total_cost - prev_total_cost
    prev_total_cost = total_cost
    return cost_diff, last_time_diff