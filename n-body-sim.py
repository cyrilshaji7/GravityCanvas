import random
import math
import numpy as np
import time

# animation update time in ms
ANIMATE_TIME = 10
# dampening to avoid dividing by zero and to avoid particles flying away at lightspeed
MIN = 1e-8
# dampening to merge bodies
MIN_DISTANCE = .2  
# maximum mass limiter
MASS_MAX = 200
# time frame for diffrentiation determines render speed (smaller the better but performance hits)
DT = 0.001
# size of the particles
SIZE = 7
# length of the tracer line
TRACER_LEN = 25
# universal gravitational constant
G = 1

class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Vec2(self.x * other, self.y * other)
        
    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)
        
    def dot(self, v):
        return self.x*v.x + self.y*v.y
    
    def get_length(self):
        return np.sqrt(self.dot(self) )
    
    def __truediv__(self, scalar):
        return Vec2(self.x / scalar, self.y / scalar)
    
    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self
    
class Body:
    def __init__(self, pos, vel, mass):
        self.pos = pos
        self.vel = vel
        self.mass = mass
        self.acc = Vec2(0, 0)
        self.prev_acc = Vec2(0, 0)

    def update(self):
        self.pos.x += self.vel.x * DT
        self.pos.y += self.vel.y * DT
        self.vel.x += self.acc.x * DT
        self.vel.y += self.acc.y * DT
        self.acc = Vec2(0, 0)

    def kinetic_energy(self):
        speed = self.vel.get_length()
        return 0.5 * self.mass * speed**2
    

# the big boy class which does most of the work to approximate acceleration of every particle 
class Simulation:

    def __init__(self, n):
        random.seed(time.time())
        self.bodies_initial = n
        self.bodies = []
        self.bodies_destroyed = 0
        self.collision = True
        self.collisions = 0
        self.mean_distance = 0
        for _ in range(n):
            # creating random positions, velocities and masses
            a = random.random() * 2 * math.pi
            sin_a = math.sin(a)
            cos_a = math.cos(a)
            r = sum([random.random() for _ in range(6)]) / 3.0 - 1.0
            r = abs(r)
            pos = Vec2(cos_a, sin_a) * (math.sqrt(n)) * 10.0 * r
            vel = Vec2(sin_a, -cos_a)
            mass = random.randint(10, MASS_MAX)
            body = Body(pos, vel, mass)
            self.bodies.append(body)

        for i in range(n):
            # finding length/magnitude of vec2
            mag = math.sqrt(self.bodies[i].pos.x ** 2 + self.bodies[i].pos.y ** 2)
            v = (i / mag) - math.sqrt(2.0)

            self.bodies[i].vel = Vec2(self.bodies[i].vel.x * v, self.bodies[i].vel.y * v)

    def total_kinetic_energy(self):
        total_KE = sum(body.kinetic_energy() for body in self.bodies)
        return total_KE

    def merge_bodies(self, body1, body2):
        # calculate new position, velocity, and mass for the merged body
        total_mass = body1.mass + body2.mass
        new_pos = Vec2((body1.pos.x * body1.mass + body2.pos.x * body2.mass) / total_mass, (body1.pos.y * body1.mass + body2.pos.y * body2.mass) / total_mass)
        new_vel = Vec2((body1.vel.x * body1.mass + body2.vel.x * body2.mass) / total_mass, (body1.vel.y * body1.mass + body2.vel.y * body2.mass) / total_mass)

        merged_body = Body(new_pos, new_vel, total_mass)
        return merged_body
    
                       
    def euler_update(self):
        total_mass = 0
        bodies_to_destroy = set()
        bodies_to_merge = set()
        total_distance = 0
        num_pairs = 0
        for i in range(len(self.bodies)):
            total_mass += self.bodies[i].mass
            p1 = self.bodies[i].pos
            for j in range(i+1, len(self.bodies)):
                if i != j and j not in bodies_to_merge:
                    p2 = self.bodies[j].pos
                    m2 = self.bodies[j].mass

                    r = Vec2(p2.x - p1.x, p2.y - p1.y)
                    mag_sq = r.x ** 2 + r.y ** 2
                    mag = math.sqrt(mag_sq)
                    a1 = r * (m2 / (max(mag_sq, MIN) * mag)) 
                    self.bodies[i].acc.x += a1.x
                    self.bodies[i].acc.y += a1.y

                    # distance = math.sqrt((self.bodies[i].pos.x - self.bodies[j].pos.x)**2 + (self.bodies[i].pos.y - self.bodies[j].pos.y)**2)
                    # total_distance += distance
                    # num_pairs += 1
                    
                    # self.mean_distance = total_distance / num_pairs
                    if mag < MIN_DISTANCE and self.collision:
                        self.collisions += 1
                        merged_body = self.merge_bodies(self.bodies[i], self.bodies[j])
                        bodies_to_destroy.add(i)
                        bodies_to_destroy.add(j)
                        bodies_to_merge.add(len(self.bodies))  # mark the insert to insert merged body
                        self.bodies_destroyed += 2
                        break

        # remove bodies flagged for destruction
        self.bodies = [body for idx, body in enumerate(self.bodies) if idx not in bodies_to_destroy]

        # add merged bodies back to the list
        for idx in sorted(list(bodies_to_merge), reverse=True):
            self.bodies.insert(idx, merged_body)

        for body in self.bodies:
            body.update()


    def verlet_update(self):
        dt_squared = DT * DT

        for body in self.bodies:
            # updating position using verlet method of integration 
            body.pos.x += body.vel.x * DT + 0.5 * body.acc.x * dt_squared
            body.pos.y += body.vel.y * DT + 0.5 * body.acc.y * dt_squared

        for i in range(len(self.bodies)):
            for j in range(i + 1, len(self.bodies)):
                r = self.bodies[j].pos - self.bodies[i].pos
                mag_sq = r.x ** 2 + r.y ** 2
                mag = math.sqrt(mag_sq)

                # newtons laws of gravitation
                force_magnitude = G * (self.bodies[i].mass * self.bodies[j].mass) / max(mag_sq, MIN_DISTANCE)
                force = r * (force_magnitude / mag)

                # Update accelerations
                self.bodies[i].acc += force / self.bodies[i].mass
                self.bodies[j].acc -= force / self.bodies[j].mass

        for body in self.bodies:
            # Update velocities using Verlet integration
            body.vel.x += 0.5 * (body.acc.x + body.prev_acc.x) * DT
            body.vel.y += 0.5 * (body.acc.y + body.prev_acc.y) * DT

            # Save current acceleration for the next iteration
            body.prev_acc = body.acc
            body.acc = Vec2(0, 0)  # Reset acceleration for the next iteration



            
    


# code to display animation using tkinter
#######################################################################


import time
from tkinter import simpledialog
import tkinter as tk
from tkinter import ttk
import collections
import statistics

class Application:
    my_queue = collections.deque(maxlen=100)

    def __init__(self, master, sim, computation_type):
        self.master = master
        self.sim = sim
        self.animation_running = False  # Flag to track animation state
        self.create_menu()
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        self.canvas = tk.Canvas(master, width=self.screen_width, height=self.screen_height, bg='black')
        self.computation_type = computation_type
        self.canvas.pack()
        self.real_time_fps = 0
        self.view_center = Vec2(0, 0)
        self.scale_factor = 1.0
        self.bind_mouse_events()
        self.traces = {}
        self.tracer_toggled = True
        self.view_stats = True


    def bind_mouse_events(self):
        self.canvas.bind("<B1-Motion>", self.pan_view)
        self.canvas.bind("<ButtonPress-1>", self.mouse_press)
        self.canvas.bind("<MouseWheel>", self.zoom)

    def mouse_press(self, event):
        self.last_x = event.x
        self.last_y = event.y

    def pan_view(self, event):
        dx = (event.x - self.last_x) / 20
        dy = (event.y - self.last_y) / 20
        self.last_x = event.x
        self.last_y = event.y

        self.view_center.x -= dx / self.scale_factor
        self.view_center.y -= dy / self.scale_factor
        self.display_bodies()

    def zoom(self, event):
        delta = event.delta
        if delta > 0:
            self.scale_factor *= 1.1  
        else:
            self.scale_factor /= 1.1 

        self.display_bodies()

    def create_menu(self):
        menubar = ttk.Frame(self.master)
        menubar.pack(side="top", fill="x")

        # Add labels for sections
        ttk.Label(menubar, text="Menu", font=("Helvetica", 16)).pack(side="left", padx=(10, 20))

        # Create buttons for menu items
        ttk.Button(menubar, text="New", command=self.new).pack(side="left", padx=5)
        ttk.Button(menubar, text="Animation Delay", command=self.edit_animate_speed).pack(side="left", padx=5)
        ttk.Button(menubar, text="Tracer Toggle", command=self.tracerToggle).pack(side="left", padx=5)
        ttk.Button(menubar, text="Edit Tracer Length", command=self.edit_tracer_length).pack(side="left", padx=5)
        ttk.Button(menubar, text="Toggle Stats for nerds", command=self.viewStats).pack(side="left", padx=5)
        ttk.Button(menubar, text="Toggle Collisions", command=self.toggle_collisions).pack(side="left", padx=5)
        ttk.Button(menubar, text="Computation Method", command=self.update_type).pack(side="left", padx=5)
        ttk.Button(menubar, text="Exit", command=self.master.destroy).pack(side="right", padx=5)

    
    def new(self):
        new_num_of_bodies = simpledialog.askinteger("New Simulation", "Enter number of bodies:", initialvalue=len(self.sim.bodies))
        if new_num_of_bodies is not None:
            self.sim.bodies_initial = new_num_of_bodies
            self.master.after_cancel(self.animation_id)
            self.animation_running = False
            self.my_queue.clear()
            self.sim = Simulation(self.sim.bodies_initial)
            self.display_bodies()
            self.start_animation()

    def edit_animate_speed(self):
        global ANIMATE_TIME
        new_animate_time = simpledialog.askfloat("Edit Animation Delay", "Enter the new delay (in ms)\nDetermines how fast frames are shown:", initialvalue=ANIMATE_TIME)

        if new_animate_time is not None:
            ANIMATE_TIME = new_animate_time

    def viewStats(self):
        self.view_stats = not self.view_stats
        
    def update_type(self):
        new_type = simpledialog.askinteger("New Computation", "Enter new Computation method\n1: Euler\n2: Verlet", initialvalue=self.computation_type)
        if new_type is not None:
            self.computation_type = new_type

    def update_animation(self):
        ############## HERE BUG
        methods = {1: "Euler", 2: "Verlet",}
        time_start = time.time()
        if self.computation_type == 1:
            self.sim.euler_update()
        else:
            self.sim.verlet_update()
        time_end = max((time.time() - time_start), MIN)
        res = min(1 / time_end, 999)
        self.my_queue.append(res)
        self.real_time_fps = statistics.geometric_mean(self.my_queue)
        self.display_bodies()

        self.fps_label = tk.Label(self.master, text=f"FPS: {self.real_time_fps:.0f}\nComputation Method = {methods.get(self.computation_type)}\nN Initial = {self.sim.bodies_initial}\nCollisions = {self.sim.collisions}\nBody-Collision Ratio = {((self.sim.bodies_initial - self.sim.collisions)/self.sim.bodies_initial ):.2f}\nTotal Kinetic Energy: {self.sim.total_kinetic_energy():.0f}\nMean Distance Between Bodies: {self.sim.mean_distance:.2f}", anchor="w", justify="left", bg='black', fg='white')
         
        if self.view_stats:
            pass
        else:
            self.fps_label = tk.Label(self.master, text=f"FPS: {self.real_time_fps:.0f}\nComputation Method = {methods.get(self.computation_type)}\nN Initial = {self.sim.bodies_initial}\nCollisions = {self.sim.collisions}\nBody-Collision Ratio = {((self.sim.bodies_initial - self.sim.collisions)/self.sim.bodies_initial ):.2f}\nTotal Kinetic Energy: {self.sim.total_kinetic_energy():.0f}\nMean Distance Between Bodies: {self.sim.mean_distance:.2f}", anchor="w", justify="left", bg='black', fg='black')
        self.fps_label.place(x=10, y=40)


        if self.animation_running:
            self.animation_id = self.master.after(int(ANIMATE_TIME), self.update_animation)

    def start_animation(self):
        # Set the animation flag and kickstart the animation loop
        self.animation_running = True
        self.update_animation()

    def tracer(self, body, color, x, y):
        if body in self.traces:
            trace = self.traces[body]
            trace.append((x, y))
            self.canvas.create_line(trace, fill=color)
            # Limit the length of the trace
            if len(trace) > TRACER_LEN:
                trace.pop(0)
        else:
            self.traces[body] = [(x, y)]

    def tracerToggle(self):
        self.tracer_toggled =  not self.tracer_toggled

    def toggle_collisions(self):
        sim.collision = not sim.collision

    def edit_tracer_length(self):
        global TRACER_LEN
        new_length = simpledialog.askfloat("Edit Tracer Length", "Enter the new Tracer Length:", initialvalue=TRACER_LEN)

        if new_length is not None:
            TRACER_LEN = new_length

    def display_bodies(self):
        self.canvas.delete("all")

        for body in self.sim.bodies:
            x = (body.pos.x - self.view_center.x) * 20 * self.scale_factor + self.screen_width / 2
            y = (body.pos.y - self.view_center.y) * 20 * self.scale_factor + self.screen_height / 2

            normalized_mass = body.mass / 100
            color_value = int(255 * normalized_mass)
            color_value = max(0, min(color_value, 255))
            color = "#{:02X}00{:02X}".format(color_value, 255 - color_value)

            
            if self.tracer_toggled:
                self.tracer(body, color, x, y)
            

            self.canvas.create_oval(x - SIZE, y - SIZE, x + SIZE, y + SIZE, fill=color)
            self.canvas.create_text(x, y - SIZE, text=f"{body.mass}", fill="white", anchor="s")



if __name__ == "__main__":
    num_of_bodies = simpledialog.askinteger("Input", "Number of bodies:")
    computation_type = simpledialog.askinteger("Input", "1: Euler\n2: Verlet")
    sim = Simulation(num_of_bodies)

    root = tk.Tk()
    root.title("Bodies Animation")
    
    app = Application(root, sim, computation_type)

    # Start the animation loop
    app.start_animation()

    root.mainloop()

