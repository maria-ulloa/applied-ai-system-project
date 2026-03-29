from dataclasses import dataclass, field
from typing import List


@dataclass
class Task:
    task_name: str
    category: str
    priority_level: int
    duration: float
    frequency: str
    is_completed: bool = False

    def complete_task(self):
        """Mark this task as completed."""
        self.is_completed = True

    def get_details(self) -> dict:
        """Return all task attributes as a dictionary."""
        return {
            "task_name": self.task_name,
            "category": self.category,
            "priority_level": self.priority_level,
            "duration": self.duration,
            "frequency": self.frequency,
            "is_completed": self.is_completed,
        }


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def update_details(self, details: dict):
        """Update pet attributes from a dictionary of new values."""
        if "name" in details:
            self.name = details["name"]
        if "species" in details:
            self.species = details["species"]
        if "age" in details:
            self.age = details["age"]


# The below classes are not dataclasses because they have more complex behavior such as attributes that get modified over time.
class User:
    def __init__(self, username: str, daily_availability: float):
        self.username = username
        self.pets: List[Pet] = []
        self.daily_availability = daily_availability

    def add_pet(self, pet: Pet):
        """Add a pet to the owner's list of pets."""
        self.pets.append(pet)

    def set_availability(self, availability: float):
        """Update the owner's daily available hours."""
        self.daily_availability = availability


class Manager:
    def __init__(self, user: User):
        self.user = user
        self.final_schedule: List[Task] = []

# Generate plan function doesn't look at the tasks completed because the user should prioritize the tasks that have not been completed yet.
    def generate_plan(self) -> List[Task]:
        """Build a prioritized schedule of pending tasks that fits within the owner's daily availability."""
        all_tasks = []
        for pet in self.user.pets:
            all_tasks.extend(pet.tasks)

        pending_tasks = [t for t in all_tasks if not t.is_completed]
        pending_tasks.sort(key=lambda t: t.priority_level, reverse=True)

        self.final_schedule = []
        time_used = 0.0
        for task in pending_tasks:
            if time_used + task.duration <= self.user.daily_availability:
                self.final_schedule.append(task)
                time_used += task.duration

        return self.final_schedule

    def get_reasoning(self) -> str:
        """Return a human-readable summary of the scheduled tasks and total time used."""
        if not self.final_schedule:
            return "No tasks have been scheduled yet. Run generate_plan() first."

        lines = [f"Schedule for {self.user.username} ({self.user.daily_availability}h available):"]
        total = 0.0
        for task in self.final_schedule:
            lines.append(f"  - {task.task_name} ({task.duration}h, priority {task.priority_level})")
            total += task.duration
        lines.append(f"Total time: {total}h")
        return "\n".join(lines)
