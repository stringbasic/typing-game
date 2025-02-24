import tkinter as tk
import tkinter.font as tkFont
from tkinter import scrolledtext
import time
import random

# --- Configuration ---
LEVELS = 10
ROUNDS_PER_LEVEL = 8
WORDS_FILE = "words.txt" # File containing words of varying difficulty

# WPM Benchmarks (Adjust these based on your definition of average)
AVERAGE_WPM = 40
FIVE_STAR_WPM = AVERAGE_WPM * 1.25  # 25% above average

# --- Helper Functions ---

def load_words(filename):
    """Loads words from a text file, categorizing by difficulty."""
    words = {}
    try:
        with open(filename, "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) >= 2:
                    level = int(parts[0])
                    words.setdefault(level, []).extend(parts[1:])
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return {}
    return words

def calculate_score(wpm, errors):
    """Calculates a star-based score based on WPM and errors."""
    #WPM accounts for 70% of the score, and errors accounts for 30%.
    #This way the player is rewarded for typing fast even if they make some errors.
    score = 0
    
    #WPM score
    if wpm >= FIVE_STAR_WPM:
        wpm_score = 0.7
    elif wpm >= AVERAGE_WPM:
        wpm_score = 0.7 * (wpm - AVERAGE_WPM) / (FIVE_STAR_WPM - AVERAGE_WPM)
    else:
        wpm_score = 0
    
    #Errors score
    if errors == 0:
        error_score = 0.3
    else:
        error_score = max(0, 0.3 * (1 - (errors / 10))) #Assuming up to 10 errors are acceptable
    
    score = wpm_score + error_score
    
    if score >= 0.9:
        return 5
    elif score >= 0.7:
        return 4
    elif score >= 0.5:
        return 3
    elif score >= 0.3:
        return 2
    else:
        return 1


# --- Game Class ---

class TypingGame:
    def __init__(self, master):
        self.master = master
        master.title("Typing Speed Challenge")
        master.geometry("800x600")

        self.words = load_words(WORDS_FILE)
        self.current_level = 1
        self.current_round = 1
        self.target_text = ""
        self.start_time = 0
        self.errors = 0
        self.playing = False  # Flag to indicate if a round is in progress

        # --- GUI Elements ---
        self.font = tkFont.Font(family="Helvetica", size=16)

        self.level_label = tk.Label(master, text=f"Level: {self.current_level}", font=self.font)
        self.level_label.pack(pady=5)

        self.round_label = tk.Label(master, text=f"Round: {self.current_round}", font=self.font)
        self.round_label.pack(pady=5)

        self.target_text_display = tk.Label(master, text="", wraplength=700, justify="left", font=self.font)
        self.target_text_display.pack(pady=10)

        self.input_text = scrolledtext.ScrolledText(master, height=5, font=self.font, wrap=tk.WORD)
        self.input_text.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        self.input_text.tag_configure("correct", foreground="green")
        self.input_text.tag_configure("incorrect", foreground="red")
        self.input_text.bind("<KeyRelease>", self.check_input)

        self.score_label = tk.Label(master, text="", font=self.font)
        self.score_label.pack(pady=10)

        self.clear_button = tk.Button(master, text="Clear", command=self.clear_input, font=self.font)
        self.clear_button.pack(side=tk.LEFT, padx=20)

        self.next_button = tk.Button(master, text="Next Round", command=self.next_round, font=self.font, state=tk.DISABLED)
        self.next_button.pack(side=tk.RIGHT, padx=20)

        # --- Initialize Game ---
        self.start_round()

    def start_round(self):
        """Starts a new round, generating text and resetting state."""
        self.score_label.config(text="")
        self.errors = 0
        self.input_text.delete("1.0", tk.END)  # Clear input text
        self.input_text.tag_remove("correct", "1.0", tk.END)
        self.input_text.tag_remove("incorrect", "1.0", tk.END)
        self.next_button.config(state=tk.DISABLED)  # Disable next button

        level = min(self.current_level, len(self.words))  # Ensure valid level
        if not self.words.get(level):
            self.target_text = "Congratulations! You've completed all levels!"
            self.target_text_display.config(text=self.target_text)
            self.playing = False
            return

        num_words = self.current_round  # Increase difficulty by adding more words
        available_words = self.words[level]
        self.target_text = " ".join(random.choice(available_words) for _ in range(num_words))
        self.target_text_display.config(text=self.target_text)
        self.start_time = time.time()
        self.playing = True
        self.input_text.focus_set()  # Give focus to the input text area


    def check_input(self, event=None):
        """Checks the user's input against the target text."""
        if not self.playing:
            return

        typed_text = self.input_text.get("1.0", tk.END).strip()
        target_text = self.target_text

        self.input_text.tag_remove("correct", "1.0", tk.END)
        self.input_text.tag_remove("incorrect", "1.0", tk.END)

        for i, char in enumerate(typed_text):
            if i < len(target_text):
                if char == target_text[i]:
                    self.input_text.tag_add("correct", f"1.{i}", f"1.{i+1}")
                else:
                    self.input_text.tag_add("incorrect", f"1.{i}", f"1.{i+1}")
                    self.errors += 1  # Count errors in real-time
            else:
                # Handle extra characters typed
                self.input_text.tag_add("incorrect", f"1.{i}", f"1.{i+1}")
                self.errors += 1

        if typed_text == target_text:
            self.playing = False
            self.end_round()


    def end_round(self):
        """Calculates the score, displays it, and prepares for the next round."""
        end_time = time.time()
        time_taken = end_time - self.start_time
        num_words = len(self.target_text.split())
        wpm = (num_words / time_taken) * 60
        score = calculate_score(wpm, self.errors)

        score_stars = "*" * score
        self.score_label.config(text=f"Score: {score_stars} (WPM: {wpm:.2f}, Errors: {self.errors})")
        self.next_button.config(state=tk.NORMAL)  # Enable next button

    def next_round(self):
        """Advances to the next round or level."""
        self.current_round += 1
        if self.current_round > ROUNDS_PER_LEVEL:
            self.current_level += 1
            self.current_round = 1

        self.level_label.config(text=f"Level: {self.current_level}")
        self.round_label.config(text=f"Round: {self.current_round}")
        self.start_round()

    def clear_input(self):
        """Clears the input text area."""
        self.input_text.delete("1.0", tk.END)
        self.input_text.tag_remove("correct", "1.0", tk.END)
        self.input_text.tag_remove("incorrect", "1.0", tk.END)
        self.errors = 0 #Reset the error count too.
        self.input_text.focus_set()

# --- Main ---

if __name__ == "__main__":
    root = tk.Tk()
    game = TypingGame(root)
    root.mainloop()
