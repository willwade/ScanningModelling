import pandas as pd
import numpy as np
import requests


# -----------------------
# GRID GENERATION METHODS
# -----------------------

def create_abc_grid(rows, cols):
    """Generate a grid with letters laid out alphabetically, including a space."""
    letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ ")
    grid_size = rows * cols
    extended_letters = (letters * ((grid_size // len(letters)) + 1))[:grid_size]
    return pd.DataFrame(
        np.array(extended_letters).reshape(rows, cols),
        columns=[f"Col {i+1}" for i in range(cols)],
        index=[f"Row {i+1}" for i in range(rows)]
    )


def create_frequency_grid(rows, cols, letter_frequencies):
    """Generate a grid with letters laid out based on frequency of use, including a space."""
    sorted_letters = sorted(letter_frequencies, key=lambda x: -letter_frequencies[x])
    sorted_letters.append(" ")  # Ensure space is included
    grid_size = rows * cols
    extended_letters = (sorted_letters * ((grid_size // len(sorted_letters)) + 1))[:grid_size]
    return pd.DataFrame(
        np.array(extended_letters).reshape(rows, cols),
        columns=[f"Col {i+1}" for i in range(cols)],
        index=[f"Row {i+1}" for i in range(rows)]
    )


def create_qwerty_grid(rows, cols):
    """Generate a QWERTY-style grid layout, including a space."""
    qwerty_layout = list("QWERTYUIOPASDFGHJKLZXCVBNM ")
    grid_size = rows * cols
    extended_qwerty = (qwerty_layout * ((grid_size // len(qwerty_layout)) + 1))[:grid_size]
    return pd.DataFrame(
        np.array(extended_qwerty).reshape(rows, cols),
        columns=[f"Col {i+1}" for i in range(cols)],
        index=[f"Row {i+1}" for i in range(rows)]
    )


def generate_custom_grid(rows, cols, custom_layout):
    """Generate a grid using a custom letter layout provided as a list, ensuring a space is included."""
    if " " not in custom_layout:
        custom_layout.append(" ")  # Add space if not already included
    grid_size = rows * cols
    extended_layout = (custom_layout * ((grid_size // len(custom_layout)) + 1))[:grid_size]
    return pd.DataFrame(
        np.array(extended_layout).reshape(rows, cols),
        columns=[f"Col {i+1}" for i in range(cols)],
        index=[f"Row {i+1}" for i in range(rows)]
    )

# --------------------------
# SCANNING SIMULATION METHODS
# --------------------------

def linear_scanning(grid, target, start_index=0, step_time=0.5):
    """Simulate linear scanning."""
    grid_values = grid.values.flatten()
    indices = np.where(grid_values == target)[0]
    if len(indices) == 0:
        raise ValueError(f"Target {target} not found in the grid.")
    steps = indices[(indices >= start_index).argmax()] - start_index + 1
    return steps * step_time, indices[(indices >= start_index).argmax()]


def row_column_scanning(grid, target, start_index=0, step_time=0.5):
    """Simulate row-column scanning."""
    rows, cols = grid.shape
    grid_values = grid.values.flatten()
    target_index = np.where(grid_values == target)[0][0]
    row_steps = abs((target_index // cols) - (start_index // cols))
    col_steps = abs((target_index % cols) - (start_index % cols))
    return (row_steps + col_steps + 1) * step_time, target_index


# --------------------------
# PREDICTION AND LONG-HOLD
# --------------------------

def simulate_fixed_prediction(grid, target, prediction_cells, step_time=0.5):
    """Simulate fixed prediction scanning using specific prediction cells."""
    if target in prediction_cells:
        steps = prediction_cells.index(target) + 1
        return steps * step_time
    else:
        return linear_scanning(grid, target, step_time=step_time)[0]


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


# --------------------------
# API-BASED PREDICTION METHODS
# --------------------------

def query_prediction_api(context, api="PPM", level="letter", num_predictions=5):
    """Query a selected prediction API."""
    if api == "PPM":
        url = "https://ppmpredictor.openassistive.org/predict"
        payload = {"input": context, "level": level, "numPredictions": num_predictions}
    elif api == "Imagineville":
        url = "https://api.imagineville.org/predict"
        payload = {"context": context, "max_predictions": num_predictions}
    else:
        raise ValueError("Invalid API selected. Choose 'PPM' or 'Imagineville'.")

    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json().get("predictions", [])
    else:
        raise Exception(f"API Error: {response.status_code} - {response.text}")


def simulate_with_prediction_api(grid, target, prev_chars, api="PPM", level="letter", num_predictions=5, step_time=0.5):
    """Simulate scanning with prediction API."""
    # Handle empty context
    context = "".join(prev_chars) if prev_chars else " "

    # Query the selected API
    predicted_set = query_prediction_api(context, api=api, level=level, num_predictions=num_predictions)

    if target in predicted_set:
        steps = predicted_set.index(target) + 1
        return steps * step_time
    else:
        return linear_scanning(grid, target, step_time=step_time)[0]


# --------------------------
# EXAMPLE USAGE AND SETTINGS
# --------------------------

def simulate_utterances(grid, utterances, technique="Linear", prediction=None, step_time=0.5, hold_time=1.0):
    """Simulate scanning for a list of utterances using the selected technique."""
    total_time = 0
    prev_chars = []
    for utterance in utterances:
        for char in utterance:
            if char not in grid.values:
                continue
            if prediction == "API":
                total_time += simulate_with_prediction_api(grid, char, prev_chars, step_time=step_time)
            elif prediction == "Long-Hold":
                word_predictions = {"H": "Hello", "T": "Thank you"}  # Example mappings
                total_time += simulate_long_hold(grid, char, word_predictions, hold_time=hold_time, step_time=step_time)
            else:
                if technique == "Linear":
                    time, _ = linear_scanning(grid, char, step_time=step_time)
                elif technique == "Row-Column":
                    time, _ = row_column_scanning(grid, char, step_time=step_time)
                total_time += time
            prev_chars.append(char)
    return total_time  


# --------------------------
# Pretty Print Grid
# --------------------------

def print_markdown_grid(grid):
    """
    Convert a Pandas DataFrame grid into a Markdown table for display.
    """
    markdown_table = "| " + " | ".join(grid.columns) + " |\n"
    markdown_table += "| " + " | ".join(["---"] * len(grid.columns)) + " |\n"
    for _, row in grid.iterrows():
        markdown_table += "| " + " | ".join(row) + " |\n"
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