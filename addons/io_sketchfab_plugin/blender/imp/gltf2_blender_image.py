# Copyright 2018 The glTF-Blender-IO authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import bpy
import os
import tempfile
from os.path import dirname, join, isfile

from ...io.imp.gltf2_io_binary import *

# Note that Image is not a glTF2.0 object
class BlenderImage():

    @staticmethod
    def get_image_path(gltf, img_idx):
        pyimage = gltf.data.images[img_idx]

        image_name = "Image_" + str(img_idx)

        if pyimage.uri:
            sep = ';base64,'
            if pyimage.uri[:5] == 'data:':
                idx = pyimage.uri.find(sep)
                if idx != -1:
                    return False, None, None

            if isfile(join(dirname(gltf.filename), pyimage.uri)):
                return True, join(dirname(gltf.filename), pyimage.uri), image_name
            else:
                pyimage.gltf.log.error("Missing file (index " + str(img_idx) + "): " + pyimage.uri)
                return False, None, None

        if pyimage.buffer_view is None:
            return False, None, None

        return False, None, None

    @staticmethod
    def create(gltf, img_idx):

        img = gltf.data.images[img_idx]

        img.blender_image_name = None

        if gltf.import_settings['pack_images'] == False:

            # Images are not packed (if image is a real file)
            real, path, img_name = BlenderImage.get_image_path(gltf, img_idx)

            if real == True:

                blender_image = bpy.data.images.load(path)
                blender_image.name = img_name
                img.blender_image_name = blender_image.name
                return

        # Create a temp image, pack, and delete image
        tmp_image = tempfile.NamedTemporaryFile(delete=False)
        img_data, img_name = BinaryData.get_image_data(gltf, img_idx)
        tmp_image.write(img_data)
        tmp_image.close()

        blender_image = bpy.data.images.load(tmp_image.name)
        blender_image.pack()
        blender_image.name = img_name
        img.blender_image_name = blender_image.name
        os.remove(tmp_image.name)
