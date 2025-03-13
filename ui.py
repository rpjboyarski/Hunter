import pyfiglet
import shutil
from utils import console

def print_banner():
    # Generate banner without justification in figlet
    banner = pyfiglet.figlet_format("HUNTER", font="bloody")

    # Color variations for blood effect
    blood_colors = ["#8B0000", "#A50000", "#B22222", "#CD0000", "#FF0000", "#FF1a1a"]

    # Get terminal width for manual centering
    terminal_width = shutil.get_terminal_size().columns

    # Process banner line by line
    for line in banner.split('\n'):
        # Calculate visible width (without counting color markup)
        visible_width = len(line)
        # Calculate left padding for centering
        padding = (terminal_width - visible_width) // 2

        # Build colored line
        colored_line = " " * padding  # Add padding at the start
        for i, char in enumerate(line):
            if char != ' ':
                color = blood_colors[i % len(blood_colors)]
                colored_line += f"[{color}]{char}[/{color}]"
            else:
                colored_line += " "

        # Print without justify parameter
        console.print(colored_line)

