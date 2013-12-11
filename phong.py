import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

kPluginNodeName = "MitsubaPhongShader"
kPluginNodeClassify = "/shader/surface"
kPluginNodeId = OpenMaya.MTypeId(0x8700B)

class phong(OpenMayaMPx.MPxNode):
        def __init__(self):
                OpenMayaMPx.MPxNode.__init__(self)
                mTwoSided = OpenMaya.MObject()
                mSpecular = OpenMaya.MObject()
                mDiffuse = OpenMaya.MObject()
                mExponent = OpenMaya.MObject()

                mOutColor = OpenMaya.MObject()

        def compute(self, plug, block):
                if plug == phong.mOutColor:
                        resultColor = OpenMaya.MFloatVector(0.0,0.0,0.0)
                        
                        color = block.inputValue( phong.mDiffuse ).asFloatVector()
                        resultColor.x=color.x
                        resultColor.y=color.y
                        resultColor.z=color.z

                        outColorHandle = block.outputValue( phong.mOutColor )
                        outColorHandle.setMFloatVector(resultColor)
                        outColorHandle.setClean()
                else:
                        return OpenMaya.kUnknownParameter


def nodeCreator():
        return phong()

def nodeInitializer():
        nAttr = OpenMaya.MFnNumericAttribute()

        try:

                phong.mTwoSided = nAttr.create("twosided", "tw", OpenMaya.MFnNumericData.kBoolean, True)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                phong.mSpecular = nAttr.createColor("specularReflectance", "sr")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(0.2,0.2,0.2)

                phong.mDiffuse = nAttr.createColor("diffuseReflectance","dr")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(.5,.5,.5)

                phong.mExponent = nAttr.create("exponent","exp", OpenMaya.MFnNumericData.kFloat, 30.0)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                phong.mOutColor = nAttr.createColor("outColor", "oc")
                nAttr.setStorable(0)
                nAttr.setHidden(0)
                nAttr.setReadable(1)
                nAttr.setWritable(0)

        except:
                sys.stderr.write("Failed to create attributes\n")
                raise

        try:
                phong.addAttribute(phong.mTwoSided)
                phong.addAttribute(phong.mSpecular)
                phong.addAttribute(phong.mDiffuse)
                phong.addAttribute(phong.mExponent)
                phong.addAttribute(phong.mOutColor)
        except:
                sys.stderr.write("Failed to add attributes\n")
                raise

        try:
                phong.attributeAffects (phong.mDiffuse, phong.mOutColor)
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
