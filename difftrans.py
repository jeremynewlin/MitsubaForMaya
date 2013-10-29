import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "MitsubaDiffuseTransmitterShader"
kPluginNodeClassify = "shader/surface"
kPluginNodeId = OpenMaya.MTypeId(0x8700D)

class difftrans(OpenMayaMPx.MPxNode):
        def __init__(self):
                OpenMayaMPx.MPxNode.__init__(self)
                mOutColor = OpenMaya.MObject()
                mReflectance = OpenMaya.MObject()

        def compute(self, plug, block):
                if plug == difftrans.mOutColor or plug.parent() == difftrans.mOutColor:
                        resultColor = OpenMaya.MFloatVector(0.0,0.0,0.0)
                        
                        color = block.inputValue( difftrans.mReflectance ).asFloatVector()

                        resultColor.x = color.x
                        resultColor.y = color.y
                        resultColor.z = color.z

                        outColorHandle = block.outputValue( difftrans.mOutColor )
                        outColorHandle.setMFloatVector(resultColor)
                        outColorHandle.setClean()
                else:
                        return OpenMaya.kUnknownParameter


def nodeCreator():
        return difftrans()

def nodeInitializer():
        nAttr = OpenMaya.MFnNumericAttribute()

        try:
                difftrans.mReflectance = nAttr.createColor("reflectance", "r")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(.5,.5,.5)

                difftrans.mOutColor = nAttr.createColor("outColor", "oc")
                nAttr.setStorable(0)
                nAttr.setHidden(0)
                nAttr.setReadable(1)
                nAttr.setWritable(0)

        except:
                sys.stderr.write("Failed to create attributes\n")
                raise

        try:
                difftrans.addAttribute(difftrans.mReflectance)
                difftrans.addAttribute(difftrans.mOutColor)
        except:
                sys.stderr.write("Failed to add attributes\n")
                raise

        try:
                difftrans.attributeAffects (difftrans.mReflectance, difftrans.mOutColor)
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
