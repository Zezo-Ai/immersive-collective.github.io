import bpy
import os
import json
from PIL import Image

# Get the current blend file name and directory
blend_file_path = bpy.data.filepath
if not blend_file_path:
    raise RuntimeError("Please save your .blend file before running this script.")

blend_file_name = os.path.splitext(os.path.basename(blend_file_path))[0]  # File name without extension
blend_file_directory = os.path.dirname(blend_file_path)

# Create a subfolder named after the blend file in the same directory
output_directory = os.path.join(blend_file_directory, blend_file_name)
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Create a subfolder for textures within the output directory
textures_directory = os.path.join(output_directory, "textures")
if not os.path.exists(textures_directory):
    os.makedirs(textures_directory)

# Dictionary to store the filenames for JSON export
exported_files = {}

# Function to convert textures to WebP format
def convert_textures_to_webp(quality=45):
    for image in bpy.data.images:
        if image.filepath and image.filepath.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = bpy.path.abspath(image.filepath)
            if os.path.exists(image_path):
                img = Image.open(image_path)
                webp_filename = f"{os.path.splitext(os.path.basename(image_path))[0]}.webp"
                webp_path = os.path.join(textures_directory, webp_filename)
                img.save(webp_path, 'webp', quality=quality)
                print(f"Converted {image.filepath} to {webp_path}")
                # Update the texture path in Blender to use the newly created WebP
                image.filepath = webp_path
                image.reload()

# Convert all textures to WebP before exporting
convert_textures_to_webp(quality=45)

# Iterate over all mesh objects in the scene and export them as GLB
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':  # Only export meshes
        # Select only the current object
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        # Create the export filename
        export_filename = f"{obj.name}.glb"
        export_path = os.path.join(output_directory, export_filename)

        # Export as GLB
        bpy.ops.export_scene.gltf(
            filepath=export_path,
            use_selection=True,  # Export only the selected object
            export_format='GLB',  # Save as .glb
            export_draco_mesh_compression_enable=True,  # Enable Draco compression
            export_draco_mesh_compression_level=6,  # Compression level
            export_image_format='WEBP',  # Export textures as WebP
            #apply_modifiers=True,  # Apply all modifiers
            export_materials='EXPORT',  # Export materials
        )

        # Add to the JSON data
        exported_files[obj.name] = export_filename
        print(f"Exported {obj.name} to {export_path}")

# Save the JSON file containing the list of exported files
json_path = os.path.join(output_directory, "exported_files.json")
with open(json_path, 'w') as json_file:
    json.dump(exported_files, json_file, indent=4)

print(f"Exported file list saved to {json_path}")
