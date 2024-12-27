# Import the library (assuming the code above is saved as `scanning_library.py`)
from scanning_library import *

# Step 1: Define letter frequencies
letter_frequencies = {
    'E': 12.49, 'T': 9.28, 'A': 8.04, 'O': 7.64, 'I': 7.57,
    'N': 7.23, 'S': 6.51, 'R': 6.28, 'H': 5.05, 'L': 4.07,
    'D': 3.82, 'C': 3.34, 'U': 2.73, 'M': 2.51, 'F': 2.40,
    'P': 2.14, 'G': 1.87, 'W': 1.68, 'Y': 1.66, 'B': 1.48,
    'V': 1.05, 'K': 0.54, 'X': 0.23, 'J': 0.16, 'Q': 0.12, 'Z': 0.09
}

# Step 2: Create different grid layouts
rows, cols = 6, 6
abc_grid = create_abc_grid(rows, cols)
frequency_grid = create_frequency_grid(rows, cols, letter_frequencies)
qwerty_grid = create_qwerty_grid(rows, cols)

print("### ABC Layout Grid")
print_markdown_grid(abc_grid)

print("\n### Frequency-Based Layout Grid")
print_markdown_grid(frequency_grid)

print("\n### QWERTY Layout Grid")
print_markdown_grid(qwerty_grid)

# Step 3: Define sample utterances
# Step 3: Define sample utterances and convert them to uppercase
utterances = ["Hello", "Yes", "No", "Thank you", "I need help"]
utterances = [utterance.upper() for utterance in utterances]  # Convert to uppercase

# Step 4: Simulate scanning using different techniques and configurations
# Linear Scanning
time_linear_abc = simulate_utterances(abc_grid, utterances, technique="Linear")
time_linear_frequency = simulate_utterances(frequency_grid, utterances, technique="Linear")

# Row-Column Scanning
time_row_column_abc = simulate_utterances(abc_grid, utterances, technique="Row-Column")
time_row_column_frequency = simulate_utterances(frequency_grid, utterances, technique="Row-Column")

# Fixed Prediction Scanning (e.g., first row contains predictions)
prediction_cells = list(abc_grid.iloc[0])  # First row as prediction cells
time_fixed_prediction = sum(simulate_fixed_prediction(abc_grid, char, prediction_cells) for utterance in utterances for char in utterance)

# Long-Hold Scanning
word_predictions = {"H": "Hello", "T": "Thank you"}  # Map letters to word predictions
time_long_hold = simulate_utterances(frequency_grid, utterances, prediction="Long-Hold", hold_time=1.0)

# Prediction API Scanning
time_api_prediction = simulate_utterances(frequency_grid, utterances, prediction="API", step_time=0.5)

# Step 5: Print Results
print("Simulation Results:")
print(f"Linear Scanning (ABC Layout): {time_linear_abc:.2f} seconds")
print(f"Linear Scanning (Frequency Layout): {time_linear_frequency:.2f} seconds")
print(f"Row-Column Scanning (ABC Layout): {time_row_column_abc:.2f} seconds")
print(f"Row-Column Scanning (Frequency Layout): {time_row_column_frequency:.2f} seconds")
print(f"Fixed Prediction Scanning: {time_fixed_prediction:.2f} seconds")
print(f"Long-Hold Scanning: {time_long_hold:.2f} seconds")
print(f"Prediction API Scanning: {time_api_prediction:.2f} seconds")