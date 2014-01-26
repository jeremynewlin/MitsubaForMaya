import sys
import maya.OpenMaya as OpenMaya				#import du module des classes communes
import maya.OpenMayaMPx as OpenMayaMPx			#import du module des classes de proxy
import maya.OpenMayaRender as OpenMayaRender	#import du module des classes propres au rendu

nodeTypeName = "MitsubaDirectionalLight"				#le nom du node
nodeTypeId = OpenMaya.MTypeId(0x87079)			#creation de l'id du node

glRenderer = OpenMayaRender.MHardwareRenderer.theRenderer()	#semble recuperer un pointeur vers le renderer hardware utiliser
glFT = glRenderer.glFunctionTable()							#renvois un pointeur vers la "table des fonctions OpenGL"

class directional(OpenMayaMPx.MPxLocatorNode):
	def __init__(self):
		OpenMayaMPx.MPxLocatorNode.__init__(self)
		mDirection = OpenMaya.MObject()
		mIrradiance = OpenMaya.MObject()
		mSamplingWeight = OpenMaya.MObject()

	def draw(self, view, path, style, status):				#procedure appele au momment du "dessin" du locator

		view.beginGL()							#fonctionne bien sans mais il semble que ce soit necessaire pour eviter les plantages...

		glFT.glBegin(OpenMayaRender.MGL_LINES)	#debut de la primive de type MGL_LINES
		glFT.glVertex3f(0.0, -0.5, 0.0)			#dessine un premier vextex
		glFT.glVertex3f(0.0, 0.5, 0.0)			#dessine le seconde vextex
		glFT.glEnd()							#fin de la primive de type MGL_LINES

		glFT.glBegin(OpenMayaRender.MGL_LINES)	#debut de la primive de type MGL_LINES
		glFT.glVertex3f(0.0, 0.5, 0.0)			#dessine un premier vextex
		glFT.glVertex3f(0.1, 0.25, 0.0)			#dessine le seconde vextex
		glFT.glEnd()							#fin de la primive de type MGL_LINES

		glFT.glBegin(OpenMayaRender.MGL_LINES)	#debut de la primive de type MGL_LINES
		glFT.glVertex3f(0.0, 0.5, 0.0)			#dessine un premier vextex
		glFT.glVertex3f(-0.1, 0.25, 0.0)			#dessine le seconde vextex
		glFT.glEnd()							#fin de la primive de type MGL_LINES

		view.endGL()


def nodeCreator():
	return OpenMayaMPx.asMPxPtr(directional())
 
def nodeInitializer():
	nAttr = OpenMaya.MFnNumericAttribute()

	try:
	        directional.mIrradiance = nAttr.createColor("irradiance", "irr")
	        nAttr.setKeyable(1) 
	        nAttr.setStorable(1)
	        nAttr.setReadable(1)
	        nAttr.setWritable(1)
	        nAttr.setDefault(1.0,1.0,1.0)

	        directional.mSamplingWeight = nAttr.create("samplingWeight", "sw", OpenMaya.MFnNumericData.kFloat, 1.0)
	        nAttr.setKeyable(1) 
	        nAttr.setStorable(1)
	        nAttr.setReadable(1)
	        nAttr.setWritable(1)

	except:
	        sys.stderr.write("Failed to create attributes\n")
	        raise

	try:
	        directional.addAttribute(directional.mIrradiance)
	        directional.addAttribute(directional.mSamplingWeight)
	except:
	        sys.stderr.write("Failed to add attributes\n")
	        raise

def initializePlugin(obj):						#procedure lance au moment de l'initialisation du plugin
	plugin = OpenMayaMPx.MFnPlugin(obj)
	try:
		plugin.registerNode(nodeTypeName, nodeTypeId, nodeCreator, nodeInitializer, OpenMayaMPx.MPxNode.kLocatorNode)
	except:
		sys.stderr.write( "Failed to register node: %s" % nodeTypeName)

def uninitializePlugin(obj):					#procedure lance au moment de la desactivation du plugin
	plugin = OpenMayaMPx.MFnPlugin(obj)
	try:
		plugin.deregisterNode(nodeTypeId)
	except:
		sys.stderr.write( "Failed to deregister node: %s" % nodeTypeName)
