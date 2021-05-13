#  De export en import rotine en de routine voor het platleggen van een vlak in een.
#Eerst een vlak kiezen in edit mode, dat wordt dan platgelegd. Dat vlak kan geexpoteerd worden met de DXF exportknop
# Er wordt een hulpvlak gemaakt waarvan de wereldmatrix kan gebruikt worden om het vlak wat later terugkomt
# van de bewerking weer in de goede richting te draaien
# Het wordt geexporteerd in blender eenheder, dus 1m is een. Als het gezien moet worden als mm schaal op 1000 zetten.
# Het bewerkte object kan weer geimporteerd worden. Het wordt meteen in de goed hoek gedraaid en op de juiste plek gezet, ook nog van curve naar mesh
bl_info = {
    "name": "DXF import export",
    "author": "Tiemen Blankert",
    "version": (1, 1),
    "blender": (2, 91, 2),
    "location": "View3D ",
    "description": "Import/export drawings on a plane",
    "warning": "",
    "doc_url": "",
    "category": "drawing",
}







import bpy
import mathutils
import bmesh
from mathutils import Vector,Matrix


# Het bedieningspaneel
 
class VIEW_PT_dxf_export(bpy.types.Panel):
    bl_category = "Edit"
    bl_label = "DXF export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    #bl_context = "objectmode"
    bl_options = {'DEFAULT_CLOSED'}
    #bl_context = "mesh_edit"    
    

    def draw(self,context):
        layout = self.layout
        col = layout.column(align=True)
        col.prop(context.scene,'dxf_export')# hier staat het file path(propperty)
        col = layout.column()
        col.prop(context.scene,'scale_factor_2')# hier de schaal factor
        column = layout.column()
        col.prop(context.scene,'resolutie')# hier de resolutie van de kromme
        #col.operator('mesh.vlak_plat',
        #            text = 'Vlak plat',
        #            )
        col.operator('export_scene.export_dxf_file')# het uitvoeren van de export

        col.operator('import_scene.import_dxf_file')
        layout = self.layout
        layout.operator('mesh.3d_mesh',
                           text = 'to 3D mesh',
                            )
                       
                        


           
# De export routine voor de DXF

class EXP_dxf_file(bpy.types.Operator):
    ''' Het object wordt geexporteerd naar de file in de box, 
    Na export kan verder gewerkt worden in Qcad'''
    bl_idname = 'export_scene.export_dxf_file'
    bl_label = 'DXF export'
    
    def execute(self,context):
        print('\n \n ***************Dit is het eerste*******************\n\n')
        bpy.ops.mesh.vlak_plat()
        path = bpy.path.abspath(context.scene.dxf_export) # path halen uit de propperty
        #path = str(context.scene.dxf_export)
        
        obj = bpy.context.object
        export_vlak = obj
        bpy.ops.object.duplicate() # nieuw ofject om te verschalen
        obj = bpy.context.object
        # alles wordt geexporteerd in blender schalen, daarom keer 100 om in centimeters te krijven
        schaal = context.scene.scale_factor_2
        mat_sca_x = mathutils.Matrix.Scale(schaal, 4,(1,0,0))
        mat_sca_y = mathutils.Matrix.Scale(schaal, 4,(0,1,0))
        
        
        obj.matrix_world = obj.matrix_world @ mat_sca_x @ mat_sca_y
        #hieronder een poging het object helemaal plat te leggen (z=0) dat lukt wel
        #maar in qcad moet toch nog steeds flatten gebruit worden, ik snap het niet
        # vervolge weken later: Het lijkt er op dat het vlak in het x,y vlak moet liggen voor het wordt
        # geexporteerd, dan hoef je geen flatten te doen in qcad.
        #print(obj.matrix_world)
        bpy.ops.object.editmode_toggle()
        obj =  bpy.context.object
        bpy.context.object.location[2]=0
        
        me = obj.data
        bm  = bmesh.from_edit_mesh(me)
        for vert in bm.verts:
            print(vert.co)
            vert.co[2]=0
        
        bpy.ops.object.editmode_toggle() 
        
        
        
        
        #obj.matrix_world = obj.matrix_world @ mat_sca_z         
        
        #  exporteren
        bpy.ops.export.dxf(filepath=path,
                    projectionThrough='NO', 
                    onlySelected=True, apply_modifiers=True,
                     mesh_as='LINEs',
                     entitylayer_from='obj.data.name',
                      entitycolor_from='default_COLOR',
                       entityltype_from='CONTINUOUS',
                        layerName_from='LAYERNAME_DEF',
                         verbose=False)                            
                                 

        # het gedupliceerde object weghalen eventueel uitzetten om de geexporteerde form te zien      
        bpy.ops.object.delete(use_global=False)
        bpy.data.objects.remove(export_vlak)
        return {'FINISHED'} 
    
    
# Het plat leggen van het vlak
    
class MESH_OT_vlak_plat(bpy.types.Operator):
    """ Leg een vlak plat voor DXF export"""
    bl_idname = "mesh.vlak_plat"
    bl_label = "vlak platleggen"
    bl_options = {'REGISTER', 'UNDO'} 
    
    def execute(self,context):
        # referentie vectoren
        v1 = Vector((0,0,1))
        v2 = Vector((0,1,0))
        # maak nieuw object van geselecteerde vlak
        obj =  bpy.context.object
        bpy.ops.mesh.duplicate()
        bpy.ops.mesh.separate(type='SELECTED')
        bpy.ops.object.editmode_toggle()


        # maak het nieuwe vlakobject het actieve object
        bpy.context.active_object.select_set(False)
        for ob in bpy.context.selected_objects:
            bpy.context.view_layer.objects.active = ob
        # apply de rotatie
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        obj = bpy.context.object
        # uitzoeken wat het kleinse punt in het vlak is
        punten = []
        for punt in obj.data.vertices:
            punt_abs = punt.co +obj.location
            punt_abs = punt_abs.to_tuple()
            punten.append(punt_abs)
        punten.sort()
        laagste = Vector((punten[0]))
        print('laagste=',laagste)
            

            

        centrum = bpy.context.object.location
        
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

        # het vlak horizontaal draaien
        bpy.ops.object.editmode_toggle()
        obj =  bpy.context.object
        me = obj.data
        bm  = bmesh.from_edit_mesh(me)
        bm.faces.ensure_lookup_table()
        normaal = bm.faces[0].normal
        bpy.context.scene['normaal_vlak'] = normaal# Het maken van een variabele die buiten het programma blijft bestaan
        verschil = normaal.rotation_difference(v1)
        print(verschil)
        matrix_rot_1 = verschil.to_matrix().to_4x4()
        obj.matrix_world = obj.matrix_world @ matrix_rot_1

        # apply rotatie
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        bpy.ops.object.editmode_toggle()

        # het vlak recht draaien in het horizontale vlak

        me = obj.data
        bm  = bmesh.from_edit_mesh(me)
        bm.faces.ensure_lookup_table()
        haaks = bm.faces[0].calc_tangent_edge()
        print(haaks)
        verschil = haaks.rotation_difference(v2)
        if haaks[1] != -1 and haaks[1] != 1:# vector valt niet samen met referentie vector
            matrix_rot_2 = verschil.to_matrix().to_4x4()
            obj.matrix_world = obj.matrix_world @ matrix_rot_2
        else:
            matrix_rot_2 =Matrix()
        bpy.ops.object.editmode_toggle()
        plat_vlak = obj
        # als je de matrix inverteert kun je die matrixen gebruiken om het object weer terug te zetten.

        m_1 = matrix_rot_1.inverted()
        m_2 = matrix_rot_2.inverted()
        
        


        # dit is een hulpvlak waar de world matix in wordt opgeslagen, het vlak moet later weg.
        # als het vlak er al is wordt het gewist voordat er een nieuw vlak wordt gemaakt
        try: 
           bpy.data.objects['hulpvlak']
           bpy.data.objects.remove(bpy.data.objects['hulpvlak'])
        except:
            pass

            
        bpy.ops.mesh.primitive_plane_add(size = 2)
        obj = bpy.context.object
        obj.name = 'hulpvlak'   
        bpy.ops.object.hide_view_set(unselected=False)
        
        obj.matrix_world = obj.matrix_world @ m_1 @ m_2
        #obj.location = centrum
        obj.location = laagste
        
        
        bpy.ops.object.select_all(action='DESELECT')
        # Het te exporteren vlak weer selekteren en actief maken
        plat_vlak.select_set(True)
        bpy.context.view_layer.objects.active = plat_vlak
        
        return{'FINISHED'} 

# Het object terug importeren
    
class IMP_dxf_file(bpy.types.Operator):
    bl_idname = 'import_scene.import_dxf_file'
    bl_label = 'DXF import'
    
    
    def execute(self,context):
        path = bpy.path.abspath(context.scene.dxf_export)
        bpy.ops.object.select_all(action='DESELECT')
        resolutie = context.scene.resolutie
        # Alle objecten van True tag voorzien, de nieuw geimporteerde hebben
        # standaard de tag False
        for obj in bpy.data.objects:
            obj.tag = True
        # collection maken voor geimporteerde figuren        
        try:
            bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children["Imports"]
        except:
            col = bpy.data.collections.new("Imports")
            root_col = bpy.context.scene.collection
            root_col.children.link(col)
            bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children["Imports"] 
    
        bpy.ops.import_scene.dxf(filepath=path,
                            merge=True, merge_options='BY_LAYER',
                            merge_lines=True,
                            import_text=True,
                            import_light=True,
                            export_acis=False, 
                            outliner_groups=True, 
                            do_bbox=True, block_options='LINKED_OBJECTS',
                            create_new_scene=False, recenter=False,
                            represent_thickness_and_width=True,
                            import_atts=True, use_georeferencing=True,
                            dxf_indi='EUCLIDEAN',
                            epsg_dxf_user="EPSG",
                            merc_dxf_lat=0, merc_dxf_lon=0, proj_scene='NONE', 
                            epsg_scene_user="EPSG", merc_scene_lat=0, merc_scene_lon=0, 
                            internal_using_scene_srid=False,
                            dxf_scale=str(1/context.scene.scale_factor_2),
                            )

        imported_objects = [obj for obj in bpy.data.objects if obj.tag is False]
        for ob in imported_objects:
            ob.select_set(True)
            
            bpy.data.collections['Imports'].objects.link(ob)
            context.scene.collection.objects.unlink(ob)
        print(imported_objects)
        
        # kijk of het hulpvlak er is, anders de geimporteerde figuren laten staan.
        try:
            m = bpy.data.objects['hulpvlak'].matrix_world
            # de gimporteerde vlakken goed draaien
            # het eerste object van de geselecteerde actief maken
            for obj in bpy.context.selected_objects:
                obj.data.resolution_u = resolutie

                obj.matrix_world = obj.matrix_world @ m 
                 
               
            bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
            # alle objecten van curve naar mesh
            bpy.ops.object.convert(target='MESH')
            
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
            punten = []
            for punt in bpy.context.object.data.vertices:
                punt_abs = punt.co +obj.location
                punt_abs = punt_abs.to_tuple() # vector naar tuple(drie getallen), anders kan je niet sorteren
                punten.append(punt_abs)
            punten.sort()
            print('Hoeveelheid punten =',len(punten))
            laagste = Vector((punten[0])) # terug naar vector
            print('laagste 2=',laagste)
            centrum = bpy.data.objects['hulpvlak'].location
            verschil =  centrum-laagste
            print('verschil =',verschil)
            for ob in bpy.context.selected_objects:
             ob.location =  ob.location + verschil        
            #bpy.data.objects.remove(bpy.data.objects['hulpvlak'])
        except:
            pass
            


        
        return {'FINISHED'} 
    
    
class MESH_OT_to_3Dmesh(bpy.types.Operator):
    """ Maakt  een mesh 3D object, dikte in te stellen. 
    als er meerdere objecten zijn, die appart kiezen """
    bl_idname = "mesh.3d_mesh"
    bl_label = " to 3D mesh"
    bl_options = {'REGISTER', 'UNDO'}

    dikte_buiten: bpy.props.FloatProperty(
        name="dikte buiten(cm)",
        default=10,
    )
    
    dikte_binnen: bpy.props.FloatProperty(
        name="dikte binnen(cm)",
        default=10,
    )
    def execute(self, context):
        dikte_buiten = self.dikte_buiten/100
        dikte_binnen = self.dikte_binnen/100
        norm = bpy.context.scene['normaal_vlak'].to_list()
        normaal = Vector((norm))
        print('normaal is;',normaal)

        
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles()
        bpy.ops.mesh.dissolve_limited(angle_limit=0.0349066)
        bpy.ops.mesh.edge_face_add()
        
        # alle normalen moeten naar een kant gedraaid worden anders gaat het met de extrude 
        # niet goed
        # Ik neem eerst het eerste vlak als normvalk, het is beter 
        #de normaal van het objectvlak te nemen.
        # Dat moet nog gebeuren
        ob = bpy.context.object
        me =  ob.data
        bm = bmesh.from_edit_mesh(me)
        referentie = -normaal
        for vlak in bm.faces:
            n = vlak.normal
            r = referentie
            #samen = n[0]-r[0]+n[1]-r[1]+r[2]-n[2]
            verschil = vlak.normal-referentie
            samen_2 = abs(verschil[0])+abs(verschil[1])+abs(verschil[2])
            print('samen 2=',samen_2)
            if abs(samen_2) < 0.01:
                print(vlak.normal-referentie)
                print('gedraaid')
                vlak.normal_flip()
                #vlak.normal_update()
        #bpy.ops.mesh.normals_make_consistent(inside=False)

        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, dikte_buiten), "orient_type":'NORMAL'})
        bm.faces.ensure_lookup_table()
        for vlak in bm.faces:
            verschil = vlak.normal-referentie
            samen_2 = abs(verschil[0])+abs(verschil[1])+abs(verschil[2])
            if samen_2 < 0.1:
                print('ik ben hier')
                for punt in vlak.verts:
                    punt.co = punt.co -normaal*dikte_binnen
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.editmode_toggle()
        
        
        return{'FINISHED'}
       
       
        
blender_classes = [
    VIEW_PT_dxf_export,
    EXP_dxf_file,
    MESH_OT_vlak_plat,
    IMP_dxf_file,
    MESH_OT_to_3Dmesh
    ]
                            
def register(): 
    # propperties om eigenschappen in op te slaan                           
    bpy.types.Scene.dxf_export = bpy.props.StringProperty(
        name='DXF Folder',
        subtype='FILE_PATH',
        )
    bpy.types.Scene.scale_factor_2 = bpy.props.FloatProperty(
        name = 'Schaal',
        default = 100,
        )
    bpy.types.Scene.resolutie = bpy.props.FloatProperty(
        name = 'Resotutie',
        default =12,
        )
    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)
        
def unregister():
    del bpy.types.Scene.dxf_export
    del bpy.types.Scene.scale_factor_2 
    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class)
    
if __name__ == '__main__':
    register()
