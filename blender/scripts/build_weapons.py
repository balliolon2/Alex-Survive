import bpy
import bmesh
import math
import os

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for collection in bpy.data.collections:
        bpy.data.collections.remove(collection)
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat)

def create_material(name, base_color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = base_color
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
    return mat

def build_lead_pipe(blend_path, glb_path):
    clear_scene()
    
    mat_metal = create_material("Mat_Rusted_Iron", (0.42, 0.44, 0.46, 1.0), roughness=0.6, metallic=0.8)
    mat_tape = create_material("Mat_Black_Tape", (0.12, 0.12, 0.14, 1.0), roughness=0.85, metallic=0.05)
    
    # 1. Main Pipe Body
    # Total length 0.70m, from Z = -0.12 to Z = +0.58. Origin (0,0,0) is at palm grip.
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=0.018,
        depth=0.70,
        location=(0.0, 0.0, 0.23)
    )
    pipe_obj = bpy.context.active_object
    pipe_obj.name = "LeadPipe"
    pipe_obj.data.materials.append(mat_metal)
    
    # 2. Threaded Collar at striking end (Z = 0.53 to 0.58)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=0.023,
        depth=0.06,
        location=(0.0, 0.0, 0.55)
    )
    collar = bpy.context.active_object
    collar.data.materials.append(mat_metal)
    
    # 3. Base cap / coupling ring at pommel (Z = -0.10)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=0.022,
        depth=0.03,
        location=(0.0, 0.0, -0.105)
    )
    pommel = bpy.context.active_object
    pommel.data.materials.append(mat_metal)
    
    # 4. Friction Tape Grip around handle (Z = -0.06 to +0.12)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=0.0205,
        depth=0.18,
        location=(0.0, 0.0, 0.03)
    )
    tape = bpy.context.active_object
    tape.data.materials.append(mat_tape)
    
    # Join parts into single weapon mesh with preserved materials
    bpy.ops.object.select_all(action='DESELECT')
    pipe_obj.select_set(True)
    collar.select_set(True)
    pommel.select_set(True)
    tape.select_set(True)
    bpy.context.view_layer.objects.active = pipe_obj
    bpy.ops.object.join()
    
    # Smooth shading
    for poly in pipe_obj.data.polygons:
        poly.use_smooth = True
        
    os.makedirs(os.path.dirname(blend_path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    
    os.makedirs(os.path.dirname(glb_path), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        use_selection=False,
        export_apply=True,
        export_yup=True
    )
    print(f"LeadPipe exported successfully to: {glb_path}")

def build_spiked_bat(blend_path, glb_path):
    clear_scene()
    
    mat_wood = create_material("Mat_Worn_Wood", (0.58, 0.42, 0.28, 1.0), roughness=0.65, metallic=0.0)
    mat_tape = create_material("Mat_Grip_Tape", (0.75, 0.72, 0.68, 1.0), roughness=0.88, metallic=0.0)
    mat_nails = create_material("Mat_Rusty_Nails", (0.28, 0.25, 0.24, 1.0), roughness=0.5, metallic=0.9)
    
    # 1. Base Bat Body
    # Knob at Z = -0.10, Handle Z = -0.08 to +0.18, Barrel Z = +0.18 to +0.72
    # Total length 0.82m. Origin (0,0,0) at palm grip (Z = 0.0).
    
    # Knob
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.024, depth=0.025, location=(0.0, 0.0, -0.09)
    )
    knob = bpy.context.active_object
    knob.data.materials.append(mat_wood)
    
    # Handle
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.015, depth=0.22, location=(0.0, 0.0, 0.03)
    )
    handle = bpy.context.active_object
    handle.data.materials.append(mat_tape) # Taped grip
    
    # Mid taper
    bpy.ops.mesh.primitive_cone_add(
        vertices=16, radius1=0.015, radius2=0.032, depth=0.24, location=(0.0, 0.0, 0.26)
    )
    taper = bpy.context.active_object
    taper.data.materials.append(mat_wood)
    
    # Barrel
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.033, depth=0.28, location=(0.0, 0.0, 0.52)
    )
    barrel = bpy.context.active_object
    barrel.data.materials.append(mat_wood)
    
    # Barrel Cap (dome)
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=16, ring_count=8, radius=0.033, location=(0.0, 0.0, 0.66)
    )
    cap = bpy.context.active_object
    cap.data.materials.append(mat_wood)
    
    # 2. Rusty Nails driven through barrel
    nail_objs = []
    nail_configs = [
        (0.46, 0.0),
        (0.52, math.pi * 0.4),
        (0.58, math.pi * 0.8),
        (0.48, math.pi * 1.2),
        (0.56, math.pi * 1.6),
        (0.62, math.pi * 0.2)
    ]
    
    for z_pos, angle in nail_configs:
        # Long nail penetrating through bat
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8,
            radius=0.0035,
            depth=0.11, # exceeds bat diameter (0.066m), so it sticks out both sides
            location=(0.0, 0.0, z_pos),
            rotation=(math.pi / 2.0, 0.0, angle)
        )
        nail = bpy.context.active_object
        nail.data.materials.append(mat_nails)
        nail_objs.append(nail)
        
    # Join everything
    bpy.ops.object.select_all(action='DESELECT')
    barrel.select_set(True)
    knob.select_set(True)
    handle.select_set(True)
    taper.select_set(True)
    cap.select_set(True)
    for n in nail_objs:
        n.select_set(True)
    bpy.context.view_layer.objects.active = barrel
    barrel.name = "SpikedBat"
    bpy.ops.object.join()
    
    for poly in barrel.data.polygons:
        poly.use_smooth = True
        
    os.makedirs(os.path.dirname(blend_path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    
    os.makedirs(os.path.dirname(glb_path), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        use_selection=False,
        export_apply=True,
        export_yup=True
    )
    print(f"SpikedBat exported successfully to: {glb_path}")

if __name__ == "__main__":
    base_dir = "C:/Users/bond/Documents/Alex-Survive"
    
    pipe_blend = f"{base_dir}/blender/weapons/lead_pipe.blend"
    pipe_glb = f"{base_dir}/alex-survive-godot/assets/models/weapons/lead_pipe.glb"
    build_lead_pipe(pipe_blend, pipe_glb)
    
    bat_blend = f"{base_dir}/blender/weapons/spiked_bat.blend"
    bat_glb = f"{base_dir}/alex-survive-godot/assets/models/weapons/spiked_bat.glb"
    build_spiked_bat(bat_blend, bat_glb)
