bl_info = {
    "name": "Export Box2D Rigid Body",
    "description": "Export the current scene's rigid body world to a json file",
    "author": "Bart Teunis",
    "version": (0, 7, 2),
    "blender": (2, 80, 0),
    "location": "File > Export",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "https://github.com/bartteunis/blender-rigidbody-exporter/wiki",
    "category": "Import-Export"}

import bpy
import json

def write_scene_physics(context, exporter, filepath, selection_only):
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
    if selection_only:
        items = [obj for obj in w.collection.objects if obj in bpy.context.selected_objects]
    else:
        items = w.collection.objects
    
    for obj in items:
        body = obj.rigid_body
        
        physics_settings = {x:body.path_resolve(x) for x in props}
        physics_settings['collision_group'] = [i for i, x in enumerate(body.collision_collections) if x == True][0]
        object_settings = {x:obj.path_resolve(x)[:] for x in oprops}
        
        # Get reference to object data
        d = obj.data
        
        # Select the necessary stuff (multiple face loops)
        physics_settings['coords'] = []
        if body.collision_shape == 'MESH' or body.collision_shape == 'CONVEX_HULL':
            for poly in d.polygons:
                l = len(poly.loop_indices)
                if (l < 3 or l > 8):
                    exporter.report({'WARNING'}, "Object: " + obj.name + " - Convex polygon shape's vertex count is less than 3 or more than 8")
                
                vtx_indices = [d.loops[x].vertex_index for x in poly.loop_indices]
                ordered_verts = [getattr(d.vertices[x].co,exporter.coordinates)[:] for x in vtx_indices]
                physics_settings['coords'].append(ordered_verts)
        
        object_list.append({'object': object_settings, 'physics': physics_settings})
        object_mapping[obj.name] = len(object_list)-1 # Index in list
    
    # Iterate over Empty's containing constraints
    if w.constraints != None:
        for obj in w.constraints.objects:
            c = obj.rigid_body_constraint
            if c!= None:
                constraint_settings = {
                    "location": obj.location[:],
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
    """Export rigid body world for use with Box2D"""
    bl_idname = "export_rigidbody.box2d"  # important since its how bpy.ops.import_test.box2d is constructed
    bl_label = "Export Rigid Body"

    # ExportHelper mixin class uses this
    filename_ext = ".phy"

    filter_glob : StringProperty(
        default="*.phy",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )
    
    selection_only : BoolProperty(
        name="Selection Only",
        description="Export selected only",
    )
    
    coordinates : EnumProperty(
        name="Coordinate",
        description="Which values to export",
        items=(
            ('xy', 'XY', ""),
            ('xz', 'XZ', ""),
            ('yz', 'YZ', ""),
        )
    )

    def execute(self, context):
        return write_scene_physics(context, self, self.filepath, self.selection_only)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportRigidBody.bl_idname, text="Rigid Body (.phy)")


def register():
    bpy.utils.register_class(ExportRigidBody)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportRigidBody)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.export_rigidbody.box2d('INVOKE_DEFAULT')