# Online Chat Mass Messaging

The project idea is to unify the multiple existing online chat fourms witha  single interface. 

---

### Motivation
The motivation behind the idea is that the user can:
  - Study the behaviour of people from a wide demographic to certain LLM agents.
  - Targetted Promotion towards specific demographic.
  - Learning human conversational pattern and sociology.
  - Generation of conversational dataset.

---

### Methodology
The websites which I intend to implement are mentioned in the websites.txt and multiple JS files will be created for each website.
Since each website possesses a different UI, I need to go through the code and analyze each site and write the respective JS code for interaction.
<br>
The code written in JS is not ment to be executed stand-alone but is the prototype for the actual code in python. The JS code can be used peicewise on the console of the respective website. 

---

### Proposed Structure 

**Class** <u>InterfacePeople</u>
 * Method GetActiveCount
 * Method GetPeople
 * Method Update
 * Method FilterByOptions
  
**Class** <u>Person</u>
 * Attribute History
 * Method SendMessage
 * Method RecvMessage
 * Method GetDetails