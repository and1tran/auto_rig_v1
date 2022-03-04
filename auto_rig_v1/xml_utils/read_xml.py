from PySide2 import QtCore, QtGui, QtWidgets
from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance
from xml.dom import minidom
import xml.etree.ElementTree as et
import os
import maya.cmds as cmds

class Autovivification(dict):
    """
    This is a Python implementation of Perl's Autovivification feature
    """
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

def read_file(path):
    if not os.path.isfile(path):
        print("The file path given can't be found on disk.")
        return None

    xml_fh = et.parse(path)

    root = xml_fh.getroot()
    read_children(root)

def read_children(root):
    # Get the children of the root/children node
    root_children = root.getchildren()

    # Iterate through all the children of the current joint.
    for name_level_item in root_children:
        joint_name = ""
        translate = []
        joint_name = name_level_item.tag

        # Now we're going through the attributes, so we get the children of the name node.
        attrib_level = name_level_item.getchildren()

        # Now iterate through the attributes working on them.
        for attrib_item in attrib_level:

            if attrib_item.tag == "tx":
                translate.append(float(attrib_item.attrib["value"]))
            if attrib_item.tag == "ty":
                translate.append(float(attrib_item.attrib["value"]))
            if attrib_item.tag == "tz":
                translate.append(float(attrib_item.attrib["value"]))

            # Now we find the children attribute tag, then we will loop through that
            # with by calling it recursively, sending the children node NOT the joints
            # underneath.
            if attrib_item.tag == "children":
                children_attrib = attrib_item
                children_elements = children_attrib.getchildren()
                children = []
                for child in children_elements:
                    children.append(child.tag)
                if children:
                    read_children(children_attrib)

        #print("\n" + str(joint_name))
        #print translate
        #print children
        create_joint(joint_name, translate, children)

def create_joint(name, translate, children):
    created_joint = cmds.joint(p=translate, a=True)
    actual_name = cmds.rename(created_joint, str(name))
    cmds.select(cl=True)
    if children:
        for child in children:
            cmds.parent(child, actual_name)
            cmds.select(cl=True)

"""
Here's the plan:
1. biped XML to read in the basic structure of a biped.
2. Spine XML to read in the number of vertebrae and to read and create joints from
    the XML.
3. Finger XML to read in the number of fingers and to read and create joints from
    the XML.
4. Toe XML to read in the number of toes and to read and create joints from the XML.
5. Each of the Spine, Finger, and Toe XMLs will have a structure like:
    <root>
        <FINGER_1>
        <FINGER_2>
        ...
    This means in the code we can have a loop to iterate through the number of counts
    to read in the number of children from the root.
    So the read function will look similar to read_children, but will start from
    <FINGER_*> then read until the end because we can pass in an XML element.
    So pass in root_children[0], root_children[1],... depending on the count from input.
"""