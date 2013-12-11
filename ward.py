import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

kPluginNodeName = "MitsubaWardShader"
kPluginNodeClassify = "/shader/surface"
kPluginNodeId = OpenMaya.MTypeId(0x8700C)

class ward(OpenMayaMPx.MPxNode):
        def __init__(self):
                OpenMayaMPx.MPxNode.__init__(self)
                mTwoSided = OpenMaya.MObject()
                mSpecular = OpenMaya.MObject()
                mDiffuse = OpenMaya.MObject()

                mVariant = OpenMaya.MObject()
                mAlphaUV = OpenMaya.MObject()

                mOutColor = OpenMaya.MObject()

        def compute(self, plug, block):
                if plug == ward.mOutColor:
                        resultColor = OpenMaya.MFloatVector(0.0,0.0,0.0)
                        
                        color = block.inputValue( ward.mDiffuse ).asFloatVector()
                        resultColor.x=color.x
                        resultColor.y=color.y
                        resultColor.z=color.z

                        outColorHandle = block.outputValue( ward.mOutColor )
                        outColorHandle.setMFloatVector(resultColor)
                        outColorHandle.setClean()
                else:
                        return OpenMaya.kUnknownParameter


def nodeCreator():
        return ward()

def nodeInitializer():
        nAttr = OpenMaya.MFnNumericAttribute()
        eAttr = OpenMaya.MFnEnumAttribute()

        try:

                ward.mTwoSided = nAttr.create("twosided", "tw", OpenMaya.MFnNumericData.kBoolean, True)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                ward.mVariant = eAttr.create("variant", "var")
                eAttr.setKeyable(1) 
                eAttr.setStorable(1)
                eAttr.setReadable(1)
                eAttr.setWritable(1)

                eAttr.addField("ward", 0)
                eAttr.addField("ward-duer", 1)
                eAttr.addField("balanced", 2)

                ward.mAlpaUV = nAttr.create("alphaUV","uv", OpenMaya.MFnNumericData.k2Float)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(0.1,0.1)

                ward.mSpecular = nAttr.createColor("specularReflectance", "sr")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(0.2,0.2,0.2)

                ward.mDiffuse = nAttr.createColor("diffuseReflectance","dr")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(.5,.5,.5)



                ward.mOutColor = nAttr.createColor("outColor", "oc")
                nAttr.setStorable(0)
                nAttr.setHidden(0)
                nAttr.setReadable(1)
                nAttr.setWritable(0)

        except:
                sys.stderr.write("Failed to create attributes\n")
                raise

        try:
                ward.addAttribute(ward.mTwoSided)
                ward.addAttribute(ward.mVariant)
                ward.addAttribute(ward.mAlpaUV)
                ward.addAttribute(ward.mSpecular)
                ward.addAttribute(ward.mDiffuse)
                ward.addAttribute(ward.mOutColor)
        except:
                sys.stderr.write("Failed to add attributes\n")
                raise

        try:
                ward.attributeAffects (ward.mDiffuse, ward.mOutColor)
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
