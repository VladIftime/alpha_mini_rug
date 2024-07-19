# alpha_mini_rug

Updates:

- **Arunco cards**
  - In combination with a simple callback to the sight.stream, the aruco_detect_markers function returns all the ids and corners of the Aruco cards the robot currently sees.
- **Smart questions**

- **Key words only English**
  - Asks a smart questions and returns the answer of the user.
- **Key words**
  - currently we implemented two questions:
    - What is your favorite color?
    - What is your favorite season?
  - the answers to the questions are predermined:
    - "red", "blue", "green", "yellow", "pink", "orange", "purple"
    - "winter", "spring", "summer", "autumn"
  - the function follows:
    - set the language the of the robot
    - create a warm introduction between the robot and the user
    - the robot asks the first question
    - the robot records the answer
    - parse the answer in tokens (words)
    - check if the word is in the key words dictionary
      - if yes: robot returns a positive response
      - if not: robot returns a hint
    - repeat
  
- **Key words Dutch and English**
  - currently we implemented one question:
    - What is your favorite time of the day?
  
- **Follow faces**
  - TODO
- **ROS**
  - Can it be done?

- **General remarks**
  
