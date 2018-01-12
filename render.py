# Generate greeble dataset
#
# Run as: blender --background --python render.py

import bpy
import os
import mathutils
import random
from math import radians

# paths
orig_path = os.getcwd() + "/Greebles-2-0-symmetric/Greebles3DS"
render_path = os.getcwd() + "/images/"

r = 15  # distance of camera to greeble
# N = 5  # scale of background image

# 80 greebles total, 5 lighting conditions
POSES_PER_GREEBLE = 200
ORIGIN = (0, 0, 0)

imsize = 48  # size of output image


def random_angle(min_angle=0, max_angle=360):
    return radians((max_angle - min_angle) * random.random() + min_angle)


def delete_obj(label):
    obj = bpy.data.objects.get(label)
    if obj is not None:
        obj.select = True
        bpy.ops.object.delete()


def add_lamp(lamp_name, lamp_type, radius=r):
    # adapted from Stack Overflow:
    # https://stackoverflow.com/questions/17355617/can-you-add-a-light-source-in-blender-using-python
    data = bpy.data.lamps.new(name=lamp_name, type=lamp_type)
    lamp_object = bpy.data.objects.new(name=lamp_name, object_data=data)
    bpy.context.scene.objects.link(lamp_object)
    lamp_object.location = (0, 0, radius)
    return lamp_object


def point_to_origin(obj):
    direction = -mathutils.Vector(obj.location)
    rot_quat = direction.to_track_quat('-Z', 'Y')
    obj.rotation_euler = rot_quat.to_euler()


def render(greeble, f, lamp_type, lamp_empty=None):
    for i in range(POSES_PER_GREEBLE):
        # rotate greeble randomly
        # greeble.rotation_euler = (random_angle(), random_angle(), random_angle())
        greeble.rotation_euler = (0, 0, random_angle())

        # rotate lamp randomly
        if lamp_empty is not None:
            mat_rot = mathutils.Euler((random_angle(), random_angle(), random_angle()), 'XYZ')
            mat_rot = mat_rot.to_matrix().to_4x4()
            lamp_empty.matrix_world = mat_rot

        bpy.context.scene.render.filepath = "{}{}_{}_{:03d}.png".format(render_path, f[:-4], lamp_type, i)
        bpy.ops.render.render(write_still=True)
    return greeble


def process_greeble(greeble, root, f):
    delete_obj("Cube")  # delete default cube
    delete_obj("Lamp")  # delete default lamp

    # delete previous greeble
    if greeble is not None:
        greeble.select = True
        bpy.ops.object.delete()

    # import .3ds file
    fpath = os.path.join(root, f)
    bpy.ops.import_scene.autodesk_3ds(filepath=fpath)

    # recenter
    # on import, all previously selected objects are deselected and the newly imported object is selected
    greeble = bpy.context.selected_objects[0]
    new_origin = (0, 0, greeble.dimensions[2] / 2)  # place center at median of greeble height (z-dimension)
    bpy.context.scene.cursor_location = new_origin
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    greeble.location = ORIGIN

    # set camera location
    camera = bpy.data.objects["Camera"]
    camera.location = (0, -r, 0)

    # point camera to origin
    point_to_origin(camera)

    # ambient lighting setup
    # world = bpy.context.scene.world
    # world.light_settings.use_environment_light = True
    # render(greeble, f, "ambient")
    # world.light_settings.use_environment_light = False

    # create empty (for lamp orbit)
    b_empty = bpy.data.objects.new("Empty", None)
    b_empty.location = ORIGIN

    # top lamp
    top_lamp = add_lamp("Top_Lamp", 'SPOT')

    # render for lamp configs
    random_lamp = add_lamp("Random_Lamp", 'POINT')
    random_lamp.parent = b_empty
    render(greeble, f, "lamps", lamp_empty=b_empty)

    delete_obj("Random_Lamp")
    delete_obj("Top_Lamp")

    return greeble


# create a scene
scene = bpy.data.scenes.new("Scene")

# rendered images should be square
bpy.context.scene.render.resolution_x = imsize * 2  # not sure why we have to double imsize
bpy.context.scene.render.resolution_y = bpy.context.scene.render.resolution_x
bpy.context.scene.render.alpha_mode = 'SKY'

# greeble object
curr_greeble = None

# complete for every .3ds file
for root, dirs, files in os.walk(orig_path):
    # pick out 3DS files
    filtered = list(filter(lambda x: x[-4:].lower() == ".3ds", files))
    for f in filtered:
        curr_greeble = process_greeble(curr_greeble, root, f)
