# greebles-generator

Python script for Blender for generating images of Greebles in random poses and lighting condtions.

Relies on 3DS files containing three-dimensional meshes created by the Tarr Lab at Carnegie Mellon University.

Instructions:
 - Download the original symmetric Greebles meshes here: http://wiki.cnbc.cmu.edu/images/Greebles-2-0-symmetric.zip
 - Unzip in same directory as render.py.

Run as: `blender --background --python render.py`

Adjustable parameters (top of render.py):
- `r`: Distance of camera to Greeble.
- `set_type`: Which subset of dataset to generate. Set to "train" to generate upright Greebles (vertical rotation only); set to "test" to generate Greebles that can rotate along all three axes. ("Test" Greebles can only rotate from -30 to 30 degrees longitudinally and laterally.)
- `imsize`: Size of output image, in pixels.
- `num_imgs`: Number of images to produce.
