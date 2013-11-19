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
        outFile.write(tabbedSpace + "     <float name=\"alphaU\" value=\"" + str(alphaUV[0]) + "\"/>\n")
        outFile.write(tabbedSpace + "     <float name=\"alphaV\" value=\"" + str(alphaUV[1]) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"specularReflectance\" value=\"" + str(specularReflectance[0][0]) + " " + str(specularReflectance[0][1]) + " " + str(specularReflectance[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + "     <srgb name=\"diffuseReflectance\" value=\"" + str(diffuseReflectance[0][0]) + " " + str(diffuseReflectance[0][1]) + " " + str(diffuseReflectance[0][2]) + "\"/>\n")
        outFile.write(tabbedSpace + " </bsdf>\n")

    else:
        print matType

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
        outFile.write(" <integrator type=\"path\">\n")
        outFile.write(" </integrator>\n")
        outFile.write("\n")
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
                    geoms.append(transform)

        #Write the material for each piece of geometry in the scene
        for geom in geoms:
            material = getShader(geom)          #Gets the user define names of the shader
            writeShader(material, outFile, "")  #Write the shader to the xml file
                
        outFile.write("\n")
        outFile.write("<!-- End of materials -->")
        outFile.write("\n")

        #Write each piece of geometry
        for geom in geoms:
            output = cwd+geom+".obj"
            cmds.select(geom)
            cmds.file(output, op=True, typ="OBJexport", es=True, force=True)
            shader = getShader(geom)
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
        self.hideEmitters=True
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

def createRenderSettings():
    global renderSettingsWindow
    renderSettingsWindow = cmds.window(title="Mitsuba Render Settings", iconName="MTS", widthHeight=(100,250), retain=True)
    cmds.columnLayout(adjustableColumn=False)
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

    global hideEmitters
    hitdeEmitters = cmds.checkBox(label='Hide Emitters', changeCommand=toggleHideEmitters)

    global samplerFrame
    samplerFrame = cmds.frameLayout(label="Sampler generator", cll=False)
    global sampler
    sampler = cmds.optionMenu(label='Type', changeCommand=changeSampler)
    cmds.menuItem("Independent Sampler")
    cmds.menuItem("Stratified Sampler")
    cmds.menuItem("Low discrepancy Sampler")
    cmds.menuItem("Halton QMC Sampler")
    cmds.menuItem("Hammersley QMC Sampler")
    cmds.menuItem("Sobol QMC Sampler")

    cmds.setParent('..')
    global renderButton
    renderButton = cmds.button(label='Render', align='center', command=callMitsuba)

def showRenderSettings(self):
    global renderSettingsWindow
    cmds.showWindow(renderSettingsWindow)

def callMitsuba(self):
    cmds.mitsuba()

def changeIntegrator(self):
    global integrator
    global settings
    settings.integrator = cmds.optionMenu(integrator, q=True, v=True)

def changeSampler(self):
    global sampler
    global settings
    settings.sampler = cmds.optionMenu(sampler, q=True, v=True)

def toggleHideEmitters(self):
    global hideEmitters
    global settings
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