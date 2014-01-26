MitsubaForMaya
==============

A Maya plugin for the Mitsuba rendering engine.

While this tool is still in progress, it is functional for many common features found in Mitsuba.  The order that I incorporate them is arbitrarily what I need to use as times goes on.

Installation
============

1. Create a directory on Maya's default plug-in path.  By default, this is <user's directory>/Documents/maya/verion/plug-ins.

2. Download the python files found in the appropriate directory.

3. Unzip the folder to the directory made in step 1.

4. Download Mitsuba here, and extract it to the same directory from step 1.  Rename the folder you extracted to "mitsuba".

5. Open Maya and load "MitsubaForMaya.py" through the normal plug-in load screen.

6. Open the Render Settings window, and select Mitsuba from the drop down menu.  ****VERY IMPORTANT**** - make sure you click over to the "Mitsuba Common" tab before you render anything.  There is a problem with the render UI and it will not render unless you do this.

Usage
=====

The first important thing to keep in mind that this plug-in requires a Camera, Aim, Up renderable camera to funciton.  This can found in Creat->Camera.  This type of camera can be controlled normally, but also allows you further control of those three attributes.

The default lighting in Mitsuba is a sunsky, so if you do not use any lighting yourself, that is what this tool will default to as well.  The other two lights available are directional and environment maps.  Mitsuba supports a variety of other lights, but they have not been ported.  To use a directional light, simply create a normal, Maya directional light and position it as normal.  For an environment map or custom sunsky, see the appropriate nodes in the Hypershader, under Maya/Lights.  Note that you can specify either an environment map or sunsky node (ie you can not have one of each).

For the two custom lights, I have set the node's attributes such that they should work and appear generally pleasant.  For fine tuning, you will have to look in this short tutorial, or the Mitsuba docs (which are extremely informative and thorough).

For a variety of Mitsuba materials, check the Hypershade under Maya/Surface.

Render settings have been set to balance render time vs. quality.  More information can be found here.  The main thing that controls render quality is the sampleCount in the Image Sampler drop down.