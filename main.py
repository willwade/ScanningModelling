# Import necessary methods and global variables from the library
from scanning_library import (
    create_abc_grid, create_frequency_grid, create_qwerty_grid, simulate_utterances, simulate_classic_aac_prediction, print_grid
)
import metrics

# Step 1: Define letter frequencies
letter_frequencies = {
    'E': 12.49, 'T': 9.28, 'A': 8.04, 'O': 7.64, 'I': 7.57,
    'N': 7.23, 'S': 6.51, 'R': 6.28, 'H': 5.05, 'L': 4.07,
    'D': 3.82, 'C': 3.34, 'U': 2.73, 'M': 2.51, 'F': 2.40,
    'P': 2.14, 'G': 1.87, 'W': 1.68, 'Y': 1.66, 'B': 1.48,
    'V': 1.05, 'K': 0.54, 'X': 0.23, 'J': 0.16, 'Q': 0.12, 'Z': 0.09, '_': 15.00
}

# Step 2: Create grids
rows, cols = 5, 6
abc_grid = create_abc_grid(rows, cols)
rows, cols = 6, 6
frequency_grid = create_frequency_grid(rows, cols, letter_frequencies)
rows, cols = 4,10
qwerty_grid = create_qwerty_grid(rows, cols)

# Step 3: Display grids
print("### ABC Layout Grid\n")
print_grid(abc_grid)

print("\n### Frequency-Based Layout Grid (Row-Major Order)\n")
print_grid(frequency_grid)

print("\n### QWERTY Layout Grid\n")
print_grid(qwerty_grid)

# Step 4: Define utterances
utterances = ["HELLO", "YES", "NO", "THANK_YOU", "I_NEED_HELP"]

# Step 5: Simulate scanning
time_linear_abc = simulate_utterances(abc_grid, utterances, technique="Linear")
time_linear_frequency = simulate_utterances(frequency_grid, utterances, technique="Linear")
time_row_column_abc = simulate_utterances(abc_grid, utterances, technique="Row-Column")
time_row_column_frequency = simulate_utterances(frequency_grid, utterances, technique="Row-Column")

# Simulate classic AAC predictions
time_classic_aac = sum(
    simulate_classic_aac_prediction(
        abc_grid,  # Use the ABC grid as the base
        char,      # Target character
        prev_chars  # Previous context for predictions
    )
    for utterance in utterances for char, prev_chars in zip(utterance, [utterance[:i] for i in range(len(utterance))])
)

time_long_hold = simulate_utterances(frequency_grid, utterances, prediction="Long-Hold", hold_time=1.0)
time_api_prediction = simulate_utterances(frequency_grid, utterances, prediction="API", step_time=0.5)

# Step 6: Print results
print("\n## Simulation Results:\n")
print(f"Linear Scanning (ABC Layout): {time_linear_abc:.2f} seconds")
print(f"Linear Scanning (Frequency Layout): {time_linear_frequency:.2f} seconds")
print(f"Classic AAC with Prediction cells Scanning Time: {time_classic_aac:.2f} seconds")
print(f"Row-Column Scanning (ABC Layout): {time_row_column_abc:.2f} seconds")
print(f"Row-Column Scanning (Frequency Layout): {time_row_column_frequency:.2f} seconds")
print(f"Long-Hold Scanning: {time_long_hold:.2f} seconds")
print(f"Prediction API Scanning Time: {time_api_prediction:.2f} seconds")


# Access the global variables from the library and display prediction accuracy
if metrics.total_predictions > 0:
    accuracy = (metrics.correct_predictions / metrics.total_predictions) * 100
    print(f"Prediction Accuracy: {metrics.correct_predictions}/{metrics.total_predictions} ({accuracy:.2f}%)")
else:
    print("No predictions were made.")