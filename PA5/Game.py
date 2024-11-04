from math import *
from random import *

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
        seed() # For random spawns
        self.screenWidth = 800
        self.screenHeight = 600

        pygame.init() 
        pygame.display.set_mode((self.screenWidth, self.screenHeight), pygame.OPENGL|pygame.DOUBLEBUF)
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

        self.shader = Shader3D()
        self.shader.use()

        self.model_matrix = ModelMatrix()

        # Manually inputed coords for spawn locations, index 0-1 is the x and z of the spawn, index 2-3 is the x and z of the direction which the player will look towards.
        self.spawn_locations = [[6, 6, 7, 7], [6, 54, 7, 53], [54, 6, 53, 7], [54, 54, 53, 53], [24, 15, 23, 16], [15, 24, 16, 23], [36, 15, 37, 16], [45, 24, 43, 23], [15, 36, 16, 37], [24, 45, 23, 44], [36, 45, 37, 44], [45, 36, 44, 37]]

        self.view_matrix = ViewMatrix()
        self.random_spawn = self.randomize_spawn()

        self.projection_matrix = ProjectionMatrix()
        self.projection_matrix.set_perspective(60, self.screenWidth/self.screenHeight, 0.5, 60)
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())

        # SHOOTING VARIABLES
        self.shootTimer = 0
        self.shootCooldown = 1
        self.bullet_height_max_and_min = 6

        # EDITOR & SPEED VARIABLES # 
        self.canFly = False
        self.movementSpeed = 3
        self.walkingSpeed = self.movementSpeed
        self.sprintspeed = 6

        self.mouseSensitivity = 0.1
        self.yawAmount = 0
        self.pitchAmount = 0


        # INTERNAL VARIABLES #
        self.boxes = []
        self.cubes = []
        self.spheres = []
        self.lights = []
        self.bullets = []
        
        self.clock = pygame.time.Clock()
        self.clock.tick()

        self.obj_model = obj_3D_loading.load_obj_file(sys.path[0] + "/models", 'Satellite.obj')
        
        # Movement presets.
        self.forwardsKey = K_w
        self.backwardsKey = K_s
        self.leftWalkKey = K_a
        self.rightWalkKey = K_d
        self.sprintKey = K_LSHIFT

        self.forwards_key_down = False
        self.left_key_down = False
        self.backwards_key_down = False
        self.right_key_down = False

        self.invisible_box_padding = 0.7 # Padding on AABB
        self.invisible_box_padding_removed_for_bullet = 0.4 # Padding which is removed for bullets

        self.light_pos = [0,0,0]

        self.spinning_spheres = []

        # Used to rotate objects around the maze
        # Their indexes are, 0: Index of sphere/light, 1: Center X, 2: Center Z, 3: Angular speed, 4: current angle of rotation.
        # For spheres, Center X and Z can be another sphere for "orbits". Simply give that sphere in the the self.spheres list instead. Such as self.spheres[3]
        self.sphere_rotation_array=[]
        self.light_rotation_array=[]

        # Network stuffs
        self.net = Client()
        self.bullet_id = 0
        self.serverGameState = json.loads(self.addPlayerToServer())

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

        #Get new server data
        self.updateGameState()

        #Controls
        if self.shootTimer > 0:
            self.shootTimer -= delta_time

        if (self.forwards_key_down):
            self.view_matrix.slide(0, 0, -self.movementSpeed * delta_time, self.canFly, self.boxes)
        if (self.backwards_key_down):
            self.view_matrix.slide(0, 0, self.movementSpeed * delta_time, self.canFly, self.boxes)
        if (self.left_key_down):
            self.view_matrix.slide(-self.movementSpeed * delta_time, 0, 0, self.canFly, self.boxes)
        if (self.right_key_down):
            self.view_matrix.slide(self.movementSpeed * delta_time, 0, 0, self.canFly, self.boxes)
        if (self.yawAmount != 0):
            self.view_matrix.rotate_on_floor(-(self.yawAmount * self.mouseSensitivity) * delta_time)
        if (self.pitchAmount != 0):
            self.view_matrix.pitch((self.pitchAmount * self.mouseSensitivity) * delta_time)

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
        
        remove_bullets = []
        for index, bullet in enumerate(self.bullets):
            value = bullet.move(delta_time, self.boxes, self.invisible_box_padding_removed_for_bullet, self.bullet_height_max_and_min)
            if value == -1:
                remove_bullets.append(index)
        
        for index in remove_bullets:
            del self.bullets[index]
                
    def display(self):
        """
        Displays all graphics for the game, is split into 'Main view' and 'Minimap' for those two viewports.
        """
        #Setup
        glEnable(GL_DEPTH_TEST) 
        glViewport(0, 0, self.screenWidth, self.screenHeight)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        #Update from new server data
        self.generatePlayerModels()

        # MAIN VIEW
        self.shader.set_view_matrix(self.view_matrix.get_matrix()) # New View Matrix each frame, important 
        self.shader.set_eye_pos(self.view_matrix.eye.x, self.view_matrix.eye.y, self.view_matrix.eye.z)       
        self.model_matrix.load_identity()
        
        self.DrawLoadedObjects()
        self.DrawCubes()
        self.DrawSpheres()
        self.DrawBullets()
        self.DrawPlayers()

        pygame.display.flip()

    def program_loop(self):
        """
        Main loop for program.
        """
        exiting = False

        while not exiting:

            #Mouse movement
            mouseX, mouseY = pygame.mouse.get_rel()
            self.yawAmount = mouseX
            self.pitchAmount = -mouseY
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0] and self.shootTimer <= 0:
                # TODO: Needs to be sent to server.
                self.ShootBullet()
                self.shootTimer = self.shootCooldown

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quitting.")
                    exiting = True

                elif event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                        print("Escaping!")
                        exiting = True
                    #Movement
                    if event.key == self.forwardsKey:
                        self.forwards_key_down = True
                    elif event.key == self.leftWalkKey:
                        self.left_key_down = True
                    elif event.key == self.backwardsKey:
                        self.backwards_key_down = True
                    elif event.key == self.rightWalkKey:
                        self.right_key_down = True
                    elif event.key == self.sprintKey:
                        self.movementSpeed = self.sprintspeed

                elif event.type == pygame.KEYUP:

                    #Movement
                    if event.key == self.forwardsKey:
                        self.forwards_key_down = False
                    elif event.key == self.leftWalkKey:
                        self.left_key_down = False
                    elif event.key == self.backwardsKey:
                        self.backwards_key_down = False
                    elif event.key == self.rightWalkKey:
                        self.right_key_down = False
                    elif event.key == self.sprintKey:
                        self.movementSpeed = self.walkingSpeed
                
            

            self.update()
            self.display()

        #OUT OF GAME LOOP
        pygame.quit()
   
    def ShootBullet(self):
        playerColors = self.serverGameState["PLAYERS"][str(self.net.id)]["COLOR"] #Make the bullet the same as the players
        self.MakeBullet(self.view_matrix.eye.x,self.view_matrix.eye.y - 0.5,self.view_matrix.eye.z, float(playerColors[0]),float(playerColors[1]),float(playerColors[2]) ,float(playerColors[0]),float(playerColors[1]),float(playerColors[2]), -self.view_matrix.norm_vector.x, -self.view_matrix.norm_vector.y, -self.view_matrix.norm_vector.z)


    """This is for when a new player joins we only create it's model once"""
    def generatePlayerModels(self):
        for player_id,player_data in self.serverGameState["PLAYERS"].items():
            if player_id != self.net.id:
                player_model = Sphere()
                player_model.scale_x = 1.5
                player_model.scale_y = 3
                player_model.scale_z = 1.5

                player_model.ambient_r = 0.1 + (player_data["COLOR"][0]/3)
                player_model.ambient_g = 0.1 + (player_data["COLOR"][1]/3)
                player_model.ambient_b = 0.1 + (player_data["COLOR"][2]/3)
                
                
                player_model.diffuse_r = player_data["COLOR"][0]
                player_model.diffuse_g = player_data["COLOR"][1]
                player_model.diffuse_b = player_data["COLOR"][2]

                player_model.specular_r = 1
                player_model.specular_g = 1
                player_model.specular_b = 1
                player_model.shine = 125

                player_model.trans_x = player_data["POSITION"][0]
                player_model.trans_y = player_data["POSITION"][1]
                player_model.trans_z = player_data["POSITION"][2]
                player_data["MODEL"] = player_model

    """
    This tells the server to add this instance to the server and what data our player has.
    returns the servers game state as string.
    """
    def addPlayerToServer(self):
        data = {"PLAYER": 
                    {
                    "ID": self.net.id,
                    "POSITION": [self.view_matrix.eye.x,self.view_matrix.eye.y,self.view_matrix.eye.z],
                    "COLOR":[random(),random(),random()],
                    }
                }
        data = json.dumps(data)
        reply = self.net.send(data)
        return reply

    """Lets the server know of our new position and gets the current game state from the server"""
    def updateGameState(self):
        self.serverGameState["PLAYERS"][str(self.net.id)]["POSITION"] = [self.view_matrix.eye.x,self.view_matrix.eye.y,self.view_matrix.eye.z]
        data = {}
        data["PLAYER"] = self.serverGameState["PLAYERS"][str(self.net.id)]
        data = json.dumps(data)
        reply = self.net.send(data)
        self.serverGameState = json.loads(reply)
        for bullet_id in self.serverGameState["BULLETS"]:
            bullet = self.serverGameState["BULLETS"][bullet_id]
            new_bullet = Bullet(
                bullet["POSITION"][0],
                bullet["POSITION"][1],
                bullet["POSITION"][2], 
                bullet["COLOR"][0],
                bullet["COLOR"][1],
                bullet["COLOR"][2],

                bullet["COLOR"][0],
                bullet["COLOR"][1],
                bullet["COLOR"][2],
                bullet["DIRECTION"][0],
                bullet["DIRECTION"][1],
                bullet["DIRECTION"][2],
                bullet["ID"])
            self.bullets.append(new_bullet)           
            


    def randomize_spawn(self):
        random_spawn = self.spawn_locations[randint(0, (self.spawn_locations.__len__() - 1))]
        self.view_matrix.look(Point(random_spawn[0], 3, random_spawn[1]), Point(random_spawn[2], 3, random_spawn[3]), Vector(0, 1, 0)) 
        # If the Y value of the look() function is changed to not be the same, remember to change the current_pitch value to fit that.

    def MakeBullet(self, x, y ,z, dr, dg, db, sr, sg, sb, direction_x, direction_y, direction_z):
        new_bullet = Bullet(x, y ,z, dr, dg, db, sr, sg, sb, direction_x, direction_y, direction_z,self.net.id)
        data = {"BULLET": new_bullet.get_data()}
        data = json.dumps(data)
        reply = self.net.send(data)
        self.serverGameState = json.loads(reply)
        

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
                  rotation_z=0,

                  emission_r=0,
                  emission_g=0,
                  emission_b=0
                  
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
        new_sphere.emission_r = emission_r
        new_sphere.emission_g = emission_g
        new_sphere.emission_b = emission_b
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
        self.DrawLights()
        
        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(15, 15, 40)
        self.model_matrix.add_rotation_y(45)
        self.model_matrix.add_rotation_z(30)
        self.model_matrix.add_scale(1, 1, 1)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.obj_model.draw(self.shader)

        self.model_matrix.pop_matrix()

    def DrawSpheres(self):
        """
        Draws all spheres into the scene.
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
            self.shader.set_material_emission(sphere.emission_r,sphere.emission_g,sphere.emission_b)

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
        for player_id,player_data in self.serverGameState["PLAYERS"].items():
            if player_id != self.net.id:
                self.DrawLights() #Need to calculate the lights for each object

                self.shader.set_material_shininess(player_data["MODEL"].shine)
                self.shader.set_material_diffuse(player_data["MODEL"].diffuse_r,player_data["MODEL"].diffuse_g, player_data["MODEL"].diffuse_b)
                self.shader.set_material_specular(player_data["MODEL"].specular_r,player_data["MODEL"].specular_g,player_data["MODEL"].specular_b)
                self.shader.set_material_ambient(player_data["MODEL"].ambient_r,player_data["MODEL"].ambient_g,player_data["MODEL"].ambient_b) #The natural color of the meterial
                
                self.model_matrix.push_matrix()
                self.model_matrix.add_translation(player_data["MODEL"].trans_x,player_data["MODEL"].trans_y,player_data["MODEL"].trans_z)
                self.model_matrix.add_scale(player_data["MODEL"].scale_x,player_data["MODEL"].scale_y,player_data["MODEL"].scale_z)
                self.shader.set_model_matrix(self.model_matrix.matrix)
                player_data["MODEL"].draw(self.shader)
                self.model_matrix.pop_matrix()

    def DrawBullets(self):
        for bullet in self.bullets:
            self.DrawLights() #Need to calculate the lights for each object
            self.shader.set_material_diffuse(bullet.body.diffuse_r,bullet.body.diffuse_g, bullet.body.diffuse_b)

            self.shader.set_material_shininess(bullet.body.shine)
            self.shader.set_material_specular(bullet.body.specular_r,bullet.body.specular_g,bullet.body.specular_b)
            self.shader.set_material_ambient(bullet.body.ambient_r,bullet.body.ambient_g,bullet.body.ambient_b) #The natural color of the meterial
            self.shader.set_material_emission(bullet.body.emission_r,bullet.body.emission_g,bullet.body.emission_b)

            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(bullet.body.trans_x,bullet.body.trans_y,bullet.body.trans_z)
            self.model_matrix.add_scale(bullet.body.scale_x,bullet.body.scale_y,bullet.body.scale_z)
            self.shader.set_model_matrix(self.model_matrix.matrix)

            bullet.body.draw(self.shader)

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
        self.MakeCube(30, center_height, 1.5,      60, height, 3,     0, 0.3, 1,      0.5, 0.5, 0.5,        0, 0, 0, 10)
        self.MakeCube(30, center_height, 58.5,      60, height, 3,     0, 0.3, 1,      0.5, 0.5, 0.5,        0, 0, 0, 10)
        self.MakeCube(1.5, center_height, 30,      3, height, 54,     0, 0.3, 1,      0.5, 0.5, 0.5,        0, 0, 0, 10)
        self.MakeCube(58.5, center_height, 30,      3, height, 54,     0, 0.3, 1,      0.5, 0.5, 0.5,        0, 0, 0, 10)

        self.MakeCube(30, center_height, 10.5,      42, height, 3,     0, 0.3, 1,      0.5, 0.5, 0.5,        0, 0, 0, 10)
        self.MakeCube(30, center_height, 49.5,      42, height, 3,     0, 0.3, 1,      0.5, 0.5, 0.5,        0, 0, 0, 10)
        self.MakeCube(10.5, center_height, 30,      3, height, 30,     0, 0.3, 1,      0.5, 0.5, 0.5,        0, 0, 0, 10)
        self.MakeCube(49.5, center_height, 30,      3, height, 30,     0, 0.3, 1,      0.5, 0.5, 0.5,        0, 0, 0, 10)

        self.MakeCube(30, center_height, 15,      6, height, 6,     0, 0.3, 1,      0.5, 0.5, 0.5,        0, 0, 0, 10)
        self.MakeCube(30, center_height, 45,      6, height, 6,     0, 0.3, 1,      0.5, 0.5, 0.5,        0, 0, 0, 10)

        self.MakeCube(15, center_height, 30,      6, height, 6,     0, 0.3, 1,      0.5, 0.5, 0.5,        0, 0, 0, 10)
        self.MakeCube(45, center_height, 30,      6, height, 6,     0, 0.3, 1,      0.5, 0.5, 0.5,        0, 0, 0, 10)

        self.MakeCube(24, center_height, 24,      6, height, 6,     0, 0.3, 1,      0.5, 0.5, 0.5,        0, 0, 0, 10)
        self.MakeCube(24, center_height, 36,      6, height, 6,     0, 0.3, 1,      0.5, 0.5, 0.5,        0, 0, 0, 10)
        self.MakeCube(36, center_height, 24,      6, height, 6,     0, 0.3, 1,      0.5, 0.5, 0.5,        0, 0, 0, 10)
        self.MakeCube(36, center_height, 36,      6, height, 6,     0, 0.3, 1,      0.5, 0.5, 0.5,        0, 0, 0, 10)

        # Lights
        self.MakeLight(6,8,6, 0.8,0.8,0.8, 0.2,0.2,0.2, 0,0,0)
        self.MakeSphere(6,8,6, 1,1,1, 0,0,0 ,0,0,0, 1,1,1, 3, emission_r=1, emission_b=1, emission_g=1)
        self.MakeLight(6,8,54, 0.8,0.8,0.8, 0.2,0.2,0.2, 0,0,0)
        self.MakeSphere(6,8,54, 1,1,1, 0,0,0 ,0,0,0, 1,1,1, 3, emission_r=1, emission_b=1, emission_g=1)

        self.MakeLight(30,10,30, 0.8,0.8,0.8, 0.4,0.4,0.4, 0,0,0) # center light
        self.light_rotation_array.append([2, 30, 30, 8, (2 * math.pi / 5), 0.0])
        self.MakeSphere(30,10,30, 1,1,1, 0,0,0 ,0,0,0, 1,1,1, 3, emission_r=1, emission_b=1, emission_g=1)
        self.sphere_rotation_array.append([2, 30, 30, 8, (2 * math.pi / 5), 0.0])

        self.MakeLight(54,8,6, 0.8,0.8,0.8, 0.2,0.2,0.2, 0,0,0)
        self.MakeSphere(54,8,6, 1,1,1, 0,0,0 ,0,0,0, 1,1,1, 3, emission_r=1, emission_b=1, emission_g=1)
        self.MakeLight(54,8,54, 0.8,0.8,0.8, 0.2,0.2,0.2, 0,0,0)
        self.MakeSphere(54,8,54, 1,1,1, 0,0,0 ,0,0,0, 1,1,1, 3, emission_r=1, emission_b=1, emission_g=1)

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