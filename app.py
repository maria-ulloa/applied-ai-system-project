import streamlit as st
from pawpal_system import User, Pet, Task, Manager

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

PRIORITY_MAP = {"Low": 1, "Medium": 3, "High": 5}

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

col1, col2 = st.columns(2)
with col1:
    category = st.text_input("Category", value="Exercise")
with col2:
    frequency = st.selectbox("Frequency", ["Daily", "Twice Daily", "Weekly"])

if st.button("Add Task"):
    pet = next(p for p in st.session_state.owner.pets if p.name == selected_pet)
    pet.tasks.append(Task(
        task_name=task_name,
        category=category,
        priority_level=PRIORITY_MAP[priority_label],
        duration=round(duration_mins / 60, 2),
        frequency=frequency,
    ))
    st.success(f'"{task_name}" added to {selected_pet}.')

for pet in st.session_state.owner.pets:
    if pet.tasks:
        with st.expander(f"{pet.name}'s tasks ({len(pet.tasks)})"):
            for task in pet.tasks:
                checked = st.checkbox(task.task_name, value=task.is_completed, key=f"{pet.name}_{task.task_name}")
                if checked and not task.is_completed:
                    task.complete_task()  # calls Task.complete_task()
            st.table([t.get_details() for t in pet.tasks])  # calls Task.get_details()

st.divider()

# --- Generate Schedule ---
st.subheader("Today's Schedule")
if st.button("Generate Schedule"):
    schedule = st.session_state.manager.generate_plan()  # calls Manager.generate_plan()
    if schedule:
        st.success(st.session_state.manager.get_reasoning())  # calls Manager.get_reasoning()
    else:
        st.warning("No tasks could be scheduled. Add tasks or increase your daily availability.")
