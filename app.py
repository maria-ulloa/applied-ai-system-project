import streamlit as st
from pawpal_system import User, Pet, Task, Manager

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
