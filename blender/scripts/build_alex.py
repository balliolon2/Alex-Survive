import bpy
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
        bpy.ops.object.transform_apply(scale=True)
        obj.data.materials.append(mat)
        vg = obj.vertex_groups.new(name=vg_name)
        vg.add(list(range(len(obj.data.vertices))), 1.0, 'REPLACE')
        mesh_parts.append(obj)
        return obj

    def add_cyl_part(name, loc, radius, depth, mat, vg_name, rot=(0,0,0)):
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=12, radius=radius, depth=depth, location=loc, rotation=rot
        )
        obj = bpy.context.active_object
        obj.name = name
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
    # Small bedroll on bottom of pack
    add_cyl_part("Bedroll", (0.0, 0.18, 1.04), 0.07, 0.38, mat_pack, "Chest", rot=(0, math.pi/2.0, 0))

    # Neck & Head
    add_cyl_part("Neck", (0.0, 0.0, 1.52), 0.065, 0.10, mat_skin, "Neck")
    add_box_part("Head", (0.0, 0.0, 1.66), (0.22, 0.22, 0.24), mat_skin, "Head")
    add_box_part("Hair", (0.0, -0.01, 1.74), (0.23, 0.23, 0.10), mat_hair, "Head")

    # Left Arm (A-pose: ~45 deg downward)
    # Shoulder L at (0.26, 0, 1.42), Elbow at (0.44, 0, 1.18), Hand at (0.60, 0, 0.94)
    add_cyl_part("UpperArm_L", (0.35, 0.0, 1.30), 0.065, 0.28, mat_jacket, "UpperArm.L", rot=(0, math.pi/4.0, 0))
    add_cyl_part("LowerArm_L", (0.52, 0.0, 1.06), 0.055, 0.28, mat_skin, "LowerArm.L", rot=(0, math.pi/4.0, 0))
    add_box_part("Hand_L", (0.64, 0.0, 0.90), (0.09, 0.09, 0.11), mat_wrap, "Hand.L")

    # Right Arm (A-pose: ~45 deg downward)
    # Shoulder R at (-0.26, 0, 1.42), Elbow at (-0.44, 0, 1.18), Hand at (-0.60, 0, 0.94)
    add_cyl_part("UpperArm_R", (-0.35, 0.0, 1.30), 0.065, 0.28, mat_jacket, "UpperArm.R", rot=(0, -math.pi/4.0, 0))
    add_cyl_part("LowerArm_R", (-0.52, 0.0, 1.06), 0.055, 0.28, mat_skin, "LowerArm.R", rot=(0, -math.pi/4.0, 0))
    add_box_part("Hand_R", (-0.64, 0.0, 0.90), (0.09, 0.09, 0.11), mat_wrap, "Hand.R")

    # Left Leg
    add_cyl_part("UpperLeg_L", (0.13, 0.0, 0.72), 0.08, 0.44, mat_pants, "UpperLeg.L")
    add_cyl_part("LowerLeg_L", (0.13, 0.0, 0.32), 0.07, 0.40, mat_pants, "LowerLeg.L")
    add_box_part("Boot_L", (0.13, 0.04, 0.07), (0.13, 0.22, 0.14), mat_boots, "Foot.L")

    # Right Leg
    add_cyl_part("UpperLeg_R", (-0.13, 0.0, 0.72), 0.08, 0.44, mat_pants, "UpperLeg.R")
    add_cyl_part("LowerLeg_R", (-0.13, 0.0, 0.32), 0.07, 0.40, mat_pants, "LowerLeg.R")
    add_box_part("Boot_R", (-0.13, 0.04, 0.07), (0.13, 0.22, 0.14), mat_boots, "Foot.R")

    # Join all body parts into single Character Mesh
    bpy.ops.object.select_all(action='DESELECT')
    for p in mesh_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = mesh_parts[0]
    bpy.ops.object.join()
    alex_mesh = bpy.context.active_object
    alex_mesh.name = "Alex_Mesh"
    
    for poly in alex_mesh.data.polygons:
        poly.use_smooth = True

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
    make_bone("UpperArm.L", (0.22, 0.0, 1.44), (0.44, 0.0, 1.18), "Chest")
    make_bone("LowerArm.L", (0.44, 0.0, 1.18), (0.60, 0.0, 0.94), "UpperArm.L")
    make_bone("Hand.L", (0.60, 0.0, 0.94), (0.68, 0.0, 0.82), "LowerArm.L")

    # Right Arm
    make_bone("UpperArm.R", (-0.22, 0.0, 1.44), (-0.44, 0.0, 1.18), "Chest")
    make_bone("LowerArm.R", (-0.44, 0.0, 1.18), (-0.60, 0.0, 0.94), "UpperArm.R")
    make_bone("Hand.R", (-0.60, 0.0, 0.94), (-0.68, 0.0, 0.82), "LowerArm.R")
    
    # SOCKET 1: Hand.R active weapon socket
    make_bone("Socket_Hand_R", (-0.64, 0.0, 0.90), (-0.64, 0.0, 1.05), "Hand.R")

    # Left Leg
    make_bone("UpperLeg.L", (0.13, 0.0, 0.95), (0.13, 0.0, 0.50), "Hips")
    make_bone("LowerLeg.L", (0.13, 0.0, 0.50), (0.13, 0.0, 0.12), "UpperLeg.L")
    make_bone("Foot.L", (0.13, 0.0, 0.12), (0.13, 0.14, 0.0), "LowerLeg.L")

    # Right Leg
    make_bone("UpperLeg.R", (-0.13, 0.0, 0.95), (-0.13, 0.0, 0.50), "Hips")
    make_bone("LowerLeg.R", (-0.13, 0.0, 0.50), (-0.13, 0.0, 0.12), "UpperLeg.R")
    make_bone("Foot.R", (-0.13, 0.0, 0.12), (-0.13, 0.14, 0.0), "LowerLeg.R")

    # SOCKET 2: Backpack holster socket
    make_bone("Socket_Backpack", (0.09, 0.24, 1.25), (0.09, 0.24, 1.48), "Chest")

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
