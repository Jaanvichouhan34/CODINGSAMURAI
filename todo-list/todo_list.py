import os
import json
import csv
import random
import time
from datetime import datetime
from colorama import init, Fore, Back
from prettytable import PrettyTable
from playsound import playsound

init(autoreset=True)

# 📁 Files
TASK_FILE = 'tasks.json'
HISTORY_FILE = 'history.log'
SOUND_FILE = 'click.mp3'  # Provide your own short sound file here
BACKUP_FILE = 'tasks_backup.json'

# 🌙 Theme Colors
THEMES = {
    "light": {
        "primary": Fore.BLACK + Back.WHITE,
        "success": Fore.GREEN,
        "error": Fore.RED,
        "info": Fore.BLUE,
        "warning": Fore.YELLOW
    },
    "dark": {
        "primary": Fore.WHITE + Back.BLACK,
        "success": Fore.LIGHTGREEN_EX,
        "error": Fore.LIGHTRED_EX,
        "info": Fore.CYAN,
        "warning": Fore.LIGHTYELLOW_EX
    }
}

current_theme = "light"
theme = THEMES[current_theme]

# 🌟 Motivational Quotes
QUOTES = [
    "Dream big. Start small. Act now.",
    "Discipline is the bridge between goals and accomplishment.",
    "Focus on being productive instead of busy.",
    "Don’t watch the clock; do what it does. Keep going.",
    "Success is not final, failure is not fatal."
]

# 🧠 Emojis by Category
EMOJIS = {
    "work": "💼",
    "personal": "🏡",
    "other": "📌"
}

PRIORITY_EMOJIS = {
    "High": "🔥",
    "Medium": "⭐",
    "Low": "🟢"
}

STATUS_COLORS = {
    "Pending": Fore.YELLOW,
    "In-Progress": Fore.CYAN,
    "Completed": Fore.GREEN
}

# For undo feature
last_action = None
last_task = None
last_task_index = None

# 🧠 Load/Save Helpers
def load_tasks():
    return json.load(open(TASK_FILE)) if os.path.exists(TASK_FILE) else []

def save_tasks(tasks):
    with open(TASK_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)

def log_history(action, task):
    with open(HISTORY_FILE, 'a') as f:
        f.write(f"{datetime.now()} - {action}: {task['task']}\n")

# 🎬 Sound
def play_sound():
    if os.path.exists(SOUND_FILE):
        try:
            playsound(SOUND_FILE)
        except:
            pass

# 🔁 Transition Animation
def transition(message="Loading", dot_count=3, delay=0.4):
    print(theme["info"] + message, end="", flush=True)
    for _ in range(dot_count):
        time.sleep(delay)
        print(".", end="", flush=True)
    print()

# 📋 Show Tasks
def show_tasks(tasks):
    if not tasks:
        print(theme["warning"] + "No tasks found.")
        return
    table = PrettyTable()
    table.field_names = ["ID", "Task", "Category", "Due Date", "Priority", "Status"]
    today = datetime.now().date()
    for idx, task in enumerate(tasks):
        emoji = EMOJIS.get(task['category'].lower(), "📝")
        priority_emoji = PRIORITY_EMOJIS.get(task.get('priority', 'Medium'), "⭐")
        status = task.get('status', 'Pending')
        due_date = task['due']
        # Highlight overdue/today
        try:
            due = datetime.strptime(due_date, "%Y-%m-%d").date()
            if status != "Completed" and due < today:
                due_date = Fore.RED + due_date + " (Overdue)" + Fore.RESET
            elif status != "Completed" and due == today:
                due_date = Fore.BLUE + due_date + " (Today)" + Fore.RESET
        except:
            pass
        table.add_row([
            idx + 1,
            f"{emoji} {task['task']}",
            task['category'],
            due_date,
            priority_emoji + " " + task.get('priority', 'Medium'),
            STATUS_COLORS.get(status, "") + status + Fore.RESET
        ])
    print(theme["primary"] + str(table))

# ✅ Add Task
def add_task(tasks):
    task_name = input("Enter task: ")
    category = input("Category (Work/Personal/Other): ").capitalize()
    due_date = input("Due date (YYYY-MM-DD): ")
    priority = input("Priority (High/Medium/Low): ").capitalize()
    status = "Pending"
    tasks.append({
        'task': task_name,
        'category': category,
        'due': due_date,
        'priority': priority if priority in PRIORITY_EMOJIS else "Medium",
        'status': status
    })
    transition("Adding task")
    save_tasks(tasks)
    play_sound()
    print(theme["success"] + "✅ Task added successfully!")

# ❌ Delete Task
def delete_task(tasks):
    global last_action, last_task, last_task_index
    show_tasks(tasks)
    index = int(input("Enter task number to delete: ")) - 1
    if 0 <= index < len(tasks):
        log_history("Deleted", tasks[index])
        transition("Deleting task")
        last_action = "delete"
        last_task = tasks[index].copy()
        last_task_index = index
        del tasks[index]
        save_tasks(tasks)
        play_sound()
        print(theme["error"] + "❌ Task deleted.")
    else:
        print(theme["error"] + "Invalid task number.")

# ✅ Complete Task
def complete_task(tasks):
    global last_action, last_task, last_task_index
    show_tasks(tasks)
    index = int(input("Enter task number to complete: ")) - 1
    if 0 <= index < len(tasks):
        log_history("Completed", tasks[index])
        transition("Completing task")
        last_action = "complete"
        last_task = tasks[index].copy()
        last_task_index = index
        tasks[index]['status'] = "Completed"
        save_tasks(tasks)
        play_sound()
        print(theme["success"] + "✅ Task marked as completed!")
    else:
        print(theme["error"] + "Invalid task number.")

# ✏️ Edit Task
def edit_task(tasks):
    show_tasks(tasks)
    index = int(input("Enter task number to edit: ")) - 1
    if 0 <= index < len(tasks):
        task = tasks[index]
        print("Leave blank to keep current value.")
        new_name = input(f"Task name [{task['task']}]: ") or task['task']
        new_cat = input(f"Category [{task['category']}]: ") or task['category']
        new_due = input(f"Due date [{task['due']}]: ") or task['due']
        new_priority = input(f"Priority [{task.get('priority', 'Medium')}]: ") or task.get('priority', 'Medium')
        new_status = input(f"Status [{task.get('status', 'Pending')}]: ") or task.get('status', 'Pending')
        task.update({
            'task': new_name,
            'category': new_cat,
            'due': new_due,
            'priority': new_priority if new_priority in PRIORITY_EMOJIS else "Medium",
            'status': new_status if new_status in STATUS_COLORS else "Pending"
        })
        save_tasks(tasks)
        play_sound()
        print(theme["success"] + "✏️ Task updated!")
    else:
        print(theme["error"] + "Invalid task number.")

# 📤 Export to CSV
def export_to_csv(tasks):
    transition("Exporting to CSV")
    with open('tasks_export.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Task', 'Category', 'Due Date', 'Priority', 'Status'])
        for task in tasks:
            writer.writerow([
                task['task'],
                task['category'],
                task['due'],
                task.get('priority', 'Medium'),
                task.get('status', 'Pending')
            ])
    play_sound()
    print(theme["success"] + "📁 Exported to tasks_export.csv")

# 🔍 Search Task
def search_tasks(tasks):
    keyword = input("Enter keyword to search: ").lower()
    results = [t for t in tasks if keyword in t['task'].lower()]
    transition("Searching")
    show_tasks(results)

# 🗃️ Filter by Category
def filter_by_category(tasks):
    category = input("Enter category to filter (Work/Personal/Other): ").capitalize()
    results = [t for t in tasks if t['category'].capitalize() == category]
    transition("Filtering")
    show_tasks(results)

# 📊 Show Statistics
def show_stats(tasks):
    total = len(tasks)
    completed = sum(1 for t in tasks if t.get('status') == "Completed")
    pending = sum(1 for t in tasks if t.get('status', 'Pending') == "Pending")
    in_progress = sum(1 for t in tasks if t.get('status') == "In-Progress")
    overdue = 0
    today = datetime.now().date()
    for t in tasks:
        try:
            due = datetime.strptime(t['due'], "%Y-%m-%d").date()
            if t.get('status') != "Completed" and due < today:
                overdue += 1
        except:
            pass
    print(theme["info"] + f"Total: {total} | Completed: {completed} | Pending: {pending} | In-Progress: {in_progress} | Overdue: {overdue}")

# 🔄 Sort Tasks
def sort_tasks(tasks):
    print("Sort by: 1. Due Date  2. Priority  3. Status")
    opt = input("Choose option: ")
    if opt == '1':
        tasks.sort(key=lambda t: t['due'])
    elif opt == '2':
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        tasks.sort(key=lambda t: priority_order.get(t.get('priority', 'Medium'), 1))
    elif opt == '3':
        status_order = {"Pending": 0, "In-Progress": 1, "Completed": 2}
        tasks.sort(key=lambda t: status_order.get(t.get('status', 'Pending'), 0))
    save_tasks(tasks)
    print(theme["success"] + "Tasks sorted!")
    show_tasks(tasks)

# ⏪ Undo Last Action
def undo_last_action(tasks):
    global last_action, last_task, last_task_index
    if last_action == "delete" and last_task is not None:
        tasks.insert(last_task_index, last_task)
        save_tasks(tasks)
        print(theme["success"] + "Undo successful: Task restored.")
    elif last_action == "complete" and last_task is not None:
        tasks[last_task_index]['status'] = last_task.get('status', 'Pending')
        save_tasks(tasks)
        print(theme["success"] + "Undo successful: Task marked as not completed.")
    else:
        print(theme["warning"] + "Nothing to undo.")
    last_action = None
    last_task = None
    last_task_index = None

# 💾 Backup & Restore
def backup_tasks(tasks):
    with open(BACKUP_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)
    print(theme["success"] + f"Backup saved to {BACKUP_FILE}")

def restore_tasks():
    if os.path.exists(BACKUP_FILE):
        with open(BACKUP_FILE, 'r') as f:
            tasks = json.load(f)
        save_tasks(tasks)
        print(theme["success"] + "Tasks restored from backup.")
        return tasks
    else:
        print(theme["error"] + "No backup file found.")
        return load_tasks()

# 📜 View History
def view_history():
    transition("Fetching history")
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            print(theme["primary"] + "\n" + f.read())
    else:
        print(theme["warning"] + "No history found.")

# 🌓 Toggle Theme
def toggle_theme():
    global current_theme, theme
    current_theme = "dark" if current_theme == "light" else "light"
    theme = THEMES[current_theme]
    print(theme["info"] + f"Theme switched to {current_theme.upper()} mode.")

# 💡 Main
def main():
    tasks = load_tasks()
    print(theme["info"] + random.choice(QUOTES))

    while True:
        print(theme["primary"] + "\n--- 📘 To-Do List Menu ---")
        print("1. View Tasks")
        print("2. Add Task")
        print("3. Delete Task")
        print("4. Complete Task")
        print("5. Edit Task")
        print("6. Export to CSV")
        print("7. Search Tasks")
        print("8. Filter by Category")
        print("9. Show Statistics")
        print("10. Sort Tasks")
        print("11. Undo Last Action")
        print("12. Backup Tasks")
        print("13. Restore Tasks")
        print("14. View History")
        print("15. Toggle Theme (Dark/Light)")
        print("16. Exit")

        choice = input("Choose an option: ")

        if choice == '1':
            transition("Displaying tasks")
            show_tasks(tasks)
        elif choice == '2':
            add_task(tasks)
        elif choice == '3':
            delete_task(tasks)
        elif choice == '4':
            complete_task(tasks)
        elif choice == '5':
            edit_task(tasks)
        elif choice == '6':
            export_to_csv(tasks)
        elif choice == '7':
            search_tasks(tasks)
        elif choice == '8':
            filter_by_category(tasks)
        elif choice == '9':
            show_stats(tasks)
        elif choice == '10':
            sort_tasks(tasks)
        elif choice == '11':
            undo_last_action(tasks)
        elif choice == '12':
            backup_tasks(tasks)
        elif choice == '13':
            tasks = restore_tasks()
        elif choice == '14':
            view_history()
        elif choice == '15':
            toggle_theme()
        elif choice == '16':
            transition("Exiting")
            print(theme["warning"] + "Goodbye! Stay productive ✨")
            break
        else:
            print(theme["error"] + "Invalid choice. Try again.")

if __name__ == '__main__':
    main()