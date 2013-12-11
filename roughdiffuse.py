import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "MitsubaRoughDiffuseShader"
kPluginNodeClassify = "shader/surface"
kPluginNodeId = OpenMaya.MTypeId(0x8700A)

class roughdiffuse(OpenMayaMPx.MPxNode):
        def __init__(self):
                OpenMayaMPx.MPxNode.__init__(self)
                mTwoSided = OpenMaya.MObject()
                mOutColor = OpenMaya.MObject()
                mReflectance = OpenMaya.MObject()
                mAlpha = OpenMaya.MObject()
                mApprox = OpenMaya.MObject()

        def compute(self, plug, block):
                if plug == roughdiffuse.mOutColor:
                        resultColor = OpenMaya.MFloatVector(0.0,0.0,0.0)
                        
                        color = block.inputValue( roughdiffuse.mReflectance ).asFloatVector()

                        resultColor.x = color.x
                        resultColor.y = color.y
                        resultColor.z = color.z

                        outColorHandle = block.outputValue( roughdiffuse.mOutColor )
                        outColorHandle.setMFloatVector(resultColor)
                        outColorHandle.setClean()
                else:
                        return OpenMaya.kUnknownParameter


def nodeCreator():
        return roughdiffuse()

def nodeInitializer():
        nAttr = OpenMaya.MFnNumericAttribute()

        try:

                roughdiffuse.mTwoSided = nAttr.create("twosided", "tw", OpenMaya.MFnNumericData.kBoolean, True)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                roughdiffuse.mReflectance = nAttr.createColor("reflectance", "r")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                roughdiffuse.mAlpha = nAttr.create("alpha","a", OpenMaya.MFnNumericData.kFloat, 0.2)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                roughdiffuse.mApprox = nAttr.create("useFastApprox","ax", OpenMaya.MFnNumericData.kBoolean, False)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                roughdiffuse.mOutColor = nAttr.createColor("outColor", "oc")
                nAttr.setStorable(0)
                nAttr.setHidden(0)
                nAttr.setReadable(1)
                nAttr.setWritable(0)

        except:
                sys.stderr.write("Failed to create attributes\n")
                raise

        try:
                roughdiffuse.addAttribute(roughdiffuse.mTwoSided)
                roughdiffuse.addAttribute(roughdiffuse.mReflectance)
                roughdiffuse.addAttribute(roughdiffuse.mAlpha)
                roughdiffuse.addAttribute(roughdiffuse.mApprox)
                roughdiffuse.addAttribute(roughdiffuse.mOutColor)
        except:
                sys.stderr.write("Failed to add attributes\n")
                raise

        try:
                roughdiffuse.attributeAffects (roughdiffuse.mReflectance, roughdiffuse.mOutColor)
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
