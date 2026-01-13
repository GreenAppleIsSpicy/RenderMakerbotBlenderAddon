import bpy 
from bpy.props import StringProperty
import os 
import BlenderPythonMakerbot as Makerbot


class MainPanel(bpy.types.Panel):
    bl_idname = "Test"
    bl_label = "Test File"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'View'
 
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, 'file_')

        
        row = layout.row()
#        row.label(text= "TEXT:")
        row.operator(silly_OT_operator.bl_idname, text="Load")
        
class silly_OT_operator(bpy.types.Operator):
    bl_label = "sillyop"
    bl_idname = "silly.op"
    
    
    def execute(self, context):
        filename = os.path.normpath(bpy.path.abspath(bpy.context.scene.file_))
        
        Makerbot.main(filename)
        
        return {"FINISHED"}
        

            
def showPath(self, context):
    filepath = bpy.context.scene.file_
    print("filepath: ", bpy.context.scene.file_)# return only //x_bot.json 
    filename = os.path.normpath(bpy.path.abspath(bpy.context.scene.file_))
    Makerbot.main(filename)
    
def register():
    bpy.utils.register_class(MainPanel)
    bpy.types.Scene.file_ = bpy.props.StringProperty(
        name= "File", 
        subtype='FILE_PATH', 
        update=showPath
    )
    bpy.utils.register_class(silly_OT_operator)

def unregister():
    bpy.utils.unregister_class(MainPanel)

    
if __name__ == "__main__":
    register()
#    filename = os.path.normpath(bpy.path.abspath(bpy.context.scene.file_))
#    print(filename)
    
    
#    Makerbot.main(filename)
    

