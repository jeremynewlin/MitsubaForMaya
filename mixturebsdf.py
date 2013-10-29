import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

kPluginNodeName = "MitsubaMixtureShader"
kPluginNodeClassify = "/shader/surface"
kPluginNodeId = OpenMaya.MTypeId(0x870011)

class mixture(OpenMayaMPx.MPxNode):
        def __init__(self):
                OpenMayaMPx.MPxNode.__init__(self)
                mBSDF = OpenMaya.MObject()
                mWeights = OpenMaya.MObject()
                mOutColor = OpenMaya.MObject()

        def compute(self, plug, block):
                if plug == mixture.mOutColor:
                        print "out color"
                        resultColor = OpenMaya.MFloatVector(0.0,0.0,0.0)
                        
                        outColorHandle = block.outputValue( mixture.mOutColor )
                        outColorHandle.setMFloatVector(resultColor)
                        outColorHandle.setClean()
                else:
                        return OpenMaya.kUnknownParameter


def nodeCreator():
        return mixture()

def nodeInitializer():
        nAttr = OpenMaya.MFnNumericAttribute()
        tAttr = OpenMaya.MFnTypedAttribute()

        try:

                mixture.mWeights = tAttr.create("weights","w",OpenMaya.MFnData.kDoubleArray)
                tAttr.setStorable(1)
                tAttr.setHidden(1)
                tAttr.setReadable(1)
                tAttr.setWritable(1)

                mixture.mOutColor = nAttr.createColor("outColor", "oc")
                nAttr.setStorable(0)
                nAttr.setHidden(0)
                nAttr.setReadable(1)
                nAttr.setWritable(0)

        except:
                sys.stderr.write("Failed to create attributes\n")
                raise

        try:
                mixture.addAttribute(mixture.mWeights)
                mixture.addAttribute(mixture.mOutColor)
        except:
                sys.stderr.write("Failed to add attributes\n")
                raise

        try:
                z=1
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
