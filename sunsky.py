import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "MitsubaSunsky"
kPluginNodeId = OpenMaya.MTypeId(0x88000)
kPluginClassify = "light"

class sunsky(OpenMayaMPx.MPxNode):
        def __init__(self):
                OpenMayaMPx.MPxNode.__init__(self)
                mUseSun = OpenMaya.MObject()
                mUseSky = OpenMaya.MObject()

def nodeCreator():
        return sunsky()

def nodeInitializer():
        nAttr = OpenMaya.MFnNumericAttribute()

        try:
                sunsky.mUseSun = nAttr.create("useSun", "sun", OpenMaya.MFnNumericData.kBoolean, True)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                sunsky.mUseSky = nAttr.create("useSky", "sky", OpenMaya.MFnNumericData.kBoolean, True)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

        except:
                sys.stderr.write("Failed to create attributes\n")
                raise

        try:
                sunsky.addAttribute(sunsky.mUseSun)
                sunsky.addAttribute(sunsky.mUseSky)
        except:
                sys.stderr.write("Failed to add attributes\n")
                raise

# initialize the script plug-in
def initializePlugin(mobject):
        mplugin = OpenMayaMPx.MFnPlugin(mobject)
        try:
                mplugin.registerNode( kPluginNodeName, kPluginNodeId, nodeCreator, 
                                        nodeInitializer, OpenMayaMPx.MPxNode.kDependNode, kPluginClassify )
        except:
                sys.stderr.write( "Failed to register node: %s" % kPluginNodeName )
                raise

# uninitialize the script plug-in
def uninitializePlugin(mobject):
        mplugin = OpenMayaMPx.MFnPlugin(mobject)
        try:
                mplugin.deregisterNode( kPluginNodeId )
        except:
                sys.stderr.write( "Failed to deregister node: %s" % kPluginNodeName )
                raise
