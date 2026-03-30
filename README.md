# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

### Smarter Scheduling

The basic schedule generator had a few errors that would cause conflict with the user when they want their realistic pet care plan for the day. I added five algorithmic methods `pawpal_system.py` to make the app more useful for a real pet owner. The first method `Task.complete_task()` archives the old completed task and generates a new one. Python's `timedelta` calculates the next due date and returns a completely new `Task` instance. Daily tasks roll over by 1 day and weekly tasks by 7 days, which makes it easier for the user since they don't have to manually reenter a reoccuring task. Additionally, the second method `Manager.complete_task()` finds the specific task across all the pets, triggers the new date, and appends the next occurence back to the pet's list right away. The date math can be found in the `Task` class and the list is managed wihin `Manager` class, so the code is a bit cleaner. The third method `Manager.sort_by_time()` provides the user with options, either all pending tasks are sorted by `duration` (shortest first, which is great for getting more quick tasks done) or by `time_str`(clock order, which is great for planning the day). For the clock sorting, the method takes care of the conversion of the "HH:MM" strings into total minutes so the sorting is numerically correct. The fourth methood I added is `Manager.filter_tasks()` lets the user filter tasks across pets by pet name, completion status, or both. If a user just wants to see the pending tasks for one of their pets, they can easily access that information without having to loop through all their other pets information. The last method I added is `Manager.detect_conflicts()` which uses a `defaultdict` to group tasks by their scheduled time. If there are multiple tasks that are fighting for the same time slot, the app gives a warning string that notifies the user of the conflict detected. I did make sure that it skips tasks with no time associated with it ("00:00") and never crashes. Even with this case, it always returns a list of warnings (even if it is empty) that the user can view and understand.

### Testing PawPal+

- Command to run tests: python3 -m pytest

- To ensure that the Manager logic and functionality works as it is supposed to, AI and I wrote three tests that cover three different areas of edge cases which allows the user to use the pet care app more efficiently. To make sure the tasks were being returned in chronological order, I tested the `sort_by_time` method by giving it three tasks completely out of order (evening, then morning, then afternoon). The Manager correctly converts the "HH:MM" strings to total minutes and calculates them correctly to return them in a correct and reasonable list (earliest to latest). To make sure there is a new task created the following day after a daily task is completed, I tested the `Manager.complete_task` method using timedelta. When a daily or weekly task is completed, the Manager should know to archive that task and generate a new one so it can be used consistently without manual reenter. The test confirms the original task is done and a new one is now waiting in the pet's list. To ensure the Manager can detect and flag duplicate set times for a task, I tested the `detect_conflicts` method. There are two different pets created (Buddy and Whiskers) and both have a task assigned to them at 09:00. The test makes sure the method detects this overlap in tasks and issues a warnig to the user with the names of both the pets and the time slot so the user knows the pets can't be in two places at once.

- I would definitely give this 4/5 stars on confidence level in the system's reliability. I tested some of the core logic in Manager and throughout the classes and fortunately all the tests passed. However, I know that there is always room for improvement meaning there may be more complex edge cases that I am not considering right now. The system will not be perfect, but with the scenarios and cases I did check, I know that it will at least work in those environments.