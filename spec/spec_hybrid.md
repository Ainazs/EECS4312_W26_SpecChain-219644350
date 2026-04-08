
# Requirement ID: FR1_hybrid_1
- Description: The system shall provide a free version of the mental health tracking tool with basic features.
- Source Persona: Financial conscious wellness user. (P_auto_2)
- Traceability: Derived from review group G2
- Acceptance Criteria: Given the user has a free account, When they log in, Then they can access basic mental health tracking features.
- Notes: Changed the source persona identified wrong as related to persona 1 but this was related to persona 2. 

# Requirement ID: FR2_hybrid_2
- Description: The system shall offer a clear and transparent upgrade path from the free version to a paid subscription for advanced features.
- Source Persona: Financial conscious wellness user.  (P_auto_1)
- Traceability: Derived from review group G2
- Acceptance Criteria: Before any account information is entered, a pricing summary that lists at least three free features and the monthly cost of the premium subscription must be available when a new user downloads the app for the first time and reaches the account creation screen.
- Notes: The requirment mentioned that it places the pricing into setting which was changed to a summary before account creation.  
---

# Requirement ID: FR3_hybrid_3
- Description: The system shall provide a at least 10 mood tracking icons that allows users to log their emotions and view them over time.
- Source Persona: Hopeful Helper (P_auto_2)
- Traceability: Derived from review group G3
- Acceptance Criteria: Given a user has accessed the mood tracking feature, When they select a mood and add a note, Then the system displays at least 10 representation of their mood history.
- Notes: Rewrote teh FR3 eacuse it was to vauge and unmeasurable. 

# Requirement ID: FR4_hybrid_4
- Description: The system shall offer a reflection prompt library that provides users with guided questions to facilitate self-reflection and journaling.
- Source Persona: Hopeful Helper (P_auto_2)
- Traceability: Derived from review group G3
- Acceptance Criteria: Given a user has accessed the reflection prompts, When they select a prompt, Then the system displays a text input field for them to write their reflection and saves it to their journal.
- Notes: This requirment was not changed. 

---

# Requirement ID: FR5_hybrid_5
- Description: The system shall allow users to track their emotions and feelings over time, providing a visual representation of their mental health progress.
- Source Persona: Daily Self-Reflection User , P_auto_3
- Traceability: Derived from review group G1
- Acceptance Criteria: Given the user has logged in, When they navigate to the tracking section, Then they can view a graphical representation of their emotions and feelings over a 7 day period.
- Notes: Changed to "7 day period" from some selected time which was unmeasurable.

# Requirement ID: FR6_hybrid_6
- Description: The system shall provide users with personalized insights and recommendations based on their tracked emotions and feelings, helping them identify patterns and areas for improvement.
- Source Persona: Daily Self-Reflection User , P_auto_3
- Traceability: Derived from review group G1
- Acceptance Criteria: Given the user has tracked their emotions and feelings for at least a week, When they view their insights, Then they receive a list of 3-5 personalized recommendations for managing their mental health.
- Notes: Nothing changed here. 

---

# Requirement ID: FR7_hybrid_7
- Description: During onboarding, the system must offer a language selection choice for all UI components, prompts, and application content.
- Source Persona: Multilingual Mental Health Seeker (P_hybrid_1)
- Traceability: Derived from review group H1
- Acceptance Criteria: When a new user reaches the language selection screen during the onboarding process, they must be able to choose at least one non-English language, and all subsequent app content must be shown in that language.
- Notes: The requirment was repitetive so created it from scratch. 

# Requirement ID: FR8_hybrid_8
- Description: The system shall offer an affordable premium subscription that provides users with unlimited access to their historical mental health data and advanced insights into their mental state.
- Source Persona: Hopeful Tracker, P_auto_4
- Traceability: Derived from review group G4
- Acceptance Criteria: Given a user subscribes to the premium version, When they have tracked their emotions for over a year, Then they can view detailed monthly and yearly reports of their mental health trends.
- Notes: Nothing was changed here.

---

# Requirement ID: FR9_hybrid_9
- Description: All third-party services that receive user data must be listed in the system's clear data privacy disclosure, which can be accessed through the app settings.
- Source Persona: Privacy concern User (P_auto_5)
- Traceability: Derived from review group G5
- Acceptance Criteria: When a user opens the data disclosure page after navigating to the privacy settings area, a list of all third-party data recipients must appear, along with a link to the third party's privacy policy and the category of data provided.
- Notes: The requiment was aout seaamless data update but the group consern was about privacy so I had to rewrite the requirments. 

# Requirement ID: FR10_hybrid_10
- Description: The system shall provide a control machenism requiring a PIN to grant access to app history. 
- Source Persona: Privacy concern User (P_auto_5)
- Traceability: Derived from review group G5
- Acceptance Criteria: The app should ask for a pin, if the incorect pin is entered then the access is denied. 
- Notes: The requirment was irrelevant to group 5 privacy issue so I rewrote it. 