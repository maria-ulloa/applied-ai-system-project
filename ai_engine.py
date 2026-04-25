import os
from dotenv import load_dotenv
from groq import Groq

# Load API key and connect it to Groq 
load_dotenv()
client = Groq(api_key = os.getenv("GROQ_API_KEY"))

# Knowledge Base needed for RAG retrieval
# Each key is a category of pet care that can be retrieved based on user queries. The values are strings containing relevant corresponding information.
KNOWLEDGE_BASE = {
    "cat_care": """
        - Cats should eat 2 times per day. Kittens may need 3 meals.
        - Fresh water should always be available. Cats are prone to dehydration.
        - Litter boxes should be scooped daily and fully cleaned weekly.
        - Cats need at least 15-20 minutes of active play per day.
        - Annual vet visits are recommended for healthy adult cats.
        - Watch for: changes in water intake, appetite loss, hiding, or lethargy these may signal illness.
        - Common issues: hairballs, urinary tract infections, dental disease.
    """, 

    "dog_care": """
        - Dogs should eat 2 times per day based on their size and breed.
        - Dogs need fresh water available at all times.
        - Most dogs need 30-60 minutes of exercise per day depending on breed.
        - Dogs should be bathed every 1-3 months depending on coat type.
        - Annual vet visits plus vaccines are recommended.
        - Watch for: excessive scratching, changes in appetite, limping, or unusual behavior.
        - Common issues: ear infections, dental disease, obesity, parasites.
    """,

    "general_care": """
        - Medications should be given at the same time each day for consistency.
        - Sudden changes in behavior, appetite, or energy are worth a vet call.
        - Dental hygiene matters, brush pets teeth or provide dental treats regularly.
        - Keep emergency vet contact saved and accessible.
        - Mental stimulation like puzzles, toys, and training is as important as physical exercise.
    """
}

# Step 1: RAG Retrieval Function
def retrieve_relevant_info(question: str) -> str:
    """
    Retrieves most relevant knowledge base chunk based on the user's question.
    """
    cat_keywords = ["cat","kitty","feline","litter","meow","purr","kitten","whiskers","feed","eat","groom","sleep"]
    dog_keywords = ["dog","puppy","canine","bark","woof","pup","hound","walk","treat","groom","sleep","fetch"]

    # Looks through each word in question.lower() and checks if any of the keywords related to cats or dogs match, returns the chunk with the best match.
    if any(word in question.lower() for word in cat_keywords):
        return KNOWLEDGE_BASE["cat_care"]
    elif any(word in question.lower() for word in dog_keywords):
        return KNOWLEDGE_BASE["dog_care"]
    else:
        return KNOWLEDGE_BASE["general_care"]

# Step 2: Using RAG retrieval to generate an answer with Groq
def answer_health_question(question: str) -> str:

    # Retrieve the relevant chunk first before generating the answer to ensure the model has the necessary context to provide a helpful response.
    context = retrieve_relevant_info(question)

    prompt = f"""
        You are PawPal+, a warm and caring pet health assistant.

        Use ONLY the following pet care information to answer the question.
        If the information provided is not enough to answer confidently, say exactly:
        "I don't have enough information on that, please consult your vet."

        PET CARE INFORMATION:
        {context}

        QUESTION: {question}

        Answer in 2-4 sentences. Be warm, clear, and always recommend a vet for serious concerns.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Something went wrong while getting an answer. ({type(e).__name__}: {e})"
    
# Step 3: Daily Check-In Evaluator
def evaluate_checkin(pet_name: str, species: str, tasks_due: list, tasks_done: str) -> str:
    """
    Takes what the owner typed about their day with their pet and compares it to what was actually scheduled for the day.
    Groq then gives a warm score and feedback based on what the owner said.
    
    pet_name: the name of the pet 
    species: the type of pet (cat, dog, etc.)
    tasks_due: the list of tasks that were scheduled for the pet today (from PawPal+)
    tasks_done: what the owner typed in the check-in text box describing their day with their pet
    """

    # Guardrail 1: If the owner didn't type anything at all, stop here and ask them to write something because we don't want an empty check-in!
    if not tasks_done.strip():
        return "⚠️ Please describe what you did for your pet today before submitting."
    
    # Guardrail 2: If the owner typed something super short like "ok" or "yes", ask for more detail because we want a real description, not just a one word answer!
    if len(tasks_done.strip()) < 10:
        return "⚠️ Your check-in is a bit vague! Please describe your pet's care in a little more detail."

    # Format the scheduled tasks as a bullet list to include in the prompt
    task_list = ""
    for task in tasks_due:
        task_list += f"- {task}\n"

    # Build the prompt using the scheduled tasks and what the owner said they did
    prompt = f"""
        You are PawPal+, a warm and caring pet care assistant.

        A pet owner is checking in about their {species} named {pet_name}.

        Tasks that were scheduled for today:
        {task_list}

        What the owner says they did today:
        {tasks_done}

        Please do the following:
        1. Give a completeness score out of 10 based on how well the scheduled tasks were covered.
        2. Give warm, encouraging feedback in 2-3 sentences.
        3. Gently mention anything important that seems missing.
        4. End with an affirmation that they are a good pet parent and doing their best.

        Keep the tone gentle, warm, and supportive. Never make the owner feel guilty.
    """

    # Send the prompt to Groq and return the LLM's response
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    # If something goes wrong with the API call, we catch the error and return a friendly message
    except Exception as e:
        return f"Something went wrong while evaluating your check-in. ({type(e).__name__}: {e})"   
 