
# vision-guided-hand-tracker

A real-time computer vision system that tracks a human hand using a two-axis pan-tilt mechanism.

## Project overview

I developed this project during my engineering studies at Lund University. I have always been interested in how software and hardware can work together to create systems that interact with the real world. With this project, I wanted to learn more about computer vision, programming, electronics, and mechanical design by combining them in one working system.

The result is a mechatronic hand-tracking system built with a camera, a computer, an Arduino, two servomotors, and a 3D-printed construction. The system detects the position of a hand and moves a light source in the same direction. A laser module is also mounted on the construction, while the moving tracking and calibration tests were carried out using a lamp.

## How it works

In its simplest form, the project works as follows: A camera sees the user's hand. The computer calculates where the hand is and sends the desired angles to a microcontroller. The controller rotates two servos that hold a light source, so the light follows the hand.

The process can be summarized in three sections:

1. **Vision** - The camera captures images.
2. **Processing** - The computer finds the hand and calculates where the system should point the light.
3. **Action** - The servos react and move the light toward the hand.

## Servo tracking logic

The camera on the computer has a point `A`, positioned in the center of the camera display. While it would be logical to give `A = (0,0)` as coordinates, OpenCV, the tool used for capturing and processing camera frames, has these coordinates in the upper-left corner of the camera display.

It is therefore necessary to calculate the center point as follows:

$$
A = \left(\frac{W}{2}, \frac{H}{2}\right)
$$

Where $W$ represents the width of the camera frame and $H$ represents its height.

MediaPipe, a machine-learning framework developed by Google, analyzes the camera frames captured by OpenCV. Its Hand Landmarker model detects 21 landmarks on the user's hand and returns their coordinates.

In the tracking program, landmark 9, which is located at the base of the middle finger, is used as a reference point for the hand. This point is called `B`, and its coordinates constantly change when the user moves their hand.

MediaPipe returns normalized coordinates, meaning that the coordinates normally range from 0 to 1.

If the normalized coordinates of the hand are $(x_h,y_h)$, the coordinates in pixels can be calculated as:

$$
B = (x_h W, y_h H)
$$

A vector from point `A` to `B`, called $\vec{C}$, can then be calculated using the coordinates of the two points:

$$
\vec{C} = \vec{B} - \vec{A}
$$

$$
\vec{C} =
\left(
x_h W - \frac{W}{2},
y_h H - \frac{H}{2}
\right)
$$

This vector represents the position of the hand relative to the center of the camera image.

The key is to separate the horizontal and vertical components to determine the pan and tilt axes. The horizontal component controls the pan axis, while the vertical component controls the tilt axis.

To simplify the calculations, the coordinates are converted into normalized values ranging from -1 to 1:

$$
e_x = 2\left(x_h-\frac{1}{2}\right)
$$

$$
e_y = 2\left(y_h-\frac{1}{2}\right)
$$

When the hand is in the center of the camera image, both values are approximately zero. As the hand moves toward the edges, their absolute values increase.

## Converting coordinates into servo angles

The two servomotors have a neutral position of approximately 90 degrees. This position serves as the starting point for calculating the required movements.

The normalized coordinates are multiplied by values that determine how far each servo should rotate. Separate offsets are also added to compensate for differences between the camera's position and the position of the mechanical construction.

The angles can be calculated using the following equations:

$$
\theta_{pan} = \theta_0 + k_p\bar{e}_x + b_p
$$

$$
\theta_{tilt} = \theta_0 + k_t\bar{e}_y + b_t
$$

Where:

- $\theta_0$ represents the neutral servo angle.
- $k_p$ represents the horizontal movement sensitivity.
- $k_t$ represents the vertical movement sensitivity.
- $b_p$ represents the horizontal calibration offset.
- $b_t$ represents the vertical calibration offset.
- $\bar{e}_x$ and $\bar{e}_y$ represent the smoothed hand coordinates.

The direction of the movement depends on how the servomotors are physically mounted. Therefore, the signs in the equations may need to be changed.

The calculated angles are then sent from Python to Arduino through serial communication. The Arduino receives the values and rotates the servomotors accordingly.

## Smoothing and response time

During the initial tests, one of the main problems was the response time of the servomotors. The movement could sometimes be delayed, and small changes in the detected hand coordinates could cause unnecessary movements.

To solve this problem, I implemented exponential smoothing.

The formula is:

$$
\bar{e}_t = \bar{e}_{t-1} + \alpha(e_t-\bar{e}_{t-1})
$$

Where:

- $e_t$ is the newest detected position.
- $\bar{e}_t$ is the smoothed position.
- $\bar{e}_{t-1}$ is the previously smoothed position.
- $\alpha$ controls how quickly the system responds.

A larger value of $\alpha$ makes the servos react faster, while a smaller value produces smoother but slower movements.

I adjusted this value through testing to find a balance between precision and response time.

Another improvement was reducing the camera resolution to 320 by 240 pixels. This reduced the amount of information that MediaPipe needed to process.

The number of commands sent to Arduino was also limited to approximately 20 commands per second.

Finally, if the system does not detect a hand for two seconds, the servos gradually return to their calibrated center positions.

## The problem with parallax

One of the most important challenges during the development of the project was the difference between the camera's position and the position of the light source.

Although the camera could correctly identify the position of the hand, the light did not always point at the same position.

This problem is called **parallax**.

Because the camera and the light source are not located at exactly the same position, they observe the target from different perspectives.

This creates both horizontal and vertical errors.

In my floor-mounted testing setup, the camera was approximately 19 cm above the light source, while the mechanism was positioned approximately 28 cm to the side of the camera.

The system was calibrated at a target distance of approximately 100 cm.

To estimate the horizontal correction, the following equation can be used:

$$
\phi = \arctan\left(\frac{s}{d}\right)
$$

Where:

- $s$ is the horizontal distance between the camera and the mechanism.
- $d$ is the distance to the target.

Using the measured distances:

$$
\phi = \arctan\left(\frac{28}{100}\right)
$$

$$
\phi \approx 15.64^\circ
$$

The approximate vertical correction can be calculated using:

$$
\psi = \arctan\left(\frac{h}{\sqrt{d^2+s^2}}\right)
$$

Where $h$ represents the vertical distance between the camera and the light source.

Using the measured values:

$$
\psi =
\arctan\left(
\frac{19}{\sqrt{100^2+28^2}}
\right)
$$

$$
\psi \approx 10.37^\circ
$$

These calculations provided an initial estimate of how much the servos needed to compensate for the position of the camera.
However, the theoretical angles were not completely accurate in practice.
The physical mounting of the servomotors, the camera's field of view, and the rotation of the mechanical construction all affected the final result.
Therefore, additional calibration was necessary.

## Calibration and testing

To improve the accuracy of the system, I performed several tests using a lamp mounted on the construction.
The laser remained switched off during the moving hand-tracking tests.
I started by positioning my hand in the center of the camera image and observing where the light pointed.
If the light was too far to the left or right, I adjusted the horizontal offset. If the light was too high or too low, I adjusted the vertical offset.
Once the center position was sufficiently accurate, I tested the movement toward the edges of the camera image.
The main testing positions were the center, left, right, upper, and lower parts of the image.
During these tests, I discovered that the horizontal servo sometimes reached its programmed movement limit before the light could follow the hand completely.
I therefore needed to consider both the allowed servo angles and the position of the construction.
After several adjustments, I managed to calibrate the system so that the light followed my hand accurately at the chosen testing distance.
An important limitation is that the calibration depends on the relative positions of the camera, the mechanism, and the target.
If the construction is moved, the calibration may need to be repeated.

## Hardware and software

The mechanical construction was designed using CAD software and manufactured through 3D printing.
It consists of a base, supporting components, and a two-axis pan-tilt mechanism.
The first servomotor controls horizontal rotation, while the second servomotor controls vertical rotation.
The servomotors are powered by an external 5 V power supply, while Arduino communicates with the computer through a USB connection.
The external power supply and Arduino share a common ground to ensure that the control signals work correctly.
The main software is written in Python.
OpenCV is responsible for capturing and processing camera frames, while MediaPipe is used to detect the hand and determine its position.
PySerial allows Python to communicate with Arduino through a serial connection.
Arduino receives the calculated servo angles at a baud rate of 115200 and controls the motors.
A laser module is also mounted on the construction. During the moving hand-tracking tests, a lamp was used as the light source instead.
The construction process also involved several practical challenges, including securing the 3D-printed plate to the servo arm, arranging the electrical connections, and making sure the components could move without mechanical interference.

## Limitations and future improvements

Although the system works well at the calibrated distance, there are still several possible improvements.
One limitation is that an ordinary webcam provides two-dimensional coordinates rather than the exact three-dimensional position of the hand.
This means that the system does not automatically know how far away the hand is.
Since the required parallax correction depends on the distance to the target, a fixed offset cannot provide perfect accuracy at every distance.
One possible improvement would be to introduce a distance sensor or a depth camera.
This would allow the system to estimate the hand's position in three dimensions and calculate more accurate servo angles.
Another improvement would be a more advanced mathematical model that takes the camera's field of view, perspective, and the exact positions of the servo axes into account.
The mechanical construction could also be improved by using more precise mounting components and reducing unnecessary movement between the different parts.
For future laser-related experiments, the laser classification and the necessary physical safety measures would also need to be verified. The software alone cannot guarantee that a moving laser is safe for human eyes.

## Conclusion

This project has given me a better understanding of how different areas of engineering can be combined to create a working physical system.
What started as a relatively simple idea developed into a project involving computer vision, mathematics, programming, electronics, mechanical design, and repeated testing.
One of the most important things I learned was that creating a working program is only one part of the engineering process.
Even when the software worked correctly, problems with mechanical mounting, power supply, communication, and calibration could prevent the system from functioning as intended.
Solving these problems helped me understand the importance of combining theoretical knowledge with practical experimentation.
The project has strengthened my interest in computer engineering and in developing systems where software and hardware interact with the physical world.
