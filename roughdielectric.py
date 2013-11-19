import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

kPluginNodeName = "MitsubaRoughDielectricShader"
kPluginNodeClassify = "/shader/surface"
kPluginNodeId = OpenMaya.MTypeId(0x87009)

class roughdielectric(OpenMayaMPx.MPxNode):
        def __init__(self):
                OpenMayaMPx.MPxNode.__init__(self)
                mReflectance = OpenMaya.MObject()
                mTransmittance = OpenMaya.MObject()
                mIntIOR = OpenMaya.MObject()
                mExtIOR = OpenMaya.MObject()

                mAlpha = OpenMaya.MObject()
                mAlpaUV = OpenMaya.MObject()
                mDistribution = OpenMaya.MObject()

                mOutColor = OpenMaya.MObject()
                mOutTransparency = OpenMaya.MObject()

        def compute(self, plug, block):
                if plug == roughdielectric.mOutColor:
                        print "out color"
                        resultColor = OpenMaya.MFloatVector(0.0,0.0,0.0)
                        
                        color = block.inputValue( roughdielectric.mReflectance ).asFloatVector()

                        outColorHandle = block.outputValue( roughdielectric.mOutColor )
                        outColorHandle.setMFloatVector(resultColor)
                        outColorHandle.setClean()
                elif plug == roughdielectric.mOutTransparency:
                        outTransHandle = block.outputValue( roughdielectric.mOutTransparency )
                        outTransHandle.setMFloatVector(OpenMaya.MFloatVector(0.75,0.75,0.75))
                        outTransHandle.setClean()
                else:
                        return OpenMaya.kUnknownParameter


def nodeCreator():
        return roughdielectric()

def nodeInitializer():
        nAttr = OpenMaya.MFnNumericAttribute()
        eAttr = OpenMaya.MFnEnumAttribute()

        try:
                roughdielectric.mDistribution = eAttr.create("distribution", "dist")
                eAttr.setKeyable(1) 
                eAttr.setStorable(1)
                eAttr.setReadable(1)
                eAttr.setWritable(1)

                eAttr.addField("beckmann", 0)
                eAttr.addField("ggx", 1)
                eAttr.addField("phong", 2)
                eAttr.addField("as", 3)

                roughdielectric.mAlpha = nAttr.create("alpha","a", OpenMaya.MFnNumericData.kFloat, 0.1)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                roughdielectric.mAlpaUV = nAttr.create("alphaUV","uv", OpenMaya.MFnNumericData.k2Float)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(0.1,0.1)

                roughdielectric.mReflectance = nAttr.createColor("specularReflectance", "r")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(1.0,1.0,1.0)
                #cmds.setAttr(roughdielectric.mReflectance, (1,1,1))

                roughdielectric.mTransmittance = nAttr.createColor("specularTransmittance","t")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(1.0,1.0,1.0)

                roughdielectric.mIntIOR = nAttr.create("InteriorIOR","intIOR", OpenMaya.MFnNumericData.kFloat, 1.0)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                roughdielectric.mExtIOR = nAttr.create("ExteriorIOR","extIOR", OpenMaya.MFnNumericData.kFloat, 1.3)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                roughdielectric.mOutColor = nAttr.createColor("outColor", "oc")
                nAttr.setStorable(0)
                nAttr.setHidden(0)
                nAttr.setReadable(1)
                nAttr.setWritable(0)

                roughdielectric.mOutTransparency = nAttr.createColor("outTransparency", "op")
                nAttr.setStorable(0)
                nAttr.setHidden(0)
                nAttr.setReadable(1)
                nAttr.setWritable(0)

        except:
                sys.stderr.write("Failed to create attributes\n")
                raise

        try:
                roughdielectric.addAttribute(roughdielectric.mDistribution)
                roughdielectric.addAttribute(roughdielectric.mAlpha)
                roughdielectric.addAttribute(roughdielectric.mAlpaUV)
                roughdielectric.addAttribute(roughdielectric.mReflectance)
                roughdielectric.addAttribute(roughdielectric.mTransmittance)
                roughdielectric.addAttribute(roughdielectric.mIntIOR)
                roughdielectric.addAttribute(roughdielectric.mExtIOR)
                roughdielectric.addAttribute(roughdielectric.mOutColor)
                roughdielectric.addAttribute(roughdielectric.mOutTransparency)
        except:
                sys.stderr.write("Failed to add attributes\n")
                raise

        try:
                roughdielectric.attributeAffects (roughdielectric.mTransmittance, roughdielectric.mOutTransparency)
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
