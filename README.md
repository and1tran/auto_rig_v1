# Auto-rig v1.05 for Maya 2022+

This tool is meant for bipeds. The GUI only has two buttons. A lot of customization and user input is left out due to keeping the rigging simple and fast. The rig will include reverse foot control and a ribbon spine.

Originally made in Python 2.7, upgraded to Python 3.7

## Installation

Place the auto_rig_v1.05 in your maya scripts folder. Maya, by default, will 
install this on your Documents folder. Your path may look like this:

C:\Users\Andy\Documents\maya\2022\scripts

## Function

Open Maya, and open your script editor to Python. Copy and paste the following 
code to run.

import auto_rig_v1.guis.auto_rig_gui as argui
gui = argui.AutoRigGUI()
gui.init_gui()

Step 1. Place joints - 
This will load up a basic biped joint skeleton for the user to position the joints.

Step 2. Make Rig - 
This will create the rig from the base skeleton in Step 1.

## Constraints

No option to orient joints.

User input for finger count.

User input for toe count.

User input for spine count.

No scaling - The control curves won't scale automatically and needs to be manually
scaled.

No CC customization.

Hierarchy must not be altered. The code depends on the naming convention. I
know this is strict, but we are working addressing this.
