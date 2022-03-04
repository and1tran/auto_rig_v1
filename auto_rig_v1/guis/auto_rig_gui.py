#!/usr/bin/env python
#SETMODE 777

#----------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------ HEADER --#

"""
:author:
    username

:synopsis:
    A one line summary of what this module does.

:description:
    A detailed description of what this module does.

:applications:
    Any applications that are required to run this script, i.e. Maya.

:see_also:
    Any other code that you have written that this module is similar to.
"""

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- IMPORTS --#

# Default Python Imports
from PySide2 import QtGui, QtWidgets, QtCore
from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance
import maya.cmds as cmds
import maya.mel as mel
from os.path import expanduser

version = cmds.about(v=True)
home = expanduser("~/maya/%s/scripts/auto_rig_v1/" % version)

# Imports That You Wrote
import auto_rig_v1.xml_utils.read_xml as read_xml
import auto_rig_v1.step_two as step_two
#----------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------- FUNCTIONS --#

def get_maya_window():
    """
    This gets a pointer to the Maya window.
    :return: A pointer to the Maya window.
    :type: pointer
    """
    maya_main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(maya_main_window_ptr), QtWidgets.QWidget)

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- CLASSES --#

class AutoRigGUI(QtWidgets.QDialog):
    """
    This class does not return anything. This class will create the GUI and store data
    for the GUI. Stacking the objects are handled in the imported stacker module, but
    duplicating and grouping the objects are within this class.
    """
    def __init__(self):
        """
        This will create all the necessary variables the class will store.
        """
        QtWidgets.QDialog.__init__(self, parent=get_maya_window())

    def init_gui(self):
        main_vb = QtWidgets.QVBoxLayout(self)
        right_align = QtCore.Qt.AlignRight

        main_vb.addLayout(self.step_1_options())
        main_vb.addLayout(self.step_2_options())

        close_btn_vb = QtWidgets.QVBoxLayout(self)
        close_btn_vb.setAlignment(right_align)
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.setFixedSize(50, 25)
        close_btn.clicked.connect(self.close)
        close_btn_vb.addWidget(close_btn)
        main_vb.addLayout(close_btn_vb)

        # Configure the window.
        self.setGeometry(400, 540, 400, 20)
        self.setWindowTitle("Auto-rig GUI")
        self.show()

    def step_1_options(self):
        step_one_vb = QtWidgets.QVBoxLayout()

        step_one_label = QtWidgets.QLabel("Step 1")
        step_one_vb.addWidget(step_one_label)

        # Create the Orient Joints Button and display the Orient Joints settings.
        #orientJntBtn = QtWidgets.QPushButton("Orient Joints")
        #orientJntBtn.clicked.connect(self.orient_jnt_settings)
        #step_one_vb.addWidget(orientJntBtn)

        placeJntBtn = QtWidgets.QPushButton("Place Joints")
        placeJntBtn.clicked.connect(self.place_jnt)
        step_one_vb.addWidget(placeJntBtn)

        return step_one_vb

    def step_2_options(self):
        step_two_vb = QtWidgets.QVBoxLayout()

        step_two_vb = QtWidgets.QVBoxLayout()

        step_two_label = QtWidgets.QLabel("Step 2")
        step_two_vb.addWidget(step_two_label)

        placeJntBtn = QtWidgets.QPushButton("Make Rig")
        placeJntBtn.clicked.connect(self.call_step_two)
        step_two_vb.addWidget(placeJntBtn)

        return step_two_vb

    def orient_jnt_settings(self):
        mel.eval("OrientJointOptions")

    def place_jnt(self):
        # Add to the home filepath by finding the biped.xml and read from it.
        filepath = home + "/xml_utils/biped.xml"
        read_xml.read_file(filepath)

        # The joints come in really huge so select them all and set their size lower.
        cmds.select("root_jnt")
        mel.eval("SelectHierarchy")
        selected_jnts = cmds.ls(sl=True)
        for joint in selected_jnts:
            cmds.setAttr(str(joint) + ".radius", 0.25)
        cmds.select(cl=True)

        # Orient the joints with X as the aim vector and Y is the up vector
        cmds.parent("ball_l_jnt", "heel_l_jnt", "ball_r_jnt", "heel_r_jnt",
                    "hand_l_jnt", "hand_r_jnt", w=True)
        cmds.joint("root_jnt", e=True, oj="xyz", sao="yup", ch=True, zso=True)

        cmds.joint("thumb_01_fng_l_jnt", e=True, oj="xyz", sao="yup", ch=True, zso=True)
        cmds.rotate(45, "thumb_01_fng_l_jnt", x=True, r=True)
        cmds.makeIdentity("thumb_01_fng_l_jnt", a=True, n=0, pn=True, r=True)
        cmds.joint("thumb_01_fng_r_jnt", e=True, oj="xyz", sao="yup", ch=True, zso=True)
        cmds.rotate(-45, "thumb_01_fng_r_jnt", x=True, r=True)
        cmds.makeIdentity("thumb_01_fng_r_jnt", a=True, n=0, pn=True, r=True)

        cmds.parent(["ball_l_jnt", "heel_l_jnt"], "ankle_l_jnt")
        cmds.parent("hand_l_jnt", "wrist_l_jnt")
        cmds.parent(["ball_r_jnt", "heel_r_jnt"], "ankle_r_jnt")
        cmds.parent("hand_r_jnt", "wrist_r_jnt")
        cmds.select(cl=True)

    def call_step_two(self):
        step_two.create_arm()