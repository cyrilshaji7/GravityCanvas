import random
import math
import numpy as np

BODIES = 50
ANIMATE_TIME = 1
MIN = 1e-6
MIN_DISTANCE = 0.2  # Adjust the value as needed


class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Vec2(self.x * other, self.y * other)
        
    def dot(self, v):
        return self.x*v.x + self.y*v.y
    
    def get_length(self):
        return np.sqrt(self.dot(self) )

class Body:
    def __init__(self, pos, vel, mass):
        self.pos = pos
        self.vel = vel
        self.mass = mass
        self.acc = Vec2(0, 0)

    def update(self, dt):
        self.pos.x += self.vel.x * dt
        self.pos.y += self.vel.y * dt
        self.vel.x += self.acc.x * dt
        self.vel.y += self.acc.y * dt
        self.acc = Vec2(0, 0)




class Simulation:
    DT = 0.01

    def __init__(self, n):
        random.seed(time.time())
        self.bodies = []
        self.bodies_destroyed = 0
        for _ in range(n):
            # creating random positions, velocities and masses
            a = random.random() * 2 * math.pi
            sin_a = math.sin(a)
            cos_a = math.cos(a)
            r = sum([random.random() for _ in range(6)]) / 3.0 - 1.0
            r = abs(r)
            pos = Vec2(cos_a, sin_a) * (n ** 0.5) * 10.0 * r
            vel = Vec2(sin_a, -cos_a)
            mass = 30
            body = Body(pos, vel, mass)
            self.bodies.append(body)

        for i in range(n):
            # finding length/magnitude of vec2
            mag = math.sqrt(self.bodies[i].pos.x ** 2 + self.bodies[i].pos.y ** 2)
            v = (i / mag) - math.sqrt(2.0)

            self.bodies[i].vel = Vec2(self.bodies[i].vel.x * v, self.bodies[i].vel.y * v)
    
    def update(self):
        bodies_to_destroy = set()  # Keep track of bodies to destroy
        for i, body1 in enumerate(self.bodies):
            for j, body2 in enumerate(self.bodies):
                if i != j and j not in bodies_to_destroy:
                    p1 = body1.pos
                    p2 = body2.pos
                    m2 = body2.mass

                    r = Vec2(p2.x - p1.x, p2.y - p1.y)
                    r_norm = r.get_length()
                    mag_sq = r.x ** 2 + r.y ** 2
                    mag = math.sqrt(mag_sq)
                    a1 = r * (m2 / (max(mag_sq, MIN) * mag)) 
                    body1.acc.x += a1.x
                    body1.acc.y += a1.y

                    # Check if bodies are too close and mark them for destruction
                    if mag < MIN_DISTANCE:
                        bodies_to_destroy.add(i)
                        bodies_to_destroy.add(j)
                        self.bodies_destroyed += 1

        # Destroy marked bodies
        self.bodies = [body for i, body in enumerate(self.bodies) if i not in bodies_to_destroy]

        for body in self.bodies:
            body.update(self.DT)


# code to display animation using tkinter
#######################################################################


import time
from tkinter import simpledialog
import tkinter as tk
import collections
import statistics


root = tk.Tk()
root.title("Bodies Animation")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

num_of_bodies = simpledialog.askinteger("Input", "Number of bodies: ")

sim = Simulation(num_of_bodies)

canvas = tk.Canvas(root, width=screen_width, height=screen_height)
canvas.pack()

my_queue = collections.deque(maxlen=1000)

def update():
    time_start = time.time()
    sim.update()
    time_end = max((time.time() - time_start), MIN)
    my_queue.append(min(1 / time_end, 999))
    real_time_fps = statistics.mean(data=my_queue)

    text = f"FPS: {real_time_fps:.1f}\n Bodies Start = {num_of_bodies} \n Bodies Left = {num_of_bodies - sim.bodies_destroyed}"

    canvas.delete("all") 
    canvas.create_text(screen_width/2, 10, text=text, fill="black", anchor="n")
    for body in sim.bodies:
        x, y = body.pos.x * 20 + screen_width/2, body.pos.y * 20 + screen_height/2  # Scale and shift for display
        canvas.create_oval(x - 7, y - 7, x + 7, y + 7, fill="red", )
    # for body in sim.bodies:
    #     x, y = body.pos.x * 20 + screen_width/2, body.pos.y * 20 + screen_height/2  # Scale and shift for display
    #     # Calculate acceleration magnitude
    #     acc_magnitude = 0
    #     # Map acceleration magnitude to a color (e.g., from blue to red)
    #     color_value = int(255 * min(acc_magnitude / 10.0, 1.0))
    #     color = "#{:02X}00{:02X}".format(255 - color_value, color_value)
        
    #     canvas.create_oval(x - 7, y - 7, x + 7, y + 7, fill=color)


def animate():
    update()
    root.after(ANIMATE_TIME, animate)  
    
animate()
root.mainloop()


