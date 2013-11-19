import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "MitsubaDiffuseShader"
kPluginNodeClassify = "shader/surface"
kPluginNodeId = OpenMaya.MTypeId(0x87003)

class diffuse(OpenMayaMPx.MPxNode):
        def __init__(self):
                OpenMayaMPx.MPxNode.__init__(self)
                mOutColor = OpenMaya.MObject()
                mReflectance = OpenMaya.MObject()


def nodeCreator():
        return diffuse()

def nodeInitializer():
        nAttr = OpenMaya.MFnNumericAttribute()

        try:
                diffuse.mReflectance = nAttr.createColor("reflectance", "r")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                diffuse.mOutColor = nAttr.createColor("outColor", "oc")
                nAttr.setStorable(0)
                nAttr.setHidden(0)
                nAttr.setReadable(1)
                nAttr.setWritable(0)

        except:
                sys.stderr.write("Failed to create attributes\n")
                raise

        try:
                diffuse.addAttribute(diffuse.mReflectance)
                diffuse.addAttribute(diffuse.mOutColor)
        except:
                sys.stderr.write("Failed to add attributes\n")
                raise

        try:
                diffuse.attributeAffects (diffuse.mReflectance, diffuse.mOutColor)
        except:
                sys.stderr.write("Failed in setting attributeAffects\n")
                raise


# initialize the script plug-in
def initializePlugin(mobject):
        mplugin = OpenMayaMPx.MFnPlugin(mobject)
        try:
                mplugin.registerNode( kPluginNodeName, kPluginNodeId, nodeCreator, 
                                        nodeInitializer, OpenMayaMPx.MPxNode.kDependNode, kPluginNodeClassify )
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
