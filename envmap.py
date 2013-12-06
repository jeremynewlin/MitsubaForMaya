import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "MitsubaEnvironmentLight"
kPluginNodeId = OpenMaya.MTypeId(0x88A29)
kPluginClassify = "/light/general"

class envmap(OpenMayaMPx.MPxNode):
        def __init__(self):
                OpenMayaMPx.MPxNode.__init__(self)
                mSource = OpenMaya.MObject()
                mScale = OpenMaya.MObject()
                mAutoGamma = OpenMaya.MObject()
                mSRGB = OpenMaya.MObject()
                mGamma = OpenMaya.MObject()
                mCache = OpenMaya.MObject()
                mSamplingWeight = OpenMaya.MObject()

        def compute(self, plug, block):
                x=1

def nodeCreator():
        return envmap()

def nodeInitializer():
        nAttr = OpenMaya.MFnNumericAttribute()

        try:
                envmap.mSource = nAttr.createColor("source", "src")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(1.0,1.0,1.0)

                envmap.mScale = nAttr.create("scale", "scale", OpenMaya.MFnNumericData.kFloat, 1.0)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                envmap.mAutoGamma = nAttr.create("autoGamma", "autoGamma", OpenMaya.MFnNumericData.kBoolean, True)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                envmap.mSRGB = nAttr.create("srgb", "srgb", OpenMaya.MFnNumericData.kBoolean, False)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                envmap.mGamma = nAttr.create("gamma", "g", OpenMaya.MFnNumericData.kFloat, 1.0)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                envmap.mCache = nAttr.create("cache", "cache", OpenMaya.MFnNumericData.kBoolean, True)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                envmap.mSamplingWeight = nAttr.create("samplingWeight", "sw", OpenMaya.MFnNumericData.kFloat, 1.0)
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)


        except:
                sys.stderr.write("Failed to create attributes\n")
                raise

        try:
                envmap.addAttribute(envmap.mSource)
                envmap.addAttribute(envmap.mGamma)
                envmap.addAttribute(envmap.mAutoGamma)
                envmap.addAttribute(envmap.mSRGB)
                envmap.addAttribute(envmap.mScale)
                envmap.addAttribute(envmap.mCache)
                envmap.addAttribute(envmap.mSamplingWeight)
        except:
                sys.stderr.write("Failed to add attributes\n")
                raise

# initialize the script plug-in
def initializePlugin(mobject):
        mplugin = OpenMayaMPx.MFnPlugin(mobject)
        try:
                mplugin.registerNode( kPluginNodeName, kPluginNodeId, nodeCreator, 
                                        nodeInitializer, OpenMayaMPx.MPxNode.kDependNode, kPluginClassify )
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
