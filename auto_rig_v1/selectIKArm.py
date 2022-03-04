#!/usr/bin/env python
#SETMODE 777

#----------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------ HEADER --#

"""
:author:
    Andy Tran

:synopsis:
    This will create an IK handle from two selected joints.

:description:
    A detailed description of what this module does.

:applications:
    Any applications that are required to run this script, i.e. Maya.

:see_also:
    Any other code that you have written that this module is similar to.
"""
#****************************************
#NOTES
"""
Orient the joints before creating the IK handle.
"""
#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- IMPORTS --#

# Default Python Imports
import maya.cmds as cmds
# Imports That You Wrote

#----------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------- FUNCTIONS --#

def createIKArm():
    selected = cmds.ls(selection=True)

    if len(selected) < 4:
        raise RuntimeError("Not enough items selected. Please select only four items.")
    elif len(selected) > 4:
        raise RuntimeError("Too many items selected. Please select only four items.")
    elif cmds.objectType(selected[0]) != "joint" or \
            cmds.objectType(selected[1]) != "joint":
        raise RuntimeError("A selected object is not a joint.")
    else:
        #print(selected)
        elbowJntList = cmds.listRelatives(selected[0], children=True)
        #print(elbowJntList)
        selected.insert(1, elbowJntList[0])
        #print(selected)
        ikHandle = cmds.ikHandle(startJoint=str(selected[0]),
                                 endEffector=str(selected[2]),
                                 solver="ikRPsolver",
                                 name="arm_rpIK")
        # Gets the first object's translation in world space, returning a list of x, y, z.
        firstJntPos = tuple(cmds.xform(selected[0],
                                 worldSpace=True, translation=True, query=True))
        secondJntPos = tuple(cmds.xform(selected[1],
                                  worldSpace=True, translation=True, query=True))
        thirdJntPos = tuple(cmds.xform(selected[2],
                                  worldSpace=True, translation=True, query=True))

        # Create the IK handle's curve to pull the elbow's normal for the exact PV.
        # Move the curve's elbow CV 40 units, should be safe for any big rigs.
        # Create a group for the exact PV, this will go to that CV and be its actual
        # pole vector. Then we set whatever the user selected as the display PV, by
        # parenting the exact PV underneath the display PV.
        ikHandleCrv = cmds.curve(degree=1, worldSpace=True, point=[firstJntPos,
                                                            secondJntPos, thirdJntPos])
        cmds.moveVertexAlongDirection(str(ikHandleCrv)+".cv[1]", normalDirection=5)
        movedCVPos = cmds.xform(str(ikHandleCrv)+".cv[1]",
                        worldSpace=True, translation=True, query=True)
        exactPV = cmds.circle(normal=(0,0,1), center=(0,0,0), name="exact_pv")
        exactPVGrp = cmds.group(exactPV, name="exactPV_grp")
        cmds.setAttr(str(exactPVGrp+".translate"),
                     movedCVPos[0], movedCVPos[1], movedCVPos[2], type="double3")
        cmds.poleVectorConstraint(exactPV, ikHandle[0])
        displayPV = cmds.rename(selected[3], "armIK_pv")
        cmds.makeIdentity(displayPV, apply=True, normal=0, preserveNormals=True,
                         translate=True, rotate=True, scale=True)
        displayPVGrp = cmds.group(displayPV, name="armIKPV_grp", world=True)
        cmds.xform(displayPVGrp, preserve=True, centerPivots=True)
        cmds.parent(exactPVGrp, displayPV)

        # Cleanup. Delete the ikHandleCurve and hide the exact PV.
        cmds.delete(ikHandleCrv)
        cmds.setAttr(str(exactPV[0])+".visibility", 0)
        cmds.select(clear=True)

        # Create the control curve.
        createControl(selected[1], selected[2], selected[4], ikHandle)

def createControl(elbowJnt="", wristJnt="", setCC="", ikHandle=[]):
    armCC = cmds.rename(setCC, "arm_cc")
    armCCGrp = cmds.group(armCC, name=armCC+"_grp")
    cmds.xform(preserve=True, centerPivots=True)
    cmds.move(0, 0, 0, armCCGrp, rotatePivotRelative=True)
    cmds.makeIdentity(armCCGrp, apply=True, normal=0, preserveNormals=True,
                      translate=True, rotate=True, scale=True)
    cmds.makeIdentity(armCC, apply=True, normal=0, preserveNormals=True,
                      translate=True, rotate=True, scale=True)
    cmds.parent(armCCGrp, wristJnt)
    cmds.setAttr(str(armCCGrp)+".translate", 0, 0, 0, type="double3")
    cmds.setAttr(str(armCCGrp)+".rotate", 0, 0, 0, type="double3")

    cmds.parent(armCCGrp, world=True)
    cmds.parent(ikHandle[0], armCC)


def send_args(start_jnt, end_jnt, PV_cc, IK_cc):
    cmds.select(start_jnt, r=True)
    cmds.select(end_jnt, PV_cc, IK_cc, add=True)
    createIKArm()
#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- CLASSES --#

