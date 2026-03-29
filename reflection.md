# PawPal+ Project Reflection

## 1. System Design
Identify three core actions a user should be able to perform with PawPal+:

- A user should be able to add specific tasks (like a morning walk, afternoon playtime, make a grooming appointment). When these tasks are added, there should be some sort of priority level given to each task and should assign each task a category so the user finds it easier to keep track of the tasks they have for their pet. 

- A user should be able to input their daily availability and get a schedule that aligns with these times as well as the tasks are able to be done within the time window. 

- A user should be able to see the schedule for that day at any time they want and they can see the reasoning behind the choices for the tasks. The list should be realistic and allow the user to easily cross off the tasks when they have done it.

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

- My initial UML design reflects a system that takes carae of multiple pets per user and uses a Manager to apply constraints and reasoning to tasks. The design uses one-to-many relationships where one User can have multiple Pets and one Pet can have multiple Tasks. The Manager class acts as the Orchestrator that looks at the relationships (such as User's daily time availability and the Pet's list of tasks) and handles them in order to make a final and realistic plan so the user can actually use. 

- The first class I decided to include was a User class. This class represents the owner of thet pet(s) and ultimately the person who is using the app. The main responsibility from the user class is to set the daily availability time of the user so it can be used to generate a realistic plan. Additionally, the user should be able to keep track of their pets, especially if they have multiple. The second class I decided to include was a Pet class. This class represents the details of the pet, including name, age, and the species. The main responsibility of a Pet is to hold a list of Task objects because it allows the system to keep track of the tasks have been assigned to that Pet. The third class I included is the Task class. This class details the name of the task, the type of task that it is, how much priority should be given to that task, the amount of time that task takes, and if it has been completed or not (whether the user should focus on it or not). The main responsibility for the Task is to store all this information for the user so they understand the types of tasks they should prioritize and how it fits into their schedule. It also lets users understand whether or not they need to keep working on that task if it is complete or not. The last class I decided to include is the Manager class. This class is in charge of the relationship between the User and the Task class. In order to generate a plan that is applicable to the user's life, the Manager class's responsibility is to keep track of the user's time limit and make sure the task fits in that time window. Additionally, the Manager class provides reasoning so the user understands why the tasks were chosen and why they were prioritizes over others.

**b. Design changes**

- Did your design change during implementation?
- Yes, the design did change during implementation because there were few places within the classes that could be cleaned up for clarify and efficiency.

- If yes, describe at least one change and why you made it.
One major change I made with the help of AI is the attribute for User's daily_availability was changed to a float when originally it was set to a string. When the Manager class needs to check for the User's availability and checks it against the time of the task to see if it fits within that availability, it will be confused and won't be able to do the computation since it can't do math on a string. Another change I made with the help of AI is removing the attribute total_time_limit from Manager class. Logically, the Manager class should really only be referencing the User's daily availability to make the plan because that is the time that matters, so the Manager shouldn't have its own time. When the Manager needs the availability time, it can reference self.user.daily_availability directly. The last change I made with the help of AI is removing the method get_tasks() from the Pet class. This is because the tasks attribute is already public so there is no use or efficiency to having a method that returns a public attribute. When tasks is needed, it can be accessed by pet.tasks directly. 

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
