from math import *

import pygame
from pygame.locals import *

import sys
import time

from Shaders import *
from Matrices import *
import ojb_3D_loading as obj_3D_loading

from client import Client

class GraphicsProgram3D:
    def __init__(self):
        # WINDOW VARIABLES AND INITIALIZATION #
        self.screenWidth = 800
        self.screenHeight = 600
        self.mini_map_screenWidth = 200
        self.mini_map_screenHeight = 150

        pygame.init() 
        pygame.display.set_mode((self.screenWidth, self.screenHeight), pygame.OPENGL|pygame.DOUBLEBUF)

        self.shader = Shader3D()
        self.shader.use()

        self.model_matrix = ModelMatrix()

        self.view_matrix = ViewMatrix()
        self.view_matrix.look(Point(3, 3, 3), Point(2, 3, 2), Vector(0, 1, 0)) 

        self.mini_map_view = ViewMatrix()
        self.mini_map_view.look(Point(3, 10, 3), Point(2.999, 1, 2.999), Vector(0, 1, 0)) 
        self.mini_map_view.rotate_on_floor(-45)

        # IF LOOK IS CHANGED, REMEMBER TO SET THE SELF.CURRENT_PITCH WITHIN MATRICES.PY TO MATCH, OTHERWISE PITCH WILL BE WEIRD

        self.projection_matrix = ProjectionMatrix()
        self.projection_matrix.set_perspective(60, self.screenWidth/self.screenHeight, 0.5, 40)
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())


        # EDITOR & SPEED VARIABLES # 
        self.canFly = False
        self.movementSpeed = 3
        self.walkingSpeed = self.movementSpeed
        self.sprintspeed = 6

        self.rotationSpeed = 120
        self.pitchSpeed = 60

        # INTERNAL VARIABLES #
        self.boxes = []
        self.cubes = []
        self.spheres = []
        self.players = []
        self.coffee_locations = []
        self.coffee_range = 0.5
        self.coffees_collected = 0
        self.coffee_locations.append([-7, -5])
        self.coffee_locations.append([11, -15])
        self.coffee_locations.append([9, -25])
        self.lights = []
        
        self.mini_map_lights = []
        self.mini_map_light = Light()

        self.minimap_indicator = Sphere()
        self.clock = pygame.time.Clock()
        self.clock.tick()

        self.obj_model = obj_3D_loading.load_obj_file(sys.path[0] + "/models", '14039_To_go_coffee_cup_with_lid_v1_L3.obj')
        
        # Movement presets.
        self.pitchUpKey = K_UP
        self.pitchDownKey = K_DOWN
        self.rotateLeftKey = K_LEFT
        self.rotateRightKey = K_RIGHT

        self.forwardsKey = K_w
        self.backwardsKey = K_s
        self.leftWalkKey = K_a
        self.rightWalkKey = K_d
        self.sprintKey = K_LSHIFT

        self.pitch_up_key_down = False  
        self.pitch_down_key_down = False  
        self.rotate_right_key_down = False
        self.rotate_left_key_down = False

        self.forwards_key_down = False
        self.left_key_down = False
        self.backwards_key_down = False
        self.right_key_down = False

        self.invisible_box_padding = 0.7 # Padding on AABB

        self.light_pos = [0,0,0]
        self.angle = 0

        # Used to rotate the light around the maze
        self.light_rotate_angle = 0 
        self.light_rotate_point = [2,5,-15] #Note hardcoded value

        # Sphere zone
        self.light_rotate_point_box = [2,5,25] #Note hardcoded value

        # Network stuffs
        #self.net = Client()

    def update(self):
        """
        Updates the game.
        """
        
        delta_time = self.clock.tick() / 1000.0
        coffee_to_remove = -1

        #Controls
        if (self.forwards_key_down):
            coffee_to_remove = self.view_matrix.slide(0, 0, -self.movementSpeed * delta_time, self.canFly, self.boxes, self.coffee_locations, self.coffee_range)
            self.mini_map_view.copy_coords(self.view_matrix)
        if (self.backwards_key_down):
            coffee_to_remove = self.view_matrix.slide(0, 0, self.movementSpeed * delta_time, self.canFly, self.boxes, self.coffee_locations, self.coffee_range)
            self.mini_map_view.copy_coords(self.view_matrix)
        if (self.left_key_down):
            coffee_to_remove = self.view_matrix.slide(-self.movementSpeed * delta_time, 0, 0, self.canFly, self.boxes, self.coffee_locations, self.coffee_range)
            self.mini_map_view.copy_coords(self.view_matrix)
        if (self.right_key_down):
            coffee_to_remove = self.view_matrix.slide(self.movementSpeed * delta_time, 0, 0, self.canFly, self.boxes, self.coffee_locations, self.coffee_range)
            self.mini_map_view.copy_coords(self.view_matrix)
        if (self.rotate_right_key_down):
            self.view_matrix.rotate_on_floor(-self.rotationSpeed * delta_time)
        if (self.rotate_left_key_down):
            self.view_matrix.rotate_on_floor(self.rotationSpeed * delta_time)
        if (self.pitch_up_key_down):
            self.view_matrix.pitch(self.pitchSpeed * delta_time)
        if (self.pitch_down_key_down):
            self.view_matrix.pitch(-self.pitchSpeed * delta_time)
        
        #Coffe power up
        if (coffee_to_remove != -1):
            self.coffee_locations.pop(coffee_to_remove)
            self.coffees_collected += 1
            self.walkingSpeed += 2
            self.movementSpeed += 2
            self.sprintspeed += 2
            self.projection_matrix.set_perspective(60, (self.screenWidth + 100 * self.coffees_collected)/(self.screenHeight), 0.5, 40)
            self.shader.set_projection_matrix(self.projection_matrix.get_matrix())

        #Rotating the light within the sceene
        self.light_rotate_angle += 2*delta_time
        self.rotate_light(self.lights[1],self.spheres[1],self.lights[-1],self.cubes[-1])

    def display(self):
        """
        Displays all graphics for the game, is split into 'Main view' and 'Minimap' for those two viewports.
        """
        #Setup
        glEnable(GL_DEPTH_TEST) 
        glViewport(0, 0, self.screenWidth, self.screenHeight)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)  

        # MAIN VIEW
        self.shader.set_view_matrix(self.view_matrix.get_matrix()) # New View Matrix each frame, important        
        self.model_matrix.load_identity()
        self.DrawLoadedObjects()
        self.DrawCubes()
        self.DrawSpheres()

        # MINI MAP
        glViewport(self.screenWidth - self.mini_map_screenWidth, self.screenHeight - self.mini_map_screenHeight, self.mini_map_screenWidth, self.mini_map_screenHeight)
        glEnable(GL_SCISSOR_TEST)

        glScissor(self.screenWidth - self.mini_map_screenWidth,self.screenHeight - self.mini_map_screenHeight,self.mini_map_screenWidth,self.mini_map_screenHeight)
        glClearColor(0.5, 0.5, 0.5, 1.0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        self.shader.set_view_matrix(self.mini_map_view.get_matrix()) # New View Matrix each frame, important
        self.model_matrix.load_identity()
        self.DrawPlayerIndicator()
        self.DrawSpheres()
        self.DrawCubes()
        self.DrawLoadedObjects()

        glDisable(GL_SCISSOR_TEST)

        pygame.display.flip()

    def program_loop(self):
        """
        Main loop for program.
        """
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
                    elif event.key == self.sprintKey:
                        self.movementSpeed = self.sprintspeed
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
                    elif event.key == self.sprintKey:
                        self.movementSpeed = self.walkingSpeed
                    #Rotation (Left - Right)    
                    elif event.key == self.rotateRightKey:
                        self.rotate_right_key_down = False
                    elif event.key == self.rotateLeftKey:
                        self.rotate_left_key_down = False
            
            #print(self.send_data())

            self.update()
            self.display()

        #OUT OF GAME LOOP
        pygame.quit()
   
   
    def send_data(self):

        data = "Hello server this is player:" + self.net.id
        reply = self.net.send(data)
        return reply


        

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
        """
        Makes a new cube and adds it to list of cubes within the game.
        """
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

    def MakeSphere(self,
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
        """
        Makes a new sphere and adds it to list of spheres within the game
        """
        new_sphere = Sphere()
        new_sphere.trans_x = translation_x
        new_sphere.trans_y = translation_y
        new_sphere.trans_z = translation_z
        new_sphere.scale_x = scale_x
        new_sphere.scale_y = scale_y
        new_sphere.scale_z = scale_z
        new_sphere.diffuse_r = diffuse_r
        new_sphere.diffuse_g = diffuse_g
        new_sphere.diffuse_b = diffuse_b
        new_sphere.specular_r = specular_r
        new_sphere.specular_g = specular_g
        new_sphere.specular_b = specular_b
        new_sphere.ambient_r = ambient_r
        new_sphere.ambient_g = ambient_g
        new_sphere.ambient_b = ambient_b
        new_sphere.shine = shine
        self.spheres.append(new_sphere)

    def MakeLight(self,                  
                  
                  possition_x = 0,
                  possition_y = 0,
                  possition_z = 0,

                  diffuse_r = 0, 
                  diffuse_g = 0, 
                  diffuse_b = 0,
                  specular_r = 0,
                  specular_g = 0,
                  specular_b = 0,
                  ambient_r = 0,
                  ambient_g = 0,
                  ambient_b = 0,
                
                  
                  ):
        """
        Makes a new light and adds it to list of lights within the game.
        Note simple3d.vert will need to be manualy updated if more lights are added!
        """
        new_light = Light()
        possition = [possition_x,possition_y,possition_z]
        diffuse = [diffuse_r,diffuse_g,diffuse_b]
        specular = [specular_r,specular_g,specular_b]
        ambient = [ambient_r,ambient_g,ambient_b]
        new_light.position = possition
        new_light.diffuse = diffuse
        new_light.specular = specular
        new_light.ambient = ambient

        self.lights.append(new_light)

    def DrawLoadedObjects(self):
        """
        Draws all loaded 3D object files.
        """
        for coffee_cup in self.coffee_locations:
            self.DrawLights()
            
            self.shader.set_material_shininess(13)
            self.shader.set_material_diffuse(1,0, 0)
            self.shader.set_material_specular(1,1,1)
            self.shader.set_material_ambient(1,0,0)
            
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(coffee_cup[0], 1.5, coffee_cup[1])
            self.model_matrix.add_rotation_x(-90)
            self.model_matrix.add_scale(0.2, 0.2, 0.2)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.obj_model.draw(self.shader)

            self.model_matrix.pop_matrix()

    def DrawSpheres(self):
        """
        Draws all spheres into the sceene.
        """
        for sphere in self.spheres:
            self.DrawLights() #Need to calculate the lights for each object

            self.shader.set_material_shininess(sphere.shine)
            self.shader.set_material_diffuse(sphere.diffuse_r,sphere.diffuse_g, sphere.diffuse_b)
            self.shader.set_material_specular(sphere.specular_r,sphere.specular_g,sphere.specular_b)
            self.shader.set_material_ambient(sphere.ambient_r,sphere.ambient_g,sphere.ambient_b) #The natural color of the meterial
            
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(sphere.trans_x,sphere.trans_y,sphere.trans_z)
            self.model_matrix.add_scale(sphere.scale_x,sphere.scale_y,sphere.scale_z)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            sphere.draw(self.shader)

            self.model_matrix.pop_matrix()

    def DrawLights(self):
        """
        Draws lights into the sceene.
        """
        self.shader.set_lights(self.lights)

    def DrawCubes(self):
        """
        Draws all cubes into the sceene.
        """
        for cube in self.cubes:
            self.DrawLights() # Need to calculate all the lights for each material values of each object.

            self.shader.set_material_shininess(cube.shine)
            self.shader.set_material_diffuse(cube.diffuse_r,cube.diffuse_g, cube.diffuse_b)
            self.shader.set_material_specular(cube.specular_r,cube.specular_g,cube.specular_b)
            self.shader.set_material_ambient(cube.ambient_r,cube.ambient_g,cube.ambient_b) #The natural color of the meterial
            
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(cube.trans_x,cube.trans_y,cube.trans_z)
            self.model_matrix.add_scale(cube.scale_x,cube.scale_y,cube.scale_z)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            cube.draw(self.shader)

            self.model_matrix.pop_matrix()

    def DrawPlayerIndicator(self):
        """
        Draws the red circle indicator on the minimap to indicate the player.
        """
        self.DrawLights() #Make sure the light is correct for the indicator

        self.shader.set_material_shininess(10)
        self.shader.set_material_diffuse(1, 0 ,0)
        self.shader.set_material_specular(1, 0 ,0)
        self.shader.set_material_ambient(1, 0 ,0) 
        self.model_matrix.push_matrix()
        
        self.model_matrix.add_translation(self.view_matrix.eye.x, self.view_matrix.eye.y + 2, self.view_matrix.eye.z)
        scale = 0.4
        self.model_matrix.add_scale(scale, scale, scale)
        self.shader.set_model_matrix(self.model_matrix.matrix)

        self.minimap_indicator.draw(self.shader)

        self.model_matrix.pop_matrix()

    def rotate_light(self,light_1:Light,light_sphere:Sphere,light_2:Light,light_box:Cube):
        """
        Rotates the lights in the scene.
        """
        #Around the maze
        light_1.position[0] = 10*cos(self.light_rotate_angle) + self.light_rotate_point[0]
        light_1.position[2] = 10*sin(self.light_rotate_angle) + self.light_rotate_point[2]
        light_sphere.trans_x = 10*cos(self.light_rotate_angle) + self.light_rotate_point[0]
        light_sphere.trans_z = 10*sin(self.light_rotate_angle) + self.light_rotate_point[2]

        #Around the sphere zone
        light_2.position[0] = 10*cos(self.light_rotate_angle) + self.light_rotate_point_box[0]
        light_2.position[2] = 10*sin(self.light_rotate_angle) + self.light_rotate_point_box[2]
        light_box.trans_x = 10*cos(self.light_rotate_angle) + self.light_rotate_point_box[0]
        light_box.trans_y = 10*cos(self.light_rotate_angle) + self.light_rotate_point_box[1]
        light_box.trans_z = 10*sin(self.light_rotate_angle) + self.light_rotate_point_box[2]

        

    def start(self):
        """
        Pre-initialization of game. Creating all the lights, cubes and spheres.
        """

        #MakeCube/MakeSphere (Translation, scale, diffuse, specular, ambiance, shine)


        #Sun
        self.MakeLight(-30,-10,10, 1,0,0, 1,0,0, 1,0,0) 
        self.MakeSphere(-30,-10,10, 5,5,5, 1,0.5,0 ,1,0.5,0, 1,0.3,0, 3)

        #Maze rotate light
        self.MakeLight(10,5,-20, 0,1,0, 0,1,0, 0,1,0)
        self.MakeSphere(10,5,-20, 1,1,1, 1,1,1 ,1,1,1, 1,1,1, 3)

        self.MakeSphere(-8,2,6, 1,1,1, 1,0.5,1 ,0.7,0,0, 0,1,0.3, 25)
        self.MakeCube(-6,1,4, 2,2,2, 0,0.9,0.4, 0,24,0.5, 0,0.5,0, 13)
        
        #Maze
        self.MakeCube(-5,2,-0.9, 12,1.5,1, 0,0.3,1, 1,1,1, 0.001,0,0, 10)
        self.MakeCube(4,2,-3, 1,1.5,5, 0,0.3,1, 1,1,1, 0.001,0,0, 10)
        self.MakeCube(9.5,2,-1, 10,1.5,1, 0,0.3,1, 1,1,1, 0.001,0,0, 10)
        self.MakeCube(2,2,-5, 4,1.5,1, 0,0.3,1, 1,1,1, 0.001,0,0, 10)
        self.MakeCube(-4,2,-8, 2,1.5,15, 0,0.3,1, 1,1,1, 0.001,0,0, 10)
        self.MakeCube(-3,2,-10, 5,1.5,2, 0,0.3,1, 1,1,1, 0.001,0,0, 10)
        self.MakeCube(3,2,-10, 1,1.5,10, 0,0.3,1, 1,1,1, 0.001,0,0, 10)
        self.MakeCube(-10,2,-15.5, 1,1.5,30, 0,0.3,1, 1,1,1, 0.001,0,0, 10)
        self.MakeCube(-2,2,-19, 7,1.5,2, 0,0.3,1, 1,1,1, 0.001,0,0, 10)
        self.MakeCube(1.5,2,-17, 2,1.5,4, 0,0.3,1, 1,1,1, 0.001,0,0, 10)
        self.MakeCube(-6,2,-26, 7,1.5,2, 0,0.3,1, 1,1,1, 0.001,0,0, 10)
        self.MakeCube(4,2,-26, 7,1.5,2, 0,0.3,1, 1,1,1, 0.001,0,0, 10)
        self.MakeCube(2.5,2,-30, 24,1.5,1.5, 0,0.3,1, 1,1,1, 0.001,0,0, 10)
        self.MakeCube(11,2,-22, 1,1.5,10, 0,0.3,1, 1,1,1, 0.001,0,0, 10)
        self.MakeCube(9,2,-22, 4,1.5,2, 0,0.3,1, 1,1,1, 0.001,0,0, 10)
        self.MakeCube(13,2,-26, 4,1.5,2, 0,0.3,1, 1,1,1, 0.001,0,0, 10)
        self.MakeCube(14,2,-11, 1,1.5,20, 0,0.3,1, 1,1,1, 0.001,0,0, 10)
        self.MakeCube(7,2,-15, 1,1.5,22, 0,0.3,1, 1,1,1, 0.001,0,0, 10)
        self.MakeCube(10,2,-13, 1,1.5,18, 0,0.3,1, 1,1,1, 0.001,0,0, 10)
        self.MakeCube(14,2,-28, 1,1.5,4, 0,0.3,1, 1,1,1, 0.001,0,0, 10)

        #Spheare zone
        self.MakeLight(20,3,20, 1,1,1, 0,1,1, 1,1,1)

        self.MakeSphere(-5,2,13, 1,1,1, 1,0.5,1 ,0.7,0,0, 0,1,0.3, 25)
        self.MakeSphere(-9,6.7,17, 2,2,2, 1,0.5,0 ,0.7,0,0.3, 0,0,0.9, 10)
        self.MakeSphere(5,-2,26, 5,5,5, 0.9,0,0.5 ,1,0,1, 0,0,1, 25)
        self.MakeSphere(-4,13,26, 1,1,1, 0.05,0,0.8 ,0.5,0.2,0.3, 0.1,0,0.9, 20)
        self.MakeSphere(-4,2,26, 1,1,1, 0.5,1,0.8 ,0.5,1,0.3, 0.1,1,0.9, 20)
        self.MakeCube(14,2,-28, 2,2,2, 1,1,1, 1,1,1, 1,1,1, 10)

        self.program_loop()

if __name__ == "__main__":
    GraphicsProgram3D().start()