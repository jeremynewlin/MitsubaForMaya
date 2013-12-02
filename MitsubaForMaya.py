import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

kPluginCmdName = "mitsuba"

global materialNodeTypes
materialNodeTypes = ["MitsubaBumpShader", "MitsubaSmoothCoatingShader", "MitsubaConductorShader", "MitsubaDielectricShader", "MitsubaDiffuseTransmitterShader", "MitsubaDiffuseShader", "MitsubaMaskShader", "MitsubaMixtureShader", "MitsubaPhongShader", "MitsubaPlasticShader", "MitsubaRoughCoatingShader", "MitsubaRoughConductorShader", "MitsubaRoughDielectricShader", "MitsubaRoughDiffuseShader", "MitsubaRoughPlasticShader", "MitsubaThinDielectricShader", "MitsubaTwoSidedShader", "MitsubaWardShader"]

def getShader(geom):
    shapeNode = cmds.listRelatives(geom, children=True, shapes=True)[0]
    sg = cmds.listConnections(shapeNode, type="shadingEngine")[0]
    shader = cmds.listConnections(sg+".surfaceShader")[0]
    return shader

def writeMedium(medium, outFile, tabbedSpace):
    outFile.write(tabbedSpace + " <medium type=\"homogeneous\"> id=\"" + medium + "\">\n")
    
    #check if we want to use sigmaA and sigmaT or sigmaT and albedo
    sigmaAS = cmds.getAttr(medium+".sigmaAS")
    if sigmaAS:
        sigmaA = cmds.getAttr(medium+".sigmaA")
        sigmaS = cmds.getAttr(medium+".sigmaS")
        outFile.write(tabbedSpace + "      <srgb name=\"sigmaA\" value=\"" + str(sigmaA[0][0]) + " " + str(sigmaA[0][1]) + " " + str(sigmaA[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + "      <srgb name=\"sigmaS\" value=\"" + str(sigmaS[0][0]) + " " + str(sigmaS[0][1]) + " " + str(sigmaS[0][2]) + "\"/>\n")
    else:
        sigmaT = cmds.getAttr(medium+".sigmaT")
        albedo = cmds.getAttr(medium+".albedo")
        outFile.write(tabbedSpace + "      <srgb name=\"sigmaT\" value=\"" + str(sigmaT[0][0]) + " " + str(sigmaT[0][1]) + " " + str(sigmaT[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + "      <srgb name=\"albedo\" value=\"" + str(albedo[0][0]) + " " + str(albedo[0][1]) + " " + str(albedo[0][2]) + "\"/>\n")

    scale = cmds.getAttr(medium+".scale")    
    outFile.write(tabbedSpace + "      <float name=\"scale\" value=\"" + str(scale) + "\"/>\n")
    outFile.write(tabbedSpace + " </medium>\n")

def writeShader(material, outFile, tabbedSpace):
    matType = cmds.nodeType(material)
    
    if matType=="MitsubaBumpShader":
        print "bump"

    elif matType=="MitsubaSmoothCoatingShader":
        print "smooth coating"
        intIOR = cmds.getAttr(material+".intIOR")
        extIOR = cmds.getAttr(material+".extIOR")
        thickness = cmds.getAttr(material+".thickness")
        sigmaA = cmds.getAttr(material+".sigmaA")
        specularReflectance = cmds.getAttr(material+".specularReflectance")

        outFile.write(tabbedSpace + " <bsdf type=\"coating\" id=\"" + material + "\">\n")
        outFile.write(tabbedSpace + "     <float name=\"intIOR\" value=\"" + str(intIOR) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"extIOR\" value=\"" + str(extIOR) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"thickness\" value=\"" + str(thickness) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"sigmaA\" value=\"" + str(sigmaA[0][0]) + " " + str(sigmaA[0][1]) + " " + str(sigmaA[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"specularReflectance\" value=\"" + str(specularReflectance[0][0]) + " " + str(specularReflectance[0][1]) + " " + str(specularReflectance[0][2]) + "\"/>\n")
        
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
    
    elif matType=="MitsubaConductorShader":
        print "conductor"
        conductorMaterial = cmds.getAttr(material+".material", asString=True)
        extEta = cmds.getAttr(material+".extEta")
        outFile.write(tabbedSpace + " <bsdf type=\"conductor\"   id=\"" + material + "\">\n")
        outFile.write(tabbedSpace + "     <string name=\"material\" value=\"" + str(conductorMaterial) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"extEta\" value=\"" + str(extEta) + "\"/>\n")
        outFile.write(tabbedSpace + " </bsdf>\n")

    elif matType=="MitsubaDielectricShader":
        print "dielectric"
        #check for a homogeneous material
        #this checks if there is a homogeneous medium, and returns the attribute that it
        #is connected to if there is one
        connections = cmds.listConnections(material, type="HomogeneousParticipatingMedium", connections=True)
        #We want to make sure it is connected to the ".material" attribute
        hasMedium = False
        medium = ""
        if connections and connections[0]==material+".material":
            hasMedium = True
            medium = connections[1]

        #Get all of the required attributes
        intIOR = cmds.getAttr(material+".intIOR")
        extIOR = cmds.getAttr(material+".extIOR")

        #Write material
        outFile.write(tabbedSpace + " <bsdf type=\"dielectric\" id=\"" + material + "\">\n")
        outFile.write(tabbedSpace + "     <float name=\"intIOR\" value=\"" + str(intIOR) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"extIOR\" value=\"" + str(extIOR) + "\"/>\n")
        outFile.write(tabbedSpace + " </bsdf>\n\n")
        if hasMedium:
            writeMedium(medium, outFile, tabbedSpace)

    elif matType=="MitsubaDiffuseTransmitterShader":
        print "difftrans"
        transmittance = cmds.getAttr(material+".transmittance")
        outFile.write(tabbedSpace + " <bsdf type=\"diffuse\" id=\"" + material + "\">\n")
        outFile.write(tabbedSpace + "     <srgb name=\"reflectance\" value=\"" + str(transmittance[0][0]) + " " + str(transmittance[0][1]) + " " + str(transmittance[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + " </bsdf>\n")

    elif matType=="MitsubaDiffuseShader":
        print "diffuse"
        reflectance = cmds.getAttr(material+".reflectance")
        outFile.write(tabbedSpace + " <bsdf type=\"diffuse\" id=\"" + material + "\">\n")
        outFile.write(tabbedSpace + "     <srgb name=\"reflectance\" value=\"" + str(reflectance[0][0]) + " " + str(reflectance[0][1]) + " " + str(reflectance[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + " </bsdf>\n")

    elif matType=="MitsubaMaskShader":
        print "mask"

    elif matType=="MitsubaMixtureShader":
        print "mixture"

    elif matType=="MitsubaPhongShader":
        print "phong"
        exponent = cmds.getAttr(material+".exponent")
        specularReflectance = cmds.getAttr(material+".specularReflectance")
        diffuseReflectance = cmds.getAttr(material+".diffuseReflectance")

        outFile.write(tabbedSpace + " <bsdf type=\"phong\" id=\"" + material + "\">\n")
        outFile.write(tabbedSpace + "     <float name=\"exponent\" value=\"" + str(exponent) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"specularReflectance\" value=\"" + str(specularReflectance[0][0]) + " " + str(specularReflectance[0][1]) + " " + str(specularReflectance[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"diffuseReflectance\" value=\"" + str(diffuseReflectance[0][0]) + " " + str(diffuseReflectance[0][1]) + " " + str(diffuseReflectance[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + " </bsdf>\n")

    elif matType=="MitsubaPlasticShader":
        print "plastic"
        intIOR = cmds.getAttr(material+".intIOR")
        extIOR = cmds.getAttr(material+".extIOR")
        specularReflectance = cmds.getAttr(material+".specularReflectance")
        diffuseReflectance = cmds.getAttr(material+".diffuseReflectance")

        outFile.write(tabbedSpace + " <bsdf type=\"plastic\" id=\"" + material + "\">\n")
        outFile.write(tabbedSpace + "     <float name=\"intIOR\" value=\"" + str(intIOR) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"extIOR\" value=\"" + str(extIOR) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"specularReflectance\" value=\"" + str(specularReflectance[0][0]) + " " + str(specularReflectance[0][1]) + " " + str(specularReflectance[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"diffuseReflectance\" value=\"" + str(diffuseReflectance[0][0]) + " " + str(diffuseReflectance[0][1]) + " " + str(diffuseReflectance[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + " </bsdf>\n")


    elif matType=="MitsubaRoughCoatingShader":
        print "roughcoating"
        distribution = cmds.getAttr(material+".distribution", asString=True)
        alpha = cmds.getAttr(material+".alpha")
        intIOR = cmds.getAttr(material+".intIOR")
        extIOR = cmds.getAttr(material+".extIOR")
        thickness = cmds.getAttr(material+".thickness")
        sigmaA = cmds.getAttr(material+".sigmaA")
        specularReflectance = cmds.getAttr(material+".specularReflectance")

        outFile.write(tabbedSpace + " <bsdf type=\"roughcoating\" id=\"" + material + "\">\n")
        outFile.write(tabbedSpace + "     <string name=\"distribution\" value=\"" + str(distribution) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"alpha\" value=\"" + str(alpha) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"intIOR\" value=\"" + str(intIOR) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"extIOR\" value=\"" + str(extIOR) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"thickness\" value=\"" + str(thickness) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"sigmaA\" value=\"" + str(sigmaA[0][0]) + " " + str(sigmaA[0][1]) + " " + str(sigmaA[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"specularReflectance\" value=\"" + str(specularReflectance[0][0]) + " " + str(specularReflectance[0][1]) + " " + str(specularReflectance[0][2]) + "\"/>\n")
        
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

    elif matType=="MitsubaRoughConductorShader":
        print "rough conductor"
        outFile.write(tabbedSpace + " <bsdf type=\"roughconductor\" id=\"" + material + "\">\n")

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
        print "rough die"
        #check for a homogeneous material
        #this checks if there is a homogeneous medium, and returns the attribute that it
        #is connected to if there is one
        connections = cmds.listConnections(material, type="HomogeneousParticipatingMedium", connections=True)
        #We want to make sure it is connected to the ".material" attribute
        hasMedium = False
        medium = ""
        if connections and connections[0]==material+".material":
            hasMedium = True
            medium = connections[1]

        #Get all of the required attributes
        intIOR = cmds.getAttr(material+".intIOR")
        extIOR = cmds.getAttr(material+".extIOR")
        specularReflectance = cmds.getAttr(material+".specularReflectance")
        specularTransmittance = cmds.getAttr(material+".specularTransmittance")

        #Write material
        outFile.write(tabbedSpace + " <bsdf type=\"dielectric\" id=\"" + material + "\">\n")
        
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
        if hasMedium:
            writeMedium(medium, outFile, tabbedSpace)

    elif matType=="MitsubaRoughDiffuseShader":
        print "rough diffuse"
        reflectance = cmds.getAttr(material+".reflectance")
        alpha = cmds.getAttr(material+".alpha")
        useFastApprox = cmds.getAttr(material+".useFastApprox")

        outFile.write(tabbedSpace + " <bsdf type=\"roughdiffuse\" id=\"" + material + "\">\n")
        outFile.write(tabbedSpace + "     <srgb name=\"reflectance\" value=\"" + str(reflectance[0][0]) + " " + str(reflectance[0][1]) + " " + str(reflectance[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"alpha\" value=\"" + str(alpha) + "\"/>\n")
        outFile.write(tabbedSpace + "     <boolean name=\"useFastApprox\" value=\"" + str(useFastApprox) + "\"/>\n")
        outFile.write(tabbedSpace + " </bsdf>\n")

    elif matType=="MitsubaRoughPlasticShader":
        print "rough plastic"
        distribution = cmds.getAttr(material+".distribution", asString=True)
        alpha = cmds.getAttr(material+".alpha")
        intIOR = cmds.getAttr(material+".intIOR")
        extIOR = cmds.getAttr(material+".extIOR")
        specularReflectance = cmds.getAttr(material+".specularReflectance")
        diffuseReflectance = cmds.getAttr(material+".diffuseReflectance")

        outFile.write(tabbedSpace + " <bsdf type=\"roughplastic\" id=\"" + material + "\">\n")
        outFile.write(tabbedSpace + "     <string name=\"distribution\" value=\"" + str(distribution) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"alpha\" value=\"" + str(alpha) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"intIOR\" value=\"" + str(intIOR) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"extIOR\" value=\"" + str(extIOR) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"specularReflectance\" value=\"" + str(specularReflectance[0][0]) + " " + str(specularReflectance[0][1]) + " " + str(specularReflectance[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"diffuseReflectance\" value=\"" + str(diffuseReflectance[0][0]) + " " + str(diffuseReflectance[0][1]) + " " + str(diffuseReflectance[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + " </bsdf>\n")

    elif matType=="MitsubaThinDielectricShader":
        print "thin dielectric"
        #check for a homogeneous material
        #this checks if there is a homogeneous medium, and returns the attribute that it
        #is connected to if there is one
        connections = cmds.listConnections(material, type="HomogeneousParticipatingMedium", connections=True)
        #We want to make sure it is connected to the ".material" attribute
        hasMedium = False
        medium = ""
        if len(connections)>0 and connections[0]==material+".material":
            hasMedium = True
            medium = connections[1]

        #Get all of the required attributes
        intIOR = cmds.getAttr(material+".intIOR")
        extIOR = cmds.getAttr(material+".extIOR")

        #Write material
        outFile.write(tabbedSpace + " <bsdf type=\"thindielectric\">\n id=\"" + material + "\">\n")
        outFile.write(tabbedSpace + "     <float name=\"intIOR\" value=\"" + str(intIOR) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"extIOR\" value=\"" + str(extIOR) + "\"/>\n")
        outFile.write(tabbedSpace + " </bsdf>\n\n")
        if hasMedium:
            writeMedium(medium, outFile, tabbedSpace)

    elif matType=="MitsubaTwoSidedShader":
        print "twosided"
        outFile.write(tabbedSpace + " <bsdf type=\"twosided\">\n id=\"" + material + "\">\n")
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
        print "ward"
        variant = cmds.getAttr(material+".variant", asString=True)
        alphaUV = cmds.getAttr(material+".alphaUV")
        specularReflectance = cmds.getAttr(material+".specularReflectance")
        diffuseReflectance = cmds.getAttr(material+".diffuseReflectance")

        outFile.write(tabbedSpace + " <bsdf type=\"phong\" id=\"" + material + "\">\n")
        outFile.write(tabbedSpace + "     <string name=\"variant\" value=\"" + str(variant) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"alphaU\" value=\"" + str(alphaUV[0][0]) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"alphaV\" value=\"" + str(alphaUV[0][1]) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"specularReflectance\" value=\"" + str(specularReflectance[0][0]) + " " + str(specularReflectance[0][1]) + " " + str(specularReflectance[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"diffuseReflectance\" value=\"" + str(diffuseReflectance[0][0]) + " " + str(diffuseReflectance[0][1]) + " " + str(diffuseReflectance[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + " </bsdf>\n")
        print "end of ward"

# Render Command
class mitsubaForMaya(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)

    # Invoked when the command is run.
    def doIt(self,argList):
        print "Rendering with Mitsuba..."
        userSelection = cmds.ls(sl=True)
        cwd = cmds.workspace(q=True, directory=True)
        print cwd

        #out mitsuba file
        outFileName = cwd+"temporary.xml"
        outFile = open(outFileName, 'w+')

        outFile.write("<?xml version=\'1.0\' encoding=\'utf-8\'?>\n")
        outFile.write("\n")
        outFile.write("<scene version=\"0.4.0\">\n")

        #Write the integrator########################################################################
        global integrator
        global integratorFrames
        activeIntegrator = cmds.optionMenu(integrator, query=True, value=True)
        activeSettings = integratorFrames[0]

        #Find the active integrator's settings frame layout
        for frame in integratorFrames:
            if cmds.frameLayout(frame, query=True, visible=True):
                activeSettings = frame


        print activeIntegrator
        if activeIntegrator=="Ambient_Occlusion":
            '''
            The order for this integrator is:
            0. intFieldGrp shadingSamples
            1. checkBox to use automatic ray length
            2. intFieldGrp rayLength (for manual rayLength)
            '''
            sSamples = cmds.intFieldGrp(integratorSettings[0], query=True, value1=True)
            outFile.write("     <integer name=\"shadingSamples\" value=\"" + str(sSamples) + "\"/>\n")

            if cmds.checkBox(integratorSettings[1], query=True, value=True):
                outFile.write("     <integer name=\"rayLength\" value=\"" + str(-1) + "\"/>\n")
            else:
                rl = cmds.intFieldGrp(integratorSettings[2], query=True, value1=True)
                outFile.write("     <integer name=\"rayLength\" value=\"" + str(rl) + "\"/>\n")
       
        #Write DI settings
        elif activeIntegrator=="Direct_Illumination":
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
        elif activeIntegrator=="Path_Tracer" or activeIntegrator=="Volumetric_Path_Tracer" or activeIntegrator=="Simple_Volumetric_Path_Tracer":
            '''
            The order for this integrator is:
            0. checkBox to use infinite samples
            1. intFieldGrp maxDepth
            2. intFieldGrp rrDepth
            3. checkBox strictNormals
            4. checkBox hideEmitters
            '''
            if activeIntegrator=="Path_Tracer":
                outFile.write(" <integrator type=\"path\">\n")
            elif activeIntegrator=="Volumetric_Path_Tracer":
                outFile.write(" <integrator type=\"volpath\">\n")
            else:
                outFile.write(" <integrator type=\"volpath_simple\">\n")

            integratorSettings = cmds.frameLayout(activeSettings, query=True, childArray=True)

            if cmds.checkBox(integratorSettings[0], query=True, value=True):
                outFile.write("     <integer name=\"maxDepth\" value=\"-1\"/>\n")
            else:
                maxDepth = cmds.intFieldGrp(integratorSettings[1], query=True, value1=True)
                outFile.write("     <integer name=\"emitterSamples\" value=\"" + str(maxDepth) + "\"/>\n")

            rrDepth = cmds.intFieldGrp(integratorSettings[2], query=True, value1=True)
            outFile.write("     <integer name=\"emitterSamples\" value=\"" + str(rrDepth) + "\"/>\n")            

            if cmds.checkBox(integratorSettings[3], query=True, value=True):
                outFile.write("     <boolean name=\"strictNormals\" value=\"true\"/>\n")
            else:
                outFile.write("     <boolean name=\"strictNormals\" value=\"false\"/>\n")

            if cmds.checkBox(integratorSettings[4], query=True, value=True):
                outFile.write("     <boolean name=\"hideEmitters\" value=\"true\"/>\n")
            else:
                outFile.write("     <boolean name=\"hideEmitters\" value=\"false\"/>\n")

        #Write bdpt
        elif activeIntegrator=="Bidirectional_Path_Tracer":
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
                outFile.write("     <integer name=\"emitterSamples\" value=\"" + str(maxDepth) + "\"/>\n")

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
        elif activeIntegrator=="Photon_Map":
            print "photonmapper"

        #Write progressive photon mapper
        elif activeIntegrator=="Progressive_Photon_Map":
            print "ppm"

        #Write sppm
        elif activeIntegrator=="Stochastic_Progressive_Photon_Map":
            print "sppm"

        #Write pssmlt
        elif activeIntegrator=="Primary_Sample_Space_Metropolis_Light_Transport":
            print "pssmlt"

        #Write psmlt
        elif activeIntegrator=="Path_Space_Metropolis_Light_Transport":
            print "psmlt"

        #Write erpt
        elif activeIntegrator=="Energy_Redistribution_Path_Tracer":
            print "eprt"

        #Write ptracer
        elif activeIntegrator=="Adjoint_Particle_Tracer":
            print "ptracer"

        #Write vpl
        elif activeIntegrator=="Virtual_Point_Lights":
            print "vpl"

        outFile.write(" </integrator>\n")
        #############################################################################################

        outFile.write(" <!-- Camera -->\n")

        cams = cmds.ls(type="camera")
        rCamShape = ""
        for cam in cams:
            isRenderable = cmds.getAttr(cam+".renderable")
            if isRenderable:
                rCamShape = cam
                break
        
        print rCamShape        
        rGroup = cmds.listConnections(rCamShape)[0]

        rGroupRels = cmds.listRelatives(rGroup)

        rCam = rGroupRels[0]
        rAim = rGroupRels[1]
        rUp  = rGroupRels[2]

        camPos = cmds.getAttr(rCam+".translate")[0]
        camAim = cmds.getAttr(rAim+".translate")[0]
        camUp  = cmds.getAttr(rUp+".translate")[0]

        outFile.write(" <sensor type=\"perspective\">\n")
        outFile.write("         <float name=\"fov\" value=\"54.43\"/>\n")
        outFile.write("         <string name=\"fovAxis\" value=\"x\"/>\n")
        outFile.write("         <float name=\"nearClip\" value=\"0.1\"/>\n")
        outFile.write("         <transform name=\"toWorld\">\n")
        outFile.write("             <lookat target=\"" + str(camAim[0]) + " " + str(camAim[1]) + " " + str(camAim[2]) + "\" origin=\"" + str(camPos[0]) + " " + str(camPos[1]) + " " + str(camPos[2]) + "\" up=\"" + str(camUp[0]-camPos[0]) + " " + str(camUp[1]-camPos[1]) + " " + str(camUp[2]-camPos[2]) + "\"/>\n")
        outFile.write("         </transform>\n")
        outFile.write("\n")
        outFile.write("         <sampler type=\"sobol\">\n")
        outFile.write("             <integer name=\"sampleCount\" value=\"256\"/>\n")
        outFile.write("             <integer name=\"scramble\" value=\"1\"/>\n")
        outFile.write("         </sampler>\n")
        outFile.write("\n")
        outFile.write("     <film type=\"ldrfilm\">\n")
        outFile.write("         <boolean name=\"banner\" value=\"false\"/>\n")
        outFile.write("         <integer name=\"height\" value=\"720\"/>\n")
        outFile.write("         <integer name=\"width\" value=\"1280\"/>\n")
        outFile.write("         <rfilter type=\"gaussian\"/>\n")
        outFile.write("         <boolean name=\"banner\" value=\"false\"/>\n")
        outFile.write("     </film>\n")
        outFile.write(" </sensor>\n")
        outFile.write("\n")

        lights = cmds.ls(type="light")
        for light in lights:
            lightType = cmds.nodeType(light)
            if lightType == "directionalLight":
                intensity = cmds.getAttr(light+".intensity")
                color = cmds.getAttr(light+".color")[0]
                print color
                irradiance = [0,0,0]
                for i in range(3):
                    irradiance[i] = intensity*color[i]
                matrix = cmds.getAttr(light+".worldMatrix")
                lightDir = [-matrix[8],-matrix[9],-matrix[10]]
                outFile.write(" <emitter type=\"directional\">\n")
                outFile.write("     <vector name=\"direction\" x=\"" + str(lightDir[0]) + "\" y=\"" + str(lightDir[1]) + "\" z=\"" + str(lightDir[2]) + "\"/>\n")
                outFile.write("     <srgb name=\"irradiance\" value=\"" + str(irradiance[0]) + " " + str(irradiance[1]) + " " + str(irradiance[2]) + "\"/>\n")
                outFile.write(" </emitter>\n")
                
        transforms = cmds.ls(type="transform")
        geoms = []

        for transform in transforms:
            rels = cmds.listRelatives(transform)
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
        for geom in geoms:
            material = getShader(geom)          #Gets the user define names of the shader
            if cmds.nodeType(material) in materialNodeTypes:
                writeShader(material, outFile, "")  #Write the shader to the xml file
                
        outFile.write("\n")
        outFile.write("<!-- End of materials -->")
        outFile.write("\n")

        #Write each piece of geometry
        for geom in geoms:
            shader = getShader(geom)
            if cmds.nodeType(shader) in materialNodeTypes:
                output = cwd+geom+".obj"
                cmds.select(geom)
                cmds.file(output, op=True, typ="OBJexport", es=True, force=True)
                outFile.write("    <shape type=\"obj\">\n")
                outFile.write("        <string name=\"filename\" value=\"" + geom + ".obj\"/>\n")
                outFile.write("        <ref id=\"" + shader + "\"/>\n")
                outFile.write("    </shape>\n")
            
        outFile.write("\n")
        outFile.write("</scene>")
        outFile.close()

        if len(userSelection) > 0:
            cmds.select(userSelection)
        else:
            cmds.select(cl=True)

##################################################
class renderSettings():
    def __init__(self):
        self.integrator="Path_Tracer"
        self.hideEmitters=False
        self.sampler="Independent_Sampler"

##################################################
#Plugin behaviour
global renderSettingsWindow
global settings
global integrator
global samplerFrame
global sampler
global renderButton
global hideEmitters
global integratorFrames

'''
This function creates the render settings window.
This includes the integrator, sample generator, image filter,
and film type.
'''
def createRenderSettings():
    global renderSettingsWindow
    renderSettingsWindow = cmds.window(title="Mitsuba Render Settings", iconName="MTS", widthHeight=(100,250), retain=True, resizeToFitChildren=True)
    cmds.columnLayout(adjustableColumn=True)
    # cmds.formLayout()
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

    cmds.optionMenu(integrator, edit=True, select=3)

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
    cmds.checkBox("Use infinite samples")
    cmds.intFieldGrp(numberOfFields=1, label="maxDepth", value1=1)
    cmds.intFieldGrp(numberOfFields=1, label="rrDepth", value1=1)
    cmds.checkBox(label = "strictNormals")
    cmds.checkBox(label = "hideEmitters")
    cmds.setParent('..')

    vpsSettings = cmds.frameLayout(label="Simple Volumetric Path Tracer", cll=True, visible=False)
    cmds.checkBox("Use infinite samples")
    cmds.intFieldGrp(numberOfFields=1, label="maxDepth", value1=1)
    cmds.intFieldGrp(numberOfFields=1, label="rrDepth", value1=1)
    cmds.checkBox(label = "strictNormals")
    cmds.checkBox(label = "hideEmitters")
    cmds.setParent('..')

    vpSettings = cmds.frameLayout(label="Volumetric Path Tracer", cll=True, visible=False)
    cmds.checkBox("Use infinite samples")
    cmds.intFieldGrp(numberOfFields=1, label="maxDepth", value1=1)
    cmds.intFieldGrp(numberOfFields=1, label="rrDepth", value1=1)
    cmds.checkBox(label = "strictNormals")
    cmds.checkBox(label = "hideEmitters")
    cmds.setParent('..')

    bdptSettings = cmds.frameLayout(label="Bidirectional Path Tracer", cll=True, visible=False)
    cmds.checkBox(label = "Use infinite samples")
    cmds.intFieldGrp(numberOfFields=1, label="maxDepth", value1=1)
    cmds.checkBox(label = "lightImage")
    cmds.checkBox(label = "sampleDirect")
    cmds.intFieldGrp(numberOfFields=1, label="rrDepth", value1=1)
    cmds.setParent('..')

    pmSettings = cmds.frameLayout(label="Photon Map", cll=True, visible=False)
    cmds.intFieldGrp(numberOfFields=1, label="directSamples", value1=16)
    cmds.intFieldGrp(numberOfFields=1, label="glossySamples", value1=32)
    cmds.checkBox(label = "Use infinite samples")
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
    cmds.checkBox(label = "Use infinite depth")
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
    cmds.checkBox(label = "Use infinite depth")
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
    cmds.checkBox(label = "Use infinite depth")
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
    cmds.checkBox(label = "Use infinite depth")
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
    cmds.checkBox(label = "Use infinite depth")
    cmds.intFieldGrp(numberOfFields=1, label="maxDepth", value1=1)
    cmds.checkBox(label = "Enable max chains", value=False)
    cmds.floatFieldGrp(numberOfFields=1, label="numChains", value1=1.0)
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
    cmds.checkBox(label = "Use infinite depth")
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

    global hideEmitters
    cmds.columnLayout(adjustableColumn=False)
    hideEmitters = cmds.checkBox(label='Hide Emitters', changeCommand=toggleHideEmitters)

    global renderButton
    cmds.columnLayout(adjustableColumn=False)
    renderButton = cmds.button(label='Render', command=callMitsuba)

def showRenderSettings(self):
    global renderSettingsWindow
    cmds.showWindow(renderSettingsWindow)

def callMitsuba(self):
    cmds.mitsuba()

def changeIntegrator(self):
    global integrator
    global integratorFrames
    selectedIntegrator = cmds.optionMenu(integrator, query=True, value=True)
    for frame in integratorFrames:
        currentIntegrator = cmds.frameLayout(frame, query=True, label=True)
        currentIntegrator = currentIntegrator.replace(" ", "_")
        if currentIntegrator == selectedIntegrator:
            cmds.frameLayout(frame, edit=True, visible=True)
        else:
            cmds.frameLayout(frame, edit=True, visible=False) 

def changeSampler(self):
    global sampler
    global settings
    # settings.sampler = cmds.optionMenu(sampler, q=True, v=True)
    # updateRenderSettings()

def toggleHideEmitters(self):
    global settings
    global hideEmitters
    settings.hideEmitters = cmds.checkBox(hideEmitters, query=True, value=True)

def gui():
    print "gui god"
    global topLevel
    topLevel = cmds.menu( l="Mitsuba", p="MayaWindow", to=True)
    item = cmds.menuItem( p=topLevel, label='Render', c=showRenderSettings )
    createRenderSettings()


def deletegui():
    cmds.deleteUI( topLevel )
    cmds.deleteUI( renderSettingsWindow )

# Creator
def cmdCreator():
    return OpenMayaMPx.asMPxPtr( mitsubaForMaya() )

# Initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    cmds.loadPlugin("diffuse.py")
    cmds.loadPlugin("dielectric.py")
    cmds.loadPlugin("twosided.py")
    # cmds.loadPlugin("sampler.py")
    # cmds.loadPlugin("mask.py")
    # cmds.loadPlugin("mixturebsdf.py")
    # cmds.loadPlugin("bump.py")
    cmds.loadPlugin("roughplastic.py")
    cmds.loadPlugin("roughcoating.py")
    cmds.loadPlugin("coating.py")
    cmds.loadPlugin("difftrans.py")
    cmds.loadPlugin("ward.py")
    cmds.loadPlugin("phong.py")
    cmds.loadPlugin("roughdiffuse.py")
    cmds.loadPlugin("roughdielectric.py")
    cmds.loadPlugin("roughconductor.py")
    cmds.loadPlugin("plastic.py")
    cmds.loadPlugin("homogeneous.py")
    cmds.loadPlugin("conductor.py")
    cmds.loadPlugin("thindielectric.py")
    gui()
    global settings
    settings = renderSettings()
    try:
        mplugin.registerCommand( kPluginCmdName, cmdCreator )
    except:
        sys.stderr.write( "Failed to register command: %s\n" % kPluginCmdName )
        raise

# Uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    cmds.unloadPlugin("diffuse.py")
    cmds.unloadPlugin("dielectric.py")
    cmds.unloadPlugin("twosided.py")
    # cmds.unloadPlugin("sampler.py")
    # cmds.unloadPlugin("mask.py")
    # cmds.unloadPlugin("mixturebsdf.py")
    # cmds.unloadPlugin("bump.py")
    cmds.unloadPlugin("roughplastic.py")
    cmds.unloadPlugin("roughcoating.py")
    cmds.unloadPlugin("coating.py")
    cmds.unloadPlugin("difftrans.py")
    cmds.unloadPlugin("ward.py")
    cmds.unloadPlugin("phong.py")
    cmds.unloadPlugin("roughdiffuse.py")
    cmds.unloadPlugin("roughdielectric.py")
    cmds.unloadPlugin("roughconductor.py")
    cmds.unloadPlugin("plastic.py")
    cmds.unloadPlugin("homogeneous.py")
    cmds.unloadPlugin("conductor.py")
    cmds.unloadPlugin("thindielectric.py")
    deletegui()
    try:
        mplugin.deregisterCommand( kPluginCmdName )
    except:
        sys.stderr.write( "Failed to unregister command: %s\n" % kPluginCmdName )