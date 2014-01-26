import maya.cmds as cmds
import maya.mel as mel

def getShader(geom):
    shapeNode = cmds.listRelatives(geom, children=True, shapes=True)[0]
    sg = cmds.listConnections(shapeNode, type="shadingEngine")[0]
    shader = cmds.listConnections(sg+".surfaceShader")[0]
    return shader

userSelection = cmds.ls(sl=True)
cwd = cmds.workspace(q=True, directory=True)

#out mitsuba file
outFileName = cwd+"temporary.xml"
outFile = open(outFileName, 'w+')

outFile.write("<?xml version=\'1.0\' encoding=\'utf-8\'?>\n")
outFile.write("\n")
outFile.write("<scene version=\"0.4.0\">\n")
outFile.write("	<integrator type=\"path\">\n")
outFile.write("	</integrator>\n")
outFile.write("\n")
outFile.write("	<!-- Camera -->\n")

cams = cmds.ls(type="camera")
rCamShape = ""
for cam in cams:
    isRenderable = cmds.getAttr(cam+".renderable")
    if isRenderable:
        rCamShape = cam
        break
        
rGroup = cmds.listConnections(rCamShape)[0]
rGroupRels = cmds.listRelatives(rGroup)
rCam = rGroupRels[0]
rAim = rGroupRels[1]
rUp  = rGroupRels[2]

camPos = cmds.getAttr(rCam+".translate")
camAim = cmds.getAttr(rAim+".translate")
camUp  = cmds.getAttr(rUp+".translate")

outFile.write("	<sensor type=\"perspective\">\n")
outFile.write("			<float name=\"fov\" value=\"54.43\"/>\n")
outFile.write("			<string name=\"fovAxis\" value=\"x\"/>\n")
outFile.write("			<float name=\"nearClip\" value=\"0.1\"/>\n")
outFile.write("			<transform name=\"toWorld\">\n")
outFile.write("				<lookat target=\"0,0,0\" origin=\"0, 5.5, 12.5\" up=\"0,1,0\"/>\n")
outFile.write("			</transform>\n")
outFile.write("\n")
outFile.write("			<sampler type=\"sobol\">\n")
outFile.write("				<integer name=\"sampleCount\" value=\"256\"/>\n")
outFile.write("				<integer name=\"scramble\" value=\"1\"/>\n")
outFile.write("			</sampler>\n")
outFile.write("\n")
outFile.write("		<film type=\"ldrfilm\">\n")
outFile.write("			<boolean name=\"banner\" value=\"false\"/>\n")
outFile.write("			<integer name=\"height\" value=\"720\"/>\n")
outFile.write("			<integer name=\"width\" value=\"1280\"/>\n")
outFile.write("			<rfilter type=\"gaussian\"/>\n")
outFile.write("		</film>\n")
outFile.write("	</sensor>\n")
outFile.write("\n")
outFile.write("	<emitter type=\"constant\"/>\n")
outFile.write("\n")

materials = cmds.ls(materials=True)
for material in materials:
    matType = cmds.nodeType(material)
    if matType=="MitsubaDiffuseShader":
        reflectance = cmds.getAttr(material+".reflectance")
        outFile.write("	<bsdf type=\"twosided\">\n")
        outFile.write("		<bsdf type=\"diffuse\" id=\"" + material + "\">\n")
        outFile.write("			<srgb name=\"reflectance\" value=\"" + str(reflectance[0][0]) + " " + str(reflectance[0][1]) + " " + str(reflectance[0][2]) + "\"/>\n")
        outFile.write("		</bsdf>\n")
        outFile.write("	</bsdf>\n")


outFile.write("\n")

transforms = cmds.ls(type="transform")
geoms = []

for transform in transforms:
	rels = cmds.listRelatives(transform)
	for rel in rels:
		if cmds.nodeType(rel)=="mesh":
			geoms.append(transform)
			
for geom in geoms:
	output = cwd+geom+".obj"
	cmds.select(geom)
	cmds.file(output, op=True, typ="OBJexport", es=True, force=True)
	shader = getShader(geom)
	outFile.write("    <shape type=\"obj\">\n")
	outFile.write("        <string name=\"filename\" value=\"" + geom + ".obj\"/>\n")
	outFile.write("        <ref id=\"" + shader + "\"/>\n")
	outFile.write("    </shape>\n")
	
outFile.write("\n")
outFile.write("</scene>")
outFile.close()

if len(userSelection) > 0:
    cmds.select(userSelection)
else:
    cmds.select(cl=True)