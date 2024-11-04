import random
from random import *

from OpenGL.GL import *
from OpenGL.GLU import *

import math
from math import *

import numpy

class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __len__(self):
        return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    
    def normalize(self):
        length = self.__len__()
        self.x /= length
        self.y /= length
        self.z /= length

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vector(self.y*other.z - self.z*other.y, self.z*other.x - self.x*other.z, self.x*other.y - self.y*other.x)


class Light:
    def __init__(self,position = [],diffuse = [],specular=[],ambient=[]):
        self.position = position
        self.diffuse = diffuse
        self.specular = specular
        self.ambient = ambient

class Cube:
    def __init__(self):
        vertex_array = [
            -0.5, -0.5,  0.5,  0.0,  0.0,  1.0,
            -0.5,  0.5,  0.5,  0.0,  0.0,  1.0,
             0.5,  0.5,  0.5,  0.0,  0.0,  1.0,
            -0.5, -0.5,  0.5,  0.0,  0.0,  1.0,
             0.5,  0.5,  0.5,  0.0,  0.0,  1.0,
             0.5, -0.5,  0.5,  0.0,  0.0,  1.0,

            -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,
            -0.5,  0.5, -0.5,  0.0,  0.0, -1.0,
             0.5,  0.5, -0.5,  0.0,  0.0, -1.0,
            -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,
             0.5,  0.5, -0.5,  0.0,  0.0, -1.0,
             0.5, -0.5, -0.5,  0.0,  0.0, -1.0,

            -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,
            -0.5, -0.5,  0.5, -1.0,  0.0,  0.0,
            -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,
            -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,
            -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,
            -0.5,  0.5, -0.5, -1.0,  0.0,  0.0,

             0.5, -0.5, -0.5,  1.0,  0.0,  0.0,
             0.5, -0.5,  0.5,  1.0,  0.0,  0.0,
             0.5,  0.5,  0.5,  1.0,  0.0,  0.0,
             0.5, -0.5, -0.5,  1.0,  0.0,  0.0,
             0.5,  0.5,  0.5,  1.0,  0.0,  0.0,
             0.5,  0.5, -0.5,  1.0,  0.0,  0.0,

            -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,
             0.5,  0.5, -0.5,  0.0,  1.0,  0.0,
             0.5,  0.5,  0.5,  0.0,  1.0,  0.0,
            -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,
             0.5,  0.5,  0.5,  0.0,  1.0,  0.0,
            -0.5,  0.5,  0.5,  0.0,  1.0,  0.0,

            -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,
             0.5, -0.5, -0.5,  0.0, -1.0,  0.0,
             0.5, -0.5,  0.5,  0.0, -1.0,  0.0,
            -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,
             0.5, -0.5,  0.5,  0.0, -1.0,  0.0,
            -0.5, -0.5,  0.5,  0.0, -1.0,  0.0,
        ]

        self.trans_x = 0
        self.trans_y = 0
        self.trans_z = 0

        self.scale_x = 0
        self.scale_y = 0
        self.scale_z = 0
        
        self.specular_r = 0
        self.specular_g = 0
        self.specular_b = 0
        self.diffuse_r = 0
        self.diffuse_g = 0
        self.diffuse_b = 0
        self.ambient_r = 0
        self.ambient_g = 0
        self.ambient_b = 0
        self.emission_r = 0
        self.emission_g = 0
        self.emission_b = 0
        self.shine = 0

        self.vertex_count = len(vertex_array) // 6

        self.vertex_buffer_id = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer_id)
        glBufferData(GL_ARRAY_BUFFER, numpy.array(vertex_array, dtype='float32'), GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def draw(self, shader):
        shader.set_attribute_buffers(self.vertex_buffer_id)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

class Sphere:
    def __init__(self, textures=False, stacks = 12, slices = 23):

        self.trans_x = 0
        self.trans_y = 0
        self.trans_z = 0

        self.scale_x = 0
        self.scale_y = 0
        self.scale_z = 0
        
        self.rotate_x = 0
        self.rotate_y = 0
        self.rotate_z = 0

        self.specular_r = 0
        self.specular_g = 0
        self.specular_b = 0

        self.diffuse_r = 0
        self.diffuse_g = 0
        self.diffuse_b = 0

        self.ambient_r = 0
        self.ambient_g = 0
        self.ambient_b = 0

        self.emission_r = 0
        self.emission_g = 0
        self.emission_b = 0
        self.shine = 0

        self.texture = textures

        vertex_array = []
        self.slices = slices

        stack_interval = pi/stacks
        slice_interval = 2.0* pi / slices
        self.vertex_count = 0

        for stack_count in range(stacks):
            stack_angle = stack_count * stack_interval
            for slice_count in range(slices +1):
                slice_angle = slice_count * slice_interval
                
                for _ in range(2):
                    vertex_array.append(sin(stack_angle) * cos(slice_angle))
                    vertex_array.append(cos(stack_angle))
                    vertex_array.append(sin(stack_angle) * sin(slice_angle))

                if (textures):
                    vertex_array.append(slice_count / slices)
                    vertex_array.append(stack_count / stacks)

                for _ in range(2):
                    vertex_array.append(sin(stack_angle + stack_interval) * cos(slice_angle))
                    vertex_array.append(cos(stack_angle + stack_interval))
                    vertex_array.append(sin(stack_angle + stack_interval) * sin(slice_angle))

                if (textures):
                    vertex_array.append(slice_count / slices)
                    vertex_array.append((stack_count + 1 )/ stacks)

                self.vertex_count += 2
            
        self.vertex_buffer_id = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer_id)
        glBufferData(GL_ARRAY_BUFFER, numpy.array(vertex_array, dtype='float32'), GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def draw(self, shader):
        if (self.texture):
            shader.set_attribute_buffers_with_uv(self.vertex_buffer_id)
        else:
            shader.set_attribute_buffers(self.vertex_buffer_id)

        for i in range(0,self.vertex_count,(self.slices +1 ) * 2):
            glDrawArrays(GL_TRIANGLE_STRIP,i,(self.slices + 1) * 2)
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

class Material:
    def __init__(self, diffuse = None, specular = None, shininess = None):
        self.diffuse = Color(0.0, 0.0, 0.0) if diffuse == None else diffuse
        self.specular = Color(0.0, 0.0, 0.0) if specular == None else specular
        self.shininess = 1 if shininess == None else shininess

class Bullet:
    def __init__(self, x, y ,z, dr, dg, db, sr, sg, sb, direction_x, direction_y, direction_z , player_id = 0):
        self.body = Sphere()
        self.body.trans_x = x
        self.body.trans_y = y
        self.body.trans_z = z
        self.body.scale_x = 0.2
        self.body.scale_y = 0.2
        self.body.scale_z = 0.2
        self.body.rotate_x = 0
        self.body.rotate_y = 0
        self.body.rotate_z = 0
        self.body.diffuse_r = dr
        self.body.diffuse_g = dg
        self.body.diffuse_b = db
        self.body.specular_r = sr
        self.body.specular_g = sg
        self.body.specular_b = sb
        self.body.ambient_r = 0
        self.body.ambient_g = 0
        self.body.ambient_b = 0
        self.body.emission_r = 0
        self.body.emission_g = 0
        self.body.emission_b = 0
        self.body.shine = 5

        self.speed = 12
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.direction_z = direction_z

        self.player_id = player_id
    
    def move(self, delta_time, arr = [], remove = 0, height = 0):
        self.body.trans_x += self.direction_x * self.speed * delta_time
        self.body.trans_y += self.direction_y * self.speed * delta_time
        self.body.trans_z += self.direction_z * self.speed * delta_time

        if (self.body.trans_y < height and self.body.trans_y > 0):
            for box in arr:
                if (box[0] + remove) <= self.body.trans_x <= (box[1] - remove) and (box[2] + remove) <= self.body.trans_z <= (box[3] - remove):
                    return -1
        else:
            if (self.body.trans_y < -5 or self.body.trans_y > (height + 5)):
                return -1

        return 1

    """Gets the bullets data required for the server"""
    def get_data(self) -> dict:
        data = {
            "POSITION" : [self.body.trans_x,self.body.trans_y,self.body.trans_z],
            "DIRECTION": [self.direction_x,self.direction_y,self.direction_z],
            "COLOR": [self.body.diffuse_r,self.body.diffuse_g,self.body.diffuse_b],
            "ID": self.player_id
        }
        return data


class MeshModel:
    def __init__(self):
        self.vertex_arrays = dict()
        self.mesh_materials = dict()
        self.materials = dict()
        self.vertex_counts = dict()
        self.vertex_buffer_ids = dict()

    def add_vertex(self, mesh_id, position, normal, uv = None):
        if mesh_id not in self.vertex_arrays:
            self.vertex_arrays[mesh_id] = []
            self.vertex_counts[mesh_id] = 0
        self.vertex_arrays[mesh_id] += [position.x, position.y, position.z, normal.x, normal.y, normal.z]
        self.vertex_counts[mesh_id] += 1

    def set_mesh_material(self, mesh_id, mat_id):
        self.mesh_materials[mesh_id] = mat_id

    def add_material(self, mat_id, mat):
        self.materials[mat_id] = mat
    
    def set_opengl_buffers(self):
        for mesh_id in self.mesh_materials.keys():
            self.vertex_buffer_ids[mesh_id] = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer_ids[mesh_id])
            glBufferData(GL_ARRAY_BUFFER, numpy.array(self.vertex_arrays[mesh_id], dtype='float32'), GL_STATIC_DRAW)
            glBindBuffer(GL_ARRAY_BUFFER, 0)

    def draw(self, shader):
        for mesh_id, mesh_material in self.mesh_materials.items():
            material = self.materials[mesh_material]
            shader.set_material_diffuse(material.diffuse.r, material.diffuse.g, material.diffuse.b)
            shader.set_material_specular(material.specular.r, material.specular.g, material.specular.b)
            shader.set_material_shininess(material.shininess)
            shader.set_attribute_buffers(self.vertex_buffer_ids[mesh_id])
            glDrawArrays(GL_TRIANGLES, 0, self.vertex_counts[mesh_id])
            glBindBuffer(GL_ARRAY_BUFFER, 0)