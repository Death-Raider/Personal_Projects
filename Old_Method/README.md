# <center> HumanoidX Team 3 Presents <br> Eye Gesture Based Remote Robotic Arm Control
## <center> By: Darsh
### <center> Project: 
- We are incorporating eye tracking and gestures with the control of robotic arms allowing for <br>
the remote use of the arm based on cameras mounted on the arm or on other locations. We believe that this <br> method will provide a versatile usecase espcially in areas were high risk is involved. Some tasks it can be helpful in are:<br>
 <ol>
    <li>performing dangerous chemical reactions (explosives)</li>
    <li>defusing squad in neutralizing bombs</li>
    <li>performing tasks in inaccessable environments (radioactive/ toxic)</li>
    <li>and many more ...</li>
 </ol>

### <center> Requirements:
- Camera module <part-no>
- Arduino Uno
- python 3.11.4 with pip 23.1.2
- robotic arm kit
### <center>Methodology:
### <center> Part 1:
- Using python (openCV) detect the eye position and hence figure out where the eye is looking on the screen.<br> The input will be an image and the output will be the pixel coordinates for the screen.
- the pixel coordintes will then be converted into coordinates in 3D space via a projection matrix <br> based upon the arm camera.
### <center> Part 2:
- looking on the screen = move the arm to that location (part 1)
- Incorporation of eye gesturesmwith blinks (as an update later)
### <center> Part 3:
- Incorporation of Arduino Uno to controle the robotic arm based upon the outputs of part 1 and part 2.
