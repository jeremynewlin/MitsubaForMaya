import maya.cmds as cmds
import maya.mel as mel

def test():
    cmds.setParent('..')
    for i in range(10):
	    print "test"

def up():
	print "dep"
	
def register():
    cmds.renderer( 'test', rendererUIName='Another Renderer')
    #cmds.renderer( 'test', edit=True, addGlobalsNode='defaultRenderGlobals' )
    cmds.renderer( 'test', edit=True, addGlobalsTab=('Common', test, up) )
    print cmds.renderer( 'test', query=True, globalsTabUpdateProcNames=True )

def unr():
    cmds.renderer('test', edit=True, unr=True)
    
    
#register()
unr()