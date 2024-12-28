import pandas as pd
import numpy as np
import requests
import json
import metrics

# -----------------------
# GRID GENERATION METHODS
# -----------------------

def create_abc_grid(rows, cols, fillers=["", "?", ".", ",", "!"]):
    """
    Generate a grid with letters laid out alphabetically, with customizable fillers.
    Spaces are represented as '_', and blank cells are filled with "".
    """
    letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ_")  # Use '_' instead of ' ' for spaces
    grid_size = rows * cols

    # Calculate how many fillers are needed
    num_fillers_needed = grid_size - len(letters)
    if num_fillers_needed > 0:
        # Use available fillers and pad with "" if needed
        extended_fillers = fillers[:num_fillers_needed] + [""] * (num_fillers_needed - len(fillers))
        extended_letters = letters + extended_fillers
    else:
        # Trim letters if grid is smaller
        extended_letters = letters[:grid_size]

    # Create and return the grid as a NumPy array
    return np.array(extended_letters).reshape(rows, cols)

    # Create and return the grid as a NumPy array
    return np.array(extended_letters).reshape(rows, cols)

def create_frequency_grid(rows, cols, letter_frequencies, fillers=["", "?", ".", ",", "!"]):
    """
    Generate a grid with letters laid out based on frequency, in a linear row-major order.
    """
    sorted_letters = sorted(letter_frequencies.keys(), key=lambda x: -letter_frequencies[x])
    # Replace space with '_'
    sorted_letters = [char if char != " " else "_" for char in sorted_letters]
    grid_size = rows * cols

    # Calculate fillers if needed
    num_fillers_needed = grid_size - len(sorted_letters)
    if num_fillers_needed > 0:
        extended_fillers = fillers[:num_fillers_needed] + [""] * (num_fillers_needed - len(fillers))
        extended_letters = sorted_letters + extended_fillers
    else:
        extended_letters = sorted_letters[:grid_size]

    # Ensure row-major order
    return np.array(extended_letters).reshape(rows, cols)

def create_qwerty_grid(rows, cols, fillers=["", "?", ".", ",", "!"]):
    """
    Generate a QWERTY-style grid layout, with customizable fillers.
    If there aren't enough fillers, the remaining cells are filled with "".
    """
    qwerty_layout = list("QWERTYUIOPASDFGHJKLZXCVBNM ")
    grid_size = rows * cols

    # Calculate how many fillers are needed
    num_fillers_needed = grid_size - len(qwerty_layout)
    if num_fillers_needed > 0:
        # Use available fillers and pad with "" if needed
        extended_fillers = fillers[:num_fillers_needed] + [""] * (num_fillers_needed - len(fillers))
        extended_qwerty = qwerty_layout + extended_fillers
    else:
        # Trim layout if grid is smaller
        extended_qwerty = qwerty_layout[:grid_size]

    # Create and return the grid as a NumPy array
    return np.array(extended_qwerty).reshape(rows, cols)

    # Create and return the grid as a NumPy array
    return np.array(extended_qwerty).reshape(rows, cols)

def generate_custom_grid(rows, cols, custom_layout, fillers=["", "?", ".", ",", "!"]):
    """
    Generate a grid using a custom letter layout provided as a list, ensuring space and fillers are included.
    If there aren't enough fillers, the remaining cells are filled with "".
    """
    if " " not in custom_layout:
        custom_layout.append(" ")  # Add space if not already included
    grid_size = rows * cols

    # Calculate how many fillers are needed
    num_fillers_needed = grid_size - len(custom_layout)
    if num_fillers_needed > 0:
        # Use available fillers and pad with "" if needed
        extended_fillers = fillers[:num_fillers_needed] + [""] * (num_fillers_needed - len(fillers))
        extended_layout = custom_layout + extended_fillers
    else:
        # Trim layout if grid is smaller
        extended_layout = custom_layout[:grid_size]

    # Create and return the grid as a NumPy array
    return np.array(extended_layout).reshape(rows, cols)

# --------------------------
# SCANNING SIMULATION METHODS
# --------------------------

def linear_scanning(grid, target, start_index=0, step_time=0.5):
    """Simulate linear scanning."""
    # Flatten the grid (NumPy array) to a 1D array
    grid_values = grid.flatten()
    target = target.upper() 
    
    # Find the indices of the target in the flattened grid
    indices = np.where(grid_values == target)[0]
    if len(indices) == 0:
        raise ValueError(f"Target {target} not found in the grid.")
    
    # Determine steps required to reach the target
    steps = indices[(indices >= start_index).argmax()] - start_index + 1
    return steps * step_time, indices[(indices >= start_index).argmax()]

def row_column_scanning(grid, target, start_index=0, step_time=0.5):
    """Simulate row-column scanning."""
    rows, cols = grid.shape
    grid_values = grid.flatten()
    target_index = np.where(grid_values == target)[0]
    if len(target_index) == 0:
        raise ValueError(f"Target {target} not found in the grid.")
    
    target_index = target_index[0]
    target_row, target_col = divmod(target_index, cols)
    start_row, start_col = divmod(start_index, cols)
    
    row_steps = abs(target_row - start_row)
    col_steps = abs(target_col - start_col)
    
    total_steps = row_steps + col_steps + 1
    return total_steps * step_time, target_index


# --------------------------
# PREDICTION AND LONG-HOLD
# --------------------------

def simulate_classic_aac_prediction(grid, target, prev_chars, api="PPM", step_time=0.5):
    """
    Simulate AAC prediction where the first row dynamically updates with context-based predictions.
    """
    # Generate context
    context = "".join(prev_chars).strip() if prev_chars else " "
    #print(f"Context: '{context}', Target: '{target}'")

    # Get predictions for the first row
    prediction_cells = query_prediction_api(
        context=context,
        api=api,
        level="word",
        mode="complete" if context.strip() else "next",
        num_predictions=len(grid[0])  # Limit to the size of the first row
    )

    # Simulate selection
    if target in prediction_cells:
        # Calculate steps to the target in the first row
        steps = prediction_cells.index(target) + 1
    else:
        # Fallback to linear scanning
        steps, _ = linear_scanning(grid, target, step_time=step_time)

    return steps * step_time

def simulate_long_hold(grid, target, word_predictions, hold_time=1.0, step_time=0.5):
    """
    Simulate a single-tap to select letters or long-hold to select word predictions.
    Word predictions are mapped to specific letters.
    """
    if target in word_predictions.values():
        # Long hold on a letter to select a word prediction
        letter = [key for key, value in word_predictions.items() if value == target][0]
        steps, _ = linear_scanning(grid, letter, step_time=step_time)
        return steps * step_time + hold_time
    else:
        # Single tap for letters
        steps, _ = linear_scanning(grid, target, step_time=step_time)
        return steps * step_time

def simulate_long_hold_with_real_predictions(grid, target, prev_chars, prediction_api="PPM", hold_time=1.0, step_time=0.5):
    """
    Simulate long-hold scanning using predictions from an external API.
    """
    context = "".join(prev_chars).strip() if prev_chars else " "  # Default context
    target = target.lower()
    #print(f"Current context: '{context}' for target '{target}'")

    predicted_words = query_prediction_api(context=context, api=prediction_api, level="word", mode="complete", num_predictions=5)
    #print(f"Predicted words: {predicted_words}")

    if target in predicted_words:
        # Direct selection using long hold
        return hold_time
    else:
        # Fall back to linear scanning
        steps, _ = linear_scanning(grid, target, step_time=step_time)
        return steps * step_time


# --------------------------
# API-BASED PREDICTION METHODS
# --------------------------


def query_prediction_api(context, api="PPM", level="letter", mode="complete", num_predictions=5):
    """
    Query the prediction API with the given context and return the top predictions.
    """
    # Replace underscores in the context with spaces for the API
    normalized_context = context.replace("_", " ").lower()
    
    url = "https://ppmpredictor.openassistive.org/predict"
    payload = {
        "input": normalized_context,
        "level": level,
        "mode": mode,  # Include the new 'mode' parameter
        "numPredictions": num_predictions,
    }
    headers = {"accept": "application/json", "Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for bad HTTP responses
        data = response.json()

        # Extract predictions and map spaces back to underscores for consistency
        predictions = [
            item["symbol"].lower() if item["symbol"] != " " else "_"
            for item in data.get("predictions", [])
        ]

        # Log raw API response and processed predictions
        #print(f"Raw API Response: {json.dumps(data, indent=2)}")
        #print(f"Processed Predictions: {predictions}")

        return predictions

    except requests.exceptions.RequestException as e:
        print(f"API Request Failed: {e}")
        return []



def simulate_with_prediction_api(grid, target, prev_chars, api="PPM", level="letter", num_predictions=5, step_time=0.5):
    """
    Simulate scanning with predictions dynamically updated by the API,
    while tracking prediction accuracy.
    """
    # Generate context and normalize target
    context = "".join(prev_chars) if prev_chars else " "
    target = target.lower()
    #print(f"Context: '{context}', Target: '{target}'")

    # Query API
    predicted_set = query_prediction_api(context, api=api, level=level, num_predictions=num_predictions)
    #print(f"API Predictions: {predicted_set}")

    # Track prediction accuracy
    metrics.total_predictions += 1
    if target in predicted_set:
        metrics.correct_predictions += 1

    # Calculate time based on predictions or fall back to linear scanning
    if target in predicted_set:
        steps = predicted_set.index(target) + 1
        return steps * step_time
    else:
        return linear_scanning(grid, target, step_time=step_time)[0]
    
# --------------------------
# EXAMPLE USAGE AND SETTINGS
# --------------------------

def simulate_utterances(grid, utterances, technique="Linear", prediction=None, step_time=0.5, hold_time=1.0, prediction_api="PPM"):
    """
    Simulate scanning for a list of utterances using the selected technique.
    Reset context between utterances to avoid bloated input to the prediction API.
    """
    total_time = 0
    for utterance in utterances:
        prev_chars = []  # Reset context for each utterance
        for char in utterance:
            grid_char = "_" if char == " " else char  # Convert spaces to '_'
            if grid_char not in grid.flatten():
                raise ValueError(f"Target {char} not found in the grid.")
            if prediction == "API":
                # Call the API-based prediction simulation
                total_time += simulate_with_prediction_api(grid, grid_char, prev_chars, api=prediction_api, step_time=step_time)
            elif prediction == "Long-Hold":
                total_time += simulate_long_hold_with_real_predictions(
                    grid, grid_char, prev_chars, prediction_api=prediction_api, hold_time=hold_time, step_time=step_time
                )
            else:
                if technique == "Linear":
                    time, _ = linear_scanning(grid, grid_char, step_time=step_time)
                elif technique == "Row-Column":
                    time, _ = row_column_scanning(grid, grid_char, step_time=step_time)
                total_time += time
            prev_chars.append(grid_char)
    return total_time

# --------------------------
# Pretty Print Grid
# --------------------------

def print_grid(grid):
    """
    Print a NumPy grid in a clean table format.
    Replace empty strings ("") with spaces (" ") for consistent spacing.
    """
    for row in grid:
        print(" | ".join([cell if cell != "" else " " for cell in row]))


def print_markdown_grid(grid):
    """
    Convert a Pandas DataFrame grid into a Markdown table for display.
    """
    col_width = max(max(len(str(x)) for x in grid.values.flatten()), 5)  # Adjust width dynamically
    markdown_table = "| " + " | ".join([f"{col:<{col_width}}" for col in grid.columns]) + " |\n"
    markdown_table += "| " + " | ".join(["-" * col_width] * len(grid.columns)) + " |\n"
    for _, row in grid.iterrows():
        markdown_table += "| " + " | ".join([f"{str(x):<{col_width}}" for x in row]) + " |\n"
    print(markdown_table)

# this is for a Jupyter notebook
def display_markdown_grid(grid, title="Grid Layout"):
    """
    Display a Pandas DataFrame grid as a Markdown table in Jupyter Notebook.
    """
    markdown_table = f"### {title}\n\n| " + " | ".join(grid.columns) + " |\n"
    markdown_table += "| " + " | ".join(["---"] * len(grid.columns)) + " |\n"
    for _, row in grid.iterrows():
        markdown_table += "| " + " | ".join(row) + " |\n"
    return Markdown(markdown_table)