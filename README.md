# Blender-qcad
The addon is made for blender to make it more easy to draw with precision.
First the DXF export and import addons in blender have to be installed(they are shipped with blender)

When you have installed the addon in the sidebar menu (n) you can fined a menu with the possibility to select a file.
This file is going to contain de DXF information.


![Fullscreen capture 5132021 100354 AM](https://user-images.githubusercontent.com/35267283/118097311-cf753080-b3d2-11eb-8724-8f6a09fcce88.jpg)


The 'Schaal', scale can be changed to get the right unities in Qcad.
100 if you want ot work in cm, 1000 for mm.

Now go to edit mode and select a plane, then press DXF export. Go to Qcad and open the file.
Now you can see the plane in qcad. Now you can use qcad to draw.
The best way is to make a new layer first, and draw in the new layer.
When you are ready you can save the file and go back to Blender.
In blender press on the DXF import.
The drawing should appear on the plane that was selected.
You can select the new added drawings and press the to 3Dmesh.
Now the lines become mesh objects, you can use them for boolean operations.

know issues:

-Sometimes the drawing is nog places on the plane but under it. The direction is good but not the location.
It is not hard to move it to the right place, I am trying to solve this problem.

-It is better in qcat to flatten the drawing first (misc/modify/flatten drawing to 2d)
If you dont do this the offset doesn't work right and everything is not on the same plane when imported in blender.

