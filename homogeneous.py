import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

kPluginNodeName = "HomogeneousParticipatingMedium"
kPluginNodeClassify = "/utility/general"
kPluginNodeId = OpenMaya.MTypeId(0x87005)

class homogeneous(OpenMayaMPx.MPxNode):
        def __init__(self):
                OpenMayaMPx.MPxNode.__init__(self)
                mMaterial = OpenMaya.MObject()
                mSigmaA = OpenMaya.MObject()
                mSigmaS = OpenMaya.MObject()
                mSigmaT = OpenMaya.MObject()
                mAlbedo = OpenMaya.MObject()
                mScale = OpenMaya.MObject()

                mUseSigmaAS = OpenMaya.MObject()
                mUserSigmaTAlbedo = OpenMaya.MObject()

                mOutColor = OpenMaya.MObject()

        def compute(self, plug, block):
                if plug == homogeneous.mUseSigmaAS:
                        asHandle = block.inputValue(plug)
                        asValue = asHandle.asBool()
                        asHandle.setBool(not asValue)
                        asHandle.setClean()

                elif plug == homogeneous.mUserSigmaTAlbedo:
                        taHandle = block.inputValue(plug)
                        taValue = taHandle.asBool()
                        taHandle.setBool(not taValue)
                        taHandle.setClean()
                else:
                        return OpenMaya.kUnknownParameter


def nodeCreator():
        return homogeneous()

def nodeInitializer():
        nAttr = OpenMaya.MFnNumericAttribute()

        try:

                homogeneous.mUseSigmaAS = nAttr.create("sigmaAS","sas", OpenMaya.MFnNumericData.kBoolean, False)
                nAttr.setKeyable(0) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                homogeneous.mSigmaA = nAttr.createColor("sigmaA", "sa")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(1.0,1.0,1.0)

                homogeneous.mSigmaS = nAttr.createColor("sigmaS", "ss")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(1.0,1.0,1.0)

                homogeneous.mUserSigmaTAlbedo = nAttr.create("sigmaTA","sta", OpenMaya.MFnNumericData.kBoolean, True)
                nAttr.setKeyable(0) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                homogeneous.mSigmaT = nAttr.createColor("sigmaT", "st")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(1.0,1.0,1.0)

                homogeneous.mAlbedo = nAttr.createColor("albedo", "a")
                nAttr.setKeyable(1) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)
                nAttr.setDefault(1.0,1.0,1.0)

                homogeneous.mScale = nAttr.create("scale","s", OpenMaya.MFnNumericData.kFloat, 1.0)
                nAttr.setKeyable(0) 
                nAttr.setStorable(1)
                nAttr.setReadable(1)
                nAttr.setWritable(1)

                homogeneous.mOutColor = nAttr.createColor("outColor", "oc")
                nAttr.setStorable(0)
                nAttr.setHidden(0)
                nAttr.setReadable(1)
                nAttr.setWritable(0)

        except:
                sys.stderr.write("Failed to create attributes\n")
                raise

        try:
                homogeneous.addAttribute(homogeneous.mUseSigmaAS)
                homogeneous.addAttribute(homogeneous.mSigmaA)
                homogeneous.addAttribute(homogeneous.mSigmaS)
                homogeneous.addAttribute(homogeneous.mUserSigmaTAlbedo)
                homogeneous.addAttribute(homogeneous.mSigmaT)
                homogeneous.addAttribute(homogeneous.mAlbedo)
                homogeneous.addAttribute(homogeneous.mScale)
                homogeneous.addAttribute(homogeneous.mOutColor)
        except:
                sys.stderr.write("Failed to add attributes\n")
                raise

        try:
                homogeneous.attributeAffects (homogeneous.mSigmaA, homogeneous.mOutColor)
                homogeneous.attributeAffects (homogeneous.mUseSigmaAS, homogeneous.mUserSigmaTAlbedo)
                homogeneous.attributeAffects (homogeneous.mUserSigmaTAlbedo, homogeneous.mUseSigmaAS)
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
