import flet as ft
import json
import os
import time

class Task:
    def __init__(self, text, due_date=None, priority=None):
        self.text = text
        self.due_date = due_date
        self.priority = priority
        self.completed = False

    def to_dict(self):
        return {
            "text": self.text,
            "due_date": self.due_date,
            "priority": self.priority,
            "completed": self.completed,
        }

    @staticmethod
    def from_dict(data):
        task = Task(data["text"], data["due_date"], data["priority"])
        task.completed = data["completed"]
        return task

class SignUpPage(ft.Column):
    def __init__(self, page):
        super().__init__()
        self.page = page

        self.username = ft.TextField(hint_text="Enter username", expand=True, bgcolor="white")
        self.password = ft.TextField(hint_text="Enter password", expand=True, password=True, bgcolor="white")
        self.error_message = ft.Text(value="", color="red")

        self.controls = [
            ft.Text("Sign Up", size=24, weight="bold"),
            self.username,
            self.password,
            ft.ElevatedButton(text="Sign Up", on_click=self.sign_up, bgcolor="#4caf50"),
            ft.TextButton(text="Already have an account? Log in", on_click=self.switch_to_login),
            self.error_message,
        ]

    def sign_up(self, e):
        username = self.username.value
        password = self.password.value

        if not username or not password:
            self.error_message.value = "Please fill in all fields."
            self.update()
            return

        users = self.load_users()

        if username in users:
            self.error_message.value = "Username already exists."
        else:
            users[username] = password
            self.save_users(users)
            self.page.controls.clear()
            self.page.add(LoginPage(self.page))
        self.update()

    def switch_to_login(self, e):
        self.page.controls.clear()
        self.page.add(LoginPage(self.page))
        self.page.update()

    @staticmethod
    def load_users():
        if os.path.exists("users.json"):
            with open("users.json", "r") as f:
                return json.load(f)
        return {}

    @staticmethod
    def save_users(users):
        with open("users.json", "w") as f:
            json.dump(users, f)

class LoginPage(ft.Column):
    def __init__(self, page):
        super().__init__()
        self.page = page

        self.username = ft.TextField(hint_text="Enter username", expand=True, bgcolor="white")
        self.password = ft.TextField(hint_text="Enter password", expand=True, password=True, bgcolor="white")
        self.error_message = ft.Text(value="", color="red")

        self.controls = [
            ft.Text("Log In", size=24, weight="bold"),
            self.username,
            self.password,
            ft.ElevatedButton(text="Log In", on_click=self.log_in, bgcolor="#4caf50"),
            ft.TextButton(text="Don't have an account? Sign up", on_click=self.switch_to_signup),
            self.error_message,
        ]

    def log_in(self, e):
        username = self.username.value
        password = self.password.value

        users = SignUpPage.load_users()

        if username in users and users[username] == password:
            self.page.controls.clear()
            self.page.add(TodoApp(self.page))
        else:
            self.error_message.value = "Invalid username or password."
        self.update()

    def switch_to_signup(self, e):
        self.page.controls.clear()
        self.page.add(SignUpPage(self.page))
        self.page.update()

class TodoApp(ft.Column):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.bg_color = "#E2725B"
        self.text_color = "#D552E4"
        self.button_color = "#4caf50"
        self.completed_color = "#b0bec5"

        self.new_task = ft.TextField(hint_text="What is your task?", expand=True, bgcolor="white", border_color=self.text_color)
        self.due_date = ft.TextField(hint_text=" (DD-MM-YYYY)", expand=True, bgcolor="white", border_color=self.text_color)
        self.priority = ft.Dropdown(
            options=[
                ft.dropdown.Option(text="Low"),
                ft.dropdown.Option(text="Medium"),
                ft.dropdown.Option(text="High"),
            ],
            bgcolor="white",
            border_color=self.text_color,
        )
        self.tasks_view = ft.Column()

        self.width = 600
        self.controls = [
            ft.Row(
                controls=[
                    self.new_task,
                    ft.FloatingActionButton(icon=ft.icons.ADD, on_click=self.add_clicked, bgcolor=self.button_color),
                ],
            ),
            ft.Row(
                controls=[
                    ft.Text("Due Date:", color=self.text_color),
                    self.due_date,
                ],
            ),
            ft.Row(
                controls=[
                    ft.Text("Priority:", color=self.text_color),
                    self.priority,
                ],
            ),
            ft.Row(
                controls=[
                    ft.ElevatedButton(text="Timer", on_click=self.open_timer_page, bgcolor=self.button_color),
                    ft.ElevatedButton(text="Schedule", on_click=self.open_schedule_page, bgcolor=self.button_color),
                ]
            ),
            self.tasks_view,
        ]

        self.load_tasks()

    def add_clicked(self, e):
        task = Task(self.new_task.value, self.due_date.value, self.priority.value)
        self.tasks_view.controls.append(
            self.create_task_control(task)
        )
        self.new_task.value = ""
        self.due_date.value = ""
        self.priority.value = None
        self.update()
        self.save_tasks()

        if task.due_date:
            self.schedule_notification(task)

    def create_task_control(self, task):
        priority_label = f"[{task.priority} Priority]" if task.priority else ""
        checkbox_label = f"{task.text} {priority_label} (Due: {task.due_date})"

        return ft.Column(
            controls=[
                ft.Checkbox(
                    label=checkbox_label,
                    on_change=self.task_completed,
                    check_color=self.button_color,
                    value=task.completed
                ),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(text="Delete", on_click=lambda event, t=task: self.delete_task(event, t), bgcolor="#d32f2f", color="white"),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
            data=task,
        )

    def load_tasks(self):
        if os.path.exists("tasks.json"):
            with open("tasks.json", "r") as f:
                tasks_data = json.load(f)
                for task_data in tasks_data:
                    task = Task.from_dict(task_data)
                    self.tasks_view.controls.append(self.create_task_control(task))

    def save_tasks(self):
        tasks = [control.data.to_dict() for control in self.tasks_view.controls]
        with open("tasks.json", "w") as f:
            json.dump(tasks, f)

    def task_completed(self, e):
        if e.control.data:
            e.control.data.completed = not e.control.data.completed
            e.control.label = f"[X] {e.control.label}" if e.control.data.completed else e.control.label.replace("[X] ", "")
            e.control.disabled = e.control.data.completed
            e.control.label_style = ft.TextStyle(color=self.completed_color) if e.control.data.completed else None
            self.save_tasks()
            self.update()

    def delete_task(self, e, task):
        self.tasks_view.controls = [control for control in self.tasks_view.controls if control.data != task]
        self.save_tasks()
        self.update()


    def open_timer_page(self, e):
        self.page.add(TimerPage(self.page))

    def open_schedule_page(self, e):
        self.page.add(SchedulePage(self.page))

class TimerPage(ft.Column):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.bg_color = "#e0f7fa"

        self.timer_input = ft.TextField(hint_text="Enter time in minutes", expand=True, bgcolor="white")
        self.timer_output = ft.Text("", color="#00796b")

        self.controls = [
            ft.Text("Set Timer (in minutes):", color="#00796b"),
            self.timer_input,
            ft.ElevatedButton(text="Start Timer", on_click=self.start_timer, bgcolor="#4caf50"),
            self.timer_output,
            ft.ElevatedButton(text="Back to To-Do List", on_click=self.back_to_todo, bgcolor="#757575"),
        ]

    def start_timer(self, e):
        try:
            minutes = int(self.timer_input.value)
            seconds = minutes * 60
            self.timer_output.value = f"Timer started for {minutes} minutes..."
            self.update()
            for i in range(seconds, 0, -1):
                time.sleep(1)
                self.timer_output.value = f"Time left: {i // 60} minutes {i % 60} seconds..."
                self.update()
            self.timer_output.value = "Time's up!"
            self.update()
        except ValueError:
            self.timer_output.value = "Please enter a valid number."
            self.update()

    def back_to_todo(self, e):
        self.page.controls.clear()
        self.page.add(TodoApp(self.page))
        self.page.update()

class SchedulePage(ft.Column):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.bg_color = "#e0f7fa"

        self.schedule_input = ft.TextField(hint_text="Enter your schedule details", expand=True, bgcolor="white")
        self.schedule_output = ft.Column()

        self.load_schedule()

        self.controls = [
            ft.Text("Create Your Schedule:", color="#00796b"),
            self.schedule_input,
            ft.ElevatedButton(text="Add to Schedule", on_click=self.add_schedule, bgcolor="#4caf50"),
            self.schedule_output,
            ft.ElevatedButton(text="Back to To-Do List", on_click=self.back_to_todo, bgcolor="#757575"),
        ]

    def load_schedule(self):
        if os.path.exists("schedule.json"):
            with open("schedule.json", "r") as f:
                schedule_data = json.load(f)
                for item in schedule_data:
                    self.schedule_output.controls.append(ft.Text(item, color="#00796b"))

    def add_schedule(self, e):
        if self.schedule_input.value:
            self.schedule_output.controls.append(ft.Text(self.schedule_input.value, color="#00796b"))
            self.save_schedule()
            self.schedule_input.value = ""
            self.update()

    def save_schedule(self):
        schedule = [control.value for control in self.schedule_output.controls]
        with open("schedule.json", "w") as f:
            json.dump(schedule, f)

    def back_to_todo(self, e):
        self.page.controls.clear()
        self.page.add(TodoApp(self.page))
        self.page.update()
def main(page: ft.Page):
    page.title = "Student To-Do App"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = "#b3e5fc"

    # Start with LoginPage
    login_page = LoginPage(page)
    page.add(login_page)
    page.update()

ft.app(main)