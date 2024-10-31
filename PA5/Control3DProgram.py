from math import *

import pygame
from pygame.locals import *

import sys
import time
import json

from Shaders import *
from Matrices import *
import ojb_3D_loading as obj_3D_loading

from client import Client

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
        self.view_matrix.look(Point(4, 3, 4), Point(5, 3, 5), Vector(0, 1, 0)) 
        # IF LOOK IS CHANGED, REMEMBER TO SET THE SELF.CURRENT_PITCH WITHIN MATRICES.PY TO MATCH, OTHERWISE PITCH WILL BE WEIRD

        self.projection_matrix = ProjectionMatrix()
        self.projection_matrix.set_perspective(60, self.screenWidth/self.screenHeight, 0.5, 60)
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
        self.lights = []
        
        self.clock = pygame.time.Clock()
        self.clock.tick()

        # LEGACY DO NOT REMOVE THO!!!!!!
        # self.obj_model = obj_3D_loading.load_obj_file(sys.path[0] + "/models", '14039_To_go_coffee_cup_with_lid_v1_L3.obj')
        
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

        self.spinning_spheres = []

        # Used to rotate objects around the maze
        # Their indexes are, 0: Index of sphere/light, 1: Center X, 2: Center Z, 3: Angular speed, 4: current angle of rotation.
        # For spheres, Center X and Z can be another sphere for "orbits". Simply give that sphere in the the self.spheres list instead. Such as self.spheres[3]
        self.sphere_rotation_array=[]
        self.light_rotation_array=[]

        # Network stuffs
        self.net = Client()
        self.server_game_state = {}

        self.tex_id1 = self.LoadTexture("/textures/JUPI.jpg")

    def LoadTexture(self, stringpath):
        surface = pygame.image.load(sys.path[0] + stringpath) 
        tex_String = pygame.image.tostring(surface, "RGBA", 1)
        width = surface.get_width()
        height = surface.get_height()
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, tex_String)
        return tex_id

    def update(self):
        """
        Updates the game.
        """
        delta_time = self.clock.tick() / 1000.0

        #Controls
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

        #Rotating the light within the sceene

        for i in range(self.light_rotation_array.__len__()):
            self.light_rotation_array[i][-1] += self.light_rotation_array[i][-2] * delta_time
            self.light_rotation_array[i][-1] %= 2 * math.pi
            self.rotate_light(self.light_rotation_array[i])
        
        for i in range(self.sphere_rotation_array.__len__()):
            self.sphere_rotation_array[i][-1] += self.sphere_rotation_array[i][-2] * delta_time
            self.sphere_rotation_array[i][-1] %= 2 * math.pi
            self.rotate_sphere(self.sphere_rotation_array[i])

        for elem in self.spinning_spheres:
            self.spheres[elem].rotate_y += 30 * delta_time

        self.update_player_positions()

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
        
        # LEGACY, DO NOT REMOVE THO!!!!
        # self.DrawLoadedObjects()

        self.DrawCubes()
        self.DrawSpheres()
        self.DrawPlayers()

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
            
            self.server_game_state = json.loads(self.send_data())
            self.add_player_to_world()


            self.update()
            self.display()

        #OUT OF GAME LOOP
        pygame.quit()
   

    """This is for when a new player joins we only create it's model once"""
    def add_player_to_world(self):
        
        if "PLAYERS" in self.server_game_state: #Just in case we havent recived any data yet
            for player in self.server_game_state["PLAYERS"]:
                if int(player["ID"])+1 > len(self.players):
                    temp = player
                    player_model = Sphere()
                    player_model.scale_x = 1
                    player_model.scale_y = 1
                    player_model.scale_z = 1
                    player_model.ambient_r = 1
                    player_model.diffuse_r = 1
                    player_model.trans_x = player["POSITION"][0]
                    player_model.trans_y = player["POSITION"][1]-2
                    player_model.trans_z = player["POSITION"][2]
                    temp["MODEL"] = player_model

                    self.players.append(temp)

    def update_player_positions(self):
        if "PLAYERS" in self.server_game_state: #Just in case we havent recived any data yet
            for player in self.server_game_state["PLAYERS"]:
                self.players[int(player["ID"])]["MODEL"].trans_x = player["POSITION"][0]
                self.players[int(player["ID"])]["MODEL"].trans_y = player["POSITION"][1]-2
                self.players[int(player["ID"])]["MODEL"].trans_z = player["POSITION"][2] 


    def send_data(self):
        data = {"PLAYER": {"ID": self.net.id, "POSITION": [self.view_matrix.eye.x,self.view_matrix.eye.y,self.view_matrix.eye.z]}}
        data = json.dumps(data)
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
                  shine = 0,
                  texture = False,

                  rotation_x=0,
                  rotation_y=0,
                  rotation_z=0
                  
                  ):
        """
        Makes a new sphere and adds it to list of spheres within the game
        """
        if (texture):
            new_sphere = Sphere(True)
        else:
            new_sphere = Sphere()
        new_sphere.trans_x = translation_x
        new_sphere.trans_y = translation_y
        new_sphere.trans_z = translation_z
        new_sphere.scale_x = scale_x
        new_sphere.scale_y = scale_y
        new_sphere.scale_z = scale_z
        new_sphere.rotate_x = rotation_x
        new_sphere.rotate_y = rotation_y
        new_sphere.rotate_z = rotation_z
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
        # LEGACY; WILL HAVE TO CHANGE
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
            self.shader.set_material_diffuse(sphere.diffuse_r,sphere.diffuse_g, sphere.diffuse_b)

            if (sphere.texture):
                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_2D, self.tex_id1)
                self.shader.set_tex_diffuse(0)

            self.shader.set_material_shininess(sphere.shine)
            self.shader.set_material_specular(sphere.specular_r,sphere.specular_g,sphere.specular_b)
            self.shader.set_material_ambient(sphere.ambient_r,sphere.ambient_g,sphere.ambient_b) #The natural color of the meterial
                
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(sphere.trans_x,sphere.trans_y,sphere.trans_z)
            self.model_matrix.add_rotation_x(sphere.rotate_x)
            self.model_matrix.add_rotation_y(sphere.rotate_y)
            self.model_matrix.add_rotation_z(sphere.rotate_z)
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

    def DrawPlayers(self):
        if len(self.players) > 0:
            for player in self.players:
                if player["ID"] != self.net.id:
                    self.DrawLights() #Need to calculate the lights for each object

                    self.shader.set_material_shininess(player["MODEL"].shine)
                    self.shader.set_material_diffuse(player["MODEL"].diffuse_r,player["MODEL"].diffuse_g, player["MODEL"].diffuse_b)
                    self.shader.set_material_specular(player["MODEL"].specular_r,player["MODEL"].specular_g,player["MODEL"].specular_b)
                    self.shader.set_material_ambient(player["MODEL"].ambient_r,player["MODEL"].ambient_g,player["MODEL"].ambient_b) #The natural color of the meterial
                    
                    self.model_matrix.push_matrix()
                    self.model_matrix.add_translation(player["MODEL"].trans_x,player["MODEL"].trans_y,player["MODEL"].trans_z)
                    self.model_matrix.add_scale(player["MODEL"].scale_x,player["MODEL"].scale_y,player["MODEL"].scale_z)
                    self.shader.set_model_matrix(self.model_matrix.matrix)
                    player["MODEL"].draw(self.shader)
                    self.model_matrix.pop_matrix()



    def rotate_sphere(self, sphere_arr):
        """
        Rotates the lights in the scene.
        """

        if (isinstance(sphere_arr[1], Sphere)):
            sphere_x = sphere_arr[1].trans_x + sphere_arr[3] * math.cos(sphere_arr[-1]) 
            sphere_z = sphere_arr[2].trans_z + sphere_arr[3] * math.sin(sphere_arr[-1]) 
        else:
            sphere_x = sphere_arr[1] + sphere_arr[3] * math.cos(sphere_arr[-1]) 
            sphere_z = sphere_arr[2] + sphere_arr[3] * math.sin(sphere_arr[-1]) 

        self.spheres[sphere_arr[0]].trans_x = sphere_x
        self.spheres[sphere_arr[0]].trans_z = sphere_z

    def rotate_light(self, light_arr):
        """
        Rotates the lights in the scene.
        """
        sphere_x = light_arr[1] + light_arr[3] * math.cos(light_arr[-1]) 
        sphere_z = light_arr[2] + light_arr[3] * math.sin(light_arr[-1]) 

        self.lights[light_arr[0]].position[0] = sphere_x
        self.lights[light_arr[0]].position[2] = sphere_z

    def start(self):
        """
        Pre-initialization of game. Creating all the lights, cubes and spheres.
        """
        # Maze
        height = 6
        center_height = height / 2
        self.MakeCube(30, center_height, 1.5,      60, height, 3,     0, 0.3, 1,      1, 1, 1,        0.001, 0, 0, 10)
        self.MakeCube(30, center_height, 58.5,      60, height, 3,     0, 0.3, 1,      1, 1, 1,        0.001, 0, 0, 10)
        self.MakeCube(1.5, center_height, 30,      3, height, 54,     0, 0.3, 1,      1, 1, 1,        0.001, 0, 0, 10)
        self.MakeCube(58.5, center_height, 30,      3, height, 54,     0, 0.3, 1,      1, 1, 1,        0.001, 0, 0, 10)

        self.MakeCube(30, center_height, 10.5,      42, height, 3,     0, 0.3, 1,      1, 1, 1,        0.001, 0, 0, 10)
        self.MakeCube(30, center_height, 49.5,      42, height, 3,     0, 0.3, 1,      1, 1, 1,        0.001, 0, 0, 10)
        self.MakeCube(10.5, center_height, 30,      3, height, 30,     0, 0.3, 1,      1, 1, 1,        0.001, 0, 0, 10)
        self.MakeCube(49.5, center_height, 30,      3, height, 30,     0, 0.3, 1,      1, 1, 1,        0.001, 0, 0, 10)

        self.MakeCube(30, center_height, 15,      6, height, 6,     0, 0.3, 1,      1, 1, 1,        0.001, 0, 0, 10)
        self.MakeCube(30, center_height, 45,      6, height, 6,     0, 0.3, 1,      1, 1, 1,        0.001, 0, 0, 10)

        self.MakeCube(15, center_height, 30,      6, height, 6,     0, 0.3, 1,      1, 1, 1,        0.001, 0, 0, 10)
        self.MakeCube(45, center_height, 30,      6, height, 6,     0, 0.3, 1,      1, 1, 1,        0.001, 0, 0, 10)

        self.MakeCube(24, center_height, 24,      6, height, 6,     0, 0.3, 1,      1, 1, 1,        0.001, 0, 0, 10)
        self.MakeCube(24, center_height, 36,      6, height, 6,     0, 0.3, 1,      1, 1, 1,        0.001, 0, 0, 10)
        self.MakeCube(36, center_height, 24,      6, height, 6,     0, 0.3, 1,      1, 1, 1,        0.001, 0, 0, 10)
        self.MakeCube(36, center_height, 36,      6, height, 6,     0, 0.3, 1,      1, 1, 1,        0.001, 0, 0, 10)

        # Lights
        self.MakeLight(6,10,6, 0.8,0.8,0.8, 0.8,0.8,0.8, 0,0,0)
        self.MakeSphere(6,10,6, 1,1,1, 1,1,1 ,1,1,1, 1,1,1, 3)
        self.MakeLight(6,10,54, 0.8,0.8,0.8, 0.8,0.8,0.8, 0,0,0)
        self.MakeSphere(6,10,54, 1,1,1, 1,1,1 ,1,1,1, 1,1,1, 3)

        self.MakeLight(30,10,30, 0.8,0.8,0.8, 0.8,0.8,0.8, 0,0,0) # center light
        self.light_rotation_array.append([2, 30, 30, 8, (2 * math.pi / 5), 0.0])
        self.MakeSphere(30,10,30, 1,1,1, 1,1,1 ,1,1,1, 1,1,1, 3)
        self.sphere_rotation_array.append([2, 30, 30, 8, (2 * math.pi / 5), 0.0])

        self.MakeLight(54,10,6, 0.8,0.8,0.8, 0.8,0.8,0.8, 0,0,0)
        self.MakeSphere(54,10,6, 1,1,1, 1,1,1 ,1,1,1, 1,1,1, 3)
        self.MakeLight(54,10,54, 0.8,0.8,0.8, 0.8,0.8,0.8, 0,0,0)
        self.MakeSphere(54,10,54, 1,1,1, 1,1,1 ,1,1,1, 1,1,1, 3)

        # Planets
        self.MakeSphere(25,24,23, 1,1,1, 1,0.5,1 ,0.7,0,0, 0,1,0.3, 25)
        self.sphere_rotation_array.append([5, 30, 30, 11, (2 * math.pi / 7), 0.0])
        self.MakeSphere(21,26.7,27, 2,2,2, 1,0.5,0 ,0.7,0,0.3, 0,0,0.9, 10)
        self.sphere_rotation_array.append([6, 30, 30, 15, (2 * math.pi / 10), 0.5])

        self.MakeSphere(26,28,36, 1,1,1, 0.05,0,0.8 ,0.5,0.2,0.3, 0.1,0,0.9, 20)
        self.sphere_rotation_array.append([7, self.spheres[6], self.spheres[6], 4, (2 * math.pi / 8), 0.0])
        self.MakeSphere(26,21,36, 1,1,1, 0,1,0.2 ,0.5,1,0.3, 0.1,1,0.9, 20)
        self.sphere_rotation_array.append([8, 30, 30, 8, (2 * math.pi / 4), 0.0])

        self.MakeSphere(30,28,30, 5,5,5, 1,1,1 ,1,1,1, 0,0,0, 25, True, 30, 0, 0)
        self.spinning_spheres.append(9)

        # Sun
        self.MakeSphere(50,30,10, 8,8,8, 1,0.5,0 ,1,0.5,0, 1,0.3,0, 3)

        self.program_loop()

if __name__ == "__main__":
    GraphicsProgram3D().start()