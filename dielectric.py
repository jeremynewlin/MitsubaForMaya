import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

kPluginNodeName = "MitsubaDielectricShader"
kPluginNodeClassify = "shader/surface/"
kPluginNodeId = OpenMaya.MTypeId(0x87004)

class dielectric(OpenMayaMPx.MPxNode):
        def __init__(self):
                OpenMayaMPx.MPxNode.__init__(self)
                mReflectance = OpenMaya.MObject()
                mTransmittance = OpenMaya.MObject()
                mIntIOR = OpenMaya.MObject()
                mExtIOR = OpenMaya.MObject()
                mMaterial = OpenMaya.MObject()

                mOutColor = OpenMaya.MObject()
                mOutTransparency = OpenMaya.MObject()

        def compute(self, plug, block):
                if plug == dielectric.mOutColor:
                        print "out color"
                        resultColor = OpenMaya.MFloatVector(0.0,0.0,0.0)
                        
                        color = block.inputValue( dielectric.mReflectance ).asFloatVector()

                        outColorHandle = block.outputValue( dielectric.mOutColor )
                        outColorHandle.setMFloatVector(resultColor)
                        outColorHandle.setClean()
                elif plug == dielectric.mOutTransparency:
                        outTransHandle = block.outputValue( dielectric.mOutTransparency )
                        outTransHandle.setMFloatVector(OpenMaya.MFloatVector(0.75,0.75,0.75))
                        outTransHandle.setClean()
                else:
                        return OpenMaya.kUnknownParameter


def nodeCreator():
        return dielectric()

def nodeInitializer():
        nAttr = OpenMaya.MFnNumericAttribute()

        try:

                dielectric.mMaterial = nAttr.createColor("material", "mat")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(1.0,1.0,1.0)

                dielectric.mReflectance = nAttr.createColor("reflectance", "r")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(1.0,1.0,1.0)

                dielectric.mTransmittance = nAttr.createColor("transmittance","t")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(1.0,1.0,1.0)

                dielectric.mIntIOR = nAttr.create("InteriorIOR","intIOR", OpenMaya.MFnNumericData.kFloat, 1.0)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                dielectric.mExtIOR = nAttr.create("ExteriorIOR","extIOR", OpenMaya.MFnNumericData.kFloat, 1.3)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                dielectric.mOutColor = nAttr.createColor("outColor", "oc")
                nAttr.setStorable(0)
                nAttr.setHidden(0)
                nAttr.setReadable(1)
                nAttr.setWritable(0)

                dielectric.mOutTransparency = nAttr.createColor("outTransparency", "op")
                nAttr.setStorable(0)
                nAttr.setHidden(0)
                nAttr.setReadable(1)
                nAttr.setWritable(0)

        except:
                sys.stderr.write("Failed to create attributes\n")
                raise

        try:
                dielectric.addAttribute(dielectric.mMaterial)
                dielectric.addAttribute(dielectric.mReflectance)
                dielectric.addAttribute(dielectric.mTransmittance)
                dielectric.addAttribute(dielectric.mIntIOR)
                dielectric.addAttribute(dielectric.mExtIOR)
                dielectric.addAttribute(dielectric.mOutColor)
                dielectric.addAttribute(dielectric.mOutTransparency)
        except:
                sys.stderr.write("Failed to add attributes\n")
                raise

        try:
                dielectric.attributeAffects (dielectric.mTransmittance, dielectric.mOutTransparency)
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
