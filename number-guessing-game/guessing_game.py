import tkinter as tk
import random
import sys
import time

# --- Dark Theme Colors ---
BG_COLOR = "#23272f"
FG_COLOR = "#f8f8f2"
ENTRY_BG = "#2d323e"
BTN_BG = "#44475a"
BTN_FG = "#f8f8f2"
FEEDBACK_COLORS = {
    "low": "#ff5555",
    "high": "#ffb86c",
    "close": "#f1fa8c",
    "correct": "#50fa7b",
    "error": "#bd93f9"
}

# --- Sound Effects ---
def beep_correct():
    if sys.platform == "win32":
        import winsound
        winsound.Beep(880, 150)
    else:
        print('\a', end='')

def beep_wrong():
    if sys.platform == "win32":
        import winsound
        winsound.Beep(220, 120)
    else:
        print('\a', end='')

# --- Game State ---
secret_number = random.randint(1, 100)
guess_count = 0
game_active = True
guesses = []
min_range = 1
max_range = 100
start_time = None
timer_id = None
best_score = None
best_time = None

# --- Main Window ---
root = tk.Tk()
root.title("Number Guessing Game")
root.geometry("440x500")
root.configure(bg=BG_COLOR)

# --- UI Elements ---
title = tk.Label(
    root,
    text="Guess a number between 1 and 100",
    font=("Arial", 14, "bold"),
    bg=BG_COLOR,
    fg=FG_COLOR
)
title.pack(pady=10)

entry = tk.Entry(
    root,
    font=("Arial", 12),
    bg=ENTRY_BG,
    fg=FG_COLOR,
    insertbackground=FG_COLOR,
    highlightbackground=BTN_BG,
    highlightcolor=BTN_BG,
    justify="center"
)
entry.pack()

feedback = tk.Label(
    root,
    text="",
    font=("Arial", 12, "bold"),
    bg=BG_COLOR,
    fg=FG_COLOR
)
feedback.pack(pady=10)

counter_label = tk.Label(
    root,
    text="Attempts: 0",
    font=("Arial", 11),
    bg=BG_COLOR,
    fg="#8be9fd"
)
counter_label.pack(pady=2)

range_hint = tk.Label(
    root,
    text="Range: 1 - 100",
    font=("Arial", 11),
    bg=BG_COLOR,
    fg="#bd93f9"
)
range_hint.pack(pady=2)

timer_label = tk.Label(
    root,
    text="Time: 0.0s",
    font=("Arial", 11),
    bg=BG_COLOR,
    fg="#f1fa8c"
)
timer_label.pack(pady=2)

highscore_label = tk.Label(
    root,
    text="Best: -- attempts, -- s",
    font=("Arial", 11),
    bg=BG_COLOR,
    fg="#50fa7b"
)
highscore_label.pack(pady=2)

history_label = tk.Label(
    root,
    text="Previous guesses: ",
    font=("Arial", 11),
    bg=BG_COLOR,
    fg="#8be9fd",
    justify="left",
    anchor="w"
)
history_label.pack(fill="x", padx=20, pady=5)

# --- Animated feedback transition ---
def animate_feedback(target_color):
    current = feedback.cget("fg")
    if current == target_color:
        return
    steps = 10
    def hex_to_rgb(h): return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))
    def rgb_to_hex(r, g, b): return f"#{r:02x}{g:02x}{b:02x}"
    start = hex_to_rgb(current)
    end = hex_to_rgb(target_color)
    for i in range(1, steps+1):
        r = int(start[0] + (end[0] - start[0]) * i / steps)
        g = int(start[1] + (end[1] - start[1]) * i / steps)
        b = int(start[2] + (end[2] - start[2]) * i / steps)
        color = rgb_to_hex(r, g, b)
        root.after(i*15, lambda c=color: feedback.config(fg=c))

# --- Timer ---
def update_timer():
    global timer_id
    if not game_active or start_time is None:
        return
    elapsed = time.time() - start_time
    timer_label.config(text=f"Time: {elapsed:.1f}s")
    timer_id = root.after(100, update_timer)

def start_timer():
    global start_time, timer_id
    start_time = time.time()
    timer_label.config(text="Time: 0.0s")
    if timer_id:
        root.after_cancel(timer_id)
    update_timer()

def stop_timer():
    global timer_id
    if timer_id:
        root.after_cancel(timer_id)
        timer_id = None

# --- Game Logic ---
def check_guess(event=None):
    global guess_count, game_active, min_range, max_range, best_score, best_time
    if not game_active:
        return
    try:
        guess = int(entry.get())
        if guess < min_range or guess > max_range:
            feedback.config(text=f"Enter a number between {min_range} and {max_range}.")
            animate_feedback(FEEDBACK_COLORS["error"])
            beep_wrong()
            return
        if guess_count == 0:
            start_timer()
        guess_count += 1
        guesses.append(guess)
        counter_label.config(text=f"Attempts: {guess_count}")
        history_label.config(text="Previous guesses: " + ", ".join(str(g) for g in guesses))
        diff = abs(guess - secret_number)
        emoji = ""
        if guess == secret_number:
            stop_timer()
            elapsed = time.time() - start_time
            feedback.config(text=f"🎉 Correct! You guessed it in {guess_count} attempts!\nTime: {elapsed:.1f}s")
            animate_feedback(FEEDBACK_COLORS["correct"])
            beep_correct()
            entry.config(state="disabled")
            check_button.config(state="disabled")
            game_active = False
            # High score logic
            if best_score is None or guess_count < best_score or (guess_count == best_score and elapsed < best_time):
                best_score = guess_count
                best_time = elapsed
                highscore_label.config(text=f"Best: {best_score} attempts, {best_time:.1f} s")
            # Confetti (simple emoji)
            for i in range(10):
                root.after(i*80, lambda: feedback.config(text=feedback.cget("text") + " 🎊"))
        elif diff <= 5:
            hint = "Too low!" if guess < secret_number else "Too high!"
            emoji = "🔥"
            feedback.config(text=f"{hint} But you're very close! {emoji}")
            animate_feedback(FEEDBACK_COLORS["close"])
            beep_wrong()
            # Update range
            if guess < secret_number and guess+1 > min_range:
                min_range = guess+1
            elif guess > secret_number and guess-1 < max_range:
                max_range = guess-1
        elif guess < secret_number:
            feedback.config(text="Too low! Try again. 😅")
            animate_feedback(FEEDBACK_COLORS["low"])
            beep_wrong()
            if guess+1 > min_range:
                min_range = guess+1
        else:
            feedback.config(text="Too high! Try again. 🤔")
            animate_feedback(FEEDBACK_COLORS["high"])
            beep_wrong()
            if guess-1 < max_range:
                max_range = guess-1
        range_hint.config(text=f"Range: {min_range} - {max_range}")
    except ValueError:
        feedback.config(text="Please enter a valid number.")
        animate_feedback(FEEDBACK_COLORS["error"])
        beep_wrong()
    entry.delete(0, tk.END)

def reset_game():
    global secret_number, guess_count, game_active, guesses, min_range, max_range, start_time
    secret_number = random.randint(1, 100)
    guess_count = 0
    game_active = True
    guesses = []
    min_range = 1
    max_range = 100
    feedback.config(text="Game reset! Guess a number between 1 and 100.")
    animate_feedback(FEEDBACK_COLORS["error"])
    counter_label.config(text="Attempts: 0")
    entry.config(state="normal")
    check_button.config(state="normal")
    entry.delete(0, tk.END)
    entry.focus_set()
    range_hint.config(text="Range: 1 - 100")
    history_label.config(text="Previous guesses: ")
    stop_timer()
    timer_label.config(text="Time: 0.0s")
    start_time = None

# --- Buttons ---
button_frame = tk.Frame(root, bg=BG_COLOR)
button_frame.pack(pady=10)

check_button = tk.Button(
    button_frame,
    text="Check",
    command=check_guess,
    font=("Arial", 12, "bold"),
    bg=BTN_BG,
    fg=BTN_FG,
    activebackground=BTN_FG,
    activeforeground=BTN_BG,
    relief=tk.RAISED,
    bd=2,
    width=10
)
check_button.grid(row=0, column=0, padx=5)

reset_button = tk.Button(
    button_frame,
    text="Reset",
    command=reset_game,
    font=("Arial", 12, "bold"),
    bg="#6272a4",
    fg=BTN_FG,
    activebackground=BTN_FG,
    activeforeground="#6272a4",
    relief=tk.RAISED,
    bd=2,
    width=10
)
reset_button.grid(row=0, column=1, padx=5)

# --- Bindings ---
entry.bind("<Return>", check_guess)

# --- Focus entry on start ---
entry.focus_set()

# --- Start the Tkinter event loop ---
root.mainloop()