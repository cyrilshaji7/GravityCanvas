import random
import math
import numpy as np

BODIES = 15
ANIMATE_TIME = 1

TAU = 2 * math.pi

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

MIN = 1e-6

class Simulation:
    DT = 0.01

    def __init__(self, n):
        random.seed(0)
        self.bodies = []
        for _ in range(n):
            a = random.random() * TAU
            sin_a = math.sin(a)
            cos_a = math.cos(a)
            r = sum([random.random() for _ in range(6)]) / 3.0 - 1.0
            r = abs(r)
            pos = Vec2(cos_a, sin_a) * (n ** 0.5) * 10.0 * r
            vel = Vec2(sin_a, -cos_a)
            body = Body(pos, vel, 1.0)
            self.bodies.append(body)

        self.bodies.sort(key=lambda body: body.pos.x ** 2 + body.pos.y ** 2)
        for i in range(n):
            mag = math.sqrt(self.bodies[i].pos.x ** 2 + self.bodies[i].pos.y ** 2)
            v = (i / mag) - math.sqrt(2.0)

            self.bodies[i].vel = Vec2(self.bodies[i].vel.x * v, self.bodies[i].vel.y * v)

    def update(self):
        for i in range(len(self.bodies)):
            p1 = self.bodies[i].pos
            for j in range(len(self.bodies)):
                if i != j:
                    p2 = self.bodies[j].pos
                    m2 = self.bodies[j].mass

                    r = Vec2(p2.x - p1.x, p2.y - p1.y)
                    r_norm = r.get_length()
                    # print(r)
                    mag_sq = r.x ** 2 + r.y ** 2
                    mag = math.sqrt(mag_sq)
                    a1 = r * (m2 / (max(mag_sq, MIN) * mag)) 
                    self.bodies[i].acc.x += a1.x
                    self.bodies[i].acc.y += a1.y

            

        for i in range(len(self.bodies)):
            self.bodies[i].update(self.DT)


import time

sim = Simulation(BODIES)

import tkinter as tk



root = tk.Tk()
root.title("Bodies Animation")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Create a canvas for drawing the positions
canvas = tk.Canvas(root, width=screen_width, height=screen_height)
canvas.pack()

def update():
    time_start = time.time()
    sim.update()
    time_end = max((time.time() - time_start), MIN)
    text = f"FPS: {1 / time_end:.2f}" + f"\nREAL TIME FPS: {1000/ANIMATE_TIME}"


    canvas.delete("all") 
    canvas.create_text(screen_width/2, 10, text=text, fill="black", anchor="n")
    for body in sim.bodies:
        x, y = body.pos.x * 20 + screen_width/2, body.pos.y * 20 + screen_height/2  # Scale and shift for display
        canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="red")

def animate():
    update()
    root.after(ANIMATE_TIME, animate)  
    
animate()
root.mainloop()]

