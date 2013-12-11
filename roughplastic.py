import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

kPluginNodeName = "MitsubaRoughPlasticShader"
kPluginNodeClassify = "/shader/surface"
kPluginNodeId = OpenMaya.MTypeId(0x87000)

class roughplastic(OpenMayaMPx.MPxNode):
        def __init__(self):
                OpenMayaMPx.MPxNode.__init__(self)
                mTwoSided = OpenMaya.MObject()
                mSpecular = OpenMaya.MObject()
                mDiffuse = OpenMaya.MObject()
                mIntIOR = OpenMaya.MObject()
                mExtIOR = OpenMaya.MObject()

                mAlpha = OpenMaya.MObject()
                mDistribution = OpenMaya.MObject()

                mOutColor = OpenMaya.MObject()

        def compute(self, plug, block):
                if plug == roughplastic.mOutColor:
                        print "TETG"
                        resultColor = OpenMaya.MFloatVector(0.0,0.0,0.0)
                        
                        color = block.inputValue( roughplastic.mDiffuse ).asFloatVector()
                        resultColor.x=color.x
                        resultColor.y=color.y
                        resultColor.z=color.z

                        outColorHandle = block.outputValue( roughplastic.mOutColor )
                        outColorHandle.setMFloatVector(resultColor)
                        outColorHandle.setClean()
                else:
                        return OpenMaya.kUnknownParameter


def nodeCreator():
        return roughplastic()

def nodeInitializer():
        nAttr = OpenMaya.MFnNumericAttribute()
        eAttr = OpenMaya.MFnEnumAttribute()

        try:

                roughplastic.mTwoSided = nAttr.create("twosided", "tw", OpenMaya.MFnNumericData.kBoolean, True)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                roughplastic.mDistribution = eAttr.create("distribution", "dist")
                eAttr.setKeyable(1) 
                eAttr.setStorable(1)
                eAttr.setReadable(1)
                eAttr.setWritable(1)

                eAttr.addField("beckmann", 0)
                eAttr.addField("ggx", 1)
                eAttr.addField("phong", 2)
                eAttr.addField("as", 3)

                roughplastic.mAlpha = nAttr.create("alpha","a", OpenMaya.MFnNumericData.kFloat, 0.1)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                roughplastic.mSpecular = nAttr.createColor("specularReflectance", "sr")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(1.0,1.0,1.0)

                roughplastic.mDiffuse = nAttr.createColor("diffuseReflectance","dr")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(.5,.5,.5)

                roughplastic.mIntIOR = nAttr.create("InteriorIOR","intIOR", OpenMaya.MFnNumericData.kFloat, 1.0)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                roughplastic.mExtIOR = nAttr.create("ExteriorIOR","extIOR", OpenMaya.MFnNumericData.kFloat, 1.000277)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                roughplastic.mOutColor = nAttr.createColor("outColor", "oc")
                nAttr.setStorable(0)
                nAttr.setHidden(0)
                nAttr.setReadable(1)
                nAttr.setWritable(0)
                nAttr.setDefault(.75,.75,.75)

        except:
                sys.stderr.write("Failed to create attributes\n")
                raise

        try:
                roughplastic.addAttribute(roughplastic.mTwoSided)
                roughplastic.addAttribute(roughplastic.mDistribution)
                roughplastic.addAttribute(roughplastic.mAlpha)
                roughplastic.addAttribute(roughplastic.mSpecular)
                roughplastic.addAttribute(roughplastic.mDiffuse)
                roughplastic.addAttribute(roughplastic.mIntIOR)
                roughplastic.addAttribute(roughplastic.mExtIOR)
                roughplastic.addAttribute(roughplastic.mOutColor)
        except:
                sys.stderr.write("Failed to add attributes\n")
                raise

        try:
                roughplastic.attributeAffects (roughplastic.mDiffuse, roughplastic.mOutColor)
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
