# Blender Rigidbody Exporter
This plugin exports the rigidbody world from a Blender project.
It exports to a json-based format that closely resembles the structure of the bpy API.

## Collision shapes
### Mesh
The mesh is the most flexible collision shape and allows several face loops.

### Convex Hull


### Cone, Cylinder, Capsule, Sphere
These all map to a circle shape in 2D.

### Box
Corresponds to a rectangle/box shape in 2D.

### More complex shapes
Some models have a very complex shape.
The requirement for a polygon shape is that it should be convex.
For a more complex concave shape this can be solved by using "Mesh > Clean up > Split Concave Faces"
