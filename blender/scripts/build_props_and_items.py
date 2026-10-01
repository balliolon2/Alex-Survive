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
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat)

def create_material(name, base_color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = base_color
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
    return mat

def export_asset(blend_path, glb_path):
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
    print(f"Exported: {glb_path}")

def build_wood_plank(base_dir):
    clear_scene()
    mat_wood = create_material("Mat_Weathered_Pine", (0.52, 0.38, 0.26, 1.0), roughness=0.8)
    mat_nail = create_material("Mat_Nail_Head", (0.2, 0.2, 0.22, 1.0), roughness=0.5, metallic=0.9)
    
    # Plank: 1.20m length (X), 0.18m width (Y), 0.035m thickness (Z)
    # Origin at rear mounting face center (0, 0, 0)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0.0, 0.0, 0.0175)
    )
    plank = bpy.context.active_object
    plank.name = "WoodPlank"
    plank.scale = (1.20, 0.18, 0.035)
    bpy.ops.object.transform_apply(scale=True)
    plank.data.materials.append(mat_wood)
    
    # 2 Nail heads
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.009, depth=0.04, location=(-0.52, 0.0, 0.02)
    )
    nail1 = bpy.context.active_object
    nail1.data.materials.append(mat_nail)
    
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.009, depth=0.04, location=(0.52, 0.0, 0.02)
    )
    nail2 = bpy.context.active_object
    nail2.data.materials.append(mat_nail)
    
    bpy.ops.object.select_all(action='DESELECT')
    plank.select_set(True)
    nail1.select_set(True)
    nail2.select_set(True)
    bpy.context.view_layer.objects.active = plank
    bpy.ops.object.join()
    
    for p in plank.data.polygons:
        p.use_smooth = True
        
    export_asset(
        f"{base_dir}/blender/environment/wood_plank.blend",
        f"{base_dir}/alex-survive-godot/assets/models/environment/wood_plank.glb"
    )

def build_workbench(base_dir):
    clear_scene()
    mat_wood = create_material("Mat_Bench_Wood", (0.45, 0.32, 0.22, 1.0), roughness=0.7)
    mat_iron = create_material("Mat_Bench_Iron", (0.22, 0.24, 0.26, 1.0), roughness=0.5, metallic=0.85)
    mat_vise = create_material("Mat_Vise_Steel", (0.18, 0.26, 0.32, 1.0), roughness=0.4, metallic=0.9)
    
    # Table top: 1.6m (X) x 0.8m (Y) x 0.08m (Z), top surface at Z = 0.90m
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0.0, 0.0, 0.86)
    )
    top = bpy.context.active_object
    top.name = "Workbench"
    top.scale = (1.60, 0.80, 0.08)
    bpy.ops.object.transform_apply(scale=True)
    top.data.materials.append(mat_wood)
    
    # 4 Legs (Iron): 0.06m x 0.06m, height 0.82m
    leg_coords = [
        (-0.74, -0.34), (0.74, -0.34),
        (-0.74, 0.34),  (0.74, 0.34)
    ]
    sub_objs = []
    for lx, ly in leg_coords:
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, location=(lx, ly, 0.41)
        )
        leg = bpy.context.active_object
        leg.scale = (0.07, 0.07, 0.82)
        bpy.ops.object.transform_apply(scale=True)
        leg.data.materials.append(mat_iron)
        sub_objs.append(leg)
        
    # Lower Shelf: Z = 0.22m
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0.0, 0.0, 0.22)
    )
    shelf = bpy.context.active_object
    shelf.scale = (1.48, 0.68, 0.04)
    bpy.ops.object.transform_apply(scale=True)
    shelf.data.materials.append(mat_wood)
    sub_objs.append(shelf)
    
    # Pegboard backboard: Width 1.60m, height from Z = 0.90 to 1.70 (center Z = 1.30), Y = 0.38
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0.0, 0.38, 1.30)
    )
    pegboard = bpy.context.active_object
    pegboard.scale = (1.60, 0.04, 0.80)
    bpy.ops.object.transform_apply(scale=True)
    pegboard.data.materials.append(mat_wood)
    sub_objs.append(pegboard)
    
    # Vise Clamp at front-left: X = -0.62, Y = -0.36, Z = 0.95
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(-0.62, -0.36, 0.96)
    )
    vise_base = bpy.context.active_object
    vise_base.scale = (0.16, 0.20, 0.12)
    bpy.ops.object.transform_apply(scale=True)
    vise_base.data.materials.append(mat_vise)
    sub_objs.append(vise_base)
    
    # Vise handle rod
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.012, depth=0.22,
        location=(-0.62, -0.47, 0.96),
        rotation=(0.0, math.pi / 2.0, 0.0)
    )
    rod = bpy.context.active_object
    rod.data.materials.append(mat_iron)
    sub_objs.append(rod)
    
    # Join everything into Workbench
    bpy.ops.object.select_all(action='DESELECT')
    top.select_set(True)
    for obj in sub_objs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = top
    bpy.ops.object.join()
    
    for p in top.data.polygons:
        p.use_smooth = True
        
    export_asset(
        f"{base_dir}/blender/environment/workbench.blend",
        f"{base_dir}/alex-survive-godot/assets/models/environment/workbench.glb"
    )

def build_canned_food(base_dir):
    clear_scene()
    mat_tin = create_material("Mat_Tin_Can", (0.75, 0.77, 0.80, 1.0), roughness=0.35, metallic=0.85)
    mat_label = create_material("Mat_Can_Label", (0.82, 0.28, 0.22, 1.0), roughness=0.75, metallic=0.0)
    
    # Can: height 0.11m, radius 0.042m. Origin at bottom center (Z = 0)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.042, depth=0.11, location=(0.0, 0.0, 0.055)
    )
    can = bpy.context.active_object
    can.name = "CannedFood"
    can.data.materials.append(mat_tin)
    
    # Label band around middle
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.0426, depth=0.075, location=(0.0, 0.0, 0.055)
    )
    label = bpy.context.active_object
    label.data.materials.append(mat_label)
    
    # Top pull-tab ring
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.012, depth=0.006, location=(0.015, 0.0, 0.113)
    )
    tab = bpy.context.active_object
    tab.data.materials.append(mat_tin)
    
    bpy.ops.object.select_all(action='DESELECT')
    can.select_set(True)
    label.select_set(True)
    tab.select_set(True)
    bpy.context.view_layer.objects.active = can
    bpy.ops.object.join()
    
    for p in can.data.polygons:
        p.use_smooth = True
        
    export_asset(
        f"{base_dir}/blender/items/canned_food.blend",
        f"{base_dir}/alex-survive-godot/assets/models/items/canned_food.glb"
    )

def build_scrap_metal(base_dir):
    clear_scene()
    mat_iron = create_material("Mat_Scrap_Iron", (0.35, 0.33, 0.32, 1.0), roughness=0.6, metallic=0.85)
    
    # Irregular jagged metal plate (L-bracket / machinery fragment)
    # Origin at bottom center
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0.0, 0.0, 0.018)
    )
    plate = bpy.context.active_object
    plate.name = "ScrapMetal"
    plate.scale = (0.20, 0.14, 0.036)
    bpy.ops.object.transform_apply(scale=True)
    plate.data.materials.append(mat_iron)
    
    # Upright flange
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0.08, 0.0, 0.07)
    )
    flange = bpy.context.active_object
    flange.scale = (0.04, 0.14, 0.08)
    bpy.ops.object.transform_apply(scale=True)
    flange.data.materials.append(mat_iron)
    
    # Bolt hole cylinder (decorative cutout)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.02, depth=0.05, location=(-0.05, 0.0, 0.02)
    )
    cutout = bpy.context.active_object
    cutout.data.materials.append(mat_iron)
    
    bpy.ops.object.select_all(action='DESELECT')
    plate.select_set(True)
    flange.select_set(True)
    cutout.select_set(True)
    bpy.context.view_layer.objects.active = plate
    bpy.ops.object.join()
    
    for p in plate.data.polygons:
        p.use_smooth = True
        
    export_asset(
        f"{base_dir}/blender/items/scrap_metal.blend",
        f"{base_dir}/alex-survive-godot/assets/models/items/scrap_metal.glb"
    )

def build_duct_tape(base_dir):
    clear_scene()
    mat_tape = create_material("Mat_Silver_Tape", (0.65, 0.68, 0.72, 1.0), roughness=0.45, metallic=0.25)
    mat_core = create_material("Mat_Cardboard_Core", (0.50, 0.38, 0.28, 1.0), roughness=0.9, metallic=0.0)
    
    # Outer tape roll: radius 0.06m, thickness 0.05m. Origin at bottom center
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.06, depth=0.05, location=(0.0, 0.0, 0.025)
    )
    tape = bpy.context.active_object
    tape.name = "DuctTape"
    tape.data.materials.append(mat_tape)
    
    # Inner cardboard core
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.038, depth=0.051, location=(0.0, 0.0, 0.025)
    )
    core = bpy.context.active_object
    core.data.materials.append(mat_core)
    
    # Small loose tape end tab
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0.065, 0.015, 0.025), rotation=(0.0, 0.0, 0.35)
    )
    tab = bpy.context.active_object
    tab.scale = (0.018, 0.035, 0.048)
    bpy.ops.object.transform_apply(scale=True)
    tab.data.materials.append(mat_tape)
    
    bpy.ops.object.select_all(action='DESELECT')
    tape.select_set(True)
    core.select_set(True)
    tab.select_set(True)
    bpy.context.view_layer.objects.active = tape
    bpy.ops.object.join()
    
    for p in tape.data.polygons:
        p.use_smooth = True
        
    export_asset(
        f"{base_dir}/blender/items/duct_tape.blend",
        f"{base_dir}/alex-survive-godot/assets/models/items/duct_tape.glb"
    )

if __name__ == "__main__":
    base_dir = "C:/Users/bond/Documents/Alex-Survive"
    build_wood_plank(base_dir)
    build_workbench(base_dir)
    build_canned_food(base_dir)
    build_scrap_metal(base_dir)
    build_duct_tape(base_dir)
