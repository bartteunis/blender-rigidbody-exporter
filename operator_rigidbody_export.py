bl_info = {
    "name": "Export Box2D Rigid Body",
    "description": "Export the current scene's rigid body world to a json file",
    "author": "Bart Teunis",
    "version": (0, 7, 0),
    "blender": (2, 78, 0),
    "location": "File > Export",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "category": "Import-Export"}

import bpy
import json

def write_scene_physics(context, filepath):
    s = context.scene
    w = s.rigidbody_world
    
    object_list = []
    object_mapping = {}     # Used to store object index in array <-> object name
    constraint_list = []
    world_settings = {}
    result = {"objects": object_list, "constraints": constraint_list}
    
    result["version"] = bl_info["version"]
    
    result["world"] = {
        "gravity": s.gravity[:],
        "time_scale": w.time_scale,
        "steps_per_second": w.steps_per_second,
        "solver_iterations": w.solver_iterations,
    }
    
    # Determine what we need first
    props = {'angular_damping','collision_shape','enabled','friction','kinematic','linear_damping','mass','restitution','type'}
    oprops = {'location','rotation_euler','scale','dimensions','name'}
    
    # Iterate over rigid body objects
    for o in w.group.objects:
        b = o.rigid_body
        
        physics_settings = {x:b.path_resolve(x) for x in props}
        physics_settings['collision_group'] = [i for i, x in enumerate(b.collision_groups) if x == True][0]
        object_settings = {x:o.path_resolve(x)[:] for x in oprops}
        
        # Get reference to object data
        d = o.data
        
        # Select the necessary stuff (single face loop)
        for poly in d.polygons:
            vtx_indices = [d.loops[x].vertex_index for x in poly.loop_indices]
            ordered_verts = [d.vertices[x].co.xy[:] for x in vtx_indices]
            physics_settings['coords'] = ordered_verts
        
        object_list.append({'object': object_settings, 'physics': physics_settings})
        object_mapping[o.name] = len(object_list)-1 # Index in list
    
    # Iterate over Empty's containing constraints
    if w.constraints != None:
        for o in w.constraints.objects:
            c = o.rigid_body_constraint
            if c!= None:
                constraint_settings = {
                    "location": o.location[:],
                    "object1": object_mapping[c.object1.name],
                    "object2": object_mapping[c.object2.name],
                    "type": c.type,
                    "disable_collisions": c.disable_collisions,
                    "enabled": c.enabled
                    }
                constraint_list.append(constraint_settings)
    
    f_collision = open(filepath,'w')
    json.dump(result,f_collision)
    f_collision.close()
    
    return {'FINISHED'}

# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ExportRigidBody(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export Rigid Body"

    # ExportHelper mixin class uses this
    filename_ext = ".phy"

    filter_glob = StringProperty(
            default="*.phy",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    #type = EnumProperty(
    #        name="Example Enum",
    #        description="Choose between two items",
    #        items=(('OPT_A', "First Option", "Description one"),
    #               ('OPT_B', "Second Option", "Description two")),
    #        default='OPT_A',
    #        )

    def execute(self, context):
        return write_scene_physics(context, self.filepath)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportRigidBody.bl_idname, text="Rigid Body (.phy)")


def register():
    bpy.utils.register_class(ExportRigidBody)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportRigidBody)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.export_test.some_data('INVOKE_DEFAULT')