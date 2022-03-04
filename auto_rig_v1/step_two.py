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
import maya.mel as mel
# Imports That You Wrote
import auto_rig_v1.auto_FKArm as rig_FK_arm
import auto_rig_v1.selectIKArm as rig_IK_arm
#----------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------- FUNCTIONS --#

def create_arm():
    parent_chest_list = []
    parent_cc_grp = []
    extras_grp = []
    delete_grp = []

    # Create the CCs to use for the limbs
    # cc_transforms = [FK_cc, IK_cc, box_cc, arrow_cc]
    cc_transforms = create_cc()
    for curr_cc in cc_transforms:
        delete_grp.append(curr_cc)

    cmds.parent("ball_l_jnt", "heel_l_jnt", "ball_r_jnt", "heel_r_jnt",
                "hand_l_jnt", "hand_r_jnt", w=True)

    # Create new joints for the footRoot separating the ankle from the foot.
    new_foot_roots = []
    dup_ankle = cmds.duplicate("ankle_l_jnt", "ankle_r_jnt", rc=True)
    new_foot_roots.append(dup_ankle[0])
    new_foot_roots.append(dup_ankle[1])
    cmds.parent(new_foot_roots, w=True)
    for foot_root in new_foot_roots:
        new_name = foot_root.replace("ankle", "footRoot")[:-1]
        cmds.rename(foot_root, new_name)
    cmds.parent("ball_l_jnt", "footRoot_l_jnt")
    cmds.parent("heel_l_jnt", "footRoot_l_jnt")
    cmds.parent("ball_r_jnt", "footRoot_r_jnt")
    cmds.parent("heel_r_jnt", "footRoot_r_jnt")
    cmds.select(cl=True)

    # new_foot_roots = cmds.duplicate("heel_l_jnt", "heel_r_jnt", st=True)
    # cmds.move(0, 0, 0, new_foot_roots, a=True)
    # for foot_root in new_foot_roots:
    #    new_name = foot_root.replace("heel", "footRoot")[:-1]
    #    cmds.rename(foot_root, new_name)
    # cmds.parent("ball_l_jnt", "footRoot_l_jnt")
    # cmds.parent("heel_l_jnt", "footRoot_l_jnt")
    # cmds.parent("ball_r_jnt", "footRoot_r_jnt")
    # cmds.parent("heel_r_jnt", "footRoot_r_jnt")
    # "footRoot_l_jnt", "footRoot_r_jnt"

    # Unparent the joints to not interfere with creating the limbs
    cmds.parent("shoulder_l_jnt", "shoulder_r_jnt", "clavicle_l_jnt", "clavicle_r_jnt",
                w=True)

    # Objects and their create calls.
    # If an arm: return grp = [IK_cc_grp, hand_cc_grp, clavicle_grp]
    # If an leg: return grp = [IK_cc_grp, foot_cc_grp]
    l_arm = CreateArm("shoulder_l_jnt", "elbow_l_jnt", "wrist_l_jnt", "arm")
    l_arm_grps = l_arm.create()
    parent_chest_list.append(l_arm_grps[2])
    parent_cc_grp.extend((l_arm_grps[0], l_arm_grps[1]))
    r_arm = CreateArm("shoulder_r_jnt", "elbow_r_jnt", "wrist_r_jnt", "arm")
    r_arm_grps = r_arm.create()
    parent_chest_list.append(r_arm_grps[2])
    parent_cc_grp.extend((r_arm_grps[0], r_arm_grps[1]))
    l_leg = CreateArm("hip_l_jnt", "knee_l_jnt", "ankle_l_jnt", "leg")
    l_leg_grps = l_leg.create()
    parent_cc_grp.extend((l_leg_grps[0], l_leg_grps[1]))
    r_leg = CreateArm("hip_r_jnt", "knee_r_jnt", "ankle_r_jnt", "leg")
    r_leg_grps = r_leg.create()
    parent_cc_grp.extend((r_leg_grps[0], r_leg_grps[1]))
    cmds.select(cl=True)

    # Create the spine.
    # spine_grps = [cog_cc, spine_crv, spine_surf, follicles_grp]
    curr_spine = CreateSpine("root_jnt", "FK_cc")
    spine_grps = curr_spine.create_spine()
    parent_cc_grp.append(spine_grps[0])
    extras_grp.extend((spine_grps[1], spine_grps[2], spine_grps[3]))

    # Create a simple neck and head ccs.
    # neck_grps = [neck_cc]
    curr_head = CreateHead("neck_01_jnt", "head_jnt", "FK_cc", "arrow_cc")
    neck_grps = curr_head.create()
    parent_chest_list.append(neck_grps)

    # Create the global controls and the hierarchy
    # master_grps = [globalControl01, extras_grp]
    curr_masterGrps = CreateGlobalControls("arrow_cc")
    master_grps = curr_masterGrps.create_gc()

    # Parent the arm groups to the chest cc
    cmds.parent(parent_chest_list, "chest_cc")
    cmds.parent(parent_cc_grp, master_grps[0])
    cmds.parent(extras_grp, master_grps[1])
    cmds.delete(delete_grp[:-1])

    cmds.select(clear=True)

def create_cc():
    """
    Create the CCs to use
    """
    FK_cc = cmds.circle(n="FK_cc", nr=(1, 0, 0), c=(0, 0, 0))[0]

    IK_cc_list = cmds.circle(n="IK_cc", nr=(0, 0, 1), c=(0, 0, 0), ch=False)
    IK_cc = IK_cc_list[0]
    cmds.select(str(IK_cc) + ".cv[0]", r=True)
    cmds.select(str(IK_cc) + ".cv[2]", add=True)
    cmds.select(str(IK_cc) + ".cv[4]", add=True)
    cmds.select(str(IK_cc) + ".cv[6]", add=True)
    cmds.scale(0.25, 0.25, 0.25, r=True)
    cmds.select(str(IK_cc) + ".cv[0:7]", r=True)
    cmds.rotate(0, 90, 0, r=True)
    cmds.select(cl=True)

    box_cc = cmds.curve(n="box_cc",
                d=1, p=[(-1, 0, -1), (-1, 0, 1), (1, 0, 1), (1, 0, -1), (-1, 0, -1),
                       (-1, 2, -1), (1, 2, -1), (1, 0, -1), (1, 0, 1), (-1, 0, 1),
                       (-1, 2, 1), (1, 2, 1), (1, 0, 1), (1, 2, 1), (1, 2, -1),
                       (-1, 2, -1), (-1, 2, 1)],
               k=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16])
    #cmds.xform(self.PV_cc, p=True, cpc=True)
    cmds.move(-1, box_cc, y=True)
    cmds.xform(box_cc, cp=True, p=True)
    cmds.makeIdentity(box_cc, a=True, n=0, pn=True, t=True, r=True, s=True)

    arrow_cc = cmds.curve(n = "arrow_cc", degree=1,
                                        point=[(-2, 0, -3), (0, 0 , -5), (2, 0, -3),
                                           (1, 0 , -3), (1, 0, -1), (3, 0, -1),
                                           (3, 0, -2), (5, 0, 0), (3, 0, 2), (3, 0, 1),
                                           (1, 0, 1), (1, 0, 3), (2, 0, 3), (0, 0, 5),
                                           (-2, 0, 3), (-1, 0, 3),
                                           (-1, 0, 1), (-3, 0, 1), (-3, 0, 2),
                                           (-5, 0, 0), (-3, 0, -2), (-3, 0, -1),
                                           (-1, 0, -1), (-1, 0, -3), (-2, 0, -3)],
               knot=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24])

    cc_transforms = [FK_cc, IK_cc, box_cc, arrow_cc]
    return cc_transforms

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- CLASSES --#

class CreateArm(object):
    """
    This class will create an arm rig.
    """
    def __init__(self, shoulder_jnt, elbow_jnt, wrist_jnt, type):
        """
        :param shoulder_jnt: The name of what will be the shoulder joint.
        :type: str

        :param elbow_jnt: The name of what will be the elbow joint.
        :type: str

        :param wrist_jnt: The name of what will be the wrist joint.
        :type: str

        :param type: The type of setup to make. This code can be used to create an
                    arm or a leg. For naming conventions.
        :type: str

        :param side: Left or Right side. For naming conventions.
        :type: str
        """
        self.type_flag = type
        self.side = ""
        self.color = 0

        self.shoulder_blend_jnt = shoulder_jnt
        self.elbow_blend_jnt = elbow_jnt
        self.wrist_blend_jnt = wrist_jnt
        #self.joint_list = [self.shoulder_blend_jnt, self.elbow_blend_jnt,
        #                   self.wrist_blend_jnt]

        self.shoulder_FK_jnt = ""
        self.elbow_FK_jnt = ""
        self.wrist_FK_jnt = ""

        self.shoulder_IK_jnt = ""
        self.elbow_IK_jnt = ""
        self.wrist_IK_jnt = ""

        self.FK_cc = "FK_cc"
        self.IK_cc = "IK_cc"
        self.PV_cc = "FK_cc"
        self.hand_cc = "box_cc"
        self.hand_cc_grp = ""

        self.arm_grp = ""
        self.clavicle_grp = ""
        self.IK_cc_grp = ""

        self.first_joint_type = ""
        self.mid_joint_type = ""
        self.shoulder_blend_rot_blc = ""
        self.elbow_blend_rot_blc = ""


    def set_hand_cc(self, cc_transform):
        """
        This will set the hand cc to add our IK/FK switch.

        :param cc_transform:
        :return: None
        """
        self.hand_cc = cc_transform

    def create(self):
        """
        This is the only function to call outside of the module. It will be the driver
        function for the rest of the class.

        :return: Success of the operation.
        :type: bool
        """
        # Make the joints and duplicate the CCs creating them by using old code.
        self.duplicate_jnts()
        self.duplicate_cc()
        self.color_cc()
        self.send_IK()
        self.send_FK()
        self.clean_up()

        # Create the hand object.
        if self.type_flag == "arm":
            curr_hand = CreateHand("hand_" + self.side + "_jnt", self.hand_cc, "hand",
                                   self.side)
            curr_hand.hand_setup(self.wrist_blend_jnt)
        elif self.type_flag == "leg":
            curr_hand = CreateHand("ball_" + self.side + "_jnt", self.hand_cc, "foot",
                                   self.side)
            curr_hand.hand_setup(self.wrist_blend_jnt)
        self.hand_cc = curr_hand.hand_cc
        cmds.setAttr(self.hand_cc + ".overrideEnabled", 1)
        cmds.setAttr(self.hand_cc + ".overrideColor", self.color)

        self.hand_cc_grp = curr_hand.hand_cc_grp

        # Blend the joints since we have the hand_cc/foot_cc now.
        self.blend_jnts()

        if self.type_flag == "arm":
            self.orient_hand()
            self.connect_clavicle()
        elif self.type_flag == "leg":
            duplicated_jnts = cmds.duplicate("footRoot_" + self.side + "_jnt",
                                             renameChildren=True)[0]
            duplicated_cc = cmds.duplicate(self.hand_cc, renameChildren=True)[0]
            curr_foot = CreateFoot("footRoot_" + self.side + "_jnt",
                                   self.hand_cc, self.side, False)
            curr_foot.create_foot()
            IK_foot = CreateFoot(duplicated_jnts, duplicated_cc, self.side, True)
            IK_foot.create_foot()
            IK_foot.clean_IK_foot(self.IK_cc)

            # Connect all the attributes from the original foot cc to the duplicated one.
            # cmds.connectAttr(IK_foot.foot_cc + ".translate", curr_foot.foot_cc +
            # ".translate")
            # cmds.connectAttr(IK_foot.foot_cc + ".rotate", curr_foot.foot_cc + ".rotate")
            # cmds.connectAttr(IK_foot.foot_cc + ".IK_FK_Switch", curr_foot.foot_cc +
            # ".IK_FK_Switch")
            # cmds.connectAttr(IK_foot.foot_cc + ".ballRoll", curr_foot.foot_cc +
            # ".ballRoll")
            # cmds.connectAttr(IK_foot.foot_cc + ".toeRoll", curr_foot.foot_cc +
            # ".toeRoll")
            # cmds.connectAttr(IK_foot.foot_cc + ".heelRoll", curr_foot.foot_cc +
            # ".heelRoll")
            # cmds.connectAttr(IK_foot.foot_cc + ".bank", curr_foot.foot_cc + ".bank")
            # cmds.connectAttr(IK_foot.foot_cc + ".toePivot", curr_foot.foot_cc +
            # ".toePivot")
            # cmds.connectAttr(IK_foot.foot_cc + ".heelPivot", curr_foot.foot_cc +
            # ".heelPivot")

            cmds.connectAttr(curr_foot.foot_cc + ".translate",
                             IK_foot.foot_cc + ".translate")
            cmds.connectAttr(curr_foot.foot_cc + ".rotate",
                             IK_foot.foot_cc + ".rotate")
            cmds.connectAttr(curr_foot.foot_cc + ".IK_FK_Switch",
                             IK_foot.foot_cc + ".IK_FK_Switch")
            cmds.connectAttr(curr_foot.foot_cc + ".ballRoll",
                             IK_foot.foot_cc + ".ballRoll")
            cmds.connectAttr(curr_foot.foot_cc + ".toeRoll",
                             IK_foot.foot_cc + ".toeRoll")
            cmds.connectAttr(curr_foot.foot_cc + ".heelRoll",
                             IK_foot.foot_cc + ".heelRoll")
            cmds.connectAttr(curr_foot.foot_cc + ".bank",
                             IK_foot.foot_cc + ".bank")
            cmds.connectAttr(curr_foot.foot_cc + ".toePivot",
                             IK_foot.foot_cc + ".toePivot")
            cmds.connectAttr(curr_foot.foot_cc + ".heelPivot",
                             IK_foot.foot_cc + ".heelPivot")

            self.orient_foot()

        cmds.setAttr(self.shoulder_IK_jnt + ".visibility", 0)
        # Return the armIK, hand, and clavicle if it is the arm.
        # Else return the legIK and foot if it is the foot.
        if self.type_flag == "arm":
            send_grps = [self.IK_cc_grp, self.hand_cc_grp, self.clavicle_grp]
        elif self.type_flag == "leg":
            send_grps = [self.IK_cc_grp, self.hand_cc_grp]
        return send_grps


    def duplicate_jnts(self):
        """
        This will duplicate the joints and set them to the FK and IK equivalent variables.

        :return: Success of the operation.
        :type: bool
        """
        name_type = ["FK", "IK", "BLD"]
        FK_duplicates = cmds.duplicate(self.shoulder_blend_jnt, rc=True)
        IK_duplicates = cmds.duplicate(self.shoulder_blend_jnt, rc=True)
        if self.type_flag == "arm":
            for type in name_type:
                if type == "FK":
                    for this in FK_duplicates:
                        list_string = this.split("_")
                        self.side = list_string[1]
                        list_string.insert(2, type)
                        new_string = "_".join(list_string)[:-1]

                        if list_string[0] == "shoulder":
                            self.shoulder_FK_jnt = cmds.rename(this, new_string)
                            self.first_joint_type = list_string[0]
                        elif list_string[0] == "elbow":
                            self.elbow_FK_jnt = cmds.rename(this, new_string)
                            self.mid_joint_type = list_string[0]
                        else:
                            self.wrist_FK_jnt = cmds.rename(this, new_string)
                elif type == "IK":
                    for this in IK_duplicates:
                        list_string = this.split("_")
                        list_string.insert(2, type)
                        new_string = "_".join(list_string)[:-1]

                        if list_string[0] == "shoulder":
                            self.shoulder_IK_jnt = cmds.rename(this, new_string)
                        elif list_string[0] == "elbow":
                            self.elbow_IK_jnt = cmds.rename(this, new_string)
                        else:
                            self.wrist_IK_jnt = cmds.rename(this, new_string)
                elif type == "BLD":
                    self.shoulder_blend_jnt = cmds.rename(self.shoulder_blend_jnt,
                                                          self.shoulder_blend_jnt[:10] +
                                                          "_" + type +
                                                          self.shoulder_blend_jnt[10:])
                    self.elbow_blend_jnt = cmds.rename(self.elbow_blend_jnt,
                                                          self.elbow_blend_jnt[:7] +
                                                          "_" + type +
                                                          self.elbow_blend_jnt[7:])
                    self.wrist_blend_jnt = cmds.rename(self.wrist_blend_jnt,
                                                       self.wrist_blend_jnt[:7] +
                                                       "_" + type +
                                                       self.wrist_blend_jnt[7:])
        elif self.type_flag == "leg":
            for type in name_type:
                if type == "FK":
                    for this in FK_duplicates:
                        list_string = this.split("_")
                        self.side = list_string[1]
                        list_string.insert(2, type)
                        new_string = "_".join(list_string)[:-1]

                        if list_string[0] == "hip":
                            self.shoulder_FK_jnt = cmds.rename(this, new_string)
                            self.first_joint_type = list_string[0]
                        elif list_string[0] == "knee":
                            self.elbow_FK_jnt = cmds.rename(this, new_string)
                            self.mid_joint_type = list_string[0]
                        else:
                            self.wrist_FK_jnt = cmds.rename(this, new_string)
                elif type == "IK":
                    for this in IK_duplicates:
                        list_string = this.split("_")
                        list_string.insert(2, type)
                        new_string = "_".join(list_string)[:-1]

                        if list_string[0] == "hip":
                            self.shoulder_IK_jnt = cmds.rename(this, new_string)
                        elif list_string[0] == "knee":
                            self.elbow_IK_jnt = cmds.rename(this, new_string)
                        else:
                            self.wrist_IK_jnt = cmds.rename(this, new_string)
                elif type == "BLD":
                    self.shoulder_blend_jnt = cmds.rename(self.shoulder_blend_jnt,
                                                          self.shoulder_blend_jnt[:5] +
                                                          "_" + type +
                                                          self.shoulder_blend_jnt[5:])
                    self.elbow_blend_jnt = cmds.rename(self.elbow_blend_jnt,
                                                          self.elbow_blend_jnt[:6] +
                                                          "_" + type +
                                                          self.elbow_blend_jnt[6:])
                    self.wrist_blend_jnt = cmds.rename(self.wrist_blend_jnt,
                                                       self.wrist_blend_jnt[:7] +
                                                       "_" + type +
                                                       self.wrist_blend_jnt[7:])

        #if self.type_flag == "arm":

        """
            # shoulder_l_jnt1 > shoulder_l_FK_jnt
            self.shoulder_FK_jnt = cmds.rename(FK_duplicates[0],
                                               FK_duplicates[0][:10] + "_FK" +
                                               FK_duplicates[0][10:][:-1])
            # elbow_l_jnt1 > elbow_l_FK_jnt
            self.elbow_FK_jnt = cmds.rename(FK_duplicates[1],
                                            FK_duplicates[1][:7] + "_FK" +
                                            FK_duplicates[1][7:][:-1])
            # wrist_l_jnt1 > wrist_l_FK_jnt
            cmds.rename(FK_duplicates[2], FK_duplicates[2][:7] + "_FK" +
                                            FK_duplicates[2][7:][:-1])
            """

    def duplicate_cc(self):
        self.FK_cc = cmds.duplicate(self.FK_cc, rc=True)[0]
        self.IK_cc = cmds.duplicate(self.IK_cc, rc=True)[0]
        if self.type_flag == "leg":
            cmds.rotate(0, 0, 90, self.IK_cc)
            cmds.makeIdentity(self.IK_cc, a=True, n=0, pn=True,
                              t=True, r=True, s=True)
        self.PV_cc = cmds.duplicate(self.FK_cc, n="PV_cc", rc=True)[0]

        cmds.parent(self.PV_cc, self.elbow_IK_jnt)
        if self.type_flag == "leg":
            cmds.setAttr(str(self.PV_cc) + ".translate", 0, -5, 0, type="double3")
            cmds.setAttr(str(self.PV_cc) + ".rotate", 0, 90, 0, type="double3")
        elif self.type_flag == "arm":
            cmds.setAttr(str(self.PV_cc) + ".translate", 0, 0, -5, type="double3")
            if self.side == "r":
                cmds.setAttr(str(self.PV_cc) + ".translate", 0, 0, 5, type="double3")
        cmds.parent(self.PV_cc, w=True)
        cmds.select(str(self.PV_cc) + ".cv[0:7]", r=True)
        if self.type_flag == "leg":
            cmds.rotate(0, 0, 90, r=True)
        elif self.type_flag == "arm":
            cmds.rotate(0, 90, 0, r=True)
        cmds.select(cl=True)

    def send_IK(self):
        rig_IK_arm.send_args(self.shoulder_IK_jnt, self.wrist_IK_jnt,
                             self.PV_cc, self.IK_cc)


    def send_FK(self):
        rig_FK_arm.parent_shapes(self.shoulder_FK_jnt, self.FK_cc)
        rig_FK_arm.parent_shapes(self.elbow_FK_jnt, self.FK_cc)

    def clean_up(self):
        cmds.delete(self.FK_cc)

        # Get the relatives into a list of armIKPV_grp and arm_cc_grp
        newIKgrp_objs = []
        add_side_list = cmds.listRelatives("armIKPV_grp", ad=True)
        add_side_list.append("armIKPV_grp")
        add_side_list_2 = cmds.listRelatives("arm_cc_grp", ad=True)
        add_side_list_2.append("arm_cc_grp")
        # Add each list to one list.
        for add_obj in add_side_list_2:
            add_side_list.append(add_obj)

        for curr_obj in add_side_list:
            # If it is a leg, then rename the arm part to leg and continue.
            if self.type_flag == "leg":
                type_name = curr_obj.replace("arm", "leg")
                curr_obj = cmds.rename(curr_obj, type_name)
            # Insert the side to the name.
            list_string = curr_obj.split("_")
            list_string.insert(1, self.side)
            new_string = "_".join(list_string)
            cmds.rename(curr_obj, new_string)
            # If these are the groups, we will group them under an IK controls grp.
            if curr_obj == "arm_cc_grp" or curr_obj == "armIKPV_grp"\
                    or curr_obj == "leg_cc_grp" or curr_obj == "legIKPV_grp":
                newIKgrp_objs.append(new_string)
            # Change the variable of the self IK_cc and PV_cc to the new names.
            if curr_obj == "arm_cc" or curr_obj == "leg_cc":
                self.IK_cc = new_string
            elif curr_obj == "armIK_pv" or curr_obj == "legIK_pv":
                self.PV_cc = new_string
        # Finally group the groups under one IK controls grp.
        self.IK_cc_grp = cmds.group(newIKgrp_objs[0], newIKgrp_objs[1],
                            n=str(self.type_flag + "IK_" + self.side + "_grp"))


        # Group the individual joint chains then group those into one arm group.
        arm_FK_grp = cmds.group(self.shoulder_FK_jnt,
                                n=self.shoulder_FK_jnt.replace("_jnt", "_grp"))
        arm_IK_grp = cmds.group(self.shoulder_IK_jnt,
                                n=self.shoulder_IK_jnt.replace("_jnt", "_grp"))
        arm_bld_grp = cmds.group(self.shoulder_blend_jnt,
                   n=self.shoulder_blend_jnt.replace("_jnt", "_grp"))
        self.arm_grp = cmds.group(arm_FK_grp, arm_IK_grp, arm_bld_grp,
                   n=self.type_flag + "_" + self.side + "_grp")

    def blend_jnts(self):
        transforms = ["X", "Y", "Z"]
        colors = ["R", "G", "B"]
        # Create the blend nodes for the shoulder and elbow
        self.shoulder_blend_rot_blc = cmds.shadingNode("blendColors",
                au=True, n=self.first_joint_type + "_" + self.side + "_rot_blc")
        self.elbow_blend_rot_blc = cmds.shadingNode("blendColors",
                au=True, n=self.mid_joint_type + "_" + self.side + "_rot_blc")

        # Connect the IK/FK Switch and connect IK to color2 and FK to color1 shoulder.
        cmds.connectAttr(self.hand_cc + ".IK_FK_Switch",
                         self.shoulder_blend_rot_blc + ".blender", f=True)
        for transform, color in zip(transforms, colors):
            cmds.connectAttr(self.shoulder_IK_jnt + ".rotate" + transform,
                        self.shoulder_blend_rot_blc + ".color1" + color, f=True)
        for transform, color in zip(transforms, colors):
            cmds.connectAttr(self.shoulder_FK_jnt + ".rotate" + transform,
                        self.shoulder_blend_rot_blc + ".color2" + color, f=True)
        for transform, color in zip(transforms, colors):
            cmds.connectAttr(self.shoulder_blend_rot_blc + ".output" + color,
                        self.shoulder_blend_jnt + ".rotate" + transform, f=True)

        # Repeat for the elbow.
        cmds.connectAttr(self.hand_cc + ".IK_FK_Switch",
                         self.elbow_blend_rot_blc + ".blender", f=True)
        for transform, color in zip(transforms, colors):
            cmds.connectAttr(self.elbow_IK_jnt + ".rotate" + transform,
                        self.elbow_blend_rot_blc + ".color1" + color, f=True)
        for transform, color in zip(transforms, colors):
            cmds.connectAttr(self.elbow_FK_jnt + ".rotate" + transform,
                        self.elbow_blend_rot_blc + ".color2" + color, f=True)
        for transform, color in zip(transforms, colors):
            cmds.connectAttr(self.elbow_blend_rot_blc + ".output" + color,
                        self.elbow_blend_jnt + ".rotate" + transform, f=True)

        # Connect the IK/FK Switch to the visibility, create the reverse joint and
        # connect the IK and PV to the reverse node.
        cmds.connectAttr(self.hand_cc + ".IK_FK_Switch", self.IK_cc + ".v", f=True)
        cmds.connectAttr(self.hand_cc + ".IK_FK_Switch", self.PV_cc + ".v", f=True)
        reverse_node = cmds.shadingNode("reverse", au=True,
                                    n=self.first_joint_type + "_" + self.side + "_rev")
        cmds.connectAttr(self.hand_cc + ".IK_FK_Switch",
                         reverse_node + ".inputX", f=True)
        cmds.connectAttr(reverse_node + ".outputX",
                         self.shoulder_FK_jnt + ".v", f=True)
        cmds.connectAttr(reverse_node + ".outputX",
                         self.elbow_FK_jnt + ".v", f=True)

    def orient_hand(self):
        # Create the locators, with correct names.
        IK_orient = cmds.spaceLocator(n="handIK_" + self.side + "_orient")[0]
        FK_orient = cmds.spaceLocator(n="handFK_" + self.side + "_orient")[0]

        # Parent the IK to the IK_cc, parent the FK to the wrist FK joint.
        cmds.parent(IK_orient, self.IK_cc)
        cmds.setAttr(IK_orient + ".translate", 0, 0, 0, type="double3")
        cmds.parent(FK_orient, self.wrist_FK_jnt)
        cmds.setAttr(FK_orient + ".translate", 0, 0, 0, type="double3")

        # Orient constrain the hand CC grp to the locators and connect the nodes, with
        # a reverse on the IK.
        orientConst = cmds.orientConstraint([IK_orient, FK_orient],
                                            self.hand_cc_grp, mo=False)[0]
        cmds.connectAttr(self.hand_cc + ".IK_FK_Switch",
                         orientConst + ".handIK_" + self.side + "_orientW0", f=True)
        reverse_node = cmds.shadingNode("reverse", au=True,
                                    n="armOrient" + self.side + "_rev")
        cmds.connectAttr(self.hand_cc + ".IK_FK_Switch",
                         reverse_node + ".inputX", f=True)
        cmds.connectAttr(reverse_node + ".outputX",
                         orientConst + ".handFK_" + self.side + "_orientW1", f=True)

        # Point constrain the hand CC grp finally.
        pointConst = cmds.pointConstraint([self.wrist_IK_jnt, self.wrist_FK_jnt],
                                          self.hand_cc_grp, mo=True)[0]
        cmds.connectAttr(self.hand_cc + ".IK_FK_Switch",
                         pointConst + "." + self.wrist_IK_jnt + "W0", f=True)
        cmds.connectAttr(self.hand_cc + ".IK_FK_Switch",
                         reverse_node + ".inputY", f=True)
        cmds.connectAttr(reverse_node + ".outputY",
                         pointConst + "." + self.wrist_FK_jnt + "W1", f=True)

        cmds.setAttr(self.hand_cc + ".overrideEnabled", 1)
        cmds.setAttr(self.hand_cc + ".overrideColor", self.color)

    def orient_foot(self):
        # Create locators and parent them to their respective drivers to parent const.
        # the foot cc grp.
        # Create the locators, with correct names.
        IK_orient = cmds.spaceLocator(n="feetIK_" + self.side + "_orient")[0]
        FK_orient = cmds.spaceLocator(n="feetFK_" + self.side + "_orient")[0]

        # Parent the IK to the IK_cc, parent the FK to the wrist FK joint.
        cmds.parent(IK_orient, self.IK_cc)
        cmds.setAttr(IK_orient + ".translate", 0, 0, 0, type="double3")
        cmds.parent(FK_orient, self.wrist_FK_jnt)
        cmds.setAttr(FK_orient + ".translate", 0, 0, 0, type="double3")

        parentConst = cmds.parentConstraint([IK_orient, FK_orient], self.hand_cc_grp,
                                            mo=False)[0]
        reverse_node = cmds.shadingNode("reverse", au=True,
                                        n="footOrient" + self.side + "_rev")
        cmds.connectAttr(self.hand_cc + ".IK_FK_Switch",
                         parentConst + "." + IK_orient + "W0", f=True)
        cmds.connectAttr(self.hand_cc + ".IK_FK_Switch",
                         reverse_node + ".inputX", f=True)
        cmds.connectAttr(reverse_node + ".outputX",
                         parentConst + "." + FK_orient + "W1", f=True)

    def connect_clavicle(self):
        # Get the clavicle and group it.
        clavicle_jnt = "clavicle_" + self.side + "_jnt"
        clavicle_grp = cmds.group(clavicle_jnt, n="clavicle_" + self.side + "_grp")
        self.clavicle_grp = clavicle_grp

        # Create a duplicate FK_cc which we will delete later.
        clavicle_cc = cmds.duplicate("FK_cc")[0]

        # Get the shape of the FK copy and add a copy of the shape to the clavicle.
        FK_cc_shape = cmds.listRelatives(clavicle_cc)[0]
        cmds.setAttr(FK_cc_shape + ".overrideEnabled", 1)
        cmds.setAttr(FK_cc_shape + ".overrideColor", self.color)
        cmds.parent(FK_cc_shape, clavicle_jnt, addObject=True, shape=True)
        # Finally parent the arm group to the clavicle joint.
        cmds.parent(self.arm_grp, clavicle_jnt)

        cmds.delete(clavicle_cc)

    def color_cc(self):
        if self.side == "l":
            self.color = 13
        elif self.side == "r":
            self.color = 6

        FK_cc_shape = cmds.listRelatives(self.FK_cc)[0]

        cmds.setAttr(FK_cc_shape + ".overrideEnabled", 1)
        cmds.setAttr(FK_cc_shape + ".overrideColor", self.color)
        cmds.setAttr(self.IK_cc + ".overrideEnabled", 1)
        cmds.setAttr(self.IK_cc + ".overrideColor", self.color)
        cmds.setAttr(self.PV_cc + ".overrideEnabled", 1)
        cmds.setAttr(self.PV_cc + ".overrideColor", self.color)

class CreateHand(object):
    """
    This class will create a hand rig.
    """
    def __init__(self, hand_jnt, hand_cc, type_flag, side):

        self.hand_jnt = hand_jnt
        self.wrist_jnt = ""
        self.hand_cc = hand_cc
        self.hand_cc_grp = ""
        self.type_flag = type_flag
        self.side = side

        self.thumb_list = []
        self.index_list = []
        self.middle_list = []
        self.ring_list = []
        self.pinkey_list = []
        self.fingers_list = [self.thumb_list, self.index_list, self.middle_list,
                             self.ring_list, self.pinkey_list]

    def hand_setup(self, wrist_jnt):
        # Get the full list of fingers then sort them into ascending order.
        sort_fingers = cmds.listRelatives(self.hand_jnt, ad=True)
        sort_fingers.sort()

        # Add them to their appropriate list for the class.
        for finger_jnt in sort_fingers:
            if "thumb" in finger_jnt:
                self.thumb_list.append(finger_jnt)
            elif "big" in finger_jnt:
                self.thumb_list.append(finger_jnt)
            elif "index" in finger_jnt:
                self.index_list.append(finger_jnt)
            elif "mid" in finger_jnt:
                self.middle_list.append(finger_jnt)
            elif "ring" in finger_jnt:
                self.ring_list.append(finger_jnt)
            elif "pinky" in finger_jnt:
                self.pinkey_list.append(finger_jnt)

        # Move the hand_cc, move the pivot to the wrist, and rename it
        if self.type_flag == "hand":
            self.hand_cc = cmds.duplicate(self.hand_cc, n="hand_" + self.side + "_cc")[0]
        elif self.type_flag == "foot":
            self.hand_cc = cmds.duplicate(self.hand_cc, n="foot_" + self.side + "_cc")[0]
        self.hand_cc_grp = cmds.group(self.hand_cc, n=self.hand_cc + "_grp")
        if self.type_flag == "hand":
            cmds.parent(self.hand_cc_grp, self.hand_jnt)
            cmds.setAttr(self.hand_cc_grp + ".translate", 0, 0, 0, type="double3")
            cmds.parent(self.hand_cc_grp, w=True)
            wrist_jnt_pos = cmds.xform(wrist_jnt, ws=True, t=True, q=True)
            cmds.move(wrist_jnt_pos[0], wrist_jnt_pos[1], wrist_jnt_pos[2],
                      self.hand_cc_grp + ".rotatePivot", self.hand_cc_grp + ".scalePivot",
                      ws=True, a=True)
            cmds.move(wrist_jnt_pos[0], wrist_jnt_pos[1], wrist_jnt_pos[2],
                      self.hand_cc + ".rotatePivot", self.hand_cc + ".scalePivot",
                      ws=True, a=True)
        elif self.type_flag == "foot":
            cmds.parent(self.hand_cc_grp, wrist_jnt)
            cmds.setAttr(self.hand_cc_grp + ".translate", 0, 0, 0, type="double3")
            cmds.parent(self.hand_cc_grp, w=True)

        # Add the IK_FK_Switch attribute
        cmds.select(self.hand_cc, r=True)
        cmds.addAttr(ln="_____", at="float", k=True,)
        cmds.addAttr(at="float", min=0.0, max=1.0, k=True,
                     ln="IK_FK_Switch", sn="IKFKSw")

        # This will create the CC and its group while in the loop because we want the
        # names to be consistent.
        for curr_finger in self.fingers_list:
            above_jnt = self.hand_jnt
            for curr_jnt in curr_finger:
                if "_tip_" in curr_jnt:
                    continue
                else:
                    finger_cc = cmds.curve(n=curr_jnt.replace("_jnt", "_cc"), d=1,
                                           p=[(0, 0.4, 0), (0, 0.4, 0.2), (0, 0.8, 0.2),
                                              (0, 0.8, -0.2),
                                              (0, 0.4, -0.2), (0, 0.4, 0), (0, 0, 0)],
                                           k=[0, 1, 2, 3, 4, 5, 6])
                    if self.type_flag == "foot":
                        cmds.rotate(90, finger_cc, y=True)
                        cmds.makeIdentity(finger_cc, a=True, n=0, pn=True,
                                          t=True, r=True, s=True)
                    finger_cc_grp = cmds.group(finger_cc,
                                            n=curr_jnt.replace("_jnt", "_grp"), r=True)
                    cmds.move(0, 0, 0, finger_cc_grp + ".rotatePivot",
                              finger_cc_grp + ".scalePivot", ws=True)
                    cmds.parent(finger_cc_grp, curr_jnt)
                    cmds.setAttr(finger_cc_grp + ".translate", 0, 0, 0, type="double3")
                    cmds.setAttr(finger_cc_grp + ".rotate", 0, 0, 0, type="double3")
                    cmds.parent(finger_cc_grp, above_jnt)
                    cmds.parent(curr_jnt, finger_cc)
                    above_jnt = curr_jnt

        # Parent the hand joint under the hand_cc, or the footRoot under the CC then
        # parent the ball to the footRoot
        if self.type_flag == "hand":
            cmds.parent(self.hand_jnt, self.hand_cc)
        elif self.type_flag == "foot":
            footRoot_jnt = "footRoot_" + self.side + "_jnt"
            cmds.parent(footRoot_jnt, self.hand_cc)

class CreateFoot(object):
    """
    This class will create a hand rig.
    """
    def __init__(self, footRoot_jnt, foot_cc, side, IK_flag):
        self.footRoot_jnt = footRoot_jnt
        self.ball_jnt = ""
        self.heel_jnt = ""
        self.foot_cc = foot_cc
        self.side = side
        self.IK_flag = IK_flag
        self.extra_indicator = ""

    def create_foot(self):
        if self.IK_flag:
            self.extra_indicator = "1"

        # Find the ball, heel, and longest toe joint.
        find_ball_list = cmds.listRelatives(self.footRoot_jnt, type="joint")
        ball_index = find_ball_list.index("ball_" + self.side + "_jnt" +
                                          self.extra_indicator)
        heel_index = find_ball_list.index("heel_" + self.side + "_jnt" +
                                          self.extra_indicator)
        self.ball_jnt = find_ball_list[ball_index]
        self.heel_jnt = find_ball_list[heel_index]

        # Get the big toe joint and the pinky joint.
        find_toes_list = cmds.listRelatives(self.ball_jnt, type="transform")
        bigToe_index = find_toes_list.index("big_01_toe_" + self.side + "_grp" +
                                            self.extra_indicator)
        pinkey_index = find_toes_list.index("pinky_01_toe_" + self.side + "_grp" +
                                            self.extra_indicator)
        bigToe_pos = cmds.xform(find_toes_list[bigToe_index], ws=True, t=True, q=True)
        pinky_pos = cmds.xform(find_toes_list[pinkey_index], ws=True, t=True, q=True)

        # Get the position of the ball joint and heel joint position.
        ball_pos = cmds.xform(self.ball_jnt, ws=True, t=True, q=True)
        heel_pos = cmds.xform(self.heel_jnt, ws=True, t=True, q=True)

        # Find the maximum Z length of the foot.
        # calc_foot_list = cmds.xform(self.ball_jnt, bb=True, ws=True, r=True, q=True)
        # z_difference = calc_foot_list[5] - calc_foot_list[2]
        # max_toe_pos = [ball_pos[0], ball_pos[1] - .1, ball_pos[2]+z_difference]
        max_toe_pos = cmds.xform("mid_tip_toe_" + self.side + "_jnt" +
                                 self.extra_indicator,
                                 ws=True, t=True, q=True)
        max_toe_pos[2] = max_toe_pos[2] + 0.05

        #inBall_pos = cmds.xform()

        # Create the reverse foot groups, parented under each other.
        revFoot = ["revBallFix", "revBall", "revToe", "revHeel",
                   "revOutBank", "revInBank"]
        revFoot_grp_list = []
        above_grp = ""
        for curr_grp in revFoot:
            if curr_grp == "revBallFix":
                revFoot_grp_list.append(cmds.group(em=True,
                                n=curr_grp + "_" + self.side + "_grp" +
                                  self.extra_indicator))
                above_grp = curr_grp + "_" + self.side + "_grp" + self.extra_indicator
            else:
                revFoot_grp_list.append(cmds.group(above_grp,
                                n=curr_grp + "_" + self.side + "_grp" +
                                  self.extra_indicator))
                above_grp = curr_grp + "_" + self.side + "_grp" + self.extra_indicator

        # Loop through the group list and move them to their respective positions.
        # Reversed group because the list starts with the ball fix grp to the in bank grp.
        for curr_grp in reversed(revFoot_grp_list):

            if "revInBank" in curr_grp:
                cmds.move(bigToe_pos[0], bigToe_pos[1], bigToe_pos[2], curr_grp,
                          a=True, ws=True)
            elif "revOutBank" in curr_grp:
                cmds.move(pinky_pos[0], pinky_pos[1], pinky_pos[2], curr_grp,
                          a=True, ws=True)
            elif "revHeel" in curr_grp:
                cmds.move(heel_pos[0], heel_pos[1], heel_pos[2], curr_grp,
                          a=True, ws=True)
            elif "revToe" in curr_grp:
                cmds.move(max_toe_pos[0], max_toe_pos[1], max_toe_pos[2], curr_grp,
                          a=True, ws=True)
            elif "revBall" in curr_grp:
                cmds.move(ball_pos[0], ball_pos[1], ball_pos[2], curr_grp,
                          a=True, ws=True)

        # Parent the foot under the rev ball grp and the ball under the rev ball fix grp.
        cmds.parent(revFoot_grp_list[5], self.foot_cc)
        cmds.parent(self.footRoot_jnt, revFoot_grp_list[1])
        cmds.parent(revFoot_grp_list[0], self.footRoot_jnt)
        cmds.parent(self.ball_jnt, revFoot_grp_list[0])

        # Create the controls on the foot.
        cmds.select(self.foot_cc, r=True)
        cmds.addAttr(ln="______", at="float", k=True,)
        cmds.addAttr(ln="ballRoll", at="float", k=True)
        cmds.addAttr(ln="toeRoll", at="float", k=True)
        cmds.addAttr(ln="heelRoll", at="float", k=True)
        cmds.addAttr(ln="bank", at="float", k=True)
        cmds.addAttr(ln="toePivot", at="float", k=True)
        cmds.addAttr(ln="heelPivot", at="float", k=True)

        foot_cc_attrs = ["ballRoll", "toeRoll", "heelRoll", "bank",
                         "toePivot", "heelPivot"]

        # Create the nodes to turn on and off the controls, these are only meant for IKs.
        IK_switch_node1 = cmds.shadingNode("multiplyDivide",
                                n="foot_01_" + self.side + "_IKSwitch_multdiv", au=True)
        IK_switch_node2 = cmds.shadingNode("multiplyDivide",
                                n="foot_01_" + self.side + "_IKSwitch_multdiv", au=True)
        IK_switch_nodes = [IK_switch_node1, IK_switch_node2]
        self.attach_foot_controls(IK_switch_nodes, foot_cc_attrs, revFoot_grp_list)

        # Now duplicate the foot for the IK leg.
        # foot_cc_grp = cmds.listRelatives(self.foot_cc, p=True)[0]
        # selected = cmds.select("foot_" + self.side + "_cc", r=True)
        # cmds.duplicate(rr=True, un=True, rc=True,
        #                                      ic=True, st=True,
        #                                      n="footDup_" + self.side + "_grp")
        # dup_foot_cc = cmds.listRelatives(duplicated_foot_grp)[0]
        # dup_foot_grp_children = cmds.listRelatives(duplicated_foot_grp, ad=True)

        # Find revBall fix and parent it under the revBall to not get deleted.
        # dup_revBall_index = dup_foot_grp_children.index(revFoot[1] + "_" +
        #                                                 self.side + "_grp1")
        # dup_revBallFix_index = dup_foot_grp_children.index(revFoot[0] + "_" +
        #                                                 self.side + "_grp1")
        # cmds.parent(dup_foot_grp_children[dup_revBallFix_index],
        #             dup_foot_grp_children[dup_revBall_index])

        # Find all the joints and delete it, will also delete the toes.
        # dup_foot_jnts = cmds.listRelatives(dup_foot_grp_children, ad=True, type="joint")
        # cmds.delete(dup_foot_jnts)
        #
        # new_dup_cc_children = cmds.listRelatives(dup_foot_cc, ad=True)

        # Find the rpIK object in the IK_cc
        # rp_IK = cmds.listRelatives(IK_cc, ad=True, type="ikHandle")[0]

        # Parent to the IK_cc
        # cmds.parent(duplicated_foot_grp, IK_cc)
        # cmds.parent(rp_IK, new_dup_cc_children[4])

        # Connect all the attributes from the original foot cc to the duplicated one.
        # cmds.connectAttr(self.foot_cc + ".translate", dup_foot_cc + ".translate")
        # cmds.connectAttr(self.foot_cc + ".rotate", dup_foot_cc + ".rotate")
        # cmds.connectAttr(self.foot_cc + ".IK_FK_Switch", dup_foot_cc + ".IK_FK_Switch")
        # cmds.connectAttr(self.foot_cc + ".ballRoll", dup_foot_cc + ".ballRoll")
        # cmds.connectAttr(self.foot_cc + ".toeRoll", dup_foot_cc + ".toeRoll")
        # cmds.connectAttr(self.foot_cc + ".heelRoll", dup_foot_cc + ".heelRoll")
        # cmds.connectAttr(self.foot_cc + ".bank", dup_foot_cc + ".bank")
        # cmds.connectAttr(self.foot_cc + ".toePivot", dup_foot_cc + ".toePivot")
        # cmds.connectAttr(self.foot_cc + ".heelPivot", dup_foot_cc + ".heelPivot")

    def attach_foot_controls(self, IK_switch_nodes, foot_attrs, revFoot_grp_list):
        transforms = ["X", "Y", "Z"]

        negative_math_node = cmds.shadingNode("multiplyDivide",
                                n="foot_01_" + self.side + "_footRev_multdiv", au=True)
        for curr_trans in transforms:
            cmds.setAttr(negative_math_node + ".input2" + curr_trans, -1)

        # Attach the IK_FK_Switch to the newly created nodes, for all of the first input.
        # IK_switch_nodes = [IK_switch_node1, IK_switch_node2]
        for curr_trans in transforms:
            cmds.connectAttr(self.foot_cc + ".IK_FK_Switch",
                             IK_switch_nodes[0] + ".input1" + curr_trans, f=True)
        for curr_trans in transforms:
            cmds.connectAttr(self.foot_cc + ".IK_FK_Switch",
                             IK_switch_nodes[1] + ".input1" + curr_trans, f=True)

        # Attach the foot attrs to the second inputs of the math nodes.
        # foot_attrs = ["ballRoll", "toeRoll", "heelRoll", "bank",
        #               "toePivot", "heelPivot"]
        cmds.connectAttr(self.foot_cc + "." + foot_attrs[0],
                         IK_switch_nodes[0] + ".input2X", f=True)
        cmds.connectAttr(self.foot_cc + "." + foot_attrs[1],
                         IK_switch_nodes[0] + ".input2Y", f=True)
        cmds.connectAttr(self.foot_cc + "." + foot_attrs[2],
                         IK_switch_nodes[0] + ".input2Z", f=True)
        cmds.connectAttr(self.foot_cc + "." + foot_attrs[3],
                         IK_switch_nodes[1] + ".input2X", f=True)
        cmds.connectAttr(self.foot_cc + "." + foot_attrs[4],
                         IK_switch_nodes[1] + ".input2Y", f=True)
        cmds.connectAttr(self.foot_cc + "." + foot_attrs[5],
                         IK_switch_nodes[1] + ".input2Z", f=True)

        # revFoot_grp_list = ["revBallFix_*SIDE*_grp", "revBall_*SIDE*_grp,
        #                     "revToe_*SIDE*_grp, "revHeel_*SIDE*_grp,
        #                     "revOutBank_*SIDE*_grp, "revInBank_*SIDE*_grp]

        # The ball fix group, roll
        cmds.connectAttr(IK_switch_nodes[0] + ".outputX",
                         negative_math_node + ".input1X", f=True)
        cmds.connectAttr(negative_math_node + ".outputX",
                         revFoot_grp_list[0] + ".rx", f=True)

        # The ball group, roll
        cmds.connectAttr(IK_switch_nodes[0] + ".outputX",
                         revFoot_grp_list[1] + ".rx", f=True)

        # The toe group, roll
        cmds.connectAttr(IK_switch_nodes[0] + ".outputY",
                         revFoot_grp_list[2] + ".rx", f=True)

        # The heel group, roll
        cmds.connectAttr(IK_switch_nodes[0] + ".outputZ",
                         revFoot_grp_list[3] + ".rx", f=True)

        # The out bank group
        cmds.connectAttr(IK_switch_nodes[1] + ".outputX",
                         revFoot_grp_list[4] + ".rz", f=True)
        # The in bank group
        cmds.connectAttr(IK_switch_nodes[1] + ".outputX",
                         revFoot_grp_list[5] + ".rz", f=True)
        if self.side == "l":
            cmds.transformLimits(revFoot_grp_list[5], rz=[0, 45], erz=[1, 0])
            cmds.transformLimits(revFoot_grp_list[4], rz=[0, 0], erz=[0, 1])
        elif self.side == "r":
            cmds.transformLimits(revFoot_grp_list[5], rz=[0, 0], erz=[0, 1])
            cmds.transformLimits(revFoot_grp_list[4], rz=[0, 45], erz=[1, 0])

        # The toe group, pivot
        cmds.connectAttr(IK_switch_nodes[1] + ".outputY",
                         revFoot_grp_list[2] + ".ry", f=True)

        # The heel group, roll
        cmds.connectAttr(IK_switch_nodes[1] + ".outputZ",
                         revFoot_grp_list[3] + ".ry", f=True)

    def clean_IK_foot(self, IK_cc):
        # Delete all the joints of the IK cc. When creating the foot, we made duplicates.
        children = cmds.listRelatives(self.foot_cc, allDescendents=True, type="joint")
        cmds.delete(children)

        # Get the rpIK and the last group, revBall_*SIDE*_grp1 of the hierarchy.
        rpIK = cmds.listRelatives(IK_cc, type="ikHandle")[0]
        new_chilren_list = cmds.listRelatives(self.foot_cc, allDescendents=True)
        revBallDup_index = new_chilren_list.index("revBall_" + self.side +
                                                  "_grp" + self.extra_indicator)

        # Group, parent under the foot IK CC and parent the rpIK
        foot_dup_grp = cmds.group(self.foot_cc, n="footDup_" + self.side + "_grp")
        cmds.parent(foot_dup_grp, IK_cc)
        cmds.parent(rpIK, new_chilren_list[revBallDup_index])

        cmds.setAttr(self.foot_cc + ".v", 0)

class CreateSpine(object):
    """
    This class will create a spine rig.
    """
    def __init__(self, root_jnt, IK_cc):
        self.spine_jnt_list = [root_jnt]
        self.base_IK_cc = IK_cc
        self.spine_crv = ""
        self.spine_surf = ""
        self.spine_IK_list = []
        self.follicles_grp = ""
        self.cog_cc = ""
        self.IK_color = 0
        self.cog_color = 0

    def create_spine(self):
        self.fill_spine_list()
        spine_surf = self.create_curve()
        self.dup_IK_cc()
        self.color_cc()
        self.create_IK()
        self.create_cog()

        spine_objs = [self.cog_cc, self.spine_crv, self.spine_surf, self.follicles_grp]
        return spine_objs

    def dup_IK_cc(self):
        self.base_IK_cc = cmds.duplicate(self.base_IK_cc, n="spine_IKDup_cc")[0]
        cmds.setAttr(self.base_IK_cc + ".rotateZ", 90)
        cmds.makeIdentity(self.base_IK_cc, a=True, n=0, pn=True, t=True, r=True, s=True)

    def fill_spine_list(self):
        curr_jnt = cmds.listRelatives(self.spine_jnt_list[0])[0]
        while cmds.listRelatives(curr_jnt):
            self.spine_jnt_list.append(curr_jnt)
            if (curr_jnt == "spine_04_jnt"):
                break
            else:
                curr_jnt = cmds.listRelatives(curr_jnt)[0]
        cmds.parent("neck_01_jnt", world=True)

    def create_curve(self):
        # Get the position of the spine joints, to position the CVs easiest.
        spine_jnt_pos = []
        for curr_jnt in self.spine_jnt_list:
            pos = cmds.xform(curr_jnt, worldSpace=True, translation=True, query=True)
            spine_jnt_pos.append(pos)

        # Make the curve and rebuild it for more definition.
        self.spine_crv = cmds.curve(degree=1, point=[spine_jnt_pos[0], spine_jnt_pos[1],
                                                     spine_jnt_pos[2], spine_jnt_pos[3],
                                                     spine_jnt_pos[4]],
                                    knot=[0,1,2,3,4], n="spine_crv")
        cmds.rebuildCurve(self.spine_crv, replaceOriginal=True,
                          rebuildType=0, end=1, keepRange=0, keepEndPoints=True,
                          keepTangents=0, spans=4, degree=3, tolerance=0.01)

        # Make the loft surface and the hair follicles, and delete the extras.
        duplicate_curve1 = cmds.duplicate(self.spine_crv, n="spine_crv2")[0]
        cmds.setAttr(self.spine_crv + ".translateX", 0.5)
        cmds.setAttr(duplicate_curve1 + ".translateX", -0.5)
        self.spine_surf = cmds.loft(self.spine_crv, duplicate_curve1,
                  constructionHistory=True, uniform=True, close=False,
                  autoReverse=1, degree=3, sectionSpans=1,
                  range=False, polygon=0, reverseSurfaceNormals=True,
                  n="spine_surf")[0]
        cmds.select(self.spine_surf, replace=True)
        mel.eval("createHair 5 1 10 0 0 1 0 5 0 2 1 1;")
        cmds.delete("hairSystem1", "hairSystem1OutputCurves", "nucleus1",
                    duplicate_curve1)
        self.follicles_grp = cmds.rename("hairSystem1Follicles", "spine_follicles_grp")
        follicles_list = cmds.listRelatives(self.follicles_grp)
        follic_count = 1
        for curr_follic in follicles_list:
            curr_follic = cmds.rename(curr_follic, "spine_follicle_" + str(follic_count))
            follic_jnt = cmds.joint(n="spine_bind_%s_jnt" % follic_count,
                                    position=[0,0,0])
            cmds.parent(follic_jnt, curr_follic)
            cmds.setAttr(follic_jnt + ".translate", 0, 0, 0, type="double3")
            follic_count = follic_count + 1

        cmds.setAttr(self.spine_crv + ".translateX", 0)

    def create_IK(self):
        counter = 0
        IK_bind_list = []
        IK_pos = ["pelvis", "", "abs", "", "chest"]
        while counter < 5:
            IK_jnt = cmds.duplicate(self.spine_jnt_list[counter],
                                    n=IK_pos[counter] + "_jnt", parentOnly=True)[0]
            if "pelvis" not in IK_jnt:
                cmds.parent(IK_jnt, world=True)
            IK_cc = cmds.duplicate(self.base_IK_cc, n=IK_pos[counter] + "_cc")[0]
            cmds.parent(IK_cc, IK_jnt)
            cmds.setAttr(IK_cc + ".translate", 0, 0, 0, type="double3")
            cmds.parent(IK_cc, world=True)
            cmds.makeIdentity(IK_cc, a=True, n=0, pn=True, t=True, r=True,
                              s=True)
            cmds.parent(IK_jnt, IK_cc)
            IK_cc_grp = cmds.group(IK_cc, n=IK_pos[counter] + "_grp")

            self.spine_IK_list.append(IK_cc_grp)
            IK_bind_list.append(IK_jnt)
            counter = counter + 2

            if "pelvis" in IK_cc_grp:
                cmds.parent(IK_cc_grp, "root_jnt")
            elif "abs" in IK_cc_grp:
                cmds.parent(IK_cc_grp, "spine_02_jnt")
            elif "chest" in IK_cc_grp:
                cmds.parent(IK_cc_grp, "spine_04_jnt")

        cmds.skinCluster(IK_bind_list, self.spine_surf)

    def create_cog(self):
        self.cog_cc = cmds.duplicate("box_cc", n="cog_cc")[0]
        cog_cc_shape = cmds.listRelatives(self.cog_cc, fullPath=True)[0]
        cmds.setAttr(cog_cc_shape + ".overrideEnabled", 1)
        cmds.setAttr(cog_cc_shape + ".overrideColor", self.cog_color)

        root_jnt = "root_jnt"
        cmds.parent(self.cog_cc, root_jnt)
        cmds.setAttr(self.cog_cc + ".translate", 0, 0, 0, type="double3")
        cmds.parent(self.cog_cc, world=True)
        cmds.makeIdentity(self.cog_cc, a=True, n=0, pn=True, t=True, r=True,
                          s=True)
        cmds.parent(root_jnt, self.cog_cc)

        # Clean up the extra nodes.
        cmds.delete(self.base_IK_cc)

    def color_cc(self):
        self.IK_color = 14
        self.cog_color = 17

        IK_cc_shape = cmds.listRelatives(self.base_IK_cc)[0]

        cmds.setAttr(IK_cc_shape + ".overrideEnabled", 1)
        cmds.setAttr(IK_cc_shape + ".overrideColor", self.IK_color)

class CreateHead(object):
    """
    This class creates simple head and neck controls.
    """
    def __init__(self, neck_jnt, head_jnt, neck_cc, arrow_cc):
        self.neck_jnt = neck_jnt
        self.head_jnt = head_jnt
        self.neck_cc = neck_cc
        self.head_cc = arrow_cc
        self.head_color = 0
        self.neck_color = 0

    def create(self):
        self.dup_cc()
        self.color_cc()
        self.create_neck()
        self.create_head()

        neck_cc = self.neck_jnt
        return neck_cc

    def dup_cc(self):
        self.neck_cc = cmds.duplicate(self.neck_cc, n="neck_cc")[0]
        self.head_cc = cmds.duplicate(self.head_cc, n="head_cc")[0]
        cmds.scale(0.1, 0.1, 0.1, self.head_cc)
        #cmds.setAttr(self.neck_cc + ".rotateZ", 90)
        cmds.makeIdentity(self.head_cc, a=True, n=0, pn=True, t=True, r=True, s=True)

    def create_neck(self):
        neck_cc_dup = cmds.duplicate(self.neck_cc, n="neck_dup_cc")[0]
        neck_cc_dup_shape = cmds.listRelatives(neck_cc_dup)[0]
        cmds.parent(neck_cc_dup_shape, self.neck_jnt, addObject=True, shape=True)
        cmds.delete(neck_cc_dup, self.neck_cc)

    def create_head(self):
        head_tip_jnt = cmds.listRelatives(self.head_jnt)[0]
        head_tip_jnt_pos = cmds.xform(head_tip_jnt, worldSpace=True, translation=True, query=True)
        head_tip_jnt_pos[1] = head_tip_jnt_pos[1] + 0.5

        head_jnt_pos = cmds.xform(self.head_jnt, worldSpace=True, translation=True, query=True)

        cmds.move(head_tip_jnt_pos[0], head_tip_jnt_pos[1], head_tip_jnt_pos[2], self.head_cc)
        cmds.makeIdentity(self.head_cc, a=True, n=0, pn=True, t=True, r=True, s=True)
        cmds.parent(self.head_jnt, self.head_cc)
        head_cc_grp = cmds.group(self.head_cc, n="head_cc_grp")

        cmds.move(head_jnt_pos[0], head_jnt_pos[1], head_jnt_pos[2], self.head_cc + ".rotatePivot",
                  self.head_cc + ".scalePivot", worldSpace=True)

        cmds.parent(head_cc_grp, self.neck_jnt)
        cmds.select(clear=True)

    def color_cc(self):
        self.head_color = 14
        self.neck_color = 14

        head_cc_shape = cmds.listRelatives(self.head_cc, fullPath=True)[0]
        cmds.setAttr(head_cc_shape + ".overrideEnabled", 1)
        cmds.setAttr(head_cc_shape + ".overrideColor", self.head_color)

        neck_cc_shape = cmds.listRelatives(self.neck_cc)[0]
        cmds.setAttr(neck_cc_shape + ".overrideEnabled", 1)
        cmds.setAttr(neck_cc_shape + ".overrideColor", self.neck_color)

class CreateGlobalControls(object):
    """
    This class creates the master groups for the rig.
    """
    def __init__(self, arrow_cc):
        self.globalControl01 = arrow_cc

    def create_gc(self):
        # Color variables
        gc1_color = 17
        gc2_color = 6
        gc3_color = 13

        master_grp = cmds.group(name="master", empty=True)
        extras_grp = cmds.group(name="extra", parent=master_grp, empty=True)
        geo_grp = cmds.group(name="geo", parent=master_grp, empty=True)

        globalControl02 = cmds.circle(name="globalControl02", center=(0,0,0),
                                      normal=(0,1,0))[0]
        cmds.scale(5.25, 5.25, 5.25, globalControl02)
        cmds.makeIdentity(globalControl02, a=True, n=0, pn=True, t=True, r=True, s=True)

        globalControl03 = cmds.circle(name="globalControl03", center=(0,0,0),
                                      normal=(0,1,0))[0]
        cmds.scale(5.7, 5.7, 5.7, globalControl03)
        cmds.makeIdentity(globalControl03, a=True, n=0, pn=True, t=True, r=True, s=True)

        self.globalControl01 = cmds.rename(self.globalControl01, "globalControl01")

        # Color the globalControl01
        gc1_shape = cmds.listRelatives(self.globalControl01, fullPath=True)[0]
        cmds.setAttr(gc1_shape + ".overrideEnabled", 1)
        cmds.setAttr(gc1_shape + ".overrideColor", gc1_color)

        # Color the globalControl02
        gc2_shape = cmds.listRelatives(globalControl02, fullPath=True)[0]
        cmds.setAttr(gc2_shape + ".overrideEnabled", 1)
        cmds.setAttr(gc2_shape + ".overrideColor", gc2_color)

        # Color the globalControl03
        gc3_shape = cmds.listRelatives(globalControl03, fullPath=True)[0]
        cmds.setAttr(gc3_shape + ".overrideEnabled", 1)
        cmds.setAttr(gc3_shape + ".overrideColor", gc3_color)

        cmds.parent(self.globalControl01, globalControl02)
        cmds.parent(globalControl02, globalControl03, relative=True)
        cmds.parent(globalControl03, master_grp, relative=True)

        master_grps = [self.globalControl01, extras_grp]
        cmds.setAttr(extras_grp + ".visibility", 0)

        return master_grps