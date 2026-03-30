# PawPal+ Project Reflection

## 1. System Design
Identify three core actions a user should be able to perform with PawPal+:

- A user should be able to add specific tasks (like a morning walk, afternoon playtime, make a grooming appointment). When these tasks are added, there should be some sort of priority level given to each task and should assign each task a category so the user finds it easier to keep track of the tasks they have for their pet. 

- A user should be able to input their daily availability and get a schedule that aligns with these times as well as the tasks are able to be done within the time window. 

- A user should be able to see the schedule for that day at any time they want and they can see the reasoning behind the choices for the tasks. The list should be realistic and allow the user to easily cross off the tasks when they have done it.

**a. Initial design**

- Briefly describe your initial UML design.
My initial UML design reflects a system that takes carae of multiple pets per user and uses a Manager to apply constraints and reasoning to tasks. The design uses one-to-many relationships where one User can have multiple Pets and one Pet can have multiple Tasks. The Manager class acts as the Orchestrator that looks at the relationships (such as User's daily time availability and the Pet's list of tasks) and handles them in order to make a final and realistic plan so the user can actually use. 

- What classes did you include, and what responsibilities did you assign to each?

The first class I decided to include was a User class. This class represents the owner of thet pet(s) and ultimately the person who is using the app. The main responsibility from the user class is to set the daily availability time of the user so it can be used to generate a realistic plan. Additionally, the user should be able to keep track of their pets, especially if they have multiple. The second class I decided to include was a Pet class. This class represents the details of the pet, including name, age, and the species. The main responsibility of a Pet is to hold a list of Task objects because it allows the system to keep track of the tasks have been assigned to that Pet. The third class I included is the Task class. This class details the name of the task, the type of task that it is, how much priority should be given to that task, the amount of time that task takes, and if it has been completed or not (whether the user should focus on it or not). The main responsibility for the Task is to store all this information for the user so they understand the types of tasks they should prioritize and how it fits into their schedule. It also lets users understand whether or not they need to keep working on that task if it is complete or not. The last class I decided to include is the Manager class. This class is in charge of the relationship between the User and the Task class. In order to generate a plan that is applicable to the user's life, the Manager class's responsibility is to keep track of the user's time limit and make sure the task fits in that time window. Additionally, the Manager class provides reasoning so the user understands why the tasks were chosen and why they were prioritizes over others.

**b. Design changes**

- Did your design change during implementation?
Yes, the design did change during implementation because there were few places within the classes that could be cleaned up for clarify and efficiency.

- If yes, describe at least one change and why you made it.
One major change I made with the help of AI is the attribute for User's daily_availability was changed to a float when originally it was set to a string. When the Manager class needs to check for the User's availability and checks it against the time of the task to see if it fits within that availability, it will be confused and won't be able to do the computation since it can't do math on a string. Another change I made with the help of AI is removing the attribute total_time_limit from Manager class. Logically, the Manager class should really only be referencing the User's daily availability to make the plan because that is the time that matters, so the Manager shouldn't have its own time. When the Manager needs the availability time, it can reference self.user.daily_availability directly. The last change I made with the help of AI is removing the method get_tasks() from the Pet class. This is because the tasks attribute is already public so there is no use or efficiency to having a method that returns a public attribute. When tasks is needed, it can be accessed by pet.tasks directly. 

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
To make the final plan the user receives as realistic as possible, my Manager considers time, priority level, and specific time slots. In terms of time, the user provides a daily availability which acts as their time window for tasks. The Manager tracks the duration of every task the user gives and stops adding tasks to the schedule when the user's daily time limit is up. The priority level ensures the tasks assigned to pets are not in any randomy order, instead the task is assigned an importance level (from highest to lowest). If the user only has two hours available, the Manager makes sure the most important tasks are scheduled before the less important tasks. The specific time slots represents the `time_str` contraints. If a task needs to happen at a specific time, the system flags it. It also makes sure there is no other task at the time, if it does find it then it warns the user. For tasks that can happen whenever, the tasks are assigned 00:00 and there is more flexibility in the schedule. 

- How did you decide which constraints mattered most?
I decided that priority and the daily time mattered the most because this is how people go about making decisions each day, it always depends on how important the task is and the question of "does it fit within my schedule?" There is a specific order in which responsibilities are done, it isn't just the order you think of them but it is more about the priority of what needs to get done first before there is no more time. I also chose the prioritize the specific time slots because missing medication that helps with health in order to fit in playtime isn't a fair trade at all, so it teaches the user to absolutely do the tasks that benefits their pet's health the most. Additionally, the priority level also ensures that these tasks were to be done before any smaller mundane tasks. I want the app to reflect reality as much as possible especially since it is expected that users would use this app to take care of their pet daily.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
The Manager (Manager is just my name for scheduler, I labeled it this to own some authenticity to my project :D) trades efficiency for priority. The Manager always looks at the level of importance of tasks and how long those tasks take to see if it fits within the time given. If a task has a high priority level associated with it, then the Manager will immediately incorporate that instead of recommending the user to complete a lot of smaller tasks with less priority. In other words, quality over quanity matters to the Manager. This can be seen in the generate_plan() method where a high priority level task will be fit into the schedule first rather than lower priority leve task even if it is something that the user would want to do becaue it really depends on the user's time availability.

- Why is that tradeoff reasonable for this scenario?
This tradeoff is reasonable because urgency is important and tasks are not equal. In pet care, it is important to do tasks that benefit the health of your pet and while giving mediciation to regulate your cat's breathing and playing with your cat both benefit its health, failing to do one is much more of a consequence than the other. It is important that those tasks that would bring pain and hurt in the future are done as quickly as possibly to avoid anything unfortunate, even if it means the user doesn't cross out more tasks and may feel unproductive. The Manager ensures that the pet's health and safety needs are met first, which is the purpose of a caretaker.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
For this project, I used AI to structure the logical code order of the methods and to make the code look cleaner and as simple as possible so it is easier to read. I had AI explain to me the different Python tools that I wasn't familar with, such as `timedelta` for doing the "HH:MM" math required in `Task` class and `defaultdict` for conflict detection. AI was also helpful in guiding how to clean up the Streamlit interface especially with the suggestion to use expanders to make the task completion feel automatic. 

- What kinds of prompts or questions were most helpful?
The most helpful prompts were the ones where I provided the context in my existing code and asked for specific behavior including explanations to the code logic and formatting the output in a way that breaks down the thought process. It just made AI much easier to understand and comprehend, it was also easier to refer back to the thoughts it had. Some questions I found the most helpful is when I asked AI to explain how Python tools help with the specific method we were debugging, I would often expand on my questions and ask it to explain why it would be more difficult doing it another way. 

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
When we were discussing the task completion logic, the AI initally suggested a simpler way to update the existing task's date. I rejected that because I wanted the app to be more realistic. I wanted it to archive the old completed task and generate a completely new one. This ensures the user has a record of what they finished today while still seeing a fresh task for tomorrow. It also eliminates a step for the user because they don't have to reenter the task tomorrow. I had to guide the AI to return a new Task instance rather than just modifying the old data.

- How did you evaluate or verify what the AI suggested?
When AI suggested edits and deletions, I would first read through the logic and would not trust the AI blindly. I would make sure there was no line where the logic breaks and that all the data is handled the way it should be for that specific function. I also made sure there was no minor errors like calling the wrong methods for the wrong tests when I had it generate the tests as well. With the tests I wrote like the creating pets, printing out the schedule, rearranging the tasks so they are out of order, I ran them in termal and checked if they failed because I can't solely rely on what I see since I might miss something. If the logic was flawed, it would fail and I would aim to fix the logic myself before moving on. 

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
The main behaviors I tested focused on the complex logic of Manager methods and Task methods. In Manager class, I tested that `generate_plan` method puts the tasks assigned the "High" priority level label were put at the top of the schedule. This meant that it shouldn't taken into account what order the tasks were added in, instead it just focuses on the priority level. Additionally, I tested that `defaultdict` used in `detect_conflicts` identifies when multiple tasks are scheduled for the same time and triggers a warning to the user. It is also really important that the daily limit is not exceeded, so I tested the manager to make sure it stops adding tasks when that number has been reached. 

- Why were these tests important?
These tests were important because these features are key points of the app, where they can create a realistic plan or unrealistic plan for the user. If the sorting of tasks is wrong, then the user might face major consequences with their pet because they missed it. If the user doesn't know that two pets have conflicting schedules, they will plan wrong and won't be able to take care of those two pets at the same time. These situations had to be tested so the logical errors in the code would be found and the corrections are reflected in the Streamlit UI. 

**b. Confidence**

- How confident are you that your scheduler works correctly?
I feel confident in the reliability of the system regarding the complex algorithmic methods I implemented (with the help of AI). The tests I had run and looked over carefully successfully passed through many edge cases, which means the app does deal with complex features as well as simple append/add features as it should. The logic is consistent and the app handles the real world needs of a pet owner without crashing on the user or losing data. If the app ever needs to warn the user, it does so in a message but doesn't crash. With more tests, I am sure I could find more bugs or scenarios that I have not fixed yet. There is always room for improvement.

- What edge cases would you test next if you had more time?
If I had more time, I would want to test for Interval Overlaps. I was thinking that if a task were at 10:00 and lasts around an hour but then another task is scheduled for 10:30, there is a conflict in time because there wouldn't be enough time for that task at 10:30. In addition to time conflict, I would like to incorporate Daylight Savings Time so that the timing is accurate all year long.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I am most satisfied with how I used AI with this project because I felt like I had more trouble last project, especially with hallucinations and not understanding the code that it would suggest to me. For this project, I was able to provide more context to the AI and carefully review the logic it explained. This time around, I was less inclined to blindly accept the edit and actually asked AI to help me understand why that change was important and solved the problem. Additionally, I was able to use more tools with the help of AI because I was able to understand why we needed the tools and how to implement them in my code. It really taught me how to critically think about code in the future. 

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
If I had another iteration, I would focus on templates for the user so the app could be much easier for them to use and friendly too. A user has to think about task names in order to put it in, but I would like to add some templated tasks for specific breeds. I would also like to add more breeds or when the user presses Other, it prompts them to put the animal name. It would be more convenient and personal for the user because they would get more specific schedules catered to their pet or breed. Additionally, since this is an app, I would like for the user to have notifications so they can be reminded to do tasks for their pet. It would be more practical for the user to get a reminder especially if they are busy throughout the day.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
One important thing I learned working with AI on this project and designing systems is how important it is to give every part of the code one specific job to do. It is not always about combining methods together to do multiple things at once, but it is actually more efficient especially with objects/classes to break down the work one step at a time. If I wasn't prompted to create classes, I don't think I would have thought of that first and I would have first put all the code under one big Class. The classes allowed me to have control and organization over my code, it also gave me the ability to debug quicker. If there was a bug with scheduling, I knew that I had to look at the `Manager`. If the time was formatted wrong, I knew there was an issue with `Task`. It kept the project from becoming really messy, it was easy to find where each job lives.  
