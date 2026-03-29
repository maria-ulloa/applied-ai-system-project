from pawpal_system import Task, Pet


def test_complete_task_changes_status():
    task = Task(task_name="Feed Buddy", category="Feeding", priority_level=5, duration=0.25, frequency="Daily")
    assert task.is_completed is False
    task.complete_task()
    assert task.is_completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="Dog", age=4)
    assert len(pet.tasks) == 0
    pet.tasks.append(Task(task_name="Morning Walk", category="Exercise", priority_level=3, duration=0.5, frequency="Daily"))
    assert len(pet.tasks) == 1
