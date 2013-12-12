import sys, os
import re
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

kPluginCmdName = "mitsuba"

global materialNodeTypes
#The list of possible material types
materialNodeTypes = ["MitsubaBumpShader", "MitsubaSmoothCoatingShader", "MitsubaConductorShader", "MitsubaDielectricShader", "MitsubaDiffuseTransmitterShader", "MitsubaDiffuseShader", "MitsubaMaskShader", "MitsubaMixtureShader", "MitsubaPhongShader", "MitsubaPlasticShader", "MitsubaRoughCoatingShader", "MitsubaRoughConductorShader", "MitsubaRoughDielectricShader", "MitsubaRoughDiffuseShader", "MitsubaRoughPlasticShader", "MitsubaThinDielectricShader", "MitsubaTwoSidedShader", "MitsubaWardShader"]

'''
Returns the surfaceShader node for a piece of geometry (geom)
'''
def getShader(geom):
    shapeNode = cmds.listRelatives(geom, children=True, shapes=True)[0]
    sg = cmds.listConnections(shapeNode, type="shadingEngine")[0]
    shader = cmds.listConnections(sg+".surfaceShader")[0]
    return shader

'''
Writes a homogeneous medium to a Mitsuba scene file (outFile)
tabbedSpace is a string of blank space to account for recursive xml
'''
def writeMedium(medium, outFile, tabbedSpace):
    outFile.write(tabbedSpace + " <medium type=\"homogeneous\" name=\"interior\">\n")
    
    #check if we want to use sigmaA and sigmaT or sigmaT and albedo
    sigmaAS = cmds.getAttr(medium+".sigmaAS")
    if sigmaAS:
        sigmaA = cmds.getAttr(medium+".sigmaA")
        sigmaS = cmds.getAttr(medium+".sigmaS")
        outFile.write(tabbedSpace + "      <rgb name=\"sigmaA\" value=\"" + str(sigmaA[0][0]) + " " + str(sigmaA[0][1]) + " " + str(sigmaA[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + "      <rgb name=\"sigmaS\" value=\"" + str(sigmaS[0][0]) + " " + str(sigmaS[0][1]) + " " + str(sigmaS[0][2]) + "\"/>\n")
    else:
        sigmaT = cmds.getAttr(medium+".sigmaT")
        albedo = cmds.getAttr(medium+".albedo")
        outFile.write(tabbedSpace + "      <rgb name=\"sigmaT\" value=\"" + str(sigmaT[0][0]) + " " + str(sigmaT[0][1]) + " " + str(sigmaT[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + "      <rgb name=\"albedo\" value=\"" + str(albedo[0][0]) + " " + str(albedo[0][1]) + " " + str(albedo[0][2]) + "\"/>\n")

    scale = cmds.getAttr(medium+".scale")    
    outFile.write(tabbedSpace + "      <float name=\"scale\" value=\"" + str(scale) + "\"/>\n")
    outFile.write(tabbedSpace + " </medium>\n")

'''
Write a surface material (material) to a Mitsuba scene file (outFile)
tabbedSpace is a string of blank space to account for recursive xml
'''
def writeShader(material, materialName, outFile, tabbedSpace):
    matType = cmds.nodeType(material)
    
    if matType=="MitsubaBumpShader":
        print "bump"

    elif matType=="MitsubaSmoothCoatingShader":
        intIOR = cmds.getAttr(material+".intIOR")
        extIOR = cmds.getAttr(material+".extIOR")
        thickness = cmds.getAttr(material+".thickness")
        sigmaA = cmds.getAttr(material+".sigmaA")
        specularReflectance = cmds.getAttr(material+".specularReflectance")

        outFile.write(tabbedSpace + " <bsdf type=\"coating\" id=\"" + materialName + "\">\n")
        outFile.write(tabbedSpace + "     <float name=\"intIOR\" value=\"" + str(intIOR) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"extIOR\" value=\"" + str(extIOR) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"thickness\" value=\"" + str(thickness) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"sigmaA\" value=\"" + str(sigmaA[0][0]) + " " + str(sigmaA[0][1]) + " " + str(sigmaA[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"specularReflectance\" value=\"" + str(specularReflectance[0][0]) + " " + str(specularReflectance[0][1]) + " " + str(specularReflectance[0][2]) + "\"/>\n")
        
        #Nested bsdf
        hasNestedBSDF = False
        connections = cmds.listConnections(material, connections=True)
        for i in range(len(connections)):
            if i%2==1:
                connection = connections[i]
                connectionType = cmds.nodeType(connection)
                if connectionType in materialNodeTypes and connections[i-1]==material+".bsdf":
                    #We've found the nested bsdf, so write it
                    writeShader(connection, connection, outFile, tabbedSpace+"    ")
                    hasNestedBSDF = True

        if not hasNestedBSDF:
            #Write a basic diffuse using the bsdf attribute
            bsdf = cmds.getAttr(material+".bsdf")
            outFile.write(tabbedSpace + "     <bsdf type=\"diffuse\">\n")
            outFile.write(tabbedSpace + "          <srgb name=\"reflectance\" value=\"" + str(bsdf[0][0]) + " " + str(bsdf[0][1]) + " " + str(bsdf[0][2]) + "\"/>\n")
            outFile.write(tabbedSpace + "     </bsdf>\n")

        outFile.write(tabbedSpace + " </bsdf>\n")
    
    elif matType=="MitsubaConductorShader":
        conductorMaterial = cmds.getAttr(material+".material", asString=True)
        extEta = cmds.getAttr(material+".extEta")
        outFile.write(tabbedSpace + " <bsdf type=\"conductor\"   id=\"" + materialName + "\">\n")
        outFile.write(tabbedSpace + "     <string name=\"material\" value=\"" + str(conductorMaterial) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"extEta\" value=\"" + str(extEta) + "\"/>\n")
        outFile.write(tabbedSpace + " </bsdf>\n")

    elif matType=="MitsubaDielectricShader":
        #Get all of the required attributes
        intIOR = cmds.getAttr(material+".intIOR")
        extIOR = cmds.getAttr(material+".extIOR")

        #Write material
        outFile.write(tabbedSpace + " <bsdf type=\"dielectric\" id=\"" + materialName + "\">\n")
        outFile.write(tabbedSpace + "     <float name=\"intIOR\" value=\"" + str(intIOR) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"extIOR\" value=\"" + str(extIOR) + "\"/>\n")
        outFile.write(tabbedSpace + " </bsdf>\n\n")

    elif matType=="MitsubaDiffuseTransmitterShader":
        transmittance = cmds.getAttr(material+".reflectance")
        outFile.write(tabbedSpace + " <bsdf type=\"diffuse\" id=\"" + materialName + "\">\n")
        outFile.write(tabbedSpace + "     <srgb name=\"reflectance\" value=\"" + str(transmittance[0][0]) + " " + str(transmittance[0][1]) + " " + str(transmittance[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + " </bsdf>\n")

    elif matType=="MitsubaDiffuseShader":
        reflectance = cmds.getAttr(material+".reflectance")
        outFile.write(tabbedSpace + " <bsdf type=\"diffuse\" id=\"" + materialName + "\">\n")
        outFile.write(tabbedSpace + "     <srgb name=\"reflectance\" value=\"" + str(reflectance[0][0]) + " " + str(reflectance[0][1]) + " " + str(reflectance[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + " </bsdf>\n")

    elif matType=="MitsubaMaskShader":
        print "mask"

    elif matType=="MitsubaMixtureShader":
        print "mixture"

    elif matType=="MitsubaPhongShader":
        exponent = cmds.getAttr(material+".exponent")
        specularReflectance = cmds.getAttr(material+".specularReflectance")
        diffuseReflectance = cmds.getAttr(material+".diffuseReflectance")

        outFile.write(tabbedSpace + " <bsdf type=\"phong\" id=\"" + materialName + "\">\n")
        outFile.write(tabbedSpace + "     <float name=\"exponent\" value=\"" + str(exponent) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"specularReflectance\" value=\"" + str(specularReflectance[0][0]) + " " + str(specularReflectance[0][1]) + " " + str(specularReflectance[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"diffuseReflectance\" value=\"" + str(diffuseReflectance[0][0]) + " " + str(diffuseReflectance[0][1]) + " " + str(diffuseReflectance[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + " </bsdf>\n")

    elif matType=="MitsubaPlasticShader":
        intIOR = cmds.getAttr(material+".intIOR")
        extIOR = cmds.getAttr(material+".extIOR")
        specularReflectance = cmds.getAttr(material+".specularReflectance")
        diffuseReflectance = cmds.getAttr(material+".diffuseReflectance")

        outFile.write(tabbedSpace + " <bsdf type=\"plastic\" id=\"" + materialName + "\">\n")
        outFile.write(tabbedSpace + "     <float name=\"intIOR\" value=\"" + str(intIOR) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"extIOR\" value=\"" + str(extIOR) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"specularReflectance\" value=\"" + str(specularReflectance[0][0]) + " " + str(specularReflectance[0][1]) + " " + str(specularReflectance[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"diffuseReflectance\" value=\"" + str(diffuseReflectance[0][0]) + " " + str(diffuseReflectance[0][1]) + " " + str(diffuseReflectance[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + " </bsdf>\n")


    elif matType=="MitsubaRoughCoatingShader":
        distribution = cmds.getAttr(material+".distribution", asString=True)
        alpha = cmds.getAttr(material+".alpha")
        intIOR = cmds.getAttr(material+".intIOR")
        extIOR = cmds.getAttr(material+".extIOR")
        thickness = cmds.getAttr(material+".thickness")
        sigmaA = cmds.getAttr(material+".sigmaA")
        specularReflectance = cmds.getAttr(material+".specularReflectance")

        outFile.write(tabbedSpace + " <bsdf type=\"roughcoating\" id=\"" + materialName + "\">\n")
        outFile.write(tabbedSpace + "     <string name=\"distribution\" value=\"" + str(distribution) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"alpha\" value=\"" + str(alpha) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"intIOR\" value=\"" + str(intIOR) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"extIOR\" value=\"" + str(extIOR) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"thickness\" value=\"" + str(thickness) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"sigmaA\" value=\"" + str(sigmaA[0][0]) + " " + str(sigmaA[0][1]) + " " + str(sigmaA[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"specularReflectance\" value=\"" + str(specularReflectance[0][0]) + " " + str(specularReflectance[0][1]) + " " + str(specularReflectance[0][2]) + "\"/>\n")
        
        #Nested bsdf
        hasNestedBSDF = False
        connections = cmds.listConnections(material, connections=True)
        for i in range(len(connections)):
            if i%2==1:
                connection = connections[i]
                connectionType = cmds.nodeType(connection)
                if connectionType in materialNodeTypes and connections[i-1]==material+".bsdf":
                    #We've found the nested bsdf, so write it
                    writeShader(connection, connection, outFile, tabbedSpace+"    ")
                    hasNestedBSDF=True
        
        if not hasNestedBSDF:
            #Write a basic diffuse using the bsdf attribute
            bsdf = cmds.getAttr(material+".bsdf")
            outFile.write(tabbedSpace + "     <bsdf type=\"diffuse\">\n")
            outFile.write(tabbedSpace + "          <srgb name=\"reflectance\" value=\"" + str(bsdf[0][0]) + " " + str(bsdf[0][1]) + " " + str(bsdf[0][2]) + "\"/>\n")
            outFile.write(tabbedSpace + "     </bsdf>\n")

        outFile.write(tabbedSpace + " </bsdf>\n")

    elif matType=="MitsubaRoughConductorShader":
        outFile.write(tabbedSpace + " <bsdf type=\"roughconductor\" id=\"" + materialName + "\">\n")

        distribution = cmds.getAttr(material+".distribution", asString=True)
        #We have different behaviour depending on the distribution
        outFile.write(tabbedSpace + "     <string name=\"distribution\" value=\"" + str(distribution) + "\"/>\n")
        #Using Anisotropic Phong, use alphaUV
        if distribution=="as":
            alphaUV = cmds.getAttr(material+".alphaUV")
            outFile.write(tabbedSpace + "     <float name=\"alphaU\" value=\"" + str(alphaUV[0]) + "\"/>\n")
            outFile.write(tabbedSpace + "     <float name=\"alphaV\" value=\"" + str(alphaUV[1]) + "\"/>\n")
        else:
            alpha = cmds.getAttr(material+".alpha")
            outFile.write(tabbedSpace + "     <float name=\"alpha\" value=\"" + str(alpha) + "\"/>\n")

        #write the rest
        conductorMaterial = cmds.getAttr(material+".material")
        extEta = cmds.getAttr(material+"extEta")
        outFile.write(tabbedSpace + "     <string name=\"material\" value=\"" + str(conductorMaterial) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"extEta\" value=\"" + str(extEta) + "\"/>\n")
        outFile.write(tabbedSpace + " </bsdf>\n")

    elif matType=="MitsubaRoughDielectricShader":
        #Get all of the required attributes
        intIOR = cmds.getAttr(material+".intIOR")
        extIOR = cmds.getAttr(material+".extIOR")
        specularReflectance = cmds.getAttr(material+".specularReflectance")
        specularTransmittance = cmds.getAttr(material+".specularTransmittance")

        #Write material
        outFile.write(tabbedSpace + " <bsdf type=\"dielectric\" id=\"" + materialName + "\">\n")
        
        distribution = cmds.getAttr(material+".distribution", asString=True)
        #We have different behaviour depending on the distribution
        outFile.write(tabbedSpace + "     <string name=\"distribution\" value=\"" + str(distribution) + "\"/>\n")
        #Using Anisotropic Phong, use alphaUV
        if distribution=="as":
            alphaUV = cmds.getAttr(material+".alphaUV")
            outFile.write(tabbedSpace + "     <float name=\"alphaU\" value=\"" + str(alphaUV[0]) + "\"/>\n")
            outFile.write(tabbedSpace + "     <float name=\"alphaV\" value=\"" + str(alphaUV[1]) + "\"/>\n")
        else:
            alpha = cmds.getAttr(material+".alpha")
            outFile.write(tabbedSpace + "     <float name=\"alpha\" value=\"" + str(alpha) + "\"/>\n")

        outFile.write(tabbedSpace + "     <float name=\"intIOR\" value=\"" + str(intIOR) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"extIOR\" value=\"" + str(extIOR) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"specularReflectance\" value=\"" + str(specularReflectance[0][0]) + " " + str(specularReflectance[0][1]) + " " + str(specularReflectance[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"specularTransmittance\" value=\"" + str(specularTransmittance[0][0]) + " " + str(specularTransmittance[0][1]) + " " + str(specularTransmittance[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + " </bsdf>\n\n")

    elif matType=="MitsubaRoughDiffuseShader":
        reflectance = cmds.getAttr(material+".reflectance")
        alpha = cmds.getAttr(material+".alpha")
        useFastApprox = cmds.getAttr(material+".useFastApprox")

        outFile.write(tabbedSpace + " <bsdf type=\"roughdiffuse\" id=\"" + materialName + "\">\n")
        outFile.write(tabbedSpace + "     <srgb name=\"reflectance\" value=\"" + str(reflectance[0][0]) + " " + str(reflectance[0][1]) + " " + str(reflectance[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"alpha\" value=\"" + str(alpha) + "\"/>\n")
        outFile.write(tabbedSpace + "     <boolean name=\"useFastApprox\" value=\"" + str(useFastApprox) + "\"/>\n")
        outFile.write(tabbedSpace + " </bsdf>\n")

    elif matType=="MitsubaRoughPlasticShader":
        distribution = cmds.getAttr(material+".distribution", asString=True)
        alpha = cmds.getAttr(material+".alpha")
        intIOR = cmds.getAttr(material+".intIOR")
        extIOR = cmds.getAttr(material+".extIOR")
        specularReflectance = cmds.getAttr(material+".specularReflectance")
        diffuseReflectance = cmds.getAttr(material+".diffuseReflectance")

        outFile.write(tabbedSpace + " <bsdf type=\"roughplastic\" id=\"" + materialName + "\">\n")
        outFile.write(tabbedSpace + "     <string name=\"distribution\" value=\"" + str(distribution) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"alpha\" value=\"" + str(alpha) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"intIOR\" value=\"" + str(intIOR) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"extIOR\" value=\"" + str(extIOR) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"specularReflectance\" value=\"" + str(specularReflectance[0][0]) + " " + str(specularReflectance[0][1]) + " " + str(specularReflectance[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"diffuseReflectance\" value=\"" + str(diffuseReflectance[0][0]) + " " + str(diffuseReflectance[0][1]) + " " + str(diffuseReflectance[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + " </bsdf>\n")

    elif matType=="MitsubaThinDielectricShader":
        #Get all of the required attributes
        intIOR = cmds.getAttr(material+".intIOR")
        extIOR = cmds.getAttr(material+".extIOR")

        #Write material
        outFile.write(tabbedSpace + " <bsdf type=\"thindielectric\">\n id=\"" + materialName + "\">\n")
        outFile.write(tabbedSpace + "     <float name=\"intIOR\" value=\"" + str(intIOR) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"extIOR\" value=\"" + str(extIOR) + "\"/>\n")
        outFile.write(tabbedSpace + " </bsdf>\n\n")

    elif matType=="MitsubaTwoSidedShader":
        outFile.write(tabbedSpace + " <bsdf type=\"twosided\" id=\"" + materialName + "\">\n")
        #Nested bsdf
        connections = cmds.listConnections(material, connections=True)
        for i in range(len(connections)):
            if i%2==1:
                connection = connections[i]
                connectionType = cmds.nodeType(connection)
                if connectionType in materialNodeTypes and connections[i-1]==material+".bsdf":
                    #We've found the nested bsdf, so write it
                    writeShader(connection, outFile, tabbedSpace+"    ")

        outFile.write(tabbedSpace + " </bsdf>\n")

    elif matType=="MitsubaWardShader":
        variant = cmds.getAttr(material+".variant", asString=True)
        alphaUV = cmds.getAttr(material+".alphaUV")
        specularReflectance = cmds.getAttr(material+".specularReflectance")
        diffuseReflectance = cmds.getAttr(material+".diffuseReflectance")

        outFile.write(tabbedSpace + " <bsdf type=\"phong\" id=\"" + materialName + "\">\n")
        outFile.write(tabbedSpace + "     <string name=\"variant\" value=\"" + str(variant) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"alphaU\" value=\"" + str(alphaUV[0][0]) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"alphaV\" value=\"" + str(alphaUV[0][1]) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"specularReflectance\" value=\"" + str(specularReflectance[0][0]) + " " + str(specularReflectance[0][1]) + " " + str(specularReflectance[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"diffuseReflectance\" value=\"" + str(diffuseReflectance[0][0]) + " " + str(diffuseReflectance[0][1]) + " " + str(diffuseReflectance[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + " </bsdf>\n")

'''
Write the appropriate integrator
'''
def writeIntegrator(outFile):
    #Write the integrator########################################################################
    global integrator
    global integratorFrames
    activeIntegrator = cmds.optionMenu(integrator, query=True, value=True)
    activeSettings = integratorFrames[0]

    #Find the active integrator's settings frame layout
    for frame in integratorFrames:
        if cmds.frameLayout(frame, query=True, visible=True):
            activeSettings = frame

    if activeIntegrator=="Ambient_Occlusion" or activeIntegrator=="Ambient Occlusion":
        '''
        The order for this integrator is:
        0. intFieldGrp shadingSamples
        1. checkBox to use automatic ray length
        2. intFieldGrp rayLength (for manual rayLength)
        '''
        outFile.write(" <integrator type=\"ao\">\n")
        integratorSettings = cmds.frameLayout(activeSettings, query=True, childArray=True)

        sSamples = cmds.intFieldGrp(integratorSettings[0], query=True, value1=True)
        outFile.write("     <integer name=\"shadingSamples\" value=\"" + str(sSamples) + "\"/>\n")

        if cmds.checkBox(integratorSettings[1], query=True, value=True):
            outFile.write("     <integer name=\"rayLength\" value=\"" + str(-1) + "\"/>\n")
        else:
            rl = cmds.intFieldGrp(integratorSettings[2], query=True, value1=True)
            outFile.write("     <integer name=\"rayLength\" value=\"" + str(rl) + "\"/>\n")
    
    #Write DI settings
    elif activeIntegrator=="Direct_Illumination" or activeIntegrator=="Direct Illumination":
        '''
        The order for this integrator is:
        0. intFieldGrp shadingSamples
        1. checkBox to use separate samples for emitters and bsdfs
        2. intFieldGrp emitterSamples
        3. intFieldGrp bsdfSamples
        4. checkBox strictNormals
        5. checkBox hideEmitters
        '''
        outFile.write(" <integrator type=\"direct\">\n")
        integratorSettings = cmds.frameLayout(activeSettings, query=True, childArray=True)
        if cmds.checkBox(integratorSettings[1], query=True, value=True):
            eSamples = cmds.intFieldGrp(integratorSettings[2], query=True, value1=True)
            bSamples = cmds.intFieldGrp(integratorSettings[3], query=True, value1=True)
            outFile.write("     <integer name=\"emitterSamples\" value=\"" + str(eSamples) + "\"/>\n")
            outFile.write("     <integer name=\"bsdfSamples\" value=\"" + str(bSamples) + "\"/>\n")
        else:
            sSamples = cmds.intFieldGrp(integratorSettings[0], query=True, value1=True)
            outFile.write("     <integer name=\"shadingSamples\" value=\"" + str(sSamples) + "\"/>\n")

        if cmds.checkBox(integratorSettings[4], query=True, value=True):
            outFile.write("     <boolean name=\"strictNormals\" value=\"true\"/>\n")
        else:
            outFile.write("     <boolean name=\"strictNormals\" value=\"false\"/>\n")

        if cmds.checkBox(integratorSettings[5], query=True, value=True):
            outFile.write("     <boolean name=\"hideEmitters\" value=\"true\"/>\n")
        else:
            outFile.write("     <boolean name=\"hideEmitters\" value=\"false\"/>\n")

    #Write path tracer, volpaths settings
    elif activeIntegrator=="Path_Tracer" or activeIntegrator=="Volumetric_Path_Tracer" or activeIntegrator=="Simple_Volumetric_Path_Tracer" \
    or   activeIntegrator=="Path Tracer" or activeIntegrator=="Volumetric Path Tracer" or activeIntegrator=="Simple Volumetric Path Tracer":
        '''
        The order for this integrator is:
        0. checkBox to use infinite samples
        1. intFieldGrp maxDepth
        2. intFieldGrp rrDepth
        3. checkBox strictNormals
        4. checkBox hideEmitters
        '''
        if activeIntegrator=="Path_Tracer" or activeIntegrator=="Path Tracer":
            outFile.write(" <integrator type=\"path\">\n")
        elif activeIntegrator=="Volumetric_Path_Tracer" or activeIntegrator=="Volumetric Path Tracer":
            outFile.write(" <integrator type=\"volpath\">\n")
        else:
            outFile.write(" <integrator type=\"volpath_simple\">\n")

        integratorSettings = cmds.frameLayout(activeSettings, query=True, childArray=True)

        if cmds.checkBox(integratorSettings[0], query=True, value=True):
            outFile.write("     <integer name=\"maxDepth\" value=\"-1\"/>\n")
        else:
            maxDepth = cmds.intFieldGrp(integratorSettings[1], query=True, value1=True)
            outFile.write("     <integer name=\"maxDepth\" value=\"" + str(maxDepth) + "\"/>\n")

        rrDepth = cmds.intFieldGrp(integratorSettings[2], query=True, value1=True)
        outFile.write("     <integer name=\"rrDepth\" value=\"" + str(rrDepth) + "\"/>\n")            

        if cmds.checkBox(integratorSettings[3], query=True, value=True):
            outFile.write("     <boolean name=\"strictNormals\" value=\"true\"/>\n")
        else:
            outFile.write("     <boolean name=\"strictNormals\" value=\"false\"/>\n")

        if cmds.checkBox(integratorSettings[4], query=True, value=True):
            outFile.write("     <boolean name=\"hideEmitters\" value=\"true\"/>\n")
        else:
            outFile.write("     <boolean name=\"hideEmitters\" value=\"false\"/>\n")

    #Write bdpt
    elif activeIntegrator=="Bidirectional_Path_Tracer" or activeIntegrator=="Bidirectional Path Tracer":
        '''
        The order for this integrator is:
        0. checkBox to use infinite samples
        1. intFieldGrp maxDepth
        2. checkBox lightImage
        3. checkBox sampleDirect
        4. intFieldGrp rrDepth
        '''
        outFile.write(" <integrator type=\"bdpt\">\n")
        integratorSettings = cmds.frameLayout(activeSettings, query=True, childArray=True)

        if cmds.checkBox(integratorSettings[0], query=True, value=True):
            outFile.write("     <integer name=\"maxDepth\" value=\"-1\"/>\n")
        else:
            maxDepth = cmds.intFieldGrp(integratorSettings[1], query=True, value1=True)
            outFile.write("     <integer name=\"maxDepth\" value=\"" + str(maxDepth) + "\"/>\n")

        if cmds.checkBox(integratorSettings[2], query=True, value=True):
            outFile.write("     <boolean name=\"lightImage\" value=\"true\"/>\n")
        else:
            outFile.write("     <boolean name=\"lightImage\" value=\"false\"/>\n")

        if cmds.checkBox(integratorSettings[3], query=True, value=True):
            outFile.write("     <boolean name=\"sampleDirect\" value=\"true\"/>\n")
        else:
            outFile.write("     <boolean name=\"sampleDirect\" value=\"false\"/>\n")

        rrDepth = cmds.intFieldGrp(integratorSettings[4], query=True, value1=True)
        outFile.write("     <integer name=\"emitterSamples\" value=\"" + str(rrDepth) + "\"/>\n")    


    #Write photon mapper
    elif activeIntegrator=="Photon_Map" or activeIntegrator=="Photon Map":
        '''
        The order for this integrator is:
        0. intFieldGrp directSamples
        1. intFieldGrp glossySamples
        2. checkBox to use infinite depth
        3. intFieldGrp maxDepth
        4. intFieldGrp globalPhotons
        5. intFieldGrp causticPhotons
        6. intFieldGrp volumePhotons
        7. floatFieldGrp globalLookupRadius
        8. floatFieldGrp causticLookupRadius
        9. intFieldGrp lookupSize
        10. checkBox to use automatic granularity
        11. intFieldGrp granularity
        12. checkBox hideEmitters
        13. intFieldGrp rrDepth
        '''
        outFile.write(" <integrator type=\"photonmapper\">\n")
        integratorSettings = cmds.frameLayout(activeSettings, query=True, childArray=True)

        directSamples = cmds.intFieldGrp(integratorSettings[0], query=True, value1=True)
        outFile.write("     <integer name=\"directSamples\" value=\"" + str(directSamples) + "\"/>\n")

        glossySamples = cmds.intFieldGrp(integratorSettings[1], query=True, value1=True)
        outFile.write("     <integer name=\"glossySamples\" value=\"" + str(glossySamples) + "\"/>\n")

        if cmds.checkBox(integratorSettings[2], query=True, value=True):
            outFile.write("     <integer name=\"maxDepth\" value=\"-1\"/>\n")
        else:
            maxDepth = cmds.intFieldGrp(integratorSettings[3], query=True, value1=True)
            outFile.write("     <integer name=\"maxDepth\" value=\"" + str(maxDepth) + "\"/>\n")

        globalPhotons = cmds.intFieldGrp(integratorSettings[4], query=True, value1=True)
        outFile.write("     <integer name=\"globalPhotons\" value=\"" + str(globalPhotons) + "\"/>\n")

        causticPhotons = cmds.intFieldGrp(integratorSettings[5], query=True, value1=True)
        outFile.write("     <integer name=\"causticPhotons\" value=\"" + str(causticPhotons) + "\"/>\n")

        volumePhotons = cmds.intFieldGrp(integratorSettings[6], query=True, value1=True)
        outFile.write("     <integer name=\"volumePhotons\" value=\"" + str(volumePhotons) + "\"/>\n")

        globalLookupRadius = cmds.floatFieldGrp(integratorSettings[7], query=True, value1=True)
        outFile.write("     <float name=\"globalLookupRadius\" value=\"" + str(globalLookupRadius) + "\"/>\n")  

        causticLookupRadius = cmds.floatFieldGrp(integratorSettings[8], query=True, value1=True)
        outFile.write("     <float name=\"causticLookupRadius\" value=\"" + str(causticLookupRadius) + "\"/>\n")            

        lookupSize = cmds.intFieldGrp(integratorSettings[9], query=True, value1=True)
        outFile.write("     <integer name=\"lookupSize\" value=\"" + str(lookupSize) + "\"/>\n")

        if cmds.checkBox(integratorSettings[10], query=True, value=True):
            outFile.write("     <integer name=\"granularity\" value=\"0\"/>\n")
        else:
            granularity = cmds.intFieldGrp(integratorSettings[11], query=True, value1=True)
            outFile.write("     <integer name=\"granularity\" value=\"" + str(granularity) + "\"/>\n")

        if cmds.checkBox(integratorSettings[12], query=True, value=True):
            outFile.write("     <boolean name=\"hideEmitters\" value=\"true\"/>\n")
        else:
            outFile.write("     <boolean name=\"hideEmitters\" value=\"false\"/>\n")

        rrDepth = cmds.intFieldGrp(integratorSettings[13], query=True, value1=True)
        outFile.write("     <integer name=\"rrDepth\" value=\"" + str(rrDepth) + "\"/>\n")    

    #Write progressive photon mapper
    elif activeIntegrator=="Progressive_Photon_Map" or activeIntegrator=="Progressive Photon Map":
        '''
        The order for this integrator is:
        0. checkBox to use infinite depth
        1. intFieldGrp maxDepth
        2. intFieldGrp photonCount
        3. checkBox to use automatic initialRadius
        4. floatFieldGrp initialRadius
        5. floatFieldGrp alpha
        6. checkBox to use automatic granularity
        7. intFieldGrp granularity
        8. checkBox hideEmitters
        9. intFieldGrp rrDepth
        10. checkBox to use infinite maxPasses
        11. intFieldGrp maxPasses
        '''
        outFile.write(" <integrator type=\"ppm\">\n")
        integratorSettings = cmds.frameLayout(activeSettings, query=True, childArray=True)

        if cmds.checkBox(integratorSettings[0], query=True, value=True):
            outFile.write("     <integer name=\"maxDepth\" value=\"-1\"/>\n")
        else:
            maxDepth = cmds.intFieldGrp(integratorSettings[1], query=True, value1=True)
            outFile.write("     <integer name=\"maxDepth\" value=\"" + str(maxDepth) + "\"/>\n")

        photonCount = cmds.intFieldGrp(integratorSettings[2], query=True, value1=True)
        outFile.write("     <integer name=\"photonCount\" value=\"" + str(photonCount) + "\"/>\n")

        if cmds.checkBox(integratorSettings[3], query=True, value=True):
            outFile.write("     <float name=\"initialRadius\" value=\"0\"/>\n")
        else:
            initialRadius = cmds.floatFieldGrp(integratorSettings[4], query=True, value1=True)
            outFile.write("     <float name=\"initialRadius\" value=\"" + str(initialRadius) + "\"/>\n")

        alpha = cmds.floatFieldGrp(integratorSettings[5], query=True, value1=True)
        outFile.write("     <float name=\"alpha\" value=\"" + str(alpha) + "\"/>\n") 

        if cmds.checkBox(integratorSettings[6], query=True, value=True):
            outFile.write("     <integer name=\"granularity\" value=\"0\"/>\n")
        else:
            granularity = cmds.intFieldGrp(integratorSettings[7], query=True, value1=True)
            outFile.write("     <integer name=\"granularity\" value=\"" + str(granularity) + "\"/>\n")

        if cmds.checkBox(integratorSettings[8], query=True, value=True):
            outFile.write("     <boolean name=\"lightImage\" value=\"true\"/>\n")
        else:
            outFile.write("     <boolean name=\"lightImage\" value=\"false\"/>\n")
       
        rrDepth = cmds.intFieldGrp(integratorSettings[9], query=True, value1=True)
        outFile.write("     <integer name=\"rrDepth\" value=\"" + str(rrDepth) + "\"/>\n")    

        if cmds.checkBox(integratorSettings[10], query=True, value=True):
            outFile.write("     <integer name=\"maxPasses\" value=\"-1\"/>\n")
        else:
            maxPasses = cmds.intFieldGrp(integratorSettings[11], query=True, value1=True)
            outFile.write("     <integer name=\"maxPasses\" value=\"" + str(maxPasses) + "\"/>\n")

    #Write sppm
    elif activeIntegrator=="Stochastic_Progressive_Photon_Map" or activeIntegrator=="Stochastic Progressive Photon Map":
        '''
        The order for this integrator is:
        0. checkBox to use infinite depth
        1. intFieldGrp maxDepth
        2. intFieldGrp photonCount
        3. checkBox to use automatic initialRadius
        4. floatFieldGrp initialRadius
        5. floatFieldGrp alpha
        6. checkBox to use automatic granularity
        7. intFieldGrp granularity
        8. checkBox hideEmitters
        9. intFieldGrp rrDepth
        10. checkBox to use infinite maxPasses
        11. intFieldGrp maxPasses
        '''
        outFile.write(" <integrator type=\"sppm\">\n")
        integratorSettings = cmds.frameLayout(activeSettings, query=True, childArray=True)

        if cmds.checkBox(integratorSettings[0], query=True, value=True):
            outFile.write("     <integer name=\"maxDepth\" value=\"-1\"/>\n")
        else:
            maxDepth = cmds.intFieldGrp(integratorSettings[1], query=True, value1=True)
            outFile.write("     <integer name=\"maxDepth\" value=\"" + str(maxDepth) + "\"/>\n")

        photonCount = cmds.intFieldGrp(integratorSettings[2], query=True, value1=True)
        outFile.write("     <integer name=\"photonCount\" value=\"" + str(photonCount) + "\"/>\n")

        if cmds.checkBox(integratorSettings[3], query=True, value=True):
            outFile.write("     <float name=\"initialRadius\" value=\"0\"/>\n")
        else:
            initialRadius = cmds.floatFieldGrp(integratorSettings[4], query=True, value1=True)
            outFile.write("     <float name=\"initialRadius\" value=\"" + str(initialRadius) + "\"/>\n")

        alpha = cmds.floatFieldGrp(integratorSettings[5], query=True, value1=True)
        outFile.write("     <float name=\"alpha\" value=\"" + str(alpha) + "\"/>\n") 

        if cmds.checkBox(integratorSettings[6], query=True, value=True):
            outFile.write("     <integer name=\"granularity\" value=\"0\"/>\n")
        else:
            granularity = cmds.intFieldGrp(integratorSettings[7], query=True, value1=True)
            outFile.write("     <integer name=\"granularity\" value=\"" + str(granularity) + "\"/>\n")

        if cmds.checkBox(integratorSettings[8], query=True, value=True):
            outFile.write("     <boolean name=\"hideEmitters\" value=\"true\"/>\n")
        else:
            outFile.write("     <boolean name=\"hideEmitters\" value=\"false\"/>\n")
        
        rrDepth = cmds.intFieldGrp(integratorSettings[9], query=True, value1=True)
        outFile.write("     <integer name=\"rrDepth\" value=\"" + str(rrDepth) + "\"/>\n")    

        if cmds.checkBox(integratorSettings[10], query=True, value=True):
            outFile.write("     <integer name=\"maxPasses\" value=\"-1\"/>\n")
        else:
            maxPasses = cmds.intFieldGrp(integratorSettings[11], query=True, value1=True)
            outFile.write("     <integer name=\"maxPasses\" value=\"" + str(maxPasses) + "\"/>\n")

    #Write pssmlt
    elif activeIntegrator=="Primary_Sample_Space_Metropolis_Light_Transport" or activeIntegrator=="Primary Sample Space Metropolis Light Transport":
        '''
        The order for this integrator is:
        0. checkBox bidirectional
        1. checkBox to use infinite depth
        2. intFieldGrp maxDepth
        3. checkBox to use automatic directSamples
        4. intFieldGrp directSamples
        5. intFieldGrp luminanceSamples
        6. checkBox twoStage
        7. checkBox hideEmitters
        8. intFieldGrp rrDepth
        9. floatFieldGrp pLarge
        '''
        outFile.write(" <integrator type=\"pssmlt\">\n")
        integratorSettings = cmds.frameLayout(activeSettings, query=True, childArray=True)

        if cmds.checkBox(integratorSettings[0], query=True, value=True):
            outFile.write("     <boolean name=\"bidirectional\" value=\"true\"/>\n")
        else:
            outFile.write("     <boolean name=\"bidirectional\" value=\"false\"/>\n")

        if cmds.checkBox(integratorSettings[1], query=True, value=True):
            outFile.write("     <integer name=\"maxDepth\" value=\"-1\"/>\n")
        else:
            maxDepth = cmds.intFieldGrp(integratorSettings[2], query=True, value1=True)
            outFile.write("     <integer name=\"maxDepth\" value=\"" + str(maxDepth) + "\"/>\n")

        if cmds.checkBox(integratorSettings[3], query=True, value=True):
            outFile.write("     <integer name=\"directSamples\" value=\"-1\"/>\n")
        else:
            directSamples = cmds.intFieldGrp(integratorSettings[4], query=True, value1=True)
            outFile.write("     <integer name=\"directSamples\" value=\"" + str(directSamples) + "\"/>\n")

        luminanceSamples = cmds.intFieldGrp(integratorSettings[5], query=True, value1=True)
        outFile.write("     <integer name=\"luminanceSamples\" value=\"" + str(luminanceSamples) + "\"/>\n")

        if cmds.checkBox(integratorSettings[6], query=True, value=True):
            outFile.write("     <boolean name=\"twoStage\" value=\"true\"/>\n")
        else:
            outFile.write("     <boolean name=\"twoStage\" value=\"false\"/>\n")

        if cmds.checkBox(integratorSettings[7], query=True, value=True):
            outFile.write("     <boolean name=\"hideEmitters\" value=\"true\"/>\n")
        else:
            outFile.write("     <boolean name=\"hideEmitters\" value=\"false\"/>\n")

        rrDepth = cmds.intFieldGrp(integratorSettings[8], query=True, value1=True)
        outFile.write("     <integer name=\"rrDepth\" value=\"" + str(rrDepth) + "\"/>\n")

        pLarge = cmds.floatFieldGrp(integratorSettings[9], query=True, value1=True)
        outFile.write("     <float name=\"pLarge\" value=\"" + str(pLarge) + "\"/>\n")

    #Write psmlt
    elif activeIntegrator=="Path_Space_Metropolis_Light_Transport" or activeIntegrator=="Path Space Metropolis Light Transport":
        '''
        The order for this integrator is:
        0. checkBox to use infinite depth
        1. intFieldGrp maxDepth
        2. checkBox to use automatic directSamples
        3. intFieldGrp directSamples
        4. intFieldGrp luminanceSamples
        5. checkBox twoStage
        6. checkBox bidirectionalMutation
        7. checkBox lensPerturbation
        8. checkBox multiChainPerturbation
        9. checkBox causticPerturbation
        10. checkBox manifoldPerturbation
        11. checkBox hideEmitters
        12. floatFieldGrp lambda
        '''
        outFile.write(" <integrator type=\"mlt\">\n")
        integratorSettings = cmds.frameLayout(activeSettings, query=True, childArray=True)

        if cmds.checkBox(integratorSettings[0], query=True, value=True):
            outFile.write("     <integer name=\"maxDepth\" value=\"-1\"/>\n")
        else:
            maxDepth = cmds.intFieldGrp(integratorSettings[1], query=True, value1=True)
            outFile.write("     <integer name=\"maxDepth\" value=\"" + str(maxDepth) + "\"/>\n")

        if cmds.checkBox(integratorSettings[2], query=True, value=True):
            outFile.write("     <integer name=\"directSamples\" value=\"-1\"/>\n")
        else:
            directSamples = cmds.intFieldGrp(integratorSettings[3], query=True, value1=True)
            outFile.write("     <integer name=\"directSamples\" value=\"" + str(directSamples) + "\"/>\n")

        luminanceSamples = cmds.intFieldGrp(integratorSettings[4], query=True, value1=True)
        outFile.write("     <integer name=\"luminanceSamples\" value=\"" + str(luminanceSamples) + "\"/>\n")

        if cmds.checkBox(integratorSettings[5], query=True, value=True):
            outFile.write("     <boolean name=\"twoStage\" value=\"true\"/>\n")
        else:
            outFile.write("     <boolean name=\"twoStage\" value=\"false\"/>\n")

        if cmds.checkBox(integratorSettings[6], query=True, value=True):
            outFile.write("     <boolean name=\"bidirectionalMutation\" value=\"true\"/>\n")
        else:
            outFile.write("     <boolean name=\"bidirectionalMutation\" value=\"false\"/>\n")

        if cmds.checkBox(integratorSettings[7], query=True, value=True):
            outFile.write("     <boolean name=\"lensPerturbation\" value=\"true\"/>\n")
        else:
            outFile.write("     <boolean name=\"lensPerturbation\" value=\"false\"/>\n")

        if cmds.checkBox(integratorSettings[8], query=True, value=True):
            outFile.write("     <boolean name=\"multiChainPerturbation\" value=\"true\"/>\n")
        else:
            outFile.write("     <boolean name=\"multiChainPerturbation\" value=\"false\"/>\n")

        if cmds.checkBox(integratorSettings[9], query=True, value=True):
            outFile.write("     <boolean name=\"causticPerturbation\" value=\"true\"/>\n")
        else:
            outFile.write("     <boolean name=\"causticPerturbation\" value=\"false\"/>\n")

        if cmds.checkBox(integratorSettings[9], query=True, value=True):
            outFile.write("     <boolean name=\"manifoldPerturbation\" value=\"true\"/>\n")
        else:
            outFile.write("     <boolean name=\"manifoldPerturbation\" value=\"false\"/>\n")

        if cmds.checkBox(integratorSettings[11], query=True, value=True):
            outFile.write("     <boolean name=\"hideEmitters\" value=\"true\"/>\n")
        else:
            outFile.write("     <boolean name=\"hideEmitters\" value=\"false\"/>\n")

        mtsLambda = cmds.floatFieldGrp(integratorSettings[12], query=True, value1=True)
        outFile.write("     <float name=\"lambda\" value=\"" + str(mtsLambda) + "\"/>\n")

    #Write erpt
    elif activeIntegrator=="Energy_Redistribution_Path_Tracer" or activeIntegrator=="Energy Redistribution Path Tracer":
        '''
        The order for this integrator is:
        0. checkBox to use infinite depth
        1. intFieldGrp maxDepth
        2. floatFieldGrp numChains
        3. checkBox to use maxChains
        4. floatFieldGrp maxChains
        5. checkBox to use automatic directSamples
        6. intFieldGrp directSamples
        7. checkBox lensPerturbation
        8. checkBox multiChainPerturbation
        9. checkBox causticPerturbation
        10. checkBox manifoldPerturbation
        11. checkBox hideEmitters
        12. floatFieldGrp lambda
        '''
        outFile.write(" <integrator type=\"mlt\">\n")
        integratorSettings = cmds.frameLayout(activeSettings, query=True, childArray=True)

        if cmds.checkBox(integratorSettings[0], query=True, value=True):
            outFile.write("     <integer name=\"maxDepth\" value=\"-1\"/>\n")
        else:
            maxDepth = cmds.intFieldGrp(integratorSettings[1], query=True, value1=True)
            outFile.write("     <integer name=\"maxDepth\" value=\"" + str(maxDepth) + "\"/>\n")

        numChains = cmds.floatFieldGrp(integratorSettings[2], query=True, value1=True)
        outFile.write("     <float name=\"numChains\" value=\"" + str(numChains) + "\"/>\n")

        if not cmds.checkBox(integratorSettings[3], query=True, value=True):
            outFile.write("     <integer name=\"maxChains\" value=\"0\"/>\n")
        else:
            maxChains = cmds.floatFieldGrp(integratorSettings[4], query=True, value1=True)
            outFile.write("     <integer name=\"maxChains\" value=\"" + str(maxChains) + "\"/>\n")

        if cmds.checkBox(integratorSettings[5], query=True, value=True):
            outFile.write("     <integer name=\"directSamples\" value=\"-1\"/>\n")
        else:
            directSamples = cmds.intFieldGrp(integratorSettings[6], query=True, value1=True)
            outFile.write("     <integer name=\"directSamples\" value=\"" + str(directSamples) + "\"/>\n")

        if cmds.checkBox(integratorSettings[7], query=True, value=True):
            outFile.write("     <boolean name=\"lensPerturbation\" value=\"true\"/>\n")
        else:
            outFile.write("     <boolean name=\"lensPerturbation\" value=\"false\"/>\n")

        if cmds.checkBox(integratorSettings[8], query=True, value=True):
            outFile.write("     <boolean name=\"multiChainPerturbation\" value=\"true\"/>\n")
        else:
            outFile.write("     <boolean name=\"multiChainPerturbation\" value=\"false\"/>\n")

        if cmds.checkBox(integratorSettings[9], query=True, value=True):
            outFile.write("     <boolean name=\"causticPerturbation\" value=\"true\"/>\n")
        else:
            outFile.write("     <boolean name=\"causticPerturbation\" value=\"false\"/>\n")

        if cmds.checkBox(integratorSettings[10], query=True, value=True):
            outFile.write("     <boolean name=\"manifoldPerturbation\" value=\"true\"/>\n")
        else:
            outFile.write("     <boolean name=\"manifoldPerturbation\" value=\"false\"/>\n")

        if cmds.checkBox(integratorSettings[11], query=True, value=True):
            outFile.write("     <boolean name=\"hideEmitters\" value=\"true\"/>\n")
        else:
            outFile.write("     <boolean name=\"hideEmitters\" value=\"false\"/>\n")

        mtsLambda = cmds.floatFieldGrp(integratorSettings[12], query=True, value1=True)
        outFile.write("     <float name=\"lambda\" value=\"" + str(mtsLambda) + "\"/>\n")\

    #Write ptracer
    elif activeIntegrator=="Adjoint_Particle_Tracer" or activeIntegrator=="Adjoint Particle Tracer":
        '''
        The order for this integrator is:
        0. checkBox to use infinite depth
        1. intFieldGrp maxDepth
        2. intFieldGrp rrDepth
        3. intFieldGrp granularity
        4. checkBox bruteForce
        5. checkBox hideEmitters
        '''
        outFile.write(" <integrator type=\"mlt\">\n")
        integratorSettings = cmds.frameLayout(activeSettings, query=True, childArray=True)

        if cmds.checkBox(integratorSettings[0], query=True, value=True):
            outFile.write("     <integer name=\"maxDepth\" value=\"-1\"/>\n")
        else:
            maxDepth = cmds.intFieldGrp(integratorSettings[1], query=True, value1=True)
            outFile.write("     <integer name=\"maxDepth\" value=\"" + str(maxDepth) + "\"/>\n")

        rrDepth = cmds.intFieldGrp(integratorSettings[2], query=True, value1=True)
        outFile.write("     <integer name=\"rrDepth\" value=\"" + str(rrDepth) + "\"/>\n")

        granularity = cmds.intFieldGrp(integratorSettings[3], query=True, value1=True)
        outFile.write("     <integer name=\"granularity\" value=\"" + str(granularity) + "\"/>\n")

        if cmds.checkBox(integratorSettings[4], query=True, value=True):
            outFile.write("     <boolean name=\"bruteForce\" value=\"true\"/>\n")
        else:
            outFile.write("     <boolean name=\"bruteForce\" value=\"false\"/>\n")

        if cmds.checkBox(integratorSettings[5], query=True, value=True):
            outFile.write("     <boolean name=\"hideEmitters\" value=\"true\"/>\n")
        else:
            outFile.write("     <boolean name=\"hideEmitters\" value=\"false\"/>\n")

    #Write vpl
    elif activeIntegrator=="Virtual_Point_Lights" or activeIntegrator=="Virtual Point Lights":
        print "vpl"

    outFile.write(" </integrator>\n\n\n")
    #############################################################################################

'''
Write image sample generator
'''
def writeSampler(outFile):
    global samplerFrames
    global sampler

    activeSampler = cmds.optionMenu(sampler, query=True, value=True)
    activeSettings = samplerFrames[0]

    for frame in samplerFrames:
        if cmds.frameLayout(frame, query=True, visible=True):
            activeSettings = frame

    if activeSampler=="Independent_Sampler" or activeSampler=="Independent Sampler":
        samplerSettings = cmds.frameLayout(activeSettings, query=True, childArray=True)
        outFile.write("         <sampler type=\"independent\">\n")

        sampleCount = cmds.intFieldGrp(samplerSettings[0], query=True, value1=True)
        outFile.write("             <integer name=\"sampleCount\" value=\"" + str(sampleCount) + "\"/>\n")

    elif activeSampler=="Stratified_Sampler" or activeSampler=="Stratified Sampler":
        samplerSettings = cmds.frameLayout(activeSettings, query=True, childArray=True)
        outFile.write("         <sampler type=\"stratified\">\n")

        sampleCount = cmds.intFieldGrp(samplerSettings[0], query=True, value1=True)
        outFile.write("             <integer name=\"sampleCount\" value=\"" + str(sampleCount) + "\"/>\n")

        dimension = cmds.intFieldGrp(samplerSettings[1], query=True, value1=True)
        outFile.write("             <integer name=\"dimension\" value=\"" + str(dimension) + "\"/>\n")

    elif activeSampler=="Low_Discrepancy_Sampler" or activeSampler=="Low_Discrepancy Sampler":
        samplerSettings = cmds.frameLayout(activeSettings, query=True, childArray=True)
        outFile.write("         <sampler type=\"ldsampler\">\n")

        sampleCount = cmds.intFieldGrp(samplerSettings[0], query=True, value1=True)
        outFile.write("             <integer name=\"sampleCount\" value=\"" + str(sampleCount) + "\"/>\n")

        dimension = cmds.intFieldGrp(samplerSettings[1], query=True, value1=True)
        outFile.write("             <integer name=\"dimension\" value=\"" + str(dimension) + "\"/>\n")

    elif activeSampler=="Halton_QMC_Sampler" or activeSampler=="Halton QMC Sampler":
        samplerSettings = cmds.frameLayout(activeSettings, query=True, childArray=True)
        outFile.write("         <sampler type=\"halton\">\n")

        sampleCount = cmds.intFieldGrp(samplerSettings[0], query=True, value1=True)
        outFile.write("             <integer name=\"sampleCount\" value=\"" + str(sampleCount) + "\"/>\n")

        scramble = cmds.intFieldGrp(samplerSettings[1], query=True, value1=True)
        outFile.write("             <integer name=\"scramble\" value=\"" + str(scramble) + "\"/>\n")

    elif activeSampler=="Hammersley_QMC_Sampler" or activeSampler=="Hammersley QMC Sampler":
        samplerSettings = cmds.frameLayout(activeSettings, query=True, childArray=True)
        outFile.write("         <sampler type=\"hammersley\">\n")

        sampleCount = cmds.intFieldGrp(samplerSettings[0], query=True, value1=True)
        outFile.write("             <integer name=\"sampleCount\" value=\"" + str(sampleCount) + "\"/>\n")

        scramble = cmds.intFieldGrp(samplerSettings[1], query=True, value1=True)
        outFile.write("             <integer name=\"scramble\" value=\"" + str(scramble) + "\"/>\n")

    elif activeSampler=="Sobol_QMC_Sampler" or activeSampler=="Sobol QMC Sampler":
        samplerSettings = cmds.frameLayout(activeSettings, query=True, childArray=True)
        outFile.write("         <sampler type=\"sobol\">\n")

        sampleCount = cmds.intFieldGrp(samplerSettings[0], query=True, value1=True)
        outFile.write("             <integer name=\"sampleCount\" value=\"" + str(sampleCount) + "\"/>\n")

        scramble = cmds.intFieldGrp(samplerSettings[1], query=True, value1=True)
        outFile.write("             <integer name=\"scramble\" value=\"" + str(scramble) + "\"/>\n")

    outFile.write("         </sampler>\n")
    outFile.write("\n")

'''
Write sensor, which include camera, image sampler, and film
'''
def writeSensor(outFile):
    outFile.write(" <!-- Camera -->\n")

    cams = cmds.ls(type="camera")
    rCamShape = ""
    for cam in cams:
        isRenderable = cmds.getAttr(cam+".renderable")
        if isRenderable:
            rCamShape = cam
            break
    
    rGroup = cmds.listConnections(rCamShape)[0]

    rGroupRels = cmds.listRelatives(rGroup)

    rCam = rGroupRels[0]
    rAim = rGroupRels[1]
    rUp  = rGroupRels[2]

    camPos = cmds.getAttr(rCam+".translate")[0]
    camAim = cmds.getAttr(rAim+".translate")[0]
    camUp  = cmds.getAttr(rUp+".translate")[0]

    #Type
    camType="perspective"
    if cmds.getAttr(rCamShape+".depthOfField"):
        camType="thinlens"

    #dof stuff
    apertureRadius = 1
    focusDistance = 1
    if camType=="thinlens":
        apertureRadius = cmds.getAttr(rCamShape+".focusRegionScale")
        focusDistance = cmds.getAttr(rCamShape+".focusDistance")

    #fov
    fov = cmds.camera(rCamShape, query=True, horizontalFieldOfView=True)

    #near clip plane
    nearClip = cmds.getAttr(rCamShape+".nearClipPlane")

    outFile.write(" <sensor type=\"" + camType + "\">\n")
    if camType=="thinlens":
        outFile.write("         <float name=\"apertureRadius\" value=\"" + str(apertureRadius) + "\"/>\n")
        outFile.write("         <float name=\"focusDistance\" value=\"" + str(focusDistance) + "\"/>\n")    
    outFile.write("         <float name=\"fov\" value=\"" + str(fov) + "\"/>\n")
    outFile.write("         <string name=\"fovAxis\" value=\"x\"/>\n")
    outFile.write("         <float name=\"nearClip\" value=\"" + str(nearClip) + "\"/>\n")
    outFile.write("         <transform name=\"toWorld\">\n")
    outFile.write("             <lookat target=\"" + str(camAim[0]) + " " + str(camAim[1]) + " " + str(camAim[2]) + "\" origin=\"" + str(camPos[0]) + " " + str(camPos[1]) + " " + str(camPos[2]) + "\" up=\"" + str(camUp[0]-camPos[0]) + " " + str(camUp[1]-camPos[1]) + " " + str(camUp[2]-camPos[2]) + "\"/>\n")
    outFile.write("         </transform>\n")
    outFile.write("\n")
    
    #write sampler generator:
    writeSampler(outFile)

    #Film
    outFile.write("     <film type=\"ldrfilm\">\n")
    
    #Resolution
    imageWidth = cmds.getAttr("defaultResolution.width")
    imageHeight = cmds.getAttr("defaultResolution.height")
    outFile.write("         <integer name=\"height\" value=\"" + str(imageHeight) + "\"/>\n")
    outFile.write("         <integer name=\"width\" value=\"" + str(imageWidth) + "\"/>\n")

    #Filter
    global rfilter
    rfilterValue = cmds.optionMenu(rfilter, query=True, value=True)
    rfilterString = ""
    if rfilterValue=="Box_filter" or rfilterValue=="Box filter":
        rfilterString = "box"
    if rfilterValue=="Tent_filter" or rfilterValue=="Tent filter":
        rfilterString = "tent"
    if rfilterValue=="Gaussian_filter" or rfilterValue=="Gaussian filter":
        rfilterString = "gaussian"
    if rfilterValue=="Mitchell_Netravali_filter" or rfilterValue=="Mitchell-Netravali filter":
        rfilterString = "mitchell"
    if rfilterValue=="Catmull_Rom_filter" or rfilterValue=="Catmull-Rom filter":
        rfilterString = "catmullrom"
    if rfilterValue=="Lanczos_filter" or rfilterValue=="Lanczos filter":
        rfilterString = "lanczos"

    outFile.write("         <rfilter type=\"" + rfilterString + "\"/>\n")
    outFile.write("         <boolean name=\"banner\" value=\"false\"/>\n")
    outFile.write("     </film>\n")
    outFile.write(" </sensor>\n")
    outFile.write("\n")

'''
Write lights
'''
def writeLights(outFile):
    lights = cmds.ls(type="light")
    sunskyLights = cmds.ls(type="MitsubaSunsky")
    areaLights = cmds.ls(type="MitsubaEnvironmentLight")

    if sunskyLights and areaLights or sunskyLights and len(sunskyLights)>1 or areaLights and len(areaLights)>1:
        print "Cannot specify more than one area light (MitsubaSunsky and MitsubaEnvironmentLight)"
        # print "Defaulting to constant environment emitter"
        # outFile.write(" <emitter type=\"constant\"/>\n")

    for light in lights:
        lightType = cmds.nodeType(light)
        if lightType == "directionalLight":
            intensity = cmds.getAttr(light+".intensity")
            color = cmds.getAttr(light+".color")[0]
            irradiance = [0,0,0]
            for i in range(3):
                irradiance[i] = intensity*color[i]
            matrix = cmds.getAttr(light+".worldMatrix")
            lightDir = [-matrix[8],-matrix[9],-matrix[10]]
            outFile.write(" <emitter type=\"directional\">\n")
            outFile.write("     <vector name=\"direction\" x=\"" + str(lightDir[0]) + "\" y=\"" + str(lightDir[1]) + "\" z=\"" + str(lightDir[2]) + "\"/>\n")
            outFile.write("     <srgb name=\"irradiance\" value=\"" + str(irradiance[0]) + " " + str(irradiance[1]) + " " + str(irradiance[2]) + "\"/>\n")
            outFile.write(" </emitter>\n")

    #Sunsky light
    if sunskyLights:
        sunsky = sunskyLights[0]
        sun = cmds.getAttr(sunsky+".useSun")
        sky = cmds.getAttr(sunsky+".useSky")
        if sun and sky:
            outFile.write(" <emitter type=\"sunsky\">\n")
        elif sun:
            outFile.write(" <emitter type=\"sun\">\n")
        elif sky:
            outFile.write(" <emitter type=\"sky\">\n")
        else:
            print "Must use either sun or sky, defaulting to sunsky"
            outFile.write(" <emitter type=\"sunsky\">\n")

        turbidity = cmds.getAttr(sunsky+".turbidity")
        albedo = cmds.getAttr(sunsky+".albedo")
        date = cmds.getAttr(sunsky+".date")
        time = cmds.getAttr(sunsky+".time")
        latitude = cmds.getAttr(sunsky+".latitude")
        longitude = cmds.getAttr(sunsky+".longitude")
        timezone = cmds.getAttr(sunsky+".timezone")
        stretch = cmds.getAttr(sunsky+".stretch")
        resolution = cmds.getAttr(sunsky+".resolution")
        sunScale = cmds.getAttr(sunsky+".sunScale")
        skyScale = cmds.getAttr(sunsky+".skyScale")
        sunRadiusScale = cmds.getAttr(sunsky+".sunRadiusScale")

        outFile.write("     <float name=\"turbidity\" value=\"" + str(turbidity) + "\"/>\n")
        outFile.write("     <srgb name=\"albedo\" value=\"" + str(albedo[0][0]) + " " + str(albedo[0][1]) + " " + str(albedo[0][2]) + "\"/>\n")
        outFile.write("     <integer name=\"year\" value=\"" + str(date[0][0]) + "\"/>\n")
        outFile.write("     <integer name=\"month\" value=\"" + str(date[0][1]) + "\"/>\n")
        outFile.write("     <integer name=\"day\" value=\"" + str(date[0][2]) + "\"/>\n")
        outFile.write("     <float name=\"hour\" value=\"" + str(time[0][0]) + "\"/>\n")
        outFile.write("     <float name=\"minute\" value=\"" + str(time[0][1]) + "\"/>\n")
        outFile.write("     <float name=\"second\" value=\"" + str(time[0][2]) + "\"/>\n")
        outFile.write("     <float name=\"latitude\" value=\"" + str(latitude) + "\"/>\n")
        outFile.write("     <float name=\"longitude\" value=\"" + str(longitude) + "\"/>\n")
        outFile.write("     <float name=\"timezone\" value=\"" + str(timezone) + "\"/>\n")
        outFile.write("     <float name=\"stretch\" value=\"" + str(stretch) + "\"/>\n")
        outFile.write("     <integer name=\"resolutionX\" value=\"" + str(resolution[0][1]) + "\"/>\n")
        outFile.write("     <integer name=\"resolutionY\" value=\"" + str(resolution[0][1]) + "\"/>\n")
        outFile.write("     <float name=\"sunScale\" value=\"" + str(sunScale) + "\"/>\n")
        outFile.write("     <float name=\"skyScale\" value=\"" + str(skyScale) + "\"/>\n")
        outFile.write("     <float name=\"sunRadiusScale\" value=\"" + str(sunRadiusScale) + "\"/>\n")

        outFile.write(" </emitter>\n")

    #Area lights
    if areaLights:
        envmap = areaLights[0]
        connections = cmds.listConnections(envmap, plugs=False, c=True)
        fileName = ""
        hasFile = False
        correctFormat = True

        if connections:
            for i in range(len(connections)):
                connection = connections[i]
                if connection == envmap+".source":
                    inConnection = connections[i+1]
                    if cmds.nodeType(inConnection) == "file":
                        fileName = cmds.getAttr(inConnection+".fileTextureName")
                        if fileName:
                            extension = fileName[len(fileName)-3:len(fileName)]
                            if extension == "hdr" or extension == "exr":
                                hasFile = True
                            else:
                                print "file must be hdr or exr"
                                correctFormat = False
                        else:
                            print "Please supply a fileName if you plan to use an environment map"
                            correctFormat = False
                    else:
                        print "Source can only be an image file"
                        correctFormat = False
        
        if correctFormat:
            if hasFile:
                scale = cmds.getAttr(envmap+".scale")
                gamma = cmds.getAttr(envmap+".gamma")
                cache = cmds.getAttr(envmap+".cache")
                samplingWeight = cmds.getAttr(envmap+".samplingWeight")

                outFile.write(" <emitter type=\"envmap\">\n")
                outFile.write("     <string name=\"filename\" value=\"" + fileName + "\"/>\n")
                outFile.write("     <float name=\"scale\" value=\"" + str(scale) + "\"/>\n")
                outFile.write("     <float name=\"gamma\" value=\"" + str(gamma) + "\"/>\n")
                if cache:
                    outFile.write("     <boolean name=\"cache\" value=\"true\"/>\n")
                else:
                    outFile.write("     <boolean name=\"cache\" value=\"false\"/>\n")

                outFile.write("     <float name=\"samplingWeight\" value=\"" + str(samplingWeight) + "\"/>\n")
                outFile.write(" </emitter>\n")
            else:
                radiance = cmds.getAttr(envmap+".source")
                samplingWeight = cmds.getAttr(envmap+".samplingWeight")
                
                outFile.write(" <emitter type=\"constant\">\n")
                outFile.write("     <srgb name=\"radiance\" value=\"" + str(radiance[0][0]) + " " + str(radiance[0][1]) + " " + str(radiance[0][2]) + "\"/>\n")
                outFile.write("     <float name=\"samplingWeight\" value=\"" + str(samplingWeight) + "\"/>\n")
                outFile.write(" </emitter>\n")

    outFile.write("\n")
    outFile.write("<!-- End of lights -->")
    outFile.write("\n\n\n")


def writeGeometryAndMaterials(outFile, cwd):
    transforms = cmds.ls(type="transform")
    geoms = []

    for transform in transforms:
        rels = cmds.listRelatives(transform)
        if rels:
            for rel in rels:
                if cmds.nodeType(rel)=="mesh":
                    visible = cmds.getAttr(transform+".visibility")
                    if cmds.attributeQuery("intermediateObject", node=transform, exists=True):
                        visible = visible and not cmds.getAttr(transform+".intermediateObject")
                    if cmds.attributeQuery("overrideEnabled", node=transform, exists=True):
                        visible = visible and cmds.getAttr(transform+".overrideVisibility")
                    if visible:
                        geoms.append(transform)

    #Write the material for each piece of geometry in the scene
    writtenMaterials = []
    for geom in geoms:
        material = getShader(geom)          #Gets the user define names of the shader
        if cmds.nodeType(material) in materialNodeTypes:
            if material not in writtenMaterials:
                if "twosided" in cmds.listAttr(material) and cmds.getAttr(material+".twosided"):
                    outFile.write("<bsdf type=\"twosided\" id=\"" + material + "\">\n")
                    writeShader(material, material+"InnerMaterial", outFile, "    ")
                    outFile.write("</bsdf>\n")
                else:
                    writeShader(material, material, outFile, "")  #Write the shader to the xml file
                writtenMaterials.append(material)
        
    outFile.write("\n")
    outFile.write("<!-- End of materials -->")
    outFile.write("\n\n\n")

    objFiles = []

    #Write each piece of geometry
    for geom in geoms:
        shader = getShader(geom)
        if cmds.nodeType(shader) in materialNodeTypes:
            output = cwd+"/scenes/"+geom+".obj"
            cmds.select(geom)
            objFiles.append(cmds.file(output, op=True, typ="OBJexport", options="groups=1;ptgroups=1;materials=0;smoothing=1;normals=1", exportSelected=True, force=True))
            outFile.write("    <shape type=\"obj\">\n")
            outFile.write("        <string name=\"filename\" value=\"" + geom + ".obj\"/>\n")
            outFile.write("        <ref id=\"" + shader + "\"/>\n")
            
            #check for a homogeneous material
            #this checks if there is a homogeneous medium, and returns the attribute that it
            #is connected to if there is one
            connections = cmds.listConnections(shader, type="HomogeneousParticipatingMedium", connections=True)
            #We want to make sure it is connected to the ".material" attribute
            hasMedium = False
            medium = ""
            if connections and connections[0]==shader+".material":
                hasMedium = True
                medium = connections[1]
            if hasMedium:
                writeMedium(medium, outFile, "    ")

            outFile.write("    </shape>\n\n")

    outFile.write("<!-- End of geometry -->")
    outFile.write("\n\n\n")
    return objFiles

'''
This registers a mel command to render with Mitsuba
'''
class mitsubaForMaya(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)

    # Invoked when the command is run.
    def doIt(self,argList):
        print "Rendering with Mitsuba..."
        
        #Save the user's selection
        userSelection = cmds.ls(sl=True)
        
        #Get the cwd
        cwd = cmds.workspace(q=True, fn=True)
        # print cwd

        ################################################################################
        #Mitsuba Scene Output###########################################################
        ################################################################################
        
        outFileName = cwd + "/scenes/temporary.xml"
        
        #Try to do animation jesus
        if cmds.getAttr("defaultRenderGlobals.animation"):
            startFrame = cmds.getAttr("defaultRenderGlobals.startFrame")
            endFrame = cmds.getAttr("defaultRenderGlobals.endFrame")
            byFrame = cmds.getAttr("defaultRenderGlobals.byFrameStep")
            
            for frame in range(startFrame, endFrame+1, byFrame):

                print "Rendering frame " + str(frame)
        
                outFile = open(outFileName, 'w+')

                #Scene stuff
                outFile.write("<?xml version=\'1.0\' encoding=\'utf-8\'?>\n")
                outFile.write("\n")
                outFile.write("<scene version=\"0.4.0\">\n")

                #Write integrator
                writeIntegrator(outFile)

                #Write camera, sampler, and film
                writeSensor(outFile)

                #Write lights
                writeLights(outFile)

                #Write geom and mats together since theyre inter-dependent
                objFiles = writeGeometryAndMaterials(outFile, cwd)
                    
                outFile.write("\n")
                outFile.write("</scene>")
                outFile.close()
                ################################################################################
                ################################################################################
                ################################################################################

                ################################################################################
                #Call Mitsuba and delete temp files#############################################
                ################################################################################

                # os.chdir(cwd)
                projectDir = cwd
                dirList = re.split(r'/', projectDir)
                mayaDir = ""

                for i in range(len(dirList)-2):
                    mayaDir+=dirList[i]+"/"

                version = cmds.about(v=True).replace(" ", "-")

                pluginDir = mayaDir + version + "/plug-ins"
                mtsDir = pluginDir + "/mitsuba"

                os.chdir(mtsDir)
                imageName = projectDir + "/images/"
                imagePrefix = cmds.getAttr("defaultRenderGlobals.imageFilePrefix")
                imageName+=imagePrefix + str(frame).zfill(3) +".png"

                os.system(mtsDir+"/mitsuba.exe " + outFileName + " -o " + imageName)

                #Delete all of the temp file we just made
                os.chdir(projectDir+"/scenes")
                os.remove(outFileName)
                for obj in objFiles:
                    os.remove(obj)
        else:
            outFile = open(outFileName, 'w+')

            #Scene stuff
            outFile.write("<?xml version=\'1.0\' encoding=\'utf-8\'?>\n")
            outFile.write("\n")
            outFile.write("<scene version=\"0.4.0\">\n")

            #Write integrator
            writeIntegrator(outFile)

            #Write camera, sampler, and film
            writeSensor(outFile)

            #Write lights
            writeLights(outFile)

            #Write geom and mats together since theyre inter-dependent
            objFiles = writeGeometryAndMaterials(outFile, cwd)
                
            outFile.write("\n")
            outFile.write("</scene>")
            outFile.close()
            ################################################################################
            ################################################################################
            ################################################################################

            ################################################################################
            #Call Mitsuba and delete temp files#############################################
            ################################################################################

            # os.chdir(cwd)
            projectDir = cwd
            dirList = re.split(r'/', projectDir)
            mayaDir = ""

            for i in range(len(dirList)-2):
                mayaDir+=dirList[i]+"/"

            version = cmds.about(v=True).replace(" ", "-")

            pluginDir = mayaDir + version + "/plug-ins"
            mtsDir = pluginDir + "/mitsuba"

            os.chdir(mtsDir)
            imageName = projectDir + "/images/"
            imagePrefix = cmds.getAttr("defaultRenderGlobals.imageFilePrefix")
            imageName+=imagePrefix + str(i).zfill(3) +".png"

            os.system(mtsDir+"/mitsuba.exe " + outFileName + " -o " + imageName)

            #Delete all of the temp file we just made
            os.chdir(projectDir+"/scenes")
            os.remove(outFileName)
            for obj in objFiles:
                os.remove(obj)

            global renderedImage
            cmds.image(renderedImage, edit=True, image=imageName)
            showRenderWindow()

        ################################################################################
        ################################################################################
        ################################################################################

        '''
        Now we need to either select the objects that the user had selected before
        they rendered, or clear the selection
        '''
        if len(userSelection) > 0:
            cmds.select(userSelection)
        else:
            cmds.select(cl=True)

# Creator
def cmdCreator():
    return OpenMayaMPx.asMPxPtr( mitsubaForMaya() )

# Initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    # cmds.loadPlugin("diffuse.py")
    # cmds.loadPlugin("dielectric.py")
    # cmds.loadPlugin("twosided.py")
    # cmds.loadPlugin("sampler.py")
    # cmds.loadPlugin("mask.py")
    # cmds.loadPlugin("mixturebsdf.py")
    # cmds.loadPlugin("bump.py")
    # cmds.loadPlugin("roughplastic.py")
    # cmds.loadPlugin("roughcoating.py")
    # cmds.loadPlugin("coating.py")
    # cmds.loadPlugin("difftrans.py")
    # cmds.loadPlugin("ward.py")
    # cmds.loadPlugin("phong.py")
    # cmds.loadPlugin("roughdiffuse.py")
    # cmds.loadPlugin("roughdielectric.py")
    # cmds.loadPlugin("roughconductor.py")
    # cmds.loadPlugin("plastic.py")
    # cmds.loadPlugin("homogeneous.py")
    # cmds.loadPlugin("conductor.py")
    # cmds.loadPlugin("thindielectric.py")
    # cmds.loadPlugin("sunsky.py")
    # cmds.loadPlugin("envmap.py")
    gui()
    try:
        mplugin.registerCommand( kPluginCmdName, cmdCreator )
    except:
        sys.stderr.write( "Failed to register command: %s\n" % kPluginCmdName )
        raise

# Uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    # cmds.unloadPlugin("diffuse.py")
    # cmds.unloadPlugin("dielectric.py")
    # cmds.unloadPlugin("twosided.py")
    # cmds.unloadPlugin("sampler.py")
    # cmds.unloadPlugin("mask.py")
    # cmds.unloadPlugin("mixturebsdf.py")
    # cmds.unloadPlugin("bump.py")
    # cmds.unloadPlugin("roughplastic.py")
    # cmds.unloadPlugin("roughcoating.py")
    # cmds.unloadPlugin("coating.py")
    # cmds.unloadPlugin("difftrans.py")
    # cmds.unloadPlugin("ward.py")
    # cmds.unloadPlugin("phong.py")
    # cmds.unloadPlugin("roughdiffuse.py")
    # cmds.unloadPlugin("roughdielectric.py")
    # cmds.unloadPlugin("roughconductor.py")
    # cmds.unloadPlugin("plastic.py")
    # cmds.unloadPlugin("homogeneous.py")
    # cmds.unloadPlugin("conductor.py")
    # cmds.unloadPlugin("thindielectric.py")
    # cmds.unloadPlugin("sunsky.py")
    # cmds.unloadPlugin("envmap.py")
    deletegui()
    try:
        mplugin.deregisterCommand( kPluginCmdName )
    except:
        sys.stderr.write( "Failed to unregister command: %s\n" % kPluginCmdName )

##################################################

##################################################

#Main render settings window
global renderSettingsWindow
global renderWindow
global renderedImage
#Handle to the active integrator
global integrator
#List of possible integrators (stored as frameLayouts)
global integratorFrames

global sampler
global samplerFrames

global rfilter

global renderButton
global fileNameField
global hideEmitters

def createIntegratorFrames():
    #Make the integrator specific settings
    global integratorFrames
    integratorFrames = []
    aoSettings = cmds.frameLayout(label="Ambient Occlusion", cll=True, visible=False)
    cmds.intFieldGrp(numberOfFields=1, label="shadingSamples", value1=1)
    cmds.checkBox(label="Use automatic ray length")
    cmds.floatFieldGrp(numberOfFields=1, label="rayLength", value1=1)
    cmds.setParent('..')

    diSettings = cmds.frameLayout(label="Direct Illumination", cll=True, visible=False)
    cmds.intFieldGrp(numberOfFields=1, label="shadingSamples", value1=1)
    cmds.checkBox(label="Use emitter and bsdf specific samplers")
    cmds.intFieldGrp(numberOfFields=1, label="emitterSamples", value1=1)
    cmds.intFieldGrp(numberOfFields=1, label="bsdfSamples", value1=1)
    cmds.checkBox(label = "strictNormals")
    cmds.checkBox(label = "hideEmitters")
    cmds.setParent('..')

    pSettings = cmds.frameLayout(label="Path Tracer", cll=True)
    cmds.checkBox("Use infinite depth", value=True)
    cmds.intFieldGrp(numberOfFields=1, label="maxDepth", value1=1)
    cmds.intFieldGrp(numberOfFields=1, label="rrDepth", value1=1)
    cmds.checkBox(label = "strictNormals")
    cmds.checkBox(label = "hideEmitters")
    cmds.setParent('..')

    vpsSettings = cmds.frameLayout(label="Simple Volumetric Path Tracer", cll=True, visible=False)
    cmds.checkBox("Use infinite depth", value=True)
    cmds.intFieldGrp(numberOfFields=1, label="maxDepth", value1=1)
    cmds.intFieldGrp(numberOfFields=1, label="rrDepth", value1=1)
    cmds.checkBox(label = "strictNormals")
    cmds.checkBox(label = "hideEmitters")
    cmds.setParent('..')

    vpSettings = cmds.frameLayout(label="Volumetric Path Tracer", cll=True, visible=False)
    cmds.checkBox("Use infinite depth", value=True)
    cmds.intFieldGrp(numberOfFields=1, label="maxDepth", value1=1)
    cmds.intFieldGrp(numberOfFields=1, label="rrDepth", value1=1)
    cmds.checkBox(label = "strictNormals")
    cmds.checkBox(label = "hideEmitters")
    cmds.setParent('..')

    bdptSettings = cmds.frameLayout(label="Bidirectional Path Tracer", cll=True, visible=False)
    cmds.checkBox(label = "Use infinite depth", value=True)
    cmds.intFieldGrp(numberOfFields=1, label="maxDepth", value1=1)
    cmds.checkBox(label = "lightImage")
    cmds.checkBox(label = "sampleDirect")
    cmds.intFieldGrp(numberOfFields=1, label="rrDepth", value1=1)
    cmds.setParent('..')

    pmSettings = cmds.frameLayout(label="Photon Map", cll=True, visible=False)
    cmds.intFieldGrp(numberOfFields=1, label="directSamples", value1=16)
    cmds.intFieldGrp(numberOfFields=1, label="glossySamples", value1=32)
    cmds.checkBox(label = "Use infinite depth", value=True)
    cmds.intFieldGrp(numberOfFields=1, label="maxDepth", value1=1)
    cmds.intFieldGrp(numberOfFields=1, label="globalPhotons", value1=250000)
    cmds.intFieldGrp(numberOfFields=1, label="causticPhotons", value1=250000)
    cmds.intFieldGrp(numberOfFields=1, label="volumePhotons", value1=250000)
    cmds.floatFieldGrp(numberOfFields=1, label="globalLookupRadius", value1=0.05)
    cmds.floatFieldGrp(numberOfFields=1, label="causticLookupRadius", value1=0.05)
    cmds.intFieldGrp(numberOfFields=1, label="lookupSize", value1=120)
    cmds.checkBox(label = "Use automatic granularity")
    cmds.intFieldGrp(numberOfFields=1, label="granularity", value1=0)
    cmds.checkBox(label = "hideEmitters")
    cmds.intFieldGrp(numberOfFields=1, label="rrDepth", value1=1)
    cmds.setParent('..')

    ppmSettings = cmds.frameLayout(label="Progressive Photon Map", cll=True, visible=False)
    cmds.checkBox(label = "Use infinite depth", value=True)
    cmds.intFieldGrp(numberOfFields=1, label="maxDepth", value1=1)
    cmds.intFieldGrp(numberOfFields=1, label="photonCount", value1=250000)
    cmds.checkBox(label = "Automatically decide initialRadius")
    cmds.floatFieldGrp(numberOfFields=1, label="initialRadius", value1=0.0)
    cmds.floatFieldGrp(numberOfFields=1, label="alpha", value1=0.7)
    cmds.checkBox(label = "Use automatic granularity")
    cmds.intFieldGrp(numberOfFields=1, label="granularity", value1=0)
    cmds.checkBox(label = "hideEmitters")
    cmds.intFieldGrp(numberOfFields=1, label="rrDepth", value1=1)
    cmds.checkBox(label = "Use infinite maxPasses")
    cmds.intFieldGrp(numberOfFields=1, label="maxPasses", value1=1)
    cmds.setParent('..')

    sppmSettings = cmds.frameLayout(label="Stochastic Progressive Photon Map", cll=True, visible=False)
    cmds.checkBox(label = "Use infinite depth", value=True)
    cmds.intFieldGrp(numberOfFields=1, label="maxDepth", value1=1)
    cmds.intFieldGrp(numberOfFields=1, label="photonCount", value1=250000)
    cmds.checkBox(label = "Automatically decide initialRadius")
    cmds.floatFieldGrp(numberOfFields=1, label="initialRadius", value1=0.0)
    cmds.floatFieldGrp(numberOfFields=1, label="alpha", value1=0.7)
    cmds.checkBox(label = "Use automatic granularity")
    cmds.intFieldGrp(numberOfFields=1, label="granularity", value1=0)
    cmds.checkBox(label = "hideEmitters")
    cmds.intFieldGrp(numberOfFields=1, label="rrDepth", value1=1)
    cmds.checkBox(label = "Use infinite maxPasses")
    cmds.intFieldGrp(numberOfFields=1, label="maxPasses", value1=1)
    cmds.setParent('..')

    pssmltSettings = cmds.frameLayout(label="Primary Sample Space Metropolis Light Transport", cll=True, visible=False)
    cmds.checkBox(label = "bidirectional")
    cmds.checkBox(label = "Use infinite depth", value=True)
    cmds.intFieldGrp(numberOfFields=1, label="maxDepth", value1=1)
    cmds.checkBox(label = "Use automatic direct samples")
    cmds.intFieldGrp(numberOfFields=1, label="directSamples", value1=16)
    cmds.intFieldGrp(numberOfFields=1, label="luminanceSamples", value1=100000)
    cmds.checkBox(label = "twoStage", value=False)
    cmds.checkBox(label = "hideEmitters", value=True)
    cmds.intFieldGrp(numberOfFields=1, label="rrDepth", value1=5)
    cmds.floatFieldGrp(numberOfFields=1, label="pLarge", value1=0.3)
    cmds.setParent('..')

    mltSettings = cmds.frameLayout(label="Path Space Metropolis Light Transport", cll=True, visible=False)
    cmds.checkBox(label = "Use infinite depth", value=True)
    cmds.intFieldGrp(numberOfFields=1, label="maxDepth", value1=1)
    cmds.checkBox(label = "Use automatic direct samples")
    cmds.intFieldGrp(numberOfFields=1, label="directSamples", value1=16)
    cmds.intFieldGrp(numberOfFields=1, label="luminanceSamples", value1=100000)
    cmds.checkBox(label = "twoStage", value=False)
    cmds.checkBox(label = "bidirectionalMutation", value=True)
    cmds.checkBox(label = "lensPerturbation", value=True)
    cmds.checkBox(label = "multiChainPerturbation", value=True)
    cmds.checkBox(label = "causticPerturbation", value=True)
    cmds.checkBox(label = "manifoldPerturbation", value=False)
    cmds.checkBox(label = "hideEmitters", value=True)
    cmds.floatFieldGrp(numberOfFields=1, label="lambda", value1=0.3)
    cmds.setParent('..')

    erptSettings = cmds.frameLayout(label="Energy Redistribution Path Tracer", cll=True, visible=False)
    cmds.checkBox(label = "Use infinite depth", value=True)
    cmds.intFieldGrp(numberOfFields=1, label="maxDepth", value1=1)
    cmds.floatFieldGrp(numberOfFields=1, label="numChains", value1=1.0)
    cmds.checkBox(label = "Enable max chains", value=False)
    cmds.floatFieldGrp(numberOfFields=1, label="maxChains", value1=1.0)
    cmds.checkBox(label = "Use automatic direct samples", value=False)
    cmds.intFieldGrp(numberOfFields=1, label="directSamples", value1=16)
    cmds.checkBox(label = "lensPerturbation", value=True)
    cmds.checkBox(label = "multiChainPerturbation", value=True)
    cmds.checkBox(label = "causticPerturbation", value=True)
    cmds.checkBox(label = "manifoldPerturbation", value=False)
    cmds.checkBox(label = "hideEmitters", value=True)
    cmds.floatFieldGrp(numberOfFields=1, label="lambda", value1=50)
    cmds.setParent('..')

    ptrSettings = cmds.frameLayout(label="Adjoint Particle Tracer", cll=True, visible=False)
    cmds.checkBox(label = "Use infinite depth", value=True)
    cmds.intFieldGrp(numberOfFields=1, label="maxDepth", value1=1)
    cmds.intFieldGrp(numberOfFields=1, label="rrDepth", value1=5)
    cmds.intFieldGrp(numberOfFields=1, label="granularity", value1=200000)
    cmds.checkBox(label = "bruteForce", value=False)
    cmds.checkBox(label = "hideEmitters", value=True)
    cmds.setParent('..')

    integratorFrames.append(aoSettings)
    integratorFrames.append(diSettings)
    integratorFrames.append(pSettings)
    integratorFrames.append(vpsSettings)
    integratorFrames.append(vpSettings)
    integratorFrames.append(bdptSettings)
    integratorFrames.append(pmSettings)
    integratorFrames.append(ppmSettings)
    integratorFrames.append(sppmSettings)
    integratorFrames.append(pssmltSettings)
    integratorFrames.append(mltSettings)
    integratorFrames.append(erptSettings)
    integratorFrames.append(ptrSettings)

def createSamplerFrames():
    global samplerFrames
    samplerFrames = []

    indSettings = cmds.frameLayout(label="Independent Sampler", cll=False, visible=True)
    cmds.intFieldGrp(numberOfFields=1, label="sampleCount", value1=4)
    cmds.setParent('..')

    stratSettings = cmds.frameLayout(label="Stratified Sampler", cll=True, visible=False)
    cmds.intFieldGrp(numberOfFields=1, label="sampleCount", value1=4)
    cmds.intFieldGrp(numberOfFields=1, label="dimension", value1=4)
    cmds.setParent('..')

    ldSettings = cmds.frameLayout(label="Low Discrepancy Sampler", cll=True, visible=False)
    cmds.intFieldGrp(numberOfFields=1, label="sampleCount", value1=4)
    cmds.intFieldGrp(numberOfFields=1, label="dimension", value1=4)
    cmds.setParent('..')

    halSettings = cmds.frameLayout(label="Halton QMC Sampler", cll=True, visible=False)
    cmds.intFieldGrp(numberOfFields=1, label="sampleCount", value1=4)
    cmds.intFieldGrp(numberOfFields=1, label="scramble", value1=0)
    cmds.setParent('..')

    hamSettings = cmds.frameLayout(label="Hammersley QMC Sampler", cll=True, visible=False)
    cmds.intFieldGrp(numberOfFields=1, label="sampleCount", value1=4)
    cmds.intFieldGrp(numberOfFields=1, label="scramble", value1=0)
    cmds.setParent('..')

    sobSettings = cmds.frameLayout(label="Sobol QMC Sampler", cll=True, visible=False)
    cmds.intFieldGrp(numberOfFields=1, label="sampleCount", value1=4)
    cmds.intFieldGrp(numberOfFields=1, label="scramble", value1=0)
    cmds.setParent('..')

    samplerFrames.append(indSettings)
    samplerFrames.append(stratSettings)
    samplerFrames.append(ldSettings)
    samplerFrames.append(halSettings)
    samplerFrames.append(hamSettings)
    samplerFrames.append(sobSettings)

'''
This function creates the render settings window.
This includes the integrator, sample generator, image filter,
and film type.
'''
def createRenderSettings():
    global renderSettingsWindow
    renderSettingsWindow = cmds.window(title="Mitsuba Render Settings", iconName="MTS", widthHeight=(100,250), retain=True, resizeToFitChildren=True)
    cmds.columnLayout(adjustableColumn=True)
    #Create integrator selection drop down menu
    global integrator
    integrator = cmds.optionMenu(label="Integrator", changeCommand=changeIntegrator)
    cmds.menuItem('Ambient Occlusion')
    cmds.menuItem('Direct Illumination')
    cmds.menuItem('Path Tracer')
    cmds.menuItem('Volumetric Path Tracer')
    cmds.menuItem('Simple Volumetric Path Tracer')
    cmds.menuItem('Bidirectional Path Tracer')
    cmds.menuItem('Photon Map')
    cmds.menuItem('Progressive Photon Map')
    cmds.menuItem('Stochastic Progressive Photon Map')
    cmds.menuItem('Primary Sample Space Metropolis Light Transport')
    cmds.menuItem('Path Space Metropolis Light Transport')
    cmds.menuItem('Energy Redistribution Path Tracer')
    cmds.menuItem('Adjoint Particle Tracer')
    cmds.menuItem('Virtual Point Lights')

    createIntegratorFrames()
    cmds.optionMenu(integrator, edit=True, select=3)


    global sampler
    sampler = cmds.optionMenu(label="Image Sampler", changeCommand=changeSampler)
    cmds.menuItem('Independent Sampler')
    cmds.menuItem('Stratified Sampler')
    cmds.menuItem('Low Discrepancy Sampler')
    cmds.menuItem('Halton QMC Sampler')
    cmds.menuItem('Hammersley QMC Sampler')
    cmds.menuItem('Sobol QMC Sampler')

    createSamplerFrames()
    cmds.optionMenu(sampler, edit=True, select=1)

    global rfilter
    rfilter = cmds.optionMenu(label="Film Reconstruction Filter")
    cmds.menuItem("Box filter")
    cmds.menuItem("Tent filter")
    cmds.menuItem("Gaussian filter")
    cmds.menuItem("Mitchell-Netravali filter")
    cmds.menuItem("Catmull-Rom filter")
    cmds.menuItem("Lanczos filter")

    global renderButton
    cmds.columnLayout(adjustableColumn=False)
    renderButton = cmds.button(label='Render', command=callMitsuba)

def createRenderWindow():
    global renderWindow
    global renderedImage
    renderWindow = cmds.window("Mitsuba Rendered Image", retain=True, resizeToFitChildren=True)
    cmds.paneLayout()
    renderedImage = cmds.image()


#Make the render settings window visible
def showRenderSettings(self):
    global renderSettingsWindow
    cmds.showWindow(renderSettingsWindow)

#Make the render window visible
def showRenderWindow():
    global renderWindow
    imageWidth = cmds.getAttr("defaultResolution.width")
    imageHeight = cmds.getAttr("defaultResolution.height")
    cmds.window(renderWindow, edit=True, widthHeight=(imageWidth, imageHeight))
    cmds.showWindow(renderWindow)

def showRenderWindowCC(self):
    global renderWindow
    imageWidth = cmds.getAttr("defaultResolution.width")
    imageHeight = cmds.getAttr("defaultResolution.height")
    cmds.window(renderWindow, edit=True, widthHeight=(imageWidth, imageHeight))
    cmds.showWindow(renderWindow)

#Mel command to render with Mitsuba
def callMitsuba(self):
    cmds.mitsuba()

'''
Since we have a number of integrators that each have a number of properties,
we need to have a number of GUI widgets.  However we only want to show
the settings for the active integrator
'''
def changeIntegrator(self):
    global integrator
    global integratorFrames
    #Query the integrator drop down menu to find the active integrator
    selectedIntegrator = cmds.optionMenu(integrator, query=True, value=True)
    #Set all other integrator frameLayout to be invisible
    for frame in integratorFrames:
        currentIntegrator = cmds.frameLayout(frame, query=True, label=True)
        currentIntegratorUnderscore = currentIntegrator.replace(" ", "_")
        if currentIntegrator == selectedIntegrator or currentIntegratorUnderscore == selectedIntegrator:
            cmds.frameLayout(frame, edit=True, visible=True)
        else:
            cmds.frameLayout(frame, edit=True, visible=False) 

def changeSampler(self):
    global sampler
    global samplerFrames
    #Query the sampler drop down menu to find the active sampler
    selectedSampler = cmds.optionMenu(sampler, query=True, value=True)
    #Set all other sampler frameLayout to be invisible
    for frame in samplerFrames:
        currentSampler = cmds.frameLayout(frame, query=True, label=True)
        currentSamplerUnderscore = currentSampler.replace(" ", "_")
        if currentSampler == selectedSampler or currentSamplerUnderscore == selectedSampler:
            cmds.frameLayout(frame, edit=True, visible=True)
        else:
            cmds.frameLayout(frame, edit=True, visible=False) 

def gui():
    global topLevel
    topLevel = cmds.menu( l="Mitsuba", p="MayaWindow", to=True)
    item = cmds.menuItem( p=topLevel, label='Render', c=showRenderSettings )
    item = cmds.menuItem( p=topLevel, label='Render Window', c=showRenderWindowCC )
    createRenderSettings()
    createRenderWindow()


def deletegui():
    cmds.deleteUI( topLevel )
    cmds.deleteUI( renderSettingsWindow )
    cmds.deleteUI( renderWindow )
