import bpy
import math
import os
from mathutils import Vector, Quaternion

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for collection in bpy.data.collections:
        bpy.data.collections.remove(collection)
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)
    for arm in bpy.data.armatures:
        bpy.data.armatures.remove(arm)
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat)

def create_material(name, base_color, roughness=0.6, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = base_color
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
    return mat

def build_alex(base_dir):
    clear_scene()
    
    # 1. Materials for Alex
    mat_jacket = create_material("Mat_Jacket", (0.24, 0.32, 0.22, 1.0), roughness=0.65) # Olive green field jacket
    mat_skin = create_material("Mat_Skin", (0.82, 0.65, 0.52, 1.0), roughness=0.55)     # Warm survivor skin
    mat_pants = create_material("Mat_Pants", (0.16, 0.18, 0.20, 1.0), roughness=0.75)   # Charcoal cargo pants
    mat_boots = create_material("Mat_Boots", (0.10, 0.10, 0.11, 1.0), roughness=0.60, metallic=0.1) # Black combat boots
    mat_pack = create_material("Mat_Backpack", (0.38, 0.26, 0.18, 1.0), roughness=0.8) # Leather / canvas brown pack
    mat_hair = create_material("Mat_Hair", (0.12, 0.10, 0.08, 1.0), roughness=0.9)     # Dark brown hair
    mat_wrap = create_material("Mat_HandWrap", (0.80, 0.78, 0.72, 1.0), roughness=0.85) # Beige hand bandages

    # 2. Build Mesh Parts with assigned Vertex Groups
    mesh_parts = []
    
    def add_box_part(name, loc, scale, mat, vg_name):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = scale
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        obj.data.materials.append(mat)
        vg = obj.vertex_groups.new(name=vg_name)
        vg.add(list(range(len(obj.data.vertices))), 1.0, 'REPLACE')
        mesh_parts.append(obj)
        return obj

    def add_sphere_part(name, loc, radius, mat, vg_name):
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=12, ring_count=8, radius=radius, location=loc
        )
        obj = bpy.context.active_object
        obj.name = name
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        obj.data.materials.append(mat)
        vg = obj.vertex_groups.new(name=vg_name)
        vg.add(list(range(len(obj.data.vertices))), 1.0, 'REPLACE')
        mesh_parts.append(obj)
        return obj

    def add_limb_segment(name, p_start, p_end, radius, mat, vg_name, segments=12):
        v = Vector(p_end) - Vector(p_start)
        length = v.length
        center = (Vector(p_start) + Vector(p_end)) * 0.5
        
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=segments,
            radius=radius,
            depth=length,
            location=center
        )
        obj = bpy.context.active_object
        obj.name = name
        
        # Orient cylinder from default (0, 0, 1) along vector v
        dir_v = v.normalized()
        rot_quat = Vector((0.0, 0.0, 1.0)).rotation_difference(dir_v)
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = rot_quat
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        
        obj.data.materials.append(mat)
        vg = obj.vertex_groups.new(name=vg_name)
        vg.add(list(range(len(obj.data.vertices))), 1.0, 'REPLACE')
        mesh_parts.append(obj)
        return obj

    # Torso (Chest + Spine)
    add_box_part("Chest", (0.0, 0.0, 1.34), (0.44, 0.26, 0.36), mat_jacket, "Chest")
    add_box_part("Hips", (0.0, 0.0, 1.04), (0.38, 0.24, 0.24), mat_pants, "Hips")
    
    # Backpack mounted on back
    add_box_part("Backpack", (0.0, 0.18, 1.28), (0.34, 0.16, 0.40), mat_pack, "Chest")
    # Small bedroll on bottom of pack (horizontal along X)
    add_limb_segment("Bedroll", (-0.18, 0.18, 1.04), (0.18, 0.18, 1.04), 0.07, mat_pack, "Chest")

    # Neck & Head
    add_limb_segment("Neck", (0.0, 0.0, 1.48), (0.0, 0.0, 1.58), 0.065, mat_skin, "Neck")
    add_box_part("Head", (0.0, 0.0, 1.66), (0.22, 0.22, 0.24), mat_skin, "Head")
    add_box_part("Hair", (0.0, -0.01, 1.74), (0.23, 0.23, 0.10), mat_hair, "Head")

    # Left Arm: Perfectly connected chain from shoulder to hand
    # Shoulder joint sphere seamlessly blends jacket into arm
    add_sphere_part("Shoulder_L", (0.22, 0.0, 1.42), 0.078, mat_jacket, "Chest")
    add_limb_segment("UpperArm_L", (0.22, 0.0, 1.42), (0.44, 0.0, 1.18), 0.072, mat_jacket, "UpperArm.L")
    add_sphere_part("Elbow_L", (0.44, 0.0, 1.18), 0.064, mat_skin, "LowerArm.L")
    add_limb_segment("LowerArm_L", (0.44, 0.0, 1.18), (0.60, 0.0, 0.94), 0.058, mat_skin, "LowerArm.L")
    add_sphere_part("Wrist_L", (0.60, 0.0, 0.94), 0.054, mat_wrap, "Hand.L")
    add_limb_segment("Hand_L", (0.60, 0.0, 0.94), (0.66, 0.0, 0.85), 0.055, mat_wrap, "Hand.L")

    # Right Arm: Perfectly connected chain from shoulder to hand
    add_sphere_part("Shoulder_R", (-0.22, 0.0, 1.42), 0.078, mat_jacket, "Chest")
    add_limb_segment("UpperArm_R", (-0.22, 0.0, 1.42), (-0.44, 0.0, 1.18), 0.072, mat_jacket, "UpperArm.R")
    add_sphere_part("Elbow_R", (-0.44, 0.0, 1.18), 0.064, mat_skin, "LowerArm.R")
    add_limb_segment("LowerArm_R", (-0.44, 0.0, 1.18), (-0.60, 0.0, 0.94), 0.058, mat_skin, "LowerArm.R")
    add_sphere_part("Wrist_R", (-0.60, 0.0, 0.94), 0.054, mat_wrap, "Hand.R")
    add_limb_segment("Hand_R", (-0.60, 0.0, 0.94), (-0.66, 0.0, 0.85), 0.055, mat_wrap, "Hand.R")

    # Left Leg: Connected chain
    add_limb_segment("UpperLeg_L", (0.13, 0.0, 0.95), (0.13, 0.0, 0.50), 0.082, mat_pants, "UpperLeg.L")
    add_sphere_part("Knee_L", (0.13, 0.0, 0.50), 0.075, mat_pants, "LowerLeg.L")
    add_limb_segment("LowerLeg_L", (0.13, 0.0, 0.50), (0.13, 0.0, 0.12), 0.072, mat_pants, "LowerLeg.L")
    add_box_part("Boot_L", (0.13, 0.04, 0.07), (0.13, 0.22, 0.14), mat_boots, "Foot.L")

    # Right Leg: Connected chain
    add_limb_segment("UpperLeg_R", (-0.13, 0.0, 0.95), (-0.13, 0.0, 0.50), 0.082, mat_pants, "UpperLeg.R")
    add_sphere_part("Knee_R", (-0.13, 0.0, 0.50), 0.075, mat_pants, "LowerLeg.R")
    add_limb_segment("LowerLeg_R", (-0.13, 0.0, 0.50), (-0.13, 0.0, 0.12), 0.072, mat_pants, "LowerLeg.R")
    add_box_part("Boot_R", (-0.13, 0.04, 0.07), (0.13, 0.22, 0.14), mat_boots, "Foot.R")

    # Create root object at (0, 0, 0) so joined mesh origin is (0, 0, 0)
    bpy.ops.mesh.primitive_cube_add(size=0.001, location=(0, 0, 0))
    root_obj = bpy.context.active_object
    root_obj.name = "Alex_Mesh"

    # Join all body parts into single Character Mesh
    bpy.ops.object.select_all(action='DESELECT')
    for p in mesh_parts:
        p.select_set(True)
    root_obj.select_set(True)
    bpy.context.view_layer.objects.active = root_obj
    bpy.ops.object.join()
    alex_mesh = bpy.context.active_object
    alex_mesh.name = "Alex_Mesh"
    
    # Apply all transforms to zero out location, rotation, scale
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # 3. Create Armature with Sockets
    bpy.ops.object.armature_add(location=(0, 0, 0))
    arm_obj = bpy.context.active_object
    arm_obj.name = "Alex_Armature"
    arm_data = arm_obj.data
    arm_data.name = "Alex_Skeleton"

    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = arm_data.edit_bones
    
    # Remove default single bone
    for b in edit_bones:
        edit_bones.remove(b)

    # Helper function to create edit bones
    def make_bone(name, head, tail, parent_name=None):
        b = edit_bones.new(name)
        b.head = head
        b.tail = tail
        if parent_name and parent_name in edit_bones:
            b.parent = edit_bones[parent_name]
        return b

    # Core Spine Hierarchy
    make_bone("Root", (0, 0, 0), (0, 0, 0.1))
    make_bone("Hips", (0, 0, 0.95), (0, 0, 1.15), "Root")
    make_bone("Spine", (0, 0, 1.15), (0, 0, 1.30), "Hips")
    make_bone("Chest", (0, 0, 1.30), (0, 0, 1.50), "Spine")
    make_bone("Neck", (0, 0, 1.50), (0, 0, 1.58), "Chest")
    make_bone("Head", (0, 0, 1.58), (0, 0, 1.80), "Neck")

    # Left Arm
    make_bone("UpperArm.L", (0.22, 0.0, 1.42), (0.44, 0.0, 1.18), "Chest")
    make_bone("LowerArm.L", (0.44, 0.0, 1.18), (0.60, 0.0, 0.94), "UpperArm.L")
    make_bone("Hand.L", (0.60, 0.0, 0.94), (0.66, 0.0, 0.85), "LowerArm.L")

    # Right Arm
    make_bone("UpperArm.R", (-0.22, 0.0, 1.42), (-0.44, 0.0, 1.18), "Chest")
    make_bone("LowerArm.R", (-0.44, 0.0, 1.18), (-0.60, 0.0, 0.94), "UpperArm.R")
    make_bone("Hand.R", (-0.60, 0.0, 0.94), (-0.66, 0.0, 0.85), "LowerArm.R")
    
    # SOCKET 1: Hand.R active weapon socket (at wrist/palm, pointing forward)
    make_bone("Socket_Hand_R", (-0.63, 0.0, 0.89), (-0.63, -0.20, 0.89), "Hand.R")

    # Left Leg
    make_bone("UpperLeg.L", (0.13, 0.0, 0.95), (0.13, 0.0, 0.50), "Hips")
    make_bone("LowerLeg.L", (0.13, 0.0, 0.50), (0.13, 0.0, 0.12), "UpperLeg.L")
    make_bone("Foot.L", (0.13, 0.0, 0.12), (0.13, 0.14, 0.0), "LowerLeg.L")

    # Right Leg
    make_bone("UpperLeg.R", (-0.13, 0.0, 0.95), (-0.13, 0.0, 0.50), "Hips")
    make_bone("LowerLeg.R", (-0.13, 0.0, 0.50), (-0.13, 0.0, 0.12), "UpperLeg.R")
    make_bone("Foot.R", (-0.13, 0.0, 0.12), (-0.13, 0.14, 0.0), "LowerLeg.R")

    # SOCKET 2: Backpack holster socket (mounted high on backpack, pointing upwards/slanted)
    make_bone("Socket_Backpack", (0.12, 0.22, 1.35), (0.12, 0.22, 1.58), "Chest")

    bpy.ops.object.mode_set(mode='OBJECT')

    # 4. Attach Armature Modifier to Alex_Mesh
    arm_mod = alex_mesh.modifiers.new(name="Armature", type='ARMATURE')
    arm_mod.object = arm_obj
    alex_mesh.parent = arm_obj

    # 5. Export
    blend_path = f"{base_dir}/blender/characters/alex.blend"
    glb_path = f"{base_dir}/alex-survive-godot/assets/models/characters/alex.glb"
    
    os.makedirs(os.path.dirname(blend_path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    
    os.makedirs(os.path.dirname(glb_path), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        use_selection=False,
        export_yup=True,
        export_skins=True
    )
    print(f"Alex character model successfully exported to: {glb_path}")

if __name__ == "__main__":
    base_dir = "C:/Users/bond/Documents/Alex-Survive"
    build_alex(base_dir)
