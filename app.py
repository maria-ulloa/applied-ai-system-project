import streamlit as st
from pawpal_system import User, Pet, Task, Manager
# Updated to import the new functions we added to ai_engine.py
from ai_engine import evaluate_checkin, answer_health_question

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

PRIORITY_MAP = {"Low": 1, "Medium": 3, "High": 5}   # UI string → int (for Task creation)
PRIORITY_LABEL = {1: "Low", 3: "Medium", 5: "High"}  # int → UI string (for display tables)

# --- Owner Setup ---
st.subheader("Owner Setup")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Your name", value="Maria")
with col2:
    daily_hours = st.number_input("Daily availability (hours)", min_value=0.5, max_value=24.0, value=3.0, step=0.5)

if st.button("Set Owner"):
    st.session_state.owner = User(username=owner_name, daily_availability=daily_hours)
    st.session_state.manager = Manager(user=st.session_state.owner)
    st.success(f"Owner set to {owner_name} with {daily_hours}h available.")

if "owner" not in st.session_state:
    st.info("Set your owner profile above to get started.")
    st.stop()

st.divider()

# --- Pet Setup ---
st.subheader("Add a Pet")
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Buddy")
with col2:
    species = st.selectbox("Species", ["Dog", "Cat", "Other"])
with col3:
    age = st.number_input("Age", min_value=0, max_value=30, value=3)

if st.button("Add Pet"):
    new_pet = Pet(name=pet_name, species=species, age=age)
    st.session_state.owner.add_pet(new_pet)  # calls User.add_pet()
    st.success(f"{pet_name} the {species} added!")

if not st.session_state.owner.pets:
    st.info("Add at least one pet above.")
    st.stop()

st.divider()

# --- Task Setup ---
st.subheader("Add a Task")
col1, col2, col3, col4 = st.columns(4)
with col1:
    selected_pet = st.selectbox("For which pet?", [p.name for p in st.session_state.owner.pets])
with col2:
    task_name = st.text_input("Task name", value="Morning walk")
with col3:
    duration_mins = st.number_input("Duration (mins)", min_value=5, max_value=240, value=30)
with col4:
    priority_label = st.selectbox("Priority", ["Low", "Medium", "High"], index=2)

col1, col2, col3 = st.columns(3)
with col1:
    category = st.text_input("Category", value="Exercise")
with col2:
    frequency = st.selectbox("Frequency", ["Daily", "Twice Daily", "Weekly"])
with col3:
    time_str = st.text_input("Scheduled time (HH:MM)", value="00:00",
                             help="Set a clock time to enable conflict detection. Leave 00:00 for unscheduled tasks.")

if st.button("Add Task"):
    pet = next(p for p in st.session_state.owner.pets if p.name == selected_pet)
    pet.tasks.append(Task(
        task_name=task_name,
        category=category,
        priority_level=PRIORITY_MAP[priority_label],
        duration=round(duration_mins / 60, 2),
        frequency=frequency,
        time_str=time_str,
    ))
    st.success(f'"{task_name}" added to {selected_pet}.')

manager: Manager = st.session_state.manager
all_tasks_exist = any(pet.tasks for pet in st.session_state.owner.pets)

if all_tasks_exist:
    st.subheader("Task Overview")

    # Conflict detection — surface warnings before anything else
    conflicts = manager.detect_conflicts()  # calls Manager.detect_conflicts()
    if conflicts:
        st.warning(f"**Scheduling conflicts detected ({len(conflicts)})** — two or more tasks are booked at the same time. Review and reschedule to avoid missing a care window.")
        with st.expander("See conflict details"):
            for conflict in conflicts:
                detail = conflict.replace("WARNING: Conflict at ", "")
                time_slot, tasks_part = detail.split(" -> ", 1)
                st.markdown(f"**{time_slot}** — {tasks_part}")

    # Sort and filter controls
    col1, col2, col3 = st.columns(3)
    with col1:
        sort_by = st.selectbox("Sort tasks by", ["Priority (high → low)", "Duration (short → long)", "Scheduled time"])
    with col2:
        filter_pet = st.selectbox("Filter by pet", ["All pets"] + [p.name for p in st.session_state.owner.pets])
    with col3:
        filter_status = st.selectbox("Filter by status", ["All", "Pending", "Completed"])

    # Resolve filter args
    pet_filter = None if filter_pet == "All pets" else filter_pet
    completed_filter = None if filter_status == "All" else (filter_status == "Completed")

    # Use Manager.filter_tasks() then sort
    filtered = manager.filter_tasks(completed=completed_filter, pet_name=pet_filter)  # calls Manager.filter_tasks()

    if sort_by in ("Duration (short → long)", "Scheduled time"):
        by = "duration" if sort_by == "Duration (short → long)" else "time_str"
        sorted_all = manager.sort_by_time(by=by)  # calls Manager.sort_by_time()
        # sort_by_time returns ALL pending tasks, so use object identity to keep only the filtered ones
        filtered_ids = {id(t) for t in filtered}
        display_tasks = [t for t in sorted_all if id(t) in filtered_ids]
    else:
        # Default: priority high → low (matches generate_plan ordering)
        display_tasks = sorted(filtered, key=lambda t: t.priority_level, reverse=True)

    if display_tasks:
        rows = []
        for t in display_tasks:
            d = t.get_details()  # calls Task.get_details()
            rows.append({
                "Task": d["task_name"],
                "Category": d["category"],
                "Priority": PRIORITY_LABEL.get(d["priority_level"], d["priority_level"]),
                "Duration": f"{int(d['duration'] * 60)} min",
                "Time": d["time_str"] if d["time_str"] != "00:00" else "—",
                "Frequency": d["frequency"],
                "Done": "✓" if d["is_completed"] else "",
            })
        st.table(rows)
    else:
        st.info("No tasks match the current filter.")

    # Inline completion checkboxes (grouped by pet)
    st.markdown("**Mark tasks complete:**")
    for pet in st.session_state.owner.pets:
        pending = [t for t in pet.tasks if not t.is_completed]
        if pending:
            with st.expander(f"{pet.name} — {len(pending)} pending"):
                for task in pending:
                    checked = st.checkbox(task.task_name, value=False, key=f"chk_{pet.name}_{task.task_name}_{id(task)}")
                    if checked:
                        next_task = manager.complete_task(pet.name, task.task_name)  # calls Manager.complete_task()
                        if next_task:
                            st.success(f'"{task.task_name}" done! Next due: {next_task.due_date}')
                        else:
                            st.success(f'"{task.task_name}" marked complete.')
                        st.rerun()

st.divider()

# --- Generate Schedule ---
st.subheader("Today's Schedule")
if st.button("Generate Schedule"):
    schedule = manager.generate_plan()  # calls Manager.generate_plan()

    conflicts = manager.detect_conflicts()
    if conflicts:
        st.warning(f"**{len(conflicts)} scheduling conflict(s) found in your task list.** Resolve them for a smoother day.")

    if schedule:
        st.success(manager.get_reasoning())  # calls Manager.get_reasoning()

        sched_rows = []
        for t in schedule:
            sched_rows.append({
                "Task": t.task_name,
                "Category": t.category,
                "Priority": PRIORITY_LABEL.get(t.priority_level, t.priority_level),
                "Duration": f"{int(t.duration * 60)} min",
                "Time": t.time_str if t.time_str != "00:00" else "—",
            })
        st.table(sched_rows)

        all_pending = manager.filter_tasks(completed=False)  # calls Manager.filter_tasks()
        skipped = [t for t in all_pending if t not in schedule]
        if skipped:
            with st.expander(f"Tasks that didn't fit today ({len(skipped)})"):
                skip_rows = [{"Task": t.task_name, "Duration": f"{int(t.duration * 60)} min",
                              "Priority": PRIORITY_LABEL.get(t.priority_level, t.priority_level)} for t in skipped]
                st.table(skip_rows)
                st.caption("Increase your daily availability to include these tasks.")
    else:
        st.warning("No tasks could be scheduled. Add tasks or increase your daily availability.")

st.divider()

# Set up the look of the daily check in section 
st.subheader("🐾 How did today go? Check in below!")
st.caption("Tell us about your day with your pet and we will let you know how you did!")

# Owner chooses which pet they want to check in about from a dropdown of their pets 
check_in_pet = st.selectbox("Which pet are you checking in about?", [p.name for p in st.session_state.owner.pets], key="checkin_pet")

# Searches for the specific pet the owner selected to check in about and grabs all the information associated with the pet (including the tasks)
selected_pet = next(p for p in st.session_state.owner.pets if p.name == check_in_pet)

# Looks through the tasks for that pet and creates a list of the tasks that were due today that have not been completed yet
pending_tasks = [t.task_name for t in selected_pet.tasks if not t.is_completed]

# Guardrail: If there are no pending tasks for that pet, we should stop and tell the owner to add some tasks first 
if not pending_tasks:
    st.info("You don't have any pending tasks for this pet yet. Add tasks above first!")

else:
    # If did not stop, it means there are pending tasks, so we show the owner the list of pending tasks for that pet as context for the check-in
    st.write(f"Tasks scheduled for {check_in_pet} today:")
    for task in pending_tasks:
            st.markdown(f"- {task}")

    # Text box for the owner to describe their day
    tasks_done = st.text_area(
        "What did you do for your pet today?",
        placeholder = "e.g. I gave Luna breakfast and dinner, we played for 30 minutes, but I forgot to clean the litter box..."
    )

    # When the owner clicks the button to submit their check-in, we call the evaluate_checkin function
    if st.button("Evaluate my day 🐾"):
        result = evaluate_checkin(
            pet_name=check_in_pet,
            species=selected_pet.species,
            tasks_due=pending_tasks,
            tasks_done=tasks_done
        )
        st.success("Here's how your day went! 🐾")
        st.markdown(result)

st.divider()

# Set up the look of the health question section
st.subheader("🩺 Have a pet health question? Ask PawPal+")
st.caption("Have a question about your pet's health, behavior, or care? Ask us anything and we will do our best to help!")

# Owner chooses which pet they want to ask a question about from a dropdown of their pets 
question_pet = st.selectbox("Which pet is your question about?", [p.name for p in st.session_state.owner.pets], key = "question_pet")
# Selects the pet object that the owner chose to ask a question about so we can use the information about that pet 
question_pet_obj = next(p for p in st.session_state.owner.pets if p.name == question_pet)

# Text box for the owner to type in their health question
user_question = st.text_input(
    "What would you like to know?",
    placeholder = "e.g. How often should I clean my cat's litter box? Or my dog has been scratching a lot lately!"
)

# When the owner clicks the button to submit their question, we call the answer_health_question function
if st.button("Ask PawPal+ 🐾"):
    # Guardrail: If the owner tries to submit an empty question, we stop and ask them to type a question first before sending to Groq 
    if not user_question.strip():
        st.warning("Please type a question first!")
    # If there is a question, we call the function to get an answer from Groq and display it to the owner
    else:
        answer = answer_health_question(user_question, question_pet_obj.species)
        st.success("Here's what PawPal+ found! 🐾")
        st.markdown(answer)

        # Store the answer and the pet it was about in session state so we can use it for the add task button
        st.session_state.last_question_answer = answer
        st.session_state.last_question_pet = question_pet_obj
        
        # If the answer from Groq includes a suggested task and the owner hasn't added one yet, we show a button to add that task to the pet's schedule
        if "📋 Suggested task:" in answer and not st.session_state.get("task_added"):
            st.session_state.show_add_button = True

# Show the add task button to the owner and asking if they would like the suggested task to be added to their pet's schedule
# We want this to be able to live after reruns so it is outside the Ask PawPal block
if st.session_state.get("show_add_button"):
    suggested = st.session_state.last_question_answer.split("📋 Suggested task:")[-1].strip()
    st.info(f"📋 Suggested task: {suggested} — would you like to add this to your pet's schedule?")

    # If the owner clicks the button to add the suggested task, we show a form to input the details of the task and then add it to the pet's tasks
    if st.button("Add this to my schedule 🐾", key = "show_form"):
        st.session_state.show_task_form = True

# Show the form to the owner so they can input task details only if they clicked the button to add the suggested task
if st.session_state.get("show_task_form"):
    suggested = st.session_state.last_question_answer.split("📋 Suggested task:")[-1].strip()
    st.markdown("**Customize this task for your schedule 🐾**")

    # Show existing tasks to the owner so they can check for duplicate tasks before adding
    pet = st.session_state.last_question_pet
    existing_tasks = [t.task_name for t in pet.tasks if not t.is_completed]
    # Guardrail: If there are already tasks in the schedule for that pet, we show them to the owner in an expander so they can check
    # if the suggested task is already included before filling out the form to add it again
    if existing_tasks:
        with st.expander(f"See {pet.name}'s current tasks before adding"):
            for t in pet.tasks:
                if not t.is_completed:
                    st.markdown(f"- {t.task_name} (Duration: {int(t.duration * 60)} min, Priority: {PRIORITY_LABEL.get(t.priority_level, t.priority_level)})")

    # Set up the form inputs for the task details (duration, category, priority, frequency, time)
    col1, col2 = st.columns(2)
    with col1:
        task_duration = st.number_input("Duration (mins)", min_value=5, max_value=240, value=30, key = "answer_duration")
    with col2:
        task_category = st.text_input("Category", value="Health", key = "answer_category")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        task_priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=1, key = "answer_priority")
    with col2:
        task_frequency = st.selectbox("Frequency", ["Daily", "Twice Daily", "Weekly"], key = "answer_frequency")
    with col3:
        task_time = st.text_input("Scheduled time (HH:MM)", value="00:00", key = "answer_time")

    # When the owner clicks the button to confirm adding the task, we create a new Task object with the details and add it to the pet's tasks
    if st.button("Confirm add to schedule 🐾", key = "confirm_add"):
        pet = st.session_state.last_question_pet
        existing = [t.task_name.lower() for t in pet.tasks]
        # Check for EXACT duplicates before adding
        if suggested.lower() in existing:
            st.warning("You already have this task in your schedule!")
        else:
            new_task = Task(
                task_name=suggested,
                category=task_category,
                priority_level=PRIORITY_MAP[task_priority],
                duration=round(task_duration / 60, 2),
                frequency=task_frequency,
                time_str=task_time,
            )
            pet.tasks.append(new_task)
            # Clear all flags and rerun so the forms and buttons diasppear and the new task shows up in the schedule
            st.session_state.show_task_form = False
            st.session_state.show_add_button = False
            st.session_state.task_added = True
            st.success(f" Added '{suggested}' to {pet.name}\'s schedule. Generate your schedule to see it included!") 
            st.rerun()
