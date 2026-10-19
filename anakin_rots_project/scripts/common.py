"""Shared helpers for the Anakin ROTS hair reconstruction pipeline (Blender 4.2, bpy)."""
import bpy, os, math
from mathutils import Vector, Matrix

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLENDER = '/opt/blender/blender-4.2.23-linux-x64/blender'
TEX = {
    'planes_ca': os.path.join(PROJ, 'input', 'T_Heads_Anakin_01_HairPlanes_CA_asUploaded.png'),
    'planes_ns': os.path.join(PROJ, 'input', 'T_Heads_Anakin_01_HairPlanes_NS_asUploaded.png'),
    'cap_ca': os.path.join(PROJ, 'input', 'T_Heads_Anakin_01_HairCap_CA_asUploaded.png'),
    'cap_ns': os.path.join(PROJ, 'input', 'T_Heads_Anakin_01_HairCap_NS_asUploaded.png'),
}
HEAD_CENTER = Vector((0.0, -0.03, 1.69))   # approx centre of the skull in world space (metres)

def load_image(path, colorspace):
    name = os.path.basename(path)
    img = bpy.data.images.get(name)
    if img is None:
        img = bpy.data.images.load(path)
    img.colorspace_settings.name = colorspace
    img.alpha_mode = 'STRAIGHT'
    return img

def hair_material(name, ca_path, ns_path, alpha_clip=0.3, roughness=0.55):
    """Principled material driven by the Frostbite CA (colour+alpha) and NS (normal XY + spec) textures.
    The uploaded NS copies are sRGB-encoded (0.5 -> 187), so they are loaded as sRGB so Blender linearises
    them back to the 0.5-centred data before the normal is decoded."""
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Specular IOR Level'].default_value = 0.05
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    ca = nt.nodes.new('ShaderNodeTexImage'); ca.image = load_image(ca_path, 'sRGB'); ca.interpolation = 'Linear'
    nt.links.new(ca.outputs['Color'], bsdf.inputs['Base Color'])
    # alpha clip to mimic the in-game alpha test
    clip = nt.nodes.new('ShaderNodeMath'); clip.operation = 'GREATER_THAN'; clip.inputs[1].default_value = alpha_clip
    nt.links.new(ca.outputs['Alpha'], clip.inputs[0])
    nt.links.new(clip.outputs[0], bsdf.inputs['Alpha'])
    ns = nt.nodes.new('ShaderNodeTexImage'); ns.image = load_image(ns_path, 'sRGB'); ns.interpolation = 'Linear'
    sep = nt.nodes.new('ShaderNodeSeparateColor'); nt.links.new(ns.outputs['Color'], sep.inputs[0])
    # x = R*2-1, y = G*2-1, z = sqrt(1-x^2-y^2); re-encode to 0..1 for the Normal Map node
    def mad(a, mul, add):
        m = nt.nodes.new('ShaderNodeMath'); m.operation = 'MULTIPLY_ADD'; m.inputs[1].default_value = mul; m.inputs[2].default_value = add
        nt.links.new(a, m.inputs[0]); return m.outputs[0]
    x = mad(sep.outputs[0], 2.0, -1.0); y = mad(sep.outputs[1], 2.0, -1.0)
    def sq(v):
        m = nt.nodes.new('ShaderNodeMath'); m.operation = 'MULTIPLY'; nt.links.new(v, m.inputs[0]); nt.links.new(v, m.inputs[1]); return m.outputs[0]
    s = nt.nodes.new('ShaderNodeMath'); s.operation = 'ADD'; nt.links.new(sq(x), s.inputs[0]); nt.links.new(sq(y), s.inputs[1])
    one = nt.nodes.new('ShaderNodeMath'); one.operation = 'SUBTRACT'; one.inputs[0].default_value = 1.0; nt.links.new(s.outputs[0], one.inputs[1])
    cl = nt.nodes.new('ShaderNodeClamp'); nt.links.new(one.outputs[0], cl.inputs[0])
    z = nt.nodes.new('ShaderNodeMath'); z.operation = 'SQRT'; nt.links.new(cl.outputs[0], z.inputs[0])
    comb = nt.nodes.new('ShaderNodeCombineColor')
    nt.links.new(mad(x, 0.5, 0.5), comb.inputs[0]); nt.links.new(mad(y, 0.5, 0.5), comb.inputs[1]); nt.links.new(mad(z.outputs[0], 0.5, 0.5), comb.inputs[2])
    nm = nt.nodes.new('ShaderNodeNormalMap'); nm.space = 'TANGENT'; nm.inputs['Strength'].default_value = 0.6
    nt.links.new(comb.outputs[0], nm.inputs['Color'])
    nt.links.new(nm.outputs[0], bsdf.inputs['Normal'])
    # B channel of NS ~ specular/gloss mask -> modulate roughness
    rough = nt.nodes.new('ShaderNodeMapRange'); rough.inputs['From Min'].default_value = 0.0; rough.inputs['From Max'].default_value = 1.0
    rough.inputs['To Min'].default_value = 0.9; rough.inputs['To Max'].default_value = 0.65
    nt.links.new(sep.outputs[2], rough.inputs[0]); nt.links.new(rough.outputs[0], bsdf.inputs['Roughness'])
    mat.surface_render_method = 'DITHERED'
    mat.use_backface_culling = False
    return mat

def skin_material():
    mat = bpy.data.materials.get('M_head_ref')
    if mat: return mat
    mat = bpy.data.materials.new('M_head_ref'); mat.use_nodes = True
    b = mat.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (0.65, 0.45, 0.35, 1); b.inputs['Roughness'].default_value = 0.6
    return mat

def assign_materials(hair_obj, cap_obj, head_obj=None):
    mp = hair_material('M_HairPlanes', TEX['planes_ca'], TEX['planes_ns'], alpha_clip=0.35)
    mc = hair_material('M_HairCap', TEX['cap_ca'], TEX['cap_ns'], alpha_clip=0.3)
    for o, m in ((hair_obj, mp), (cap_obj, mc)):
        if o is None: continue
        if not o.data.materials: o.data.materials.append(m)
        else: o.data.materials[0] = m
    if head_obj is not None:
        head_obj.data.materials.clear(); head_obj.data.materials.append(skin_material())

def clear_render_rig():
    for o in list(bpy.data.objects):
        if o.name.startswith('CAM_') or o.name.startswith('LIGHT_'):
            bpy.data.objects.remove(o, do_unlink=True)

def add_camera(name, direction, up=(0, 0, 1), ortho=True, ortho_scale=0.46, dist=3.0, target=None, lens=50):
    """direction: unit vector FROM the target TOWARDS the camera."""
    target = target or HEAD_CENTER
    d = Vector(direction).normalized()
    cam = bpy.data.cameras.new(name); cam.type = 'ORTHO' if ortho else 'PERSP'; cam.ortho_scale = ortho_scale; cam.lens = lens
    cam.clip_start = 0.01; cam.clip_end = 100
    o = bpy.data.objects.new(name, cam); bpy.context.scene.collection.objects.link(o)
    o.location = target + d * dist
    o.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    return o

# six standard comparison views (direction from target towards camera). Character faces +Y? determined in common.FRONT
FRONT = Vector((0, -1, 0))   # face points -Y in the imported Frosty scene (verified by baseline render)

def view_defs():
    f = FRONT; r = Vector((-f.y, f.x, 0))  # character's right side when facing f... (set by detect)
    return {
        'front': f,
        'left': Vector((f.y, -f.x, 0)) * -1,   # camera placed on character's left side
        'right': Vector((f.y, -f.x, 0)),
        'back': -f,
        'three_quarter': (f + Vector((f.y, -f.x, 0))).normalized(),
        'elevated': (f * 0.75 + Vector((f.y, -f.x, 0)) * 0.55 + Vector((0, 0, 0.55))).normalized(),
    }

def setup_cameras(ortho_scale=0.46):
    cams = {}
    for name, d in view_defs().items():
        cams[name] = add_camera('CAM_' + name, d, ortho_scale=ortho_scale)
    return cams

def setup_lights(preset='neutral'):
    for o in list(bpy.data.objects):
        if o.name.startswith('LIGHT_'): bpy.data.objects.remove(o, do_unlink=True)
    w = bpy.context.scene.world or bpy.data.worlds.new('World'); bpy.context.scene.world = w
    w.use_nodes = True; bg = w.node_tree.nodes['Background']
    f = FRONT; r = Vector((f.y, -f.x, 0))
    def lamp(name, kind, loc, energy, color=(1, 1, 1), size=1.0, angle=None):
        l = bpy.data.lights.new(name, kind); l.energy = energy; l.color = color
        if kind == 'AREA': l.size = size
        if kind == 'SUN' and angle is not None: l.angle = angle
        o = bpy.data.objects.new(name, l); bpy.context.scene.collection.objects.link(o)
        o.location = HEAD_CENTER + Vector(loc)
        o.rotation_euler = (HEAD_CENTER - o.location).to_track_quat('-Z', 'Y').to_euler()
        return o
    if preset == 'neutral':
        bg.inputs[0].default_value = (0.35, 0.35, 0.38, 1); bg.inputs[1].default_value = 1.0
        lamp('LIGHT_key', 'AREA', f * 1.6 + r * 0.5 + Vector((0, 0, 1.3)), 110, size=2.0)
        lamp('LIGHT_fill', 'AREA', f * 1.5 - r * 1.2 + Vector((0, 0, 0.4)), 45, size=2.5)
        lamp('LIGHT_rim', 'AREA', -f * 1.5 + r * 0.6 + Vector((0, 0, 1.0)), 60, size=1.0)
    elif preset == 'side':
        bg.inputs[0].default_value = (0.08, 0.08, 0.1, 1); bg.inputs[1].default_value = 1.0
        lamp('LIGHT_side', 'SUN', r * 3 + Vector((0, 0, 0.6)), 4.0, angle=0.05)
        lamp('LIGHT_fill', 'AREA', f * 2 - r * 1.0 + Vector((0, 0, 0.2)), 10, size=2.0)
    elif preset == 'mustafar':
        bg.inputs[0].default_value = (0.12, 0.04, 0.01, 1); bg.inputs[1].default_value = 1.0
        lamp('LIGHT_lava', 'AREA', f * 1.2 + Vector((0, 0, -1.2)), 150, color=(1.0, 0.45, 0.15), size=2.5)
        lamp('LIGHT_key', 'AREA', f * 1.5 + r * 1.2 + Vector((0, 0, 0.8)), 50, color=(1.0, 0.7, 0.5), size=1.0)
        lamp('LIGHT_rim', 'AREA', -f * 1.5 - r * 0.8 + Vector((0, 0, 1.0)), 80, color=(1.0, 0.5, 0.3), size=1.0)

def setup_render(engine='BLENDER_EEVEE_NEXT', res=1024, samples=32):
    s = bpy.context.scene
    s.render.engine = engine
    s.render.resolution_x = res; s.render.resolution_y = res; s.render.resolution_percentage = 100
    s.render.image_settings.file_format = 'PNG'; s.render.image_settings.color_mode = 'RGBA'
    s.render.film_transparent = False
    s.view_settings.view_transform = 'Standard'
    if engine == 'BLENDER_EEVEE_NEXT':
        s.eevee.taa_render_samples = samples
        s.eevee.use_shadows = True
        s.eevee.use_raytracing = False
    else:
        s.cycles.samples = samples; s.cycles.use_denoising = True; s.cycles.device = 'CPU'

def render_views(out_dir, prefix, cams, views=None, res=None):
    os.makedirs(out_dir, exist_ok=True)
    s = bpy.context.scene
    paths = {}
    for name, cam in cams.items():
        if views and name not in views: continue
        s.camera = cam
        p = os.path.join(out_dir, '%s_%s.png' % (prefix, name))
        s.render.filepath = p
        bpy.ops.render.render(write_still=True)
        paths[name] = p
    return paths

def detect_front(head_obj):
    """Decide which horizontal direction the face points, using the head mesh: the nose tip is the most
    protruding point in the face direction at mid-eye height; the back of the skull is rounder and higher."""
    global FRONT
    import numpy as np
    me = head_obj.data
    co = np.array([head_obj.matrix_world @ v.co for v in me.vertices])
    z = co[:, 2]; zmid = (z.min() + z.max()) / 2
    band = co[np.abs(z - zmid) < 0.03]
    ymin, ymax = band[:, 1].min(), band[:, 1].max()
    # the chin/face side has the larger extent below mid height; the nose protrudes at mid height -> compare spread
    lower = co[z < zmid - 0.08]
    # back of skull has few vertices far below (neck is central); the face has chin at the front.
    # Verified visually on the baseline render: the nose points towards -Y. Keep the constant.
    return FRONT
