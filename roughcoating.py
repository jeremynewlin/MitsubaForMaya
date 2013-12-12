import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

kPluginNodeName = "MitsubaRoughCoatingShader"
kPluginNodeClassify = "/shader/surface"
kPluginNodeId = OpenMaya.MTypeId(0x8700F)

class roughcoating(OpenMayaMPx.MPxNode):
        def __init__(self):
                OpenMayaMPx.MPxNode.__init__(self)
                mIntIOR = OpenMaya.MObject()
                mExtIOR = OpenMaya.MObject()
                mThickness = OpenMaya.MObject()
                mSigmaA = OpenMaya.MObject()
                mBSDF = OpenMaya.MObject()

                mAlpha = OpenMaya.MObject()
                mDistribution = OpenMaya.MObject()

                mReflectance = OpenMaya.MObject()
                mOutColor = OpenMaya.MObject()

        def compute(self, plug, block):
                if plug == roughcoating.mOutColor or plug.parent() == roughcoating.mOutColor:
                        color = block.inputValue( roughcoating.mBSDF ).asFloatVector()

                        outColorHandle = block.outputValue( roughcoating.mOutColor )
                        outColorHandle.setMFloatVector(color)
                        outColorHandle.setClean()
                else:
                        return OpenMaya.kUnknownParameter


def nodeCreator():
        return roughcoating()

def nodeInitializer():
        nAttr = OpenMaya.MFnNumericAttribute()
        eAttr = OpenMaya.MFnEnumAttribute()

        try:

                roughcoating.mDistribution = eAttr.create("distribution", "dist")
                eAttr.setKeyable(1) 
                eAttr.setStorable(1)
                eAttr.setReadable(1)
                eAttr.setWritable(1)

                eAttr.addField("beckmann", 0)
                eAttr.addField("ggx", 1)
                eAttr.addField("phong", 2)

                roughcoating.mAlpha = nAttr.create("alpha","a", OpenMaya.MFnNumericData.kFloat, 0.1)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                roughcoating.mIntIOR = nAttr.create("InteriorIOR","intIOR", OpenMaya.MFnNumericData.kFloat, 1.5046)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                roughcoating.mExtIOR = nAttr.create("ExteriorIOR","extIOR", OpenMaya.MFnNumericData.kFloat, 1.000277)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                roughcoating.mThickness = nAttr.create("thickness","th", OpenMaya.MFnNumericData.kFloat, 1.0)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                roughcoating.mSigmaA = nAttr.createColor("sigmaA", "sa")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                roughcoating.mReflectance = nAttr.createColor("specularReflectance", "sr")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(1.0,1.0,1.0)

                roughcoating.mBSDF = nAttr.createColor("bsdf", "bsdf")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(0.0,0.0,0.0)

                roughcoating.mOutColor = nAttr.createColor("outColor", "oc")
                nAttr.setStorable(0)
                nAttr.setHidden(0)
                nAttr.setReadable(1)
                nAttr.setWritable(0)

        except:
                sys.stderr.write("Failed to create attributes\n")
                raise

        try:
                roughcoating.addAttribute(roughcoating.mDistribution)
                roughcoating.addAttribute(roughcoating.mAlpha)
                roughcoating.addAttribute(roughcoating.mThickness)
                roughcoating.addAttribute(roughcoating.mSigmaA)
                roughcoating.addAttribute(roughcoating.mBSDF)
                roughcoating.addAttribute(roughcoating.mReflectance)
                roughcoating.addAttribute(roughcoating.mIntIOR)
                roughcoating.addAttribute(roughcoating.mExtIOR)
                roughcoating.addAttribute(roughcoating.mOutColor)
        except:
                sys.stderr.write("Failed to add attributes\n")
                raise

        try:
                roughcoating.attributeAffects(roughcoating.mBSDF, roughcoating.mOutColor)
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
