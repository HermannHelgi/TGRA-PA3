
from math import * # trigonometry

from Base3DObjects import *

class ModelMatrix:
    def __init__(self):
        self.matrix = [ 1, 0, 0, 0,
                        0, 1, 0, 0,
                        0, 0, 1, 0,
                        0, 0, 0, 1 ]
        self.stack = []
        self.stack_count = 0
        self.stack_capacity = 0

    def load_identity(self):
        self.matrix = [ 1, 0, 0, 0,
                        0, 1, 0, 0,
                        0, 0, 1, 0,
                        0, 0, 0, 1 ]

    def copy_matrix(self):
        new_matrix = [0] * 16
        for i in range(16):
            new_matrix[i] = self.matrix[i]
        return new_matrix

    def add_transformation(self, matrix2):
        counter = 0
        new_matrix = [0] * 16
        for row in range(4):
            for col in range(4):
                for i in range(4):
                    new_matrix[counter] += self.matrix[row*4 + i]*matrix2[col + 4*i]
                counter += 1
        self.matrix = new_matrix

    def add_nothing(self):
        other_matrix = [1, 0, 0, 0,
                        0, 1, 0, 0,
                        0, 0, 1, 0,
                        0, 0, 0, 1]
        self.add_transformation(other_matrix)
    
    def add_translation(self, x=0, y=0, z=0):
        other_matrix = [1, 0, 0, x,
                        0, 1, 0, y,
                        0, 0, 1, z,
                        0, 0, 0, 1]
        self.add_transformation(other_matrix)
    
    def add_scale(self, x=1, y=1, z=1):
        other_matrix = [x, 0, 0, 0,
                        0, y, 0, 0,
                        0, 0, z, 0,
                        0, 0, 0, 1]
        self.add_transformation(other_matrix)

    def add_rotation_x(self, theta=0):
        theta = self.degrees_to_radians(theta)
        other_matrix = [1, 0, 0, 0,
                        0, cos(theta), -sin(theta), 0,
                        0, sin(theta), cos(theta), 0,
                        0, 0, 0, 1]
        self.add_transformation(other_matrix)

    def add_rotation_y(self, theta=0):
        theta = self.degrees_to_radians(theta)
        other_matrix = [cos(theta), 0, sin(theta), 0,
                        0, 1, 0, 0,
                        -sin(theta), 0, cos(theta), 0,
                        0, 0, 0, 1]
        self.add_transformation(other_matrix)
    
    def add_rotation_z(self, theta=0):
        theta = self.degrees_to_radians(theta)
        other_matrix = [cos(theta), -sin(theta), 0, 0,
                        sin(theta), cos(theta), 0, 0,
                        0, 0, 1, 0,
                        0, 0, 0, 1]
        self.add_transformation(other_matrix)

    # YOU CAN TRY TO MAKE PUSH AND POP (AND COPY) LESS DEPENDANT ON GARBAGE COLLECTION
    # THAT CAN FIX SMOOTHNESS ISSUES ON SOME COMPUTERS
    def push_matrix(self):
        self.stack.append(self.copy_matrix())

    def pop_matrix(self):
        self.matrix = self.stack.pop()

    def degrees_to_radians(self, degrees):
        return (degrees * pi / 180)

    # This operation mainly for debugging
    def __str__(self):
        ret_str = ""
        counter = 0
        for _ in range(4):
            ret_str += "["
            for _ in range(4):
                ret_str += " " + str(self.matrix[counter]) + " "
                counter += 1
            ret_str += "]\norm_vector"
        return ret_str

class ViewMatrix:
    def __init__(self):
        self.eye = Point(0, 0, 0)
        self.u = Vector(1, 0, 0)
        self.v = Vector(0, 1, 0)
        self.norm_vector = Vector(0, 0, 1)

        self.current_pitch = 0.0
        self.max_pitch = math.radians(90)
        self.min_pitch = math.radians(-90)

    def slide(self, del_u, del_v, del_n, canFly, arr=[], coffee=[], coffee_range=0):
        old_x = self.eye.x
        old_z = self.eye.z
        self.eye.x += self.u.x * del_u + self.v.x * del_v + self.norm_vector.x * del_n
        self.eye.z += self.u.z * del_u + self.v.z * del_v + self.norm_vector.z * del_n
        new_x = self.eye.x
        new_z = self.eye.z

        for box in arr:
            if box[0] <= self.eye.x <= box[1] and box[2] <= self.eye.z <= box[3]:
                hit_x, clamp_x = self.check_hit_and_clamp(old_x, new_x, box[0], box[1])
                hit_z, clamp_z = self.check_hit_and_clamp(old_z, new_z, box[2], box[3])
                
                if hit_x >= 0 or hit_z >= 0:
                    if hit_x >= 0:
                        self.eye.x = clamp_x
                    if hit_z >= 0:
                        self.eye.z = clamp_z

        coffee_to_remove = -1
        for index, coffee_cup in enumerate(coffee):
            if (sqrt((coffee_cup[0] - self.eye.x) ** 2 + (coffee_cup[1] - self.eye.z) ** 2) < coffee_range):
                coffee_to_remove = index

        if (canFly):
            self.eye.y += self.u.y * del_u + self.v.y * del_v + self.norm_vector.y * del_n
        
        return coffee_to_remove

    def copy_coords(self, another_view_matrix : 'ViewMatrix'):
        self.eye.x = another_view_matrix.eye.x
        self.eye.z = another_view_matrix.eye.z

    def check_hit_and_clamp(self, old_pos, new_pos, min_bound, max_bound):
        EPSILON = 0.0001
        hit = -1
        clamp_pos = new_pos

        if old_pos < min_bound and new_pos >= min_bound:
            hit = (min_bound - old_pos) / (new_pos - old_pos)
            clamp_pos = min_bound - EPSILON
        if old_pos > max_bound and new_pos <= max_bound: 
            hit = (max_bound - old_pos) / (new_pos - old_pos)
            clamp_pos = max_bound + EPSILON

        return hit, clamp_pos

    def isNegative(self, num):
        if (num < 0):
            return -1
        else:
            return 1

    def rotate_on_floor(self, angle):
        angle = self.degrees_to_radians(angle)
        temp = cos(angle) * self.u.x + sin(angle) * self.u.z
        self.u.z = cos(angle) * self.u.z - sin(angle) * self.u.x
        self.u.x = temp

        temp = cos(angle) * self.v.x + sin(angle) * self.v.z
        self.v.z = cos(angle) * self.v.z - sin(angle) * self.v.x
        self.v.x = temp

        temp = cos(angle) * self.norm_vector.x + sin(angle) * self.norm_vector.z
        self.norm_vector.z = cos(angle) * self.norm_vector.z - sin(angle) * self.norm_vector.x
        self.norm_vector.x = temp
    
    def pitch(self, angle):
        angle = self.degrees_to_radians(angle)
        new_pitch = self.current_pitch + angle

        if new_pitch > self.max_pitch:
            angle = self.max_pitch - self.current_pitch
            self.current_pitch = self.max_pitch
        elif new_pitch < self.min_pitch:
            angle = self.min_pitch - self.current_pitch
            self.current_pitch = self.min_pitch
        else:
            self.current_pitch = new_pitch

        c = cos(angle)
        s = sin(angle)

        temp = self.v * c + self.norm_vector * s
        self.norm_vector = self.v * -s + self.norm_vector * c
        self.v = temp

    def degrees_to_radians(self, degrees):
        return (degrees * pi / 180)

    def look(self, eye, center, up):
        self.eye = eye
        self.norm_vector = (eye - center)
        self.norm_vector.normalize()
        self.u = up.cross(self.norm_vector)
        self.u.normalize()
        self.v = self.norm_vector.cross(self.u)

    def get_matrix(self):
        minusEye = Vector(-self.eye.x, -self.eye.y, -self.eye.z)
        return [self.u.x, self.u.y, self.u.z, minusEye.dot(self.u),
                self.v.x, self.v.y, self.v.z, minusEye.dot(self.v),
                self.norm_vector.x, self.norm_vector.y, self.norm_vector.z, minusEye.dot(self.norm_vector),
                0,        0,        0,        1]


# The ProjectionMatrix class builds transformations concerning
# the camera's "lens"

class ProjectionMatrix:
    def __init__(self):
        self.left = -1
        self.right = 1
        self.bottom = -1
        self.top = 1
        self.near = -1
        self.far = 1

    def set_perspective(self, fovy, aspect_ratio, near, far):
        self.near = near
        self.far = far
        self.top = near * tan((fovy * pi / 180)/ 2)
        self.bottom = -self.top
        self.right = self.top * aspect_ratio
        self.left = -self.right

    def get_matrix(self):
        A = (2 * self.near) / (self.right - self.left) 
        B = (self.right + self.left) / (self.right - self.left)
        C = (2 * self.near) / (self.top - self.bottom)
        D = (self.top + self.bottom) / (self.top - self.bottom)
        E = -(self.far + self.near) / (self.far - self.near)
        F = (-2 * self.far * self.near) / (self.far - self.near)

        return [A,0,B,0,
                0,C,D,0,
                0,0,E,F,
                0,0,-1,0]