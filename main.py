from pawpal_system import Task, Pet, User, Manager

owner = User(username="Maria", daily_availability=4.0)

ginger = Pet(name="Ginger", species="Cat", age=9)
miko = Pet(name="Miko", species="Dog", age=3)

# Tasks added intentionally out of order (time_str shuffled)
ginger.tasks.append(Task(task_name="Playtime", category="Exercise", priority_level=4, duration=1.0, frequency="Daily", time_str="15:00"))
ginger.tasks.append(Task(task_name="Clean Litter Box",category="Hygiene",  priority_level=6, duration=0.25, frequency="Daily", time_str="08:00"))
ginger.tasks.append(Task(task_name="Feed Ginger", category="Feeding",  priority_level=5, duration=0.25, frequency="Twice Daily", time_str="19:30"))
ginger.tasks.append(Task(task_name="Morning Walk", category="Exercise", priority_level=3, duration=0.5,  frequency="Daily", time_str="07:00"))

miko.tasks.append(Task(task_name="Feed Miko", category="Feeding",  priority_level=5, duration=0.25, frequency="Twice Daily", time_str="18:00"))
miko.tasks.append(Task(task_name="Evening Walk", category="Exercise", priority_level=3, duration=0.5, frequency="Daily", time_str="17:00"))
miko.tasks.append(Task(task_name="Bath Time", category="Hygiene",  priority_level=2, duration=0.75, frequency="Weekly", time_str="08:00"))  # conflicts with Ginger's Clean Litter Box

owner.add_pet(ginger)
owner.add_pet(miko)

manager = Manager(user=owner)

manager.generate_plan()
print("\nPAWPAL+ TODAY'S SCHEDULE")
print(manager.get_reasoning())

#sort_by_time: sorted by duration (shortest first)
print("\nSORTED BY DURATION (shortest first)")
for t in manager.sort_by_time(by="duration"):
    print(f" {t.task_name:<20} {t.duration}h")

#sort_by_time: sorted by scheduled time (HH:MM)
print("\nSORTED BY TIME OF DAY (HH:MM)")
for t in manager.sort_by_time(by="time_str"):
    print(f" {t.time_str} {t.task_name}")

#filter_tasks: only pending tasks 
print("\nPENDING TASKS (all pets)")
for t in manager.filter_tasks(completed=False):
    print(f" [ ] {t.task_name}")

#filter_tasks: only Ginger's tasks 
print("\nALL TASKS FOR GINGER")
for t in manager.filter_tasks(pet_name="Ginger"):
    status = "done" if t.is_completed else "pending"
    print(f" {t.task_name:<20} [{status}]")

#filter_tasks: only Miko's pending tasks
print("\nPENDING TASKS FOR MIKO")
for t in manager.filter_tasks(completed=False, pet_name="Miko"):
    print(f" {t.task_name}")

print("\nCONFLICT DETECTION")
conflicts = manager.detect_conflicts()
if conflicts:
    for w in conflicts:
        print(f"{w}")
else:
    print(" No scheduling conflicts found.")
