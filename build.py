# -----------------
# Extension Details
# -----------------

name = "Space Station"
version = "0.1"
developer = "Type Supply"
developerURL = "http://typesupply.com"
roboFontVersion = "3.2"
pycOnly = False
menuItems = [
    dict(
        path="menu_glyphEditorSpaceStation.py",
        preferredName="Glyph Editor",
        shortKey=("command", "/")
    ),
    dict(
        path="menu_fontEditorSpaceStation.py",
        preferredName="Font Editor",
        shortKey=""
    )
]

installAfterBuild = True

# ----------------------
# Don't edit below here.
# ----------------------

from AppKit import *
import os
import shutil
from mojo.extensions import ExtensionBundle

# Convert short key modifiers.

modifierMap = {
	"command": NSCommandKeyMask,
    "control": NSAlternateKeyMask,
    "option": NSAlternateKeyMask,
    "shift": NSShiftKeyMask,
    "capslock": NSAlphaShiftKeyMask,
}

for menuItem in menuItems:
	shortKey = menuItem.get("shortKey")
	if isinstance(shortKey, tuple):
		shortKey = list(shortKey)
		character = shortKey.pop(-1)
		modifiers = [modifierMap.get(modifier, modifier) for modifier in shortKey]
		if len(modifiers) == 1:
			modifiers = modifiers[0]
		else:
			m = None
			for modifier in modifiers:
				if m is None:
					m = modifier
				else:
					m |= modifier
			modifiers = m
		converted = (modifiers, character)
		menuItem["shortKey"] = tuple(converted)

# Make the various paths.

basePath = os.path.dirname(__file__)
sourcePath = os.path.join(basePath, "source")
libPath = os.path.join(sourcePath, "code")
licensePath = os.path.join(basePath, "license.txt")
requirementsPath = os.path.join(basePath, "requirements.txt")
extensionFile = "%s.roboFontExt" % name
buildPath = os.path.join(basePath, "build")
extensionPath = os.path.join(buildPath, extensionFile)

# Build the extension.

B = ExtensionBundle()
B.name = name
B.developer = developer
B.developerURL = developerURL
B.version = version
B.launchAtStartUp = True
B.mainScript = "main.py"
B.html = os.path.exists(os.path.join(sourcePath, "documentation", "index.html"))
B.requiresVersionMajor = roboFontVersion.split(".")[0]
B.requiresVersionMinor = roboFontVersion.split(".")[1]
B.addToMenu = menuItems
with open(licensePath) as license:
    B.license = license.read()
with open(requirementsPath) as requirements:
    B.requirements = requirements.read()
print("Building extension...", end=" ")
v = B.save(extensionPath, libPath=libPath, pycOnly=pycOnly)
print("done!")
errors = B.validationErrors()
if errors:
	print("Uh oh! There were errors:")
	print(errors)

# Install the extension.

if installAfterBuild:
	print("Installing extension...", end=" ")
	installDirectory = os.path.expanduser("~/Library/Application Support/RoboFont/plugins")
	installPath = os.path.join(installDirectory, extensionFile)
	if os.path.exists(installPath):
		shutil.rmtree(installPath)
	shutil.copytree(extensionPath, installPath)
	print("done!")
	print("RoboFont must now be restarted.")
