import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

kPluginNodeName = "MitsubaThinDielectricShader"
kPluginNodeClassify = "/shader/surface"
kPluginNodeId = OpenMaya.MTypeId(0x87001)

class thindielectric(OpenMayaMPx.MPxNode):
        def __init__(self):
                OpenMayaMPx.MPxNode.__init__(self)
                mReflectance = OpenMaya.MObject()
                mTransmittance = OpenMaya.MObject()
                mIntIOR = OpenMaya.MObject()
                mExtIOR = OpenMaya.MObject()

                mOutColor = OpenMaya.MObject()
                mOutTransparency = OpenMaya.MObject()

                mMedium = OpenMaya.MObject()

        def compute(self, plug, block):
                if plug == thindielectric.mOutColor:
                        print "out color"
                        resultColor = OpenMaya.MFloatVector(0.0,0.0,0.0)
                        
                        color = block.inputValue( thindielectric.mReflectance ).asFloatVector()

                        outColorHandle = block.outputValue( thindielectric.mOutColor )
                        outColorHandle.setMFloatVector(resultColor)
                        outColorHandle.setClean()
                elif plug == thindielectric.mOutTransparency:
                        outTransHandle = block.outputValue( thindielectric.mOutTransparency )
                        outTransHandle.setMFloatVector(OpenMaya.MFloatVector(0.75,0.75,0.75))
                        outTransHandle.setClean()
                else:
                        return OpenMaya.kUnknownParameter


def nodeCreator():
        return thindielectric()

def nodeInitializer():
        nAttr = OpenMaya.MFnNumericAttribute()

        try:
                thindielectric.mMedium = nAttr.createColor("medium", "m")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(1.0,1.0,1.0)

                thindielectric.mReflectance = nAttr.createColor("reflectance", "r")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(1.0,1.0,1.0)
                #cmds.setAttr(thindielectric.mReflectance, (1,1,1))

                thindielectric.mTransmittance = nAttr.createColor("transmittance","t")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(1.0,1.0,1.0)

                thindielectric.mIntIOR = nAttr.create("InteriorIOR","intIOR", OpenMaya.MFnNumericData.kFloat, 1.0)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                thindielectric.mExtIOR = nAttr.create("ExteriorIOR","extIOR", OpenMaya.MFnNumericData.kFloat, 1.3)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                thindielectric.mOutColor = nAttr.createColor("outColor", "oc")
                nAttr.setStorable(0)
                nAttr.setHidden(0)
                nAttr.setReadable(1)
                nAttr.setWritable(0)

                thindielectric.mOutTransparency = nAttr.createColor("outTransparency", "op")
                nAttr.setStorable(0)
                nAttr.setHidden(0)
                nAttr.setReadable(1)
                nAttr.setWritable(0)

        except:
                sys.stderr.write("Failed to create attributes\n")
                raise

        try:
                thindielectric.addAttribute(thindielectric.mMedium)
                thindielectric.addAttribute(thindielectric.mReflectance)
                thindielectric.addAttribute(thindielectric.mTransmittance)
                thindielectric.addAttribute(thindielectric.mIntIOR)
                thindielectric.addAttribute(thindielectric.mExtIOR)
                thindielectric.addAttribute(thindielectric.mOutColor)
                thindielectric.addAttribute(thindielectric.mOutTransparency)
        except:
                sys.stderr.write("Failed to add attributes\n")
                raise

        try:
                thindielectric.attributeAffects (thindielectric.mTransmittance, thindielectric.mOutTransparency)
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
