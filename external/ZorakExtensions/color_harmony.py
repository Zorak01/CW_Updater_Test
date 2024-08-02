import bpy
import colorsys
from bpy.types import Operator, PropertyGroup
from bpy.props import FloatVectorProperty, EnumProperty

# Define the harmony modes and their corresponding number of colors
harmony_modes = [
    ('ANALOGOUS', "Analogous", ""),
    ('COMPLEMENTARY', "Complementary", ""),
    ('MONOCHROMATIC', "Monochromatic", ""),
    ('TRIAD', "Triad", ""),
    ('SQUARE', "Square", ""),
    ('SHADE', "Shade", ""),
]

# Function to generate harmonious colors
def generate_harmony_colors(base_color, mode):
    h, s, v = colorsys.rgb_to_hsv(*base_color)
    colors = []
    
    if mode == 'ANALOGOUS':
        for i in [-0.2, -0.1, 0, 0.1, 0.2]:
            colors.append(colorsys.hsv_to_rgb((h + i) % 1.0, s, v))
    elif mode == 'COMPLEMENTARY':
        comp_color = colorsys.hsv_to_rgb((h + 0.5) % 1.0, s, v)
        colors = [
            colorsys.hsv_to_rgb(h, s, v),
            comp_color,
            (comp_color[0] * 0.8, comp_color[1] * 0.8, comp_color[2] * 0.8),
            (comp_color[0] * 1.2, comp_color[1] * 1.2, comp_color[2] * 1.2)
        ]
    elif mode == 'MONOCHROMATIC':
        for i in [0.8, 1.0, 1.2]:
            colors.append(colorsys.hsv_to_rgb(h, s, v * i))
    elif mode == 'TRIAD':
        for i in [0, 1/3, 2/3]:
            colors.append(colorsys.hsv_to_rgb((h + i) % 1.0, s, v))
    elif mode == 'SQUARE':
        for i in [0, 0.25, 0.5, 0.75]:
            colors.append(colorsys.hsv_to_rgb((h + i) % 1.0, s, v))
    elif mode == 'SHADE':
        for i in [0.4, 0.7, 1.0, 1.3, 1.6]:
            colors.append(colorsys.hsv_to_rgb(h, s, v * i))
    
    return colors

# Property group to store the addon properties
class ColorHarmonyProperties(PropertyGroup):
    base_color: FloatVectorProperty(
        name="Base Color",
        subtype='COLOR',
        min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0),
        update=lambda self, context: update_color_previews(context)
    )
    harmony_mode: EnumProperty(
        name="Harmony Mode",
        items=harmony_modes,
        default='SHADE',
        update=lambda self, context: update_color_previews(context)
    )

def update_color_previews(context):
    props = context.scene.color_harmony_props
    colors = generate_harmony_colors(props.base_color, props.harmony_mode)
    num_slots = len(colors)
    
    for i in range(num_slots):
        color_prop = getattr(context.scene, f"color_preview_{i}")
        color_prop[0] = colors[i][0]
        color_prop[1] = colors[i][1]
        color_prop[2] = colors[i][2]

    # Hide unused slots
    for i in range(num_slots, 5):
        color_prop = getattr(context.scene, f"color_preview_{i}")
        color_prop[0] = 0.5
        color_prop[1] = 0.5
        color_prop[2] = 0.5

def create_color_previews():
    for i in range(5):  # Assuming a maximum of 5 color previews
        setattr(bpy.types.Scene, f"color_preview_{i}", FloatVectorProperty(
            name=f"Color Preview {i+1}",
            subtype='COLOR',
            min=0.0, max=1.0,
            default=(0.5, 0.5, 0.5)
        ))

def remove_color_previews():
    for i in range(5):
        delattr(bpy.types.Scene, f"color_preview_{i}")

class COLOR_OT_HarmonyPopover(Operator):
    bl_idname = "color.harmony_popover"
    bl_label = "Color Harmony"
    bl_description = "Display the Color Harmony Popover"

    def execute(self, context):
        return context.window_manager.invoke_popup(self, width=300)

    def draw(self, context):
        layout = self.layout
        props = context.scene.color_harmony_props

        layout.prop(props, "base_color", text="Base Color")
        layout.prop(props, "harmony_mode", text="Harmony Mode")

        num_slots = len(generate_harmony_colors(props.base_color, props.harmony_mode))
        
        # Create a row for color previews
        row = layout.row(align=True)
        for i in range(num_slots):
            row.prop(context.scene, f"color_preview_{i}", text="")
        
        # Add button to add colors to the real color palette
        layout.operator("color.add_harmony_colors", text="Add to Palette", icon='COLOR')

class COLOR_OT_AddHarmonyColors(Operator):
    bl_idname = "color.add_harmony_colors"
    bl_label = "Add Harmony Colors to Palette"
    bl_description = "Add the previewed harmony colors to the real color palette"

    def execute(self, context):
        props = context.scene.color_harmony_props
        colors = generate_harmony_colors(props.base_color, props.harmony_mode)
        palette = context.scene.color_palette

        for color in colors:
            new_color = palette.colors.add()
            new_color.color = (*color, 1.0)
        
        # Force UI update
        context.area.tag_redraw()

        return {'FINISHED'}

def register():
    bpy.utils.register_class(COLOR_OT_HarmonyPopover)
    bpy.utils.register_class(COLOR_OT_AddHarmonyColors)
    bpy.utils.register_class(ColorHarmonyProperties)
    create_color_previews()

def unregister():
    bpy.utils.unregister_class(COLOR_OT_HarmonyPopover)
    bpy.utils.unregister_class(COLOR_OT_AddHarmonyColors)
    bpy.utils.unregister_class(ColorHarmonyProperties)
    remove_color_previews()

if __name__ == "__main__":
    register()
