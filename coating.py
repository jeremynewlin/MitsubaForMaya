import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

kPluginNodeName = "MitsubaSmoothCoatingShader"
kPluginNodeClassify = "/shader/surface"
kPluginNodeId = OpenMaya.MTypeId(0x8700E)

class coating(OpenMayaMPx.MPxNode):
        def __init__(self):
                OpenMayaMPx.MPxNode.__init__(self)
                mIntIOR = OpenMaya.MObject()
                mExtIOR = OpenMaya.MObject()
                mThickness = OpenMaya.MObject()
                mSigmaA = OpenMaya.MObject()
                mBSDF = OpenMaya.MObject()

                mReflectance = OpenMaya.MObject()
                mOutColor = OpenMaya.MObject()

        def compute(self, plug, block):
                if plug == coating.mOutColor or plug.parent() == coating.mOutColor:
                        color = block.inputValue( coating.mBSDF ).asFloatVector()

                        outColorHandle = block.outputValue( coating.mOutColor )
                        outColorHandle.setMFloatVector(color)
                        outColorHandle.setClean()
                else:
                        return OpenMaya.kUnknownParameter


def nodeCreator():
        return coating()

def nodeInitializer():
        nAttr = OpenMaya.MFnNumericAttribute()

        try:
                coating.mIntIOR = nAttr.create("InteriorIOR","intIOR", OpenMaya.MFnNumericData.kFloat, 1.5046)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                coating.mExtIOR = nAttr.create("ExteriorIOR","extIOR", OpenMaya.MFnNumericData.kFloat, 1.000277)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                coating.mThickness = nAttr.create("thickness","th", OpenMaya.MFnNumericData.kFloat, 1.0)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                coating.mSigmaA = nAttr.createColor("sigmaA", "sa")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                coating.mReflectance = nAttr.createColor("specularReflectance", "sr")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(1.0,1.0,1.0)

                coating.mBSDF = nAttr.createColor("bsdf", "bsdf")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(0.0,0.0,0.0)

                coating.mOutColor = nAttr.createColor("outColor", "oc")
                nAttr.setStorable(0)
                nAttr.setHidden(0)
                nAttr.setReadable(1)
                nAttr.setWritable(0)

        except:
                sys.stderr.write("Failed to create attributes\n")
                raise

        try:
                coating.addAttribute(coating.mThickness)
                coating.addAttribute(coating.mSigmaA)
                coating.addAttribute(coating.mBSDF)
                coating.addAttribute(coating.mReflectance)
                coating.addAttribute(coating.mIntIOR)
                coating.addAttribute(coating.mExtIOR)
                coating.addAttribute(coating.mOutColor)
        except:
                sys.stderr.write("Failed to add attributes\n")
                raise

        try:
                coating.attributeAffects(coating.mBSDF, coating.mOutColor)
                # print "attr affects"
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
