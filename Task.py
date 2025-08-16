import streamlit as st
from datetime import date
import json
import os

# Assuming file_handler.py exists with the FileHandler class as provided
# If you don't have it, you can define it directly in this script.
# For simplicity, I've defined a simple one here.
class FileHandler:
    def __init__(self, filename):
        self.filename = filename

    def save_data(self, data):
        """Saves a list of dictionaries to a JSON file."""
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=4)
    
    def load_data(self):
        """Loads data from a JSON file and returns a list of dictionaries."""
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

# --- Your original Task classes ---
class Task:
    def __init__(self, name, description, status, due_date, reminder_duration=None):
        self.name = name
        self.description = description
        self.status = status
        self.due_date = due_date
        self.reminder_duration = reminder_duration
        self.created_date = date.today().strftime('%Y-%m-%d')

    def display_details(self):
        # We'll adapt this for Streamlit output
        pass
    
    def to_dict(self):
        return {
            "type": "Task",
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "due_date": self.due_date.strftime('%Y-%m-%d'),
            "reminder_duration": self.reminder_duration,
            "created_date": self.created_date
        }

class WorkTask(Task):
    def __init__(self, name, description, status, due_date, priority, reminder_duration=None):
        super().__init__(name, description, status, due_date, reminder_duration)
        self.priority = priority

    def display_details(self):
        # Adapted for Streamlit
        pass

    def to_dict(self):
        data = super().to_dict()
        data["priority"] = self.priority
        data["type"] = "WorkTask"
        return data

class PersonalTask(Task):
    def __init__(self, name, description, status, due_date, category, reminder_duration=None):
        super().__init__(name, description, status, due_date, reminder_duration)
        self.category = category
    
    def display_details(self):
        # Adapted for Streamlit
        pass
    
    def to_dict(self):
        data = super().to_dict()
        data["category"] = self.category
        data["type"] = "PersonalTask"
        return data

def create_task_from_dict(task_dict):
    """Helper function to create a Task object from a dictionary."""
    task_type = task_dict.get("type", "Task")
    due_date = date.fromisoformat(task_dict['due_date'])
    
    if task_type == "WorkTask":
        return WorkTask(
            task_dict['name'], task_dict['description'], task_dict['status'],
            due_date, task_dict['priority'], task_dict.get('reminder_duration')
        )
    elif task_type == "PersonalTask":
        return PersonalTask(
            task_dict['name'], task_dict['description'], task_dict['status'],
            due_date, task_dict['category'], task_dict.get('reminder_duration')
        )
    else:
        return Task(
            task_dict['name'], task_dict['description'], task_dict['status'],
            due_date, task_dict.get('reminder_duration')
        )

class TaskManager:
    def __init__(self):
        self.tasks = []
        self.file_handler = FileHandler("tasks.json")
        self.load_tasks()

    def add_task(self, task_object):
        self.tasks.append(task_object)
        self.save_tasks()

    def delete_task(self, task_name):
        initial_count = len(self.tasks)
        self.tasks = [task for task in self.tasks if task.name != task_name]
        if len(self.tasks) < initial_count:
            self.save_tasks()
            return True
        return False

    def complete_task(self, task_name):
        for task in self.tasks:
            if task.name == task_name:
                task.status = "Complete"
                self.save_tasks()
                return True
        return False

    def save_tasks(self):
        data_to_save = [task.to_dict() for task in self.tasks]
        self.file_handler.save_data(data_to_save)
    
    def load_tasks(self):
        loaded_dicts = self.file_handler.load_data()
        if loaded_dicts:
            self.tasks = [create_task_from_dict(d) for d in loaded_dicts]

# --- Streamlit UI Code ---

# Initialize the session state for tasks if it doesn't exist
if 'task_manager' not in st.session_state:
    st.session_state.task_manager = TaskManager()

st.set_page_config(
    page_title="Task Management System",
    page_icon="✅",
    layout="wide"
)

# App Title
st.title("✅ My Task Manager")
st.markdown("---")

# Main content area
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Add a New Task")
    with st.form("task_form"):
        task_type = st.radio("Task Type", ("Work Task", "Personal Task"))
        name = st.text_input("Task Name", key="name")
        description = st.text_area("Description", key="description")
        due_date = st.date_input("Due Date", min_value=date.today())
        
        status_options = ["Pending", "In-Progress", "Complete"]
        status = st.selectbox("Status", status_options)

        if task_type == "Work Task":
            priority = st.text_input("Priority (e.g., High, Low)")
            reminder_duration = st.number_input("Reminder (days before due)", min_value=0, value=0)
            submitted = st.form_submit_button("Add Work Task")
            if submitted and name:
                new_task = WorkTask(name, description, status, due_date, priority, reminder_duration)
                st.session_state.task_manager.add_task(new_task)
                st.success(f"Work Task '{name}' added successfully!")
        
        elif task_type == "Personal Task":
            category = st.text_input("Category (e.g., Quick_task, Hobby)")
            reminder_duration = st.number_input("Reminder (days before due)", min_value=0, value=0)
            submitted = st.form_submit_button("Add Personal Task")
            if submitted and name:
                new_task = PersonalTask(name, description, status, due_date, category, reminder_duration)
                st.session_state.task_manager.add_task(new_task)
                st.success(f"Personal Task '{name}' added successfully!")

with col2:
    st.header("Your Task List")
    manager = st.session_state.task_manager
    tasks = manager.tasks
    
    if not tasks:
        st.info("No tasks found. Add a new task on the left.")
    else:
        for i, task in enumerate(tasks):
            with st.expander(f"**{i+1}. {task.name}** ({task.status})"):
                st.markdown(f"**Description:** {task.description}")
                st.markdown(f"**Due Date:** {task.due_date.strftime('%Y-%m-%d')}")
                st.markdown(f"**Days Remaining:** {(task.due_date - date.today()).days}")
                st.markdown(f"**Created On:** {task.created_date}")
                if task.reminder_duration:
                    st.markdown(f"**Reminder:** {task.reminder_duration} days before due date.")
                
                # Display specific attributes for subclasses
                if isinstance(task, WorkTask):
                    st.markdown(f"**Priority:** {task.priority}")
                elif isinstance(task, PersonalTask):
                    st.markdown(f"**Category:** {task.category}")

                # Action buttons for each task
                task_col1, task_col2 = st.columns(2)
                with task_col1:
                    if st.button("Mark as Complete", key=f"complete_{i}"):
                        if manager.complete_task(task.name):
                            st.experimental_rerun()
                        else:
                            st.error(f"Failed to mark task '{task.name}' as complete.")
                with task_col2:
                    if st.button("Delete Task", key=f"delete_{i}"):
                        if manager.delete_task(task.name):
                            st.experimental_rerun()
                        else:
                            st.error(f"Failed to delete task '{task.name}'.")

# To run this Streamlit app, save the code as a Python file (e.g., `app.py`)
# and run the following command in your terminal:
# `streamlit run app.py`
