
# N-Body Simulation Readme

This README provides an overview of an N-body simulation program written in Python, which simulates the gravitational interaction between multiple bodies using the `tkinter` library.

## Table of Contents
1. [Introduction](#introduction)
2. [Dependencies](#dependencies)
3. [Usage](#usage)
4. [Customizing the Simulation](#customizing-the-simulation)

## Introduction

The N-body simulation is a Python program that simulates the gravitational interaction between a specified number of bodies. Each body has a position, velocity, and mass, and they interact with each other based on Newton's law of universal gravitation. The program includes two parts:

1. **Physics Simulation:** The core of the simulation is implemented in the `Simulation` class, which calculates the movements of the bodies over time. The simulation uses the equations of motion to update the positions and velocities of the bodies.

2. **Visualization:** The program provides a graphical visualization of the bodies' movements. It uses the `tkinter` library to create a simple animation window. You can customize the appearance of the bodies by providing custom image files.

## Dependencies

Before running the N-body simulation, you need to install the following Python library:

- `numpy`:  Primarily used for numerical and scientific computing.


## Usage

1. Clone or download the code from the repository to your local machine.

2. Install the required dependencies, as mentioned in the "Dependencies" section.

3. Customize the program by providing custom images for the bodies. Place these image files in the same directory as the code.

4. Open a terminal and navigate to the directory where the code is located.

5. Run the program using Python:

```bash
python n_body_simulation.py
```

6. A window will open displaying the N-body simulation. You will be prompted to enter the number of bodies you want in the simulation.

7. The simulation will run, and you can observe the gravitational interactions between the bodies. The window will display the real-time frames per second (FPS) and the number of bodies.

8. You can close the simulation window at any time to exit the program.

## Customizing the Simulation

To customize the N-body simulation, you can modify the code in the following ways:

1. **Simulation Parameters:** Adjust the simulation parameters, such as the number of bodies (`BODIES`) and the time step (`DT`), to change the characteristics of the simulation.

2. **Physics Simulation:** Modify the physics simulation code if you want to introduce additional forces or constraints to the system.

3. **Rendering:** You can customize the rendering by changing the colors, sizes, and shapes of the bodies on the screen.

Feel free to experiment with the code and tailor the simulation to your specific needs.
