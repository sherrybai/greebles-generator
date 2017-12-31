'''
Generate greeble dataset

Run as: blender --background --python render.py
'''

import bpy
import os
import mathutils
from math import radians

# paths
orig_path = os.getcwd() + "/Greebles-2-0-symmetric/Greebles3DS"
render_path = os.getcwd() + "/images/"

r = 15  # radius of camera orbit
azimuths = 18
a_inc = radians(360/azimuths)

elevations = 9 # number of elevations
e_inc = radians(10) # 5 degrees

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

	# set camera location
	camera = bpy.data.objects["Camera"]
	camera.location = (0, -r, 0)

	# point camera to origin
	direction = -mathutils.Vector(camera.location)
	rot_quat = direction.to_track_quat('-Z', 'Y')
	camera.rotation_euler = rot_quat.to_euler()

	# create empty (for camera orbit)     
	b_empty = bpy.data.objects.new("Empty", None)
	b_empty.location = (0, 0, 0)
	camera.parent = b_empty

	# rotate camera
	for a in range(azimuths):
		# rotate greeble (to simulate camera orbit)
		greeble.rotation_euler = (0, 0, a * a_inc)
		for e in range(elevations):
			mat_rot = mathutils.Matrix.Rotation(e_inc*(e-elevations//2), 4, 'X')
			b_empty.matrix_world = mat_rot
			bpy.context.scene.update() 
			# render
			bpy.context.scene.render.filepath = render_path + f[:-4] + "_a" + str(a) + "_e" + str(e) + ".png"
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
