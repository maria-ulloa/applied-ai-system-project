from dataclasses import dataclass, field
from typing import List


@dataclass
class Task:
    task_name: str
    category: str
    priority_level: int
    duration: float
    is_completed: bool = False

    def complete_task(self):
        pass

    def get_details(self) -> dict:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def get_tasks(self) -> List[Task]:
        pass

    def update_details(self, details: dict):
        pass

# The below classes are not dataclasses because they have more complex behavior such as attributes that get modified over time. 
class User:
    def __init__(self, username: str, daily_availability: str):
        self.username = username
        self.pets: List[Pet] = []
        self.daily_availability = daily_availability

    def add_pet(self, pet: Pet):
        pass

    def set_availability(self, availability: str):
        pass


class Manager:
    def __init__(self, user: User, total_time_limit: float):
        self.user = user
        self.final_schedule: List[Task] = []
        self.total_time_limit = total_time_limit

    def generate_plan(self) -> List[Task]:
        pass

    def get_reasoning(self) -> str:
        pass
