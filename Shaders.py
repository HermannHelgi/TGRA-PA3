
from OpenGL.GL import *
from math import * # trigonometry

import sys

from Base3DObjects import *

class Shader3D:
    def __init__(self):
        vert_shader = glCreateShader(GL_VERTEX_SHADER)
        shader_file = open(sys.path[0] + "/simple3D.vert")
        glShaderSource(vert_shader,shader_file.read())
        shader_file.close()
        glCompileShader(vert_shader)
        result = glGetShaderiv(vert_shader, GL_COMPILE_STATUS)
        if (result != 1): # shader didn't compile
            print("Couldn't compile vertex shader\nShader compilation Log:\n" + str(glGetShaderInfoLog(vert_shader)))

        frag_shader = glCreateShader(GL_FRAGMENT_SHADER)
        shader_file = open(sys.path[0] + "/simple3D.frag")
        glShaderSource(frag_shader,shader_file.read())
        shader_file.close()
        glCompileShader(frag_shader)
        result = glGetShaderiv(frag_shader, GL_COMPILE_STATUS)
        if (result != 1): # shader didn't compile
            print("Couldn't compile fragment shader\nShader compilation Log:\n" + str(glGetShaderInfoLog(frag_shader)))

        self.renderingProgramID = glCreateProgram()
        glAttachShader(self.renderingProgramID, vert_shader)
        glAttachShader(self.renderingProgramID, frag_shader)
        glLinkProgram(self.renderingProgramID)
        result = glGetProgramiv(self.renderingProgramID, GL_LINK_STATUS)
        if (result != 1): # shaders didn't link
            print("Couldn't link shader program\nLink compilation Log:\n" + str(glGetProgramInfoLog(self.renderingProgramID)))

        self.positionLoc			= glGetAttribLocation(self.renderingProgramID, "a_position")
        glEnableVertexAttribArray(self.positionLoc)

        self.normalLoc = glGetAttribLocation(self.renderingProgramID, "a_normal")
        glEnableVertexAttribArray(self.normalLoc)

        #Light variables
        self.lightPosLoc = glGetUniformLocation(self.renderingProgramID,"u_light_position")
        self.lightDifLoc = glGetUniformLocation(self.renderingProgramID,"u_light_diffuse")
        self.lightSpecLoc = glGetUniformLocation(self.renderingProgramID,"u_light_specular")
        self.lightAmbLoc = glGetUniformLocation(self.renderingProgramID,"u_light_ambient")


        #Material variables
        self.matDifLoc = glGetUniformLocation(self.renderingProgramID,"u_material_diffuse")
        self.matSpecLoc = glGetUniformLocation(self.renderingProgramID,"u_material_specular")
        self.matAmbLoc = glGetUniformLocation(self.renderingProgramID,"u_material_ambient")
        self.matShineLoc = glGetUniformLocation(self.renderingProgramID,"u_shininess")

        self.globalAmbLoc = glGetUniformLocation(self.renderingProgramID,"u_global_ambient")
        self.eyePosLoc = glGetUniformLocation(self.renderingProgramID,"u_eye_pos")

        self.modelMatrixLoc = glGetUniformLocation(self.renderingProgramID, "u_model_matrix")
        self.ViewMatrixLoc = glGetUniformLocation(self.renderingProgramID, "u_view_matrix")
        self.projectionMatrixLoc = glGetUniformLocation(self.renderingProgramID, "u_projection_matrix")

    def set_eye_pos(self,x,y,z):
        glUniform4f(self.eyePosLoc,x,y,z,0.0)
    def set_global_ambient(self,r,g,b):
        glUniform4f(self.globalAmbLoc,r,g,b,1.0)

    def set_material_diffuse(self, r, g, b):
        glUniform4f(self.matDifLoc,r,g,b,1.0)
    def set_material_specular(self, r, g, b):
        glUniform4f(self.matSpecLoc,r,g,b,1.0)
    def set_material_ambient(self, r, g, b):
        glUniform4f(self.matAmbLoc,r,g,b,1.0)
    def set_material_shininess(self, x):
        glUniform1f(self.matShineLoc,x)

    
    def set_light_possition(self,x,y,z):
        glUniform4f(self.lightPosLoc,x,y,z,0)
    def set_light_diffuse(self,r,g,b):
        glUniform4f(self.lightDifLoc,r,g,b,1.0)
    def set_light_specular(self,r,g,b):
        glUniform4f(self.lightSpecLoc,r,g,b,1.0)
    def set_light_ambient(self,r,g,b):
        glUniform4f(self.lightAmbLoc,r,g,b,1.0)




    def use(self):
        try:
            glUseProgram(self.renderingProgramID)   
        except OpenGL.error.GLError:
            print(glGetProgramInfoLog(self.renderingProgramID))
            raise

    def set_model_matrix(self, matrix_array):
        glUniformMatrix4fv(self.modelMatrixLoc, 1, True, matrix_array)

    def set_view_matrix(self, matrix_array):
        glUniformMatrix4fv(self.ViewMatrixLoc, 1, True, matrix_array)

    def set_projection_matrix(self, matrix_array):
        glUniformMatrix4fv(self.projectionMatrixLoc, 1, True, matrix_array)

    def set_position_attribute(self, vertex_array):
        glVertexAttribPointer(self.positionLoc, 3, GL_FLOAT, False, 0, vertex_array)

    def set_normal_attribute(self, vertex_array):
        glVertexAttribPointer(self.normalLoc, 3, GL_FLOAT, True, 0, vertex_array)  