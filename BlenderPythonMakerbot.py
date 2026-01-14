
import bpy
import json
import numpy as np
################################################################
# helper functions BEGIN
################################################################
"""
See YouTube tutorial for helper functions here: https://youtu.be/Is8Qu7onvzM
"""

def purge_orphans():
    """
    Remove all orphan data blocks

    see this from more info:
    https://youtu.be/3rNqVPtbhzc?t=149
    """
    if bpy.app.version >= (3, 0, 0):
        # run this only for Blender versions 3.0 and higher
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    else:
        # run this only for Blender versions lower than 3.0
        # call purge_orphans() recursively until there are no more orphan data blocks to purge
        result = bpy.ops.outliner.orphans_purge()
        if result.pop() != "CANCELLED":
            purge_orphans()


def clean_scene():
    """
    Removing all of the objects, collection, materials, particles,
    textures, images, curves, meshes, actions, nodes, and worlds from the scene

    Checkout this video explanation with example

    "How to clean the scene with Python in Blender (with examples)"
    https://youtu.be/3rNqVPtbhzc
    """
    # make sure the active object is not in Edit Mode
    if bpy.context.active_object and bpy.context.active_object.mode == "EDIT":
        bpy.ops.object.editmode_toggle()

    # make sure non of the objects are hidden from the viewport, selection, or disabled
    for obj in bpy.data.objects:
        obj.hide_set(False)
        obj.hide_select = False
        obj.hide_viewport = False

    # select all the object and delete them (just like pressing A + X + D in the viewport)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    # find all the collections and remove them
    collection_names = [col.name for col in bpy.data.collections]
    for name in collection_names:
        bpy.data.collections.remove(bpy.data.collections[name])

    # in the case when you modify the world shader
    # delete and recreate the world object
    world_names = [world.name for world in bpy.data.worlds]
    for name in world_names:
        bpy.data.worlds.remove(bpy.data.worlds[name])
    # create a new world data block
    bpy.ops.world.new()
    bpy.context.scene.world = bpy.data.worlds["World"]

    purge_orphans()


def active_object():
    """
    returns the currently active object
    """
    return bpy.context.active_object


################################################################
# helper functions END
################################################################

def add_node(node_tree, name1):
    '''
    add_node(node_tree, name1)
        node_tree: bpy.data.node_groups
        name1: string
    
    Does what it says, 
    adds a node to the provided node tree for an object (e.g. geometry nodes i.e. bpy.data.node_groups["Geometry Nodes"]) with name "name1" (e.g. "GeometryNodeExtrudeMesh")
    '''
    new_node = node_tree.nodes.new(type=name1)
        
    return new_node

def connect_nodes(node_tree, node_out, name_out, node_in, name_in):
    '''
    connect_nodes(node_tree, node_out, name_out, node_in, name_in)
        node_tree:  bpy.data.node_groups
        node_out:   string
        name_out:   string
        node_in:    string or int
        name_in:    string or int
    
    Does what it says, connects two nodes together.
    
    It connects node_out's output "name_out" to node_in's input "name_in".
    name_out and name_in can be either strings (referring to the name of the output/input) or ints (referring to the index from top to bottom of the output/input).
    '''
    node_tree.links.new(node_out.outputs[name_out], node_in.inputs[name_in])


def create_plane():
    '''
    create_plane()
    
    Does not do what it says.
    This is an example for the usage of add_node() and connect_node()
    
    Creates a plane then extrudes that plane using geometry nodes.
    End result should be a cube.
    '''
    bpy.ops.mesh.primitive_plane_add()
    bpy.ops.node.new_geometry_nodes_modifier()
    
    node_tree = bpy.data.node_groups['Geometry Nodes']
    Input = node_tree.nodes['Group Input']
    Output = node_tree.nodes['Group Output']
    
    Extrude_node = add_node(node_tree, "GeometryNodeExtrudeMesh")
    
    connect_nodes(node_tree, Input, "Geometry", Extrude_node, "Mesh")
    connect_nodes(node_tree, Extrude_node, "Mesh", Output, "Geometry")
    
    Extrude_node.inputs[3].default_value = 2.0

def import_ply(location):
    '''
    import_ply(location)
        location: string
    
    Does more than what it says.
    
    Imports a pointcloud object with the given file location. 
    Then uses geometry nodes on it to convert it into connect the dots style representation with hair.
    This is intended for use with pointcloud objects made from 3D print files.
    Note the color on the pointcloud effects the radius of the hair.
    
    returns the new pointcloud object.
    '''
    bpy.ops.wm.ply_import(filepath = location)
    Pointcloud = bpy.context.object
    bpy.ops.node.new_geometry_nodes_modifier()
    pcgn = bpy.data.node_groups['Geometry Nodes'] # "point cloud geometry nodes"
    Input = pcgn.nodes['Group Input']
    Output = pcgn.nodes['Group Output']
    
    MeshToPoints = add_node(pcgn, "GeometryNodeMeshToPoints")
    PointsToCurves = add_node(pcgn, "GeometryNodePointsToCurves")
    ResampleCurve = add_node(pcgn, "GeometryNodeResampleCurve")
    
    Multiply = add_node(pcgn, "ShaderNodeMath")
    LessThan = add_node(pcgn, "ShaderNodeMath")
    Multiply1 = add_node(pcgn, "ShaderNodeVectorMath")
    Multiply2 = add_node(pcgn, "ShaderNodeVectorMath")
    Multiply3 = add_node(pcgn, "ShaderNodeVectorMath")
    Multiply4 = add_node(pcgn, "ShaderNodeVectorMath")
    Add1 = add_node(pcgn, "ShaderNodeVectorMath")
    RandomValue = add_node(pcgn, "FunctionNodeRandomValue")
    
    Position1 = add_node(pcgn, "GeometryNodeInputPosition")
    Position2 = add_node(pcgn, "GeometryNodeInputPosition")
    Position3 = add_node(pcgn, "GeometryNodeInputPosition")
    NamedAttribute = add_node(pcgn, "GeometryNodeInputNamedAttribute")
    
    Multiply.operation = "MULTIPLY"
    LessThan.operation = "LESS_THAN"
    Multiply1.operation = "MULTIPLY"
    Multiply2.operation = "MULTIPLY"
    Multiply3.operation = "MULTIPLY"
    Multiply4.operation = "MULTIPLY"
    RandomValue.data_type = "FLOAT_VECTOR"
    
    NamedAttribute.data_type = "FLOAT_COLOR"
    
    connect_nodes(pcgn, Input, "Geometry", MeshToPoints, "Mesh")
    connect_nodes(pcgn, MeshToPoints, "Points", PointsToCurves, "Points")
    connect_nodes(pcgn, PointsToCurves, "Curves", ResampleCurve, "Curve")
    connect_nodes(pcgn, ResampleCurve, "Curve", Output, "Geometry")
    
    connect_nodes(pcgn, RandomValue, "Value", Multiply1, "Vector")
    connect_nodes(pcgn, Position1, "Position", Add1, 0)
    connect_nodes(pcgn, Multiply1, "Vector", Add1, 1)
    connect_nodes(pcgn, Add1, "Vector", MeshToPoints, "Position")
    
    connect_nodes(pcgn, NamedAttribute, "Attribute", Multiply2, "Vector")
    connect_nodes(pcgn, Multiply2, "Vector", Multiply, 0)
    connect_nodes(pcgn, Position2, "Position", Multiply3, "Vector")
    connect_nodes(pcgn, Multiply3, "Vector", LessThan, "Value")
    connect_nodes(pcgn, LessThan, "Value", Multiply, 1)
    connect_nodes(pcgn, Multiply, "Value", MeshToPoints, "Radius")
    
    connect_nodes(pcgn, Position3, "Position", Multiply4, "Vector")
    connect_nodes(pcgn, Multiply4, "Vector", PointsToCurves, "Curve Group ID")
    
    ResampleCurve.inputs[2].default_value = 10000
    
    RandomValue.inputs[0].default_value = [-1, -1, 0]
    RandomValue.inputs[1].default_value = [1, 1, 0]
    
    NamedAttribute.inputs[0].default_value = "Col"
    Multiply2.inputs[1].default_value = [150, 0, 0]
    
    Multiply3.inputs[1].default_value = [0, 0, 1]
    LessThan.inputs[1].default_value = 300
    
    Multiply4.inputs[1].default_value = [0, 0, 100]
    
    Pointcloud.hide_set(True)

    return Pointcloud

def setup_material(Name, color):
    '''
    setup_material(Name, color)
        Name:   string
        color:  rgba vector
    
    Does what it says.
    
    Creates a new material gives it the specified name and color.
    
    returns the new material.
    '''
    bpy.ops.material.new()
    new_mat = bpy.data.materials[-1]
    new_mat.name = Name
    Mat = bpy.data.materials[new_mat.name]
    Mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
    
    return Mat
    
def create_scene():
    '''
    create_scene()
    
    Does what it says.
    
    Sets up the scene for its intended use case.
    '''
    bpy.ops.object.light_add(type="SUN")
    bpy.ops.transform.rotate(value=0.75, orient_axis='X')
    bpy.ops.transform.rotate(value=1.3, orient_axis='Z')
    bpy.context.object.data.energy = 10

    bpy.ops.mesh.primitive_plane_add()
    bpy.ops.transform.resize(value = (100, 100, 1))
    floormat = setup_material("Floor Material", (0, 0, 0.5, 1))
    
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0.116305, 0.61335, 1, 1)

    
def renderMakerbot(PC):
    '''
    renderMakerbot(PC)
        PC: pointcloud object already imported to blender
        
    Doesn't do what it says.
        
    Turns pointcloud int to hair of object and changes rendering mode so that the hair is visible.
    '''
    bpy.ops.mesh.primitive_plane_add()
    PLANE = bpy.context.object
    bpy.ops.object.curves_empty_hair_add()
    hairSD = bpy.data.node_groups['Surface Deform']
    hairSD_Output = hairSD.nodes["Group Output"]
    ObjectInfo = add_node(hairSD, "GeometryNodeObjectInfo")
    SetMaterial = add_node(hairSD, "GeometryNodeSetMaterial")
    connect_nodes(hairSD, ObjectInfo, "Geometry", SetMaterial, "Geometry")
    connect_nodes(hairSD, SetMaterial, "Geometry", hairSD_Output, "Geometry")
    
    ObjectInfo.inputs[0].default_value = PC
    
    Filmat = setup_material("Filament Material", (0.8, 0, 0, 1))
    SetMaterial.inputs[2].default_value = Filmat
    
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU'
    # bpy.data.screens["Scripting"].areas[5].spaces[0].shading.type = 'RENDERED'

    for area in bpy.data.screens["Layout"].areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].shading.type = 'RENDERED'
            break
    print(" ")
            
    PLANE.hide_set(True)
    
    subprocess.run([f'{sys.executable}', "-m", "pip", "install", "open3d", "--target", "4.3\\python\\lib\\site-packages"], check=True)
    
def import_makerbot(location, file_name = ""):
    '''
    import_makerbot(location, file_name):
        location:   string
        file_name:  string
        
    Does not do what it says.
    
    Takes the location of a makerbot file's parent folder and the name of that file (excluding .makerbot) opens and then converts the toolpath into a pointcloud.
    Will save to a folder named "pointcloud" that lives in the file's parent folder. 
    If this folder does not exist the pointcloud will fail to save.
    
    currently there is a bug where printing some files with "sparse infill" causes visual errors with the render, I have opted to removing infill from these modesls
    
    returns the location of the pointcloud
    '''
    
    import json
    import numpy as np
    import zipfile
    

    files_name = file_name
    name = "TEST"


    with zipfile.ZipFile(f'{location}', 'r') as mbot:
        try:
            code = mbot.read('print.jsontoolpath')
            
        except:
            code = '{"command":{"function":"move","metadata":{"relative":{"a":false,"x":false,"y":false,"z":false}},"parameters":{"a":0.0,"feedrate":0.0,"x":0.0,"y":0.0,"z":0.0},"tags":[]}}'
            print('Fail Makerbot Sketch')
            name = 'FAILED: Makerbot Sketch'

    data = json.loads(code)

    l = len(data)

    points = np.zeros((l, 3))
    colors = np.zeros((l, 3))
    j = 0
    state = 'Makerbot Print'
    no_Support = False
    
    for i in range(l):
        try:
            if data[i]['command']['metadata']['relative']['a']:
                state = 'Cura'
            
            if no_Support:
                if 'Support' in data[i]['command']['tags']:
                    j += 1
                    continue
                
            if state == 'Cura':
                if 'Restart' in data[i]['command']['tags'] or 'Retract' in data[i]['command']['tags']:
                    j += 1
                    continue
                
                try:
                    points[i] = [data[i]['command']['parameters']['x'], data[i]['command']['parameters']['y'], data[i]['command']['parameters']['z']]
                    colors[i, 0] = data[i]['command']['parameters']['a']/np.sqrt((points[i, 0] - points[i-1, 0])**2 + (points[i, 1] - points[i-1, 1])**2)
                except:
                    j += 1
                
            if state == 'Makerbot Print':
                try:
                    points[i] = [data[i]['command']['parameters']['x'], data[i]['command']['parameters']['y'], data[i]['command']['parameters']['z']]
                    colors[i, 0] = (data[i]['command']['parameters']['a'] - data[i-1]['command']['parameters']['a'])/np.sqrt((points[i, 0] - points[i-1, 0])**2 + (points[i, 1] - points[i-1, 1])**2)
                except:
                    j += 1
                
        except:
            j+=1
            

    print(f'Slicer: {state}')
    for val in colors:
        if np.isnan(val[0]):
            val[0] = 0
        if np.isinf(val[0]):
            val[0] = 0


    points /= 1
    
    k = save_pointcloud(points, colors, location, name)

    return f"{location}\\..\\pointclouds\\{name}.ply"

def save_pointcloud(points, colors, location, name):
    l = len(points)

    text = f'''ply
format ascii 1.0
comment Created by GreenAppleIsSpicy
element vertex {l}
property double x
property double y
property double z
property uchar red
property uchar green
property uchar blue
end_header
'''

    ucolors = np.array(255 * colors, dtype=np.uint8)
    ucolors = np.clip(ucolors, 0, 40)

    with open(f"{location}\\..\\pointclouds\\{name}.ply", "w") as text_file:
        text_file.write(text)
        for i in range(l):
            text_file.write(f"{points[i, 0]} {points[i, 1]} {points[i, 2]} {ucolors[i, 0]} {ucolors[i, 1]} {ucolors[i, 2]} \n")
    
    return f"{location}\\..\\pointclouds\\{name}.ply"
    
def main(filepath):
    clean_scene()
    file = import_makerbot(filepath)
    Pointcloud = import_ply(file)
    renderMakerbot(Pointcloud)

    create_scene()

