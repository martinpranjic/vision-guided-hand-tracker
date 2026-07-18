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

## Servo tracking logic

The camera on the computer has a point $A$, positioned in the center of the camera display. While it would be logical to give $A=(0,0)$ as coordinates, OpenCV, the tool that is used for capturing and processing camera frames, has these coordinates in the upper-left corner of the camera display. It's necessary to calculate the center point as follows:

$$
A=
\left(
\frac{\mathrm{frame\_width}}{2},
\frac{\mathrm{frame\_height}}{2}
\right)
$$

MediaPipe, a machine-learning framework developed by Google, analyzes the camera frames captured by OpenCV. Its Hand Landmarker model detects 21 landmarks on the user's hand and returns their coordinates. Point $B$ is estimated by calculating the average position of landmarks $0$, $5$, $9$, $13$, and $17$, representing the wrist and the bases of the fingers. The point on the user's hand is point $B$, and has coordinates which constantly change when the user moves the hand. A vector from point $A$ to $B$, let's call it $\vec{C}$, can be calculated with the help of the points' coordinates:

$$
\vec{C}=\vec{B}-\vec{A}=\left(B_x-A_x,\;B_y-A_y\right)
$$

This vector can then be used to calculate the angles at which the servos need to operate to point the laser at point $B$. The key is to separate the $x$- and $y$-components to determine the pan and tilt axes. The $x$-component controls the pan axis, while the $y$-component controls the tilt axis.
