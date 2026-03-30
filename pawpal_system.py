from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional


@dataclass
class Task:
    task_name: str
    category: str
    priority_level: int
    duration: float
    frequency: str
    time_str: str = "00:00"  # optional HH:MM schedule time
    due_date: date = field(default_factory=date.today)
    is_completed: bool = False

    # Maps each frequency label to the timedelta until the next occurrence.
    _RECURRENCE: dict = field(default_factory=lambda: {
        "Daily":       timedelta(days=1),
        "Twice Daily": timedelta(days=1),
        "Weekly":      timedelta(weeks=1),
    })

    def complete_task(self) -> Optional["Task"]:
        """Mark this task as completed and return a new Task for the next occurrence.

        Returns:
            A new Task with due_date advanced by the frequency interval,
            or None if the frequency has no recurrence pattern defined.
        """
        self.is_completed = True
        delta = self._RECURRENCE.get(self.frequency)
        if delta is None:
            return None
        return Task(
            task_name=self.task_name,
            category=self.category,
            priority_level=self.priority_level,
            duration=self.duration,
            frequency=self.frequency,
            time_str=self.time_str,
            due_date=self.due_date + delta,
        )

    def get_details(self) -> dict:
        """Return all task attributes as a dictionary."""
        return {
            "task_name": self.task_name,
            "category": self.category,
            "priority_level": self.priority_level,
            "duration": self.duration,
            "frequency": self.frequency,
            "time_str": self.time_str,
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

    def sort_by_time(self, by: str = "duration") -> List[Task]:
        """Return all pending tasks sorted by a time attribute.

        Args:
            by: Sort key — "duration" sorts by numeric hours (shortest first),
                "time_str" sorts by scheduled clock time in HH:MM format.

        Raises:
            ValueError: If an unsupported sort key is passed.
        """
        all_tasks = []
        for pet in self.user.pets:
            all_tasks.extend(pet.tasks)

        pending = [t for t in all_tasks if not t.is_completed]

        def _to_minutes(time_hm: str) -> int:
            hours, minutes = time_hm.split(":")
            return int(hours) * 60 + int(minutes)

        if by == "duration":
            key_fn = lambda t: t.duration
        elif by == "time_str":
            key_fn = lambda t: _to_minutes(t.time_str)
        else:
            raise ValueError(f"Unsupported sort key: {by}")

        return sorted(pending, key=key_fn)

    def complete_task(self, pet_name: str, task_name: str) -> Optional[Task]:
        """Mark a task complete and automatically schedule its next occurrence.

        Finds the first matching pending task for the given pet, marks it done,
        and appends a new Task with the next due_date to that pet's task list.

        Args:
            pet_name:  Name of the pet whose task should be completed.
            task_name: Name of the task to complete (case-insensitive).

        Returns:
            The newly created next-occurrence Task, or None if no recurrence applies
            or the task could not be found.
        """
        for pet in self.user.pets:
            if pet.name.lower() != pet_name.lower():
                continue
            for task in pet.tasks:
                if task.task_name.lower() == task_name.lower() and not task.is_completed:
                    next_task = task.complete_task()
                    if next_task is not None:
                        pet.tasks.append(next_task)
                    return next_task
        return None

    def filter_tasks(self, completed: bool = None, pet_name: str = None) -> List[Task]:
        """Filter tasks across all pets by completion status and/or pet name.

        Args:
            completed: True = only completed, False = only pending, None = both.
            pet_name:  Pet name to restrict results to, or None for all pets.
        """
        results = []
        for pet in self.user.pets:
            if pet_name is not None and pet.name.lower() != pet_name.lower():
                continue
            for task in pet.tasks:
                if completed is not None and task.is_completed != completed:
                    continue
                results.append(task)
        return results

    def detect_conflicts(self) -> List[str]:
        """Check for tasks across all pets scheduled at the same time.

        Skips tasks with no explicit time set (time_str == "00:00").
        Returns a list of warning strings, one per conflicting time slot.
        """
        slots = defaultdict(list)
        for pet in self.user.pets:
            for task in pet.tasks:
                if not task.is_completed and task.time_str != "00:00":
                    slots[task.time_str].append((pet.name, task.task_name))

        return [
            f"WARNING: Conflict at {time_str} -> " + ", ".join(f"{p}: {t}" for p, t in entries)
            for time_str, entries in slots.items()
            if len(entries) > 1
        ]

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
