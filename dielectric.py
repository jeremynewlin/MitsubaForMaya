import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "MitsubaDielectricShader"
kPluginNodeClassify = "shader/surface"
kPluginNodeId = OpenMaya.MTypeId(0x8701E)

class dielectric(OpenMayaMPx.MPxNode):
        def __init__(self):
                OpenMayaMPx.MPxNode.__init__(self)
                mOutColor = OpenMaya.MObject()
                mReflectance = OpenMaya.MObject()
                mTransmittance = OpenMaya.MObject()
                mIntIOR = OpenMaya.MObject()
                mExtIOR = OpenMaya.MObject()

        def compute(self, plug, block):
                if plug == dielectric.mOutColor or plug.parent() == dielectric.mOutColor:
                        resultColor = OpenMaya.MFloatVector(0.0,0.0,0.0)
                        
                        color = block.inputValue( dielectric.mReflectance ).asFloatVector()

                        resultColor.x = color.x
                        resultColor.y = color.y
                        resultColor.z = color.z

                        outColorHandle = block.outputValue( dielectric.mOutColor )
                        outColorHandle.setMFloatVector(resultColor)
                        outColorHandle.setClean()
                else:
                        return OpenMaya.kUnknownParameter


def nodeCreator():
        return dielectric()

def nodeInitializer():
        nAttr = OpenMaya.MFnNumericAttribute()

        try:
                dielectric.mReflectance = nAttr.createColor("reflectance", "r")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                dielectric.mTransmittance = nAttr.createColor("transmittance","t")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                status = OpenMaya.MStatus()

                dielectric.mIntIOR = nAttr.create("InteriorIOR","iior", OpenMaya.MFnNumericData.kFloat, 1.0)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                dielectric.mExtIOR = nAttr.create("ExteriorIOR","eior", OpenMaya.MFnNumericData.kFloat, 1.3)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                dielectric.mOutColor = nAttr.createColor("outColor", "oc")
                nAttr.setStorable(0)
                nAttr.setHidden(0)
                nAttr.setReadable(1)
                nAttr.setWritable(0)

        except:
                sys.stderr.write("Failed to create attributes\n")
                raise

        try:
                dielectric.addAttribute(dielectric.mReflectance)
                dielectric.addAttribute(dielectric.mTransmittance)
                dielectric.addAttribute(dielectric.mIntIOR)
                dielectric.addAttribute(dielectric.mExtIOR)
                dielectric.addAttribute(dielectric.mOutColor)
        except:
                sys.stderr.write("Failed to add attributes\n")
                raise

        try:
                dielectric.attributeAffects (dielectric.mReflectance, dielectric.mOutColor)
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
