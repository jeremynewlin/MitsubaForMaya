import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

kPluginNodeName = "MitsubaConductorShader"
kPluginNodeClassify = "/shader/surface"
kPluginNodeId = OpenMaya.MTypeId(0x87002)

class conductor(OpenMayaMPx.MPxNode):
        def __init__(self):
                OpenMayaMPx.MPxNode.__init__(self)
                mTwoSided = OpenMaya.MObject()
                mMaterial = OpenMaya.MObject()
                mEta = OpenMaya.MObject()
                mK = OpenMaya.MObject()
                mExtEta = OpenMaya.MObject()

                mSpecularReflectance = OpenMaya.MObject()

                mOutColor = OpenMaya.MObject()

        def compute(self, plug, block):
                if plug == conductor.mOutColor:
                        resultColor = OpenMaya.MFloatVector(0.5,0.5,0.0)
                        
                        outColorHandle = block.outputValue( conductor.mOutColor )
                        outColorHandle.setMFloatVector(resultColor)
                        outColorHandle.setClean()
                else:
                        return OpenMaya.kUnknownParameter


def nodeCreator():
        return conductor()

def nodeInitializer():
        nAttr = OpenMaya.MFnNumericAttribute()
        eAttr = OpenMaya.MFnEnumAttribute()

        try:

                conductor.mTwoSided = nAttr.create("twosided", "tw", OpenMaya.MFnNumericData.kBoolean, True)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                conductor.mMaterial = eAttr.create("material", "mat")
                eAttr.setKeyable(1) 
                eAttr.setStorable(1)
                eAttr.setReadable(1)
                eAttr.setWritable(1)

                eAttr.addField("a-C", 0)
                eAttr.addField("Ag", 1)
                eAttr.addField("Al", 2)
                eAttr.addField("AlAs", 3)
                eAttr.addField("AlAs_palik", 4)
                eAttr.addField("AlSb", 5)
                eAttr.addField("AlSb_palik",  6)
                eAttr.addField("Au", 7)
                eAttr.addField("Be", 8)
                eAttr.addField("Be_palik", 9)
                eAttr.addField("Cr", 10)
                eAttr.addField("CsI", 11)
                eAttr.addField("CsI_palik", 12)

                conductor.mK = nAttr.createColor("k", "k")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(1.0,1.0,1.0)

                conductor.mEta = nAttr.createColor("eta","e")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(1.0,1.0,1.0)

                conductor.mExtEta = nAttr.create("extEta","ee", OpenMaya.MFnNumericData.kFloat, 1.0)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                conductor.mSpecularReflectance = nAttr.createColor("specularReflectance", "sr")
                nAttr.setStorable(0)
                nAttr.setHidden(0)
                nAttr.setReadable(1)
                nAttr.setWritable(0)
                nAttr.setDefault(1.0,1.0,1.0)

                conductor.mOutColor = nAttr.createColor("outColor", "oc")
                nAttr.setStorable(0)
                nAttr.setHidden(0)
                nAttr.setReadable(1)
                nAttr.setWritable(0)
                nAttr.setDefault(0.5,0.5,0.0)


        except:
                sys.stderr.write("Failed to create attributes\n")
                raise

        try:
                conductor.addAttribute(conductor.mTwoSided)
                conductor.addAttribute(conductor.mMaterial)
                conductor.addAttribute(conductor.mK)
                conductor.addAttribute(conductor.mEta)
                conductor.addAttribute(conductor.mExtEta)
                conductor.addAttribute(conductor.mSpecularReflectance)
                conductor.addAttribute(conductor.mOutColor)
        except:
                sys.stderr.write("Failed to add attributes\n")
                raise

        try:
                x=1
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
