'''
Generate greeble dataset

Run as: blender --background --python render.py
'''

import bpy
import os
import mathutils
from math import pi

# paths
orig_path = os.getcwd() + "/Greebles-2-0-symmetric/Greebles3DS"
render_path = os.getcwd() + "/images/"

r = 15  # radius of camera orbit
azimuths = 1
a_inc = 2*pi/azimuths

imsize = 96 # size of output image

def process_greeble(greeble, root, f):
	# delete default cube
	cube = bpy.data.objects.get("Cube")
	if cube is not None:
		cube.select = True
		bpy.ops.object.delete()
	
	# delete previous greeble
	if greeble is not None:
		greeble.select = True
		bpy.ops.object.delete()

	# import .3ds file
	fpath = os.path.join(root, f)
	bpy.ops.import_scene.autodesk_3ds(filepath = fpath)

	# recenter
	# on import, all previously selected objects are deselected and  the newly imported object is selected
	greeble = bpy.context.selected_objects[0]
	new_origin = (0, 0, greeble.dimensions[2]/2)  # place center at median of greeble height (z-dimension)
	bpy.context.scene.cursor_location = new_origin
	bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
	greeble.location = (0, 0, 0)

	'''
	# set lamp location
	lamp = bpy.data.objects["Lamp"]
	lamp.location = (5, -5.0, -10)

	lamp_data = bpy.data.lamps.new(name="New Lamp", type='POINT')
	lamp_object = bpy.data.objects.new(name="New Lamp", object_data=lamp_data)
	scene.objects.link(lamp_object)
	lamp_object.location = (5.0, 5.0, -10)
	lamp_object.select = True
	scene.objects.active = lamp_object
	'''

	# set camera location
	camera = bpy.data.objects["Camera"]
	camera.location = (0, -r, 0)

	# point camera to origin
	direction = -mathutils.Vector(camera.location)
	rot_quat = direction.to_track_quat('-Z', 'Y')
	camera.rotation_euler = rot_quat.to_euler()

	# rotate greeble (to simulate camera orbit)
	for a in range(azimuths):
		# rotate
		greeble.rotation_euler = (0, 0, a * a_inc)
		# render
		bpy.context.scene.render.filepath = render_path + f[:-4] + "_a" + str(a) + ".png"
		bpy.ops.render.render(write_still=True)
	
	return greeble

# create a scene
scene = bpy.data.scenes.new("Scene")

# rendered images should be square
bpy.context.scene.render.resolution_x = imsize
bpy.context.scene.render.resolution_y = bpy.context.scene.render.resolution_x

# greeble object
greeble = None

# complete for every .3ds file
for root, dirs, files in os.walk(orig_path):
	# pick out 3DS files
	filtered = list(filter(lambda x: x[-4:].lower() == ".3ds", files))
	for f in filtered:
		greeble = process_greeble(greeble, root, f)
