from pawpal_system import Task, Pet, User, Manager

owner = User(username="Maria", daily_availability=2.0)

ginger = Pet(name="Ginger", species="Cat", age=9)
miko = Pet(name="Miko", species="Dog", age=3)

ginger.tasks.append(Task(task_name="Morning Walk", category="Exercise", priority_level=3, duration=0.5, frequency="Daily"))
ginger.tasks.append(Task(task_name="Feed Ginger", category="Feeding", priority_level=5, duration=0.25, frequency="Twice Daily"))

miko.tasks.append(Task(task_name="Evening Walk", category="Exercise", priority_level=3, duration=0.5, frequency="Daily"))
miko.tasks.append(Task(task_name="Feed Miko", category="Feeding", priority_level=5, duration=0.25, frequency="Twice Daily"))

ginger.tasks.append(Task(task_name="Clean Litter Box", category="Hygiene",   priority_level=6, duration=0.25, frequency="Daily"))
ginger.tasks.append(Task(task_name="Feed Ginger", category="Feeding",   priority_level=5, duration=0.25, frequency="Twice Daily"))
ginger.tasks.append(Task(task_name="Playtime", category="Exercise",  priority_level=4, duration=1.0,  frequency="Daily"))

owner.add_pet(ginger)
owner.add_pet(miko)

manager = Manager(user=owner)
manager.generate_plan()

print("PAWPAL+ TODAY'S SCHEDULE")
print(manager.get_reasoning())
