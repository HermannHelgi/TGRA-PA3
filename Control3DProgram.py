# from OpenGL.GL import *
# from OpenGL.GLU import *
from math import *

import pygame
from pygame.locals import *

import sys
import time

from Shaders import *
from Matrices import *

class GraphicsProgram3D:
    def __init__(self):

        # WINDOW VARIABLES AND INITIALIZATION #
        self.screenWidth = 800
        self.screenHeight = 600

        pygame.init() 
        pygame.display.set_mode((self.screenWidth, self.screenHeight), pygame.OPENGL|pygame.DOUBLEBUF)

        self.shader = Shader3D()
        self.shader.use()

        self.model_matrix = ModelMatrix()

        self.view_matrix = ViewMatrix()
        self.view_matrix.look(Point(3, 3, 3), Point(2, 3, 2), Vector(0, 1, 0)) 
        # IF LOOK IS CHANGED, REMEMBER TO SET THE SELF.CURRENT_PITCH WITHIN MATRICES.PY TO MATCH, OTHERWISE PITCH WILL BE WEIRD

        self.projection_matrix = ProjectionMatrix()
        self.projection_matrix.set_perspective(60, self.screenWidth/self.screenHeight, 0.5, 10)
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())

        self.boxes = []
        self.cubes = []

        self.cube = Cube()

        self.clock = pygame.time.Clock()
        self.clock.tick()

        # EDITOR & SPEED VARIABLES # 
        self.canFly = False
        self.movementSpeed = 3

        self.rotationSpeed = 120
        self.pitchSpeed = 60

        # INTERNAL VARIABLES #
        self.pitchUpKey = K_UP
        self.pitchDownKey = K_DOWN
        self.rotateLeftKey = K_LEFT
        self.rotateRightKey = K_RIGHT

        self.forwardsKey = K_w
        self.backwardsKey = K_s
        self.leftWalkKey = K_a
        self.rightWalkKey = K_d

        self.pitch_up_key_down = False  
        self.pitch_down_key_down = False  
        self.rotate_right_key_down = False
        self.rotate_left_key_down = False

        self.forwards_key_down = False
        self.left_key_down = False
        self.backwards_key_down = False
        self.right_key_down = False

        self.invisible_box_padding = 0.7

        self.zoob = 1

    def update(self):
        delta_time = self.clock.tick() / 1000.0

        if (self.forwards_key_down):
            self.view_matrix.slide(0, 0, -self.movementSpeed * delta_time, self.canFly, self.boxes)
        if (self.backwards_key_down):
            self.view_matrix.slide(0, 0, self.movementSpeed * delta_time, self.canFly, self.boxes)
        if (self.left_key_down):
            self.view_matrix.slide(-self.movementSpeed * delta_time, 0, 0, self.canFly, self.boxes)
        if (self.right_key_down):
            self.view_matrix.slide(self.movementSpeed * delta_time, 0, 0, self.canFly, self.boxes)
        if (self.rotate_right_key_down):
            self.view_matrix.rotate_on_floor(-self.rotationSpeed * delta_time)
        if (self.rotate_left_key_down):
            self.view_matrix.rotate_on_floor(self.rotationSpeed * delta_time)
        if (self.pitch_up_key_down):
            self.view_matrix.pitch(self.pitchSpeed * delta_time)
        if (self.pitch_down_key_down):
            self.view_matrix.pitch(-self.pitchSpeed * delta_time)




    def display(self):
        glEnable(GL_DEPTH_TEST)  ### --- NEED THIS FOR NORMAL 3D BUT MANY EFFECTS BETTER WITH glDisable(GL_DEPTH_TEST) ... try it! --- ###

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)  ### --- YOU CAN ALSO CLEAR ONLY THE COLOR OR ONLY THE DEPTH --- ###

        glViewport(0, 0, self.screenWidth, self.screenHeight)



        #Effecting meterial stuff effects the other...
        #Try testing using values from 0 - 1. easy to see results that way..


        self.shader.set_view_matrix(self.view_matrix.get_matrix()) # New View Matrix each frame, important
        
        #self.shader.set_global_ambient(0,0.3,10)
        self.model_matrix.load_identity()
        self.DrawCubes()

        #For some reason editing editing the variables for the second model matrix effects the first one...??
        """
        self.shader.set_light1_diffuse(1,0,1)
        self.shader.set_light1_possition(0,2,7)
        self.model_matrix.push_matrix()
        self.shader.set_material_diffuse(0,1,1)
        self.model_matrix.add_translation(-2.2+self.zoob,1.5,4)
        self.model_matrix.add_scale(2,2,2)
        self.cubes[0].draw(self.shader)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.model_matrix.pop_matrix()
        """

        pygame.display.flip()

    def program_loop(self):
        exiting = False

        while not exiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quitting.")
                    exiting = True

                elif event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                        print("Escaping!")
                        exiting = True
                    #Pitch (Up - Down)
                    if event.key == self.pitchUpKey:
                        self.pitch_up_key_down = True
                    elif event.key == self.pitchDownKey:
                        self.pitch_down_key_down = True
                    #Movement
                    elif event.key == self.forwardsKey:
                        self.forwards_key_down = True
                    elif event.key == self.leftWalkKey:
                        self.left_key_down = True
                    elif event.key == self.backwardsKey:
                        self.backwards_key_down = True
                    elif event.key == self.rightWalkKey:
                        self.right_key_down = True
                    #Rotation (Left - Right)
                    elif event.key == self.rotateRightKey:
                        self.rotate_right_key_down = True
                    elif event.key == self.rotateLeftKey:
                        self.rotate_left_key_down = True

                elif event.type == pygame.KEYUP:
                    #Pitch (Up - Down)
                    if event.key == self.pitchUpKey:
                        self.pitch_up_key_down = False
                    elif event.key == self.pitchDownKey:
                        self.pitch_down_key_down = False
                    #Movement
                    elif event.key == self.forwardsKey:
                        self.forwards_key_down = False
                    elif event.key == self.leftWalkKey:
                        self.left_key_down = False
                    elif event.key == self.backwardsKey:
                        self.backwards_key_down = False
                    elif event.key == self.rightWalkKey:
                        self.right_key_down = False
                    #Rotation (Left - Right)    
                    elif event.key == self.rotateRightKey:
                        self.rotate_right_key_down = False
                    elif event.key == self.rotateLeftKey:
                        self.rotate_left_key_down = False
            
            self.update()
            self.display()

        #OUT OF GAME LOOP
        pygame.quit()

    def MakeCube(self,
                  translation_x=0, 
                  translation_y=0, 
                  translation_z=0,
                  
                  scale_x=1, 
                  scale_y=1, 
                  scale_z=1, 
                  
                  diffuse_r = 0, 
                  diffuse_g = 0, 
                  diffuse_b = 0,
                  specular_r = 0,
                  specular_g = 0,
                  specular_b = 0,
                  ambient_r = 0,
                  ambient_g = 0,
                  ambient_b = 0,
                  shine = 0
                  
                  ):
        new_cube = Cube()
        new_cube.trans_x = translation_x
        new_cube.trans_y = translation_y
        new_cube.trans_z = translation_z
        new_cube.scale_x = scale_x
        new_cube.scale_y = scale_y
        new_cube.scale_z = scale_z
        new_cube.diffuse_r = diffuse_r
        new_cube.diffuse_g = diffuse_g
        new_cube.diffuse_b = diffuse_b
        new_cube.specular_r = specular_r
        new_cube.specular_g = specular_g
        new_cube.specular_b = specular_b
        new_cube.ambient_r = ambient_r
        new_cube.ambient_g = ambient_g
        new_cube.ambient_b = ambient_b
        new_cube.shine = shine


        self.cubes.append(new_cube)
        self.boxes.append([translation_x - 0.5 * scale_x - self.invisible_box_padding, translation_x + 0.5 * scale_x + self.invisible_box_padding, translation_z - 0.5 * scale_z - self.invisible_box_padding, self.invisible_box_padding + translation_z + 0.5 * scale_z])

    def DrawCubes(self):
        for cube in self.cubes:
            self.model_matrix.push_matrix()


            self.model_matrix.add_translation(cube.trans_x,cube.trans_y,cube.trans_z)
            self.model_matrix.add_scale(cube.scale_x,cube.scale_y,cube.scale_z)
            cube.draw(self.shader)

            self.shader.set_light_possition(0,4243,154)
            self.shader.set_light_diffuse(1,0,255)
            self.shader.set_light_specular(255,255,255)
            self.shader.set_light_ambient(13,0.3,255)

            self.shader.set_material_shininess(cube.shine)
            self.shader.set_material_diffuse(cube.diffuse_r,cube.diffuse_g, cube.diffuse_b)
            self.shader.set_material_specular(cube.specular_r,cube.specular_g,cube.specular_b)
            self.shader.set_material_ambient(cube.ambient_r,cube.ambient_g,cube.ambient_b) #The natural color of the meterial
            
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.model_matrix.pop_matrix()



    def start(self):
        #MakeCube (Translation, scale, diffuse, specular, ambiance, shine)
        
        self.MakeCube(2,2,2, 1,1.5,1, 0,0.3,1, 0.0013,0,0, 0.001,0,0, 10)
        self.MakeCube(6,2,2, 6,1.5,2, 0,0.3,1, 0,0.3,0, 0,0.05,0, 10)
        self.MakeCube(-6,2,2, 1,1.5,2, 0,0.3,1, 0,0.3,0, 0,0.05,0, 10)
        self.MakeCube(-2,2,2, 1,1.5,2, 0,0.3,1, 0,0.3,0, 0,0.05,0, 10)
        self.MakeCube(6.4,2,-2, 6,1.5,2, 0,0.3,1, 0,0.3,0, 0,0.05,0, 10)
        self.MakeCube(2,2,-6, 1,1.5,1, 0,0.3,1, 0,0.3,0, 0,0.05,0, 10)
        self.MakeCube(-6,2,-6, 1,1.5,1, 0,0.3,1, 0,0.3,0, 0,0.05,0, 10)


        #Pyramid
        #Top
        self.MakeCube(12,6,12, 1,1.5,1, 0,0.3,1, 0,0.3,0, 0,0.05,0, 10)
        #Next top
        self.MakeCube(11,4,11, 1,1.5,1, 1,0.3,0.05, 0.009,0.3,0, 0,0.05,0, 10)
        self.MakeCube(13,4,11, 1,1.5,1, 0,0.3,1, 0,0.3,0, 0,0.05,0, 10)
        self.MakeCube(11,4,13, 1,1.5,1, 0,0.3,1, 0,0.3,0, 0,0.05,0, 10)
        self.MakeCube(13,4,13, 1,1.5,1, 0,0.3,1, 0,0.3,0, 0,0.05,0, 10)

        #Middle layer
        self.MakeCube(12,2,10, 1,1.5,1, 23,0,0, 0,0,0, 0,0.05,0, 10)
        self.MakeCube(14,2,10, 1,1.5,1, 0.5,0,1, 0,0.3,0, 0,0.05,0, 10)
        self.MakeCube(14,2,12, 1,1.5,1, 0.9,0.3,0, 0,0.3,0, 0,0.05,0, 10)
        self.MakeCube(10,2,12, 1,1.5,1, 0,0.3,1, 0,0.3,0, 0,0.05,0, 10)
        self.MakeCube(12,2,14, 1,1.5,1, 0,0.3,1, 0,0.3,0, 0,0.05,0, 10)
        self.MakeCube(10,2,14, 1,1.5,1, 0,0.3,1, 0,0.3,0, 0,0.05,0, 10)
        self.MakeCube(10,2,10, 1,1.5,1, 0,0.3,1, 0,0.3,0, 0,0.05,0, 10)
        self.MakeCube(12,2,12, 1,1.5,1, 0,0.3,1, 0,0.3,0, 0,0.05,0, 10)
        self.MakeCube(14,2,14, 1,1.5,1, 0,0.3,1, 0,0.3,0, 0,0.05,0, 10)
        #Next bottom
        self.MakeCube(11,0,11, 1,1.5,1, 0,0.3,1, 0,0.3,0, 0,0.05,0, 10)
        self.MakeCube(13,0,11, 1,1.5,1, 0,0.3,1, 0,0.3,0, 0,0.05,0, 10)
        self.MakeCube(11,0,13, 1,1.5,1, 0,0.3,1, 0,0.3,0, 0,0.05,0, 10)
        self.MakeCube(13,0,13, 1,1.5,1, 0,0.3,1, 0,0.3,0, 0,0.05,0, 10)
        #Bottom
        self.MakeCube(12,-2,12, 1,1.5,1, 0,0.3,1, 0,0.3,0, 0,0.05,0, 10)


        self.program_loop()

if __name__ == "__main__":
    GraphicsProgram3D().start()