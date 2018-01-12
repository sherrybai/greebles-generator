# Generate greeble dataset
#
# Run as: blender --background --python render.py

import bpy, os, mathutils, random
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


def render(greeble, f, lamp_type):
    for i in range(POSES_PER_GREEBLE):
        # rotate greeble randomly
        greeble.rotation_euler = (random_angle(), random_angle(), random_angle())
        bpy.context.scene.render.filepath = render_path + f[:-4] + "_" + lamp_type + "_" + str(i) + ".png"
        bpy.ops.render.render(write_still=True)
    return greeble


def random_angle():
    return radians(360 * random.random())


def delete_obj(label):
    obj = bpy.data.objects.get(label)
    if obj is not None:
        obj.select = True
        bpy.ops.object.delete()


def add_lamp(lamp_name, lamp_type, radius=r):
    # adapted from Stack Overflow:
    # https://stackoverflow.com/questions/17355617/can-you-add-a-light-source-in-blender-using-python
    data = bpy.data.lamps.new(name=lamp_name, type=lamp_type)
    object = bpy.data.objects.new(name=lamp_name, object_data=data)
    bpy.context.scene.objects.link(object)
    object.location = (0, 0, radius)
    return object


def point_to_origin(obj):
    direction = -mathutils.Vector(obj.location)
    rot_quat = direction.to_track_quat('-Z', 'Y')
    obj.rotation_euler = rot_quat.to_euler()


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
    world = bpy.context.scene.world
    world.light_settings.use_environment_light = True
    render(greeble, f, "ambient")
    world.light_settings.use_environment_light = False

    # lamp setup
    # spot_lamp = add_lamp("Lamp", 'POINT')
    # spot_lamp.data.quadratic_attenuation = 0.2

    # create empty (for lamp orbit)
    b_empty = bpy.data.objects.new("Empty", None)
    b_empty.location = ORIGIN

    # render for four different lighting configs
    n_lamps = 4
    for i in range(n_lamps):
        lamp = add_lamp("Lamp"+str(i), 'POINT')
        lamp.parent = b_empty
        mat_rot = mathutils.Euler((random_angle(), random_angle(), random_angle()), 'XYZ')
        mat_rot = mat_rot.to_matrix().to_4x4()
        b_empty.matrix_world = mat_rot
        render(greeble, f, str(i))

    for i in range(n_lamps):
        delete_obj("Lamp"+str(i))

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
