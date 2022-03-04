#!/usr/bin/env python
#SETMODE 777

#----------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------ HEADER --#

"""
:author:
    Andy Tran

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
import maya.cmds as cmds
# Imports That You Wrote

#----------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------- FUNCTIONS --#

def verify_joint(test_obj):
    """
    This will verify the given object is a joint.

    :param joint: The object to test
    :type unicode

    :return: Whether the object is a joint.
    :type: bool
    """
    if str(cmds.objectType(test_obj)) != "joint":
        return False
    else:
        return True

def parent_shapes_chain(joint, cc_transform):
    """
    This will parent all the shapes under the CC transform passed in to the joint.

    :param joint: Joint to parent CC shapes under.
    :type: unicode

    :param cc_transform: The transform object given to pull shapes from.
    :type: unicode

    :return: The success of the operation.
    :type: bool
    """
    if verify_joint(joint):

        # Get the children of the joint chain.
        target_jnts = find_children(joint)
        target_jnts.insert(0, joint)

        # Create a duplicates list to delete. We want each FK cc to be independent, and
        # that isn't possible by adding shapes
        delete_duplicates = []

        for curr_joint in target_jnts:
            # Duplicate the CC, get the shapes of it into a list, and add it to the list
            # to be deleted.
            duplicate_cc = cmds.duplicate(cc_transform)
            childShapes = cmds.listRelatives(duplicate_cc, children=True, shapes=True)
            delete_duplicates.append(duplicate_cc)

            # Parent each CC shape under the current joint.
            for curr_cc_shape in childShapes:
                cmds.parent(curr_cc_shape, curr_joint, add=True, shape=True)

        # Delete each dupilcate individually to be thorough.
        for cc_dup in delete_duplicates:
            cmds.delete(cc_dup)

        cmds.select(clear=True)
        return True
    else:
        print("The first object is not a joint")
        return False

def parent_shapes(joint, cc_transform):
    """
    This will parent all the shapes under the CC transform passed in to the joint.

    :param joint: Joint to parent CC shapes under.
    :type: unicode

    :param cc_transform: The transform object given to pull shapes from.
    :type: unicode

    :return: The success of the operation.
    :type: bool
    """
    if verify_joint(joint):

        # Duplicate the CC, get the shapes of it into a list, and add it to the list
        # to be deleted.
        duplicate_cc = cmds.duplicate(cc_transform, rc=True)
        childShapes = cmds.listRelatives(duplicate_cc, children=True, shapes=True)

        # Parent each CC shape under the current joint.
        for curr_cc_shape in childShapes:
            cmds.parent(curr_cc_shape, joint, add=True, shape=True)

        cmds.delete(duplicate_cc)

        cmds.select(clear=True)
        return True
    else:
        print("The first object is not a joint")
        return False

def find_children(joint):
    """
    This will take the first joint in a chain and return the full path to the children
    joints in a list

    :param joint: The first joint in the chain.
    :type: unicode

    :return: A list of the children joints in the full path format, excluding the last
    joint because this will be assumed to be the wrist or ankle.
    :type: list
    """
    children_full = cmds.listRelatives(joint, ad=True, f=True, typ="joint")
    children_full.sort()
    return children_full[:-1]

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- CLASSES --#

