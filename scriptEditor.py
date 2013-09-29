import maya.cmds as cmds
import maya.mel as mel

materials = cmds.ls(materials=True)

print ""

for material in materials:
    matType = cmds.nodeType(material)
    if matType=="MitsubaDiffuseShader":
        reflectance = cmds.getAttr(material+".reflectance")
        print "<bsdf type=\"diffuse\" id=\"" + material + "\">"
        print "    <srgb name=\"reflectance\" value=\"" + str(reflectance[0][0]) + " " + str(reflectance[0][1]) + " " + str(reflectance[0][2]) + "\"/>"
        print "</bsdf>"