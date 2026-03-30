from datetime import date, timedelta

from pawpal_system import Manager, Pet, Task, User


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


def test_sort_by_time():
    # CONDITION CHECKED: Tasks are returned in chronological order.
    #
    # We give the scheduler three tasks intentionally out of order
    # (evening first, then morning, then afternoon). After sorting,
    # the list must come back earliest-to-latest by clock time.
    pet = Pet(name="Buddy", species="Dog", age=4)
    pet.tasks = [
        Task(task_name="Evening Walk",   category="Exercise", priority_level=2, duration=0.5,  frequency="Daily", time_str="18:00"),
        Task(task_name="Morning Feed",   category="Feeding",  priority_level=5, duration=0.25, frequency="Daily", time_str="07:00"),
        Task(task_name="Afternoon Meds", category="Health",   priority_level=4, duration=0.1,  frequency="Daily", time_str="13:00"),
    ]
    user = User(username="Alex", daily_availability=8.0)
    user.add_pet(pet)
    manager = Manager(user)

    sorted_tasks = manager.sort_by_time("time_str")

    # Pull out just the time strings so the assert is easy to read.
    times = [t.time_str for t in sorted_tasks]
    # CONDITION: The times must be in ascending (earliest-first) order.
    assert times == ["07:00", "13:00", "18:00"]


def test_daily_recurrence():
    # CONDITION CHECKED: Marking a daily task complete creates a new task for the following day.
    #
    # We start with one task due today. After completing it, the scheduler
    # should automatically create a follow-up task due tomorrow.
    today = date.today()
    pet = Pet(name="Whiskers", species="Cat", age=2)
    pet.tasks = [
        Task(task_name="Morning Feed", category="Feeding", priority_level=5,
             duration=0.25, frequency="Daily", due_date=today),
    ]
    user = User(username="Alex", daily_availability=8.0)
    user.add_pet(pet)
    manager = Manager(user)

    next_task = manager.complete_task("Whiskers", "Morning Feed")

    # CONDITION: The original task is now marked as done.
    assert pet.tasks[0].is_completed is True
    # CONDITION: A new follow-up task was returned (not None).
    assert next_task is not None
    # CONDITION: The new task was added to the pet's task list (now 2 total).
    assert len(pet.tasks) == 2
    # CONDITION: The new task is due exactly one day after the original.
    assert next_task.due_date == today + timedelta(days=1)


def test_conflict_detection():
    # CONDITION CHECKED: The scheduler flags duplicate times across pets.
    #
    # Two pets both have a task at 09:00. detect_conflicts() should catch
    # this overlap and return a warning that names both pets and the time.
    pet1 = Pet(name="Buddy",    species="Dog", age=4)
    pet2 = Pet(name="Whiskers", species="Cat", age=2)
    pet1.tasks = [Task(task_name="Morning Feed", category="Feeding", priority_level=5, duration=0.25, frequency="Daily", time_str="09:00")]
    pet2.tasks = [Task(task_name="Morning Feed", category="Feeding", priority_level=5, duration=0.25, frequency="Daily", time_str="09:00")]

    user = User(username="Alex", daily_availability=8.0)
    user.add_pet(pet1)
    user.add_pet(pet2)
    manager = Manager(user)

    warnings = manager.detect_conflicts()

    # CONDITION: Exactly one conflict was detected (one shared time slot).
    assert len(warnings) == 1
    # CONDITION: The warning message includes the conflicting time.
    assert "09:00"    in warnings[0]
    # CONDITION: The warning message names both pets involved in the conflict.
    assert "Buddy"    in warnings[0]
    assert "Whiskers" in warnings[0]
