# Eye Gesture Based Remote Robotic Arm Control

## Presented by: **HumanoidX Team 3**  
### By: **Darsh**

---

### Project Overview

This project involves controlling a robotic arm through eye gestures, using eye tracking to determine the direction of the gaze and mapping that information to move the robotic arm remotely. The system will use cameras mounted either on the robotic arm or in other locations, allowing for versatile operation, especially in high-risk or inaccessible environments.

Some tasks where this system can be helpful include:
- Performing dangerous chemical reactions (e.g., handling explosives)
- Defusing bombs in hazardous environments
- Performing tasks in inaccessible environments (e.g., radioactive or toxic settings)
- And many more...

---

### Project Requirements

To set up the system, the following components are required:
- **Camera Module** 
- **Arduino Uno**
- **Python 3.11.4** with **pip 23.1.2**
- **Robotic Arm Kit**

---

### Methodology

The project is divided into multiple parts:

#### Part 1: Eye Position Detection and Mapping
- Use **OpenCV** in Python to detect the eye position and determine where the eye is focused on the screen.
- Input: Image (captured from the camera)
- Output: Pixel coordinates on the screen indicating where the user is looking.

The detected pixel coordinates will be mapped into a 3D space using a **projection matrix**, which will be based on the camera's perspective of the robotic arm.

#### Part 2: Moving the Robotic Arm Based on Eye Gaze
- The robotic arm will move to the location on the screen where the eye is focused, as identified in Part 1.
- **Eye gestures** (such as blinking) will be incorporated as an update to control specific actions or commands.

#### Part 3: Arduino Uno Integration
- The **Arduino Uno** will be used to control the robotic arm based on the gaze information and eye gestures.
- The Arduino will receive commands from Python (via serial communication) and translate them into actions for the robotic arm.

---

### Conclusion

This project aims to create an innovative and efficient way to control robotic arms in hazardous situations. The combination of eye tracking, gesture recognition, and remote control via Arduino offers a highly versatile and safe solution for various real-world applications, from bomb disposal to performing complex tasks in dangerous environments.