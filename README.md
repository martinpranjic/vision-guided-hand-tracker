# vision-guided-hand-tracker
A real-time computer vision system that tracks a human hand using a two-axis pan-tilt mechanism.

## Project overview

This project is being done before my initial computer engineering and mathematics studies at Lund University. All around the world, software and hardware are being connected to advance the human species, and due to this fact together with my interests and ambitions of studying at a world-class level, I will be making a mechatronic system designed to track a human hand with the help of a camera, programming, servos and much more.

## How it works

In its most simple form, the project can be described as follows: A camera sees the user's hand. The computer calculates where the hand is and sends the coordinates to a microcontroller. The controller rotates two servos that hold some form of light (LED or laser), so the light points at the hand. 

The process can be summarized in three sections:
1. Vision - the camera pictures.
2. Thinking - the computer finds the hand and decides where the system should point the light.
3. Action - the servos react and point the light at the hand.
