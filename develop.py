from AppKit import *
import os
import subprocess
import time
import shutil

robofont = "/usr/local/bin/robofont"
workspace = NSWorkspace.sharedWorkspace()
directory = os.path.dirname(__file__)
buildDirectory = os.path.join(directory, "build")
buildCompletedMarkerPath = os.path.join(buildDirectory, "build completed")
openDocumentsRecordPath = os.path.join(buildDirectory, "open documents")

if os.path.exists(buildCompletedMarkerPath):
    os.remove(buildCompletedMarkerPath)
if os.path.exists(openDocumentsRecordPath):
    os.remove(openDocumentsRecordPath)

# Build the extension.

print("Building extension...")

buildScriptPath = os.path.join(directory, "build.py")
subprocess.call([robofont, "-p", buildScriptPath])

buildCompletedMarkerCode = """
f = open("{buildCompletedMarkerPath}", "w")
f.write("")
f.close()
"""

buildCompletedMarkerCode = buildCompletedMarkerCode.format(
    buildCompletedMarkerPath=buildCompletedMarkerPath
)

success = False
subprocess.call([robofont, "-c", buildCompletedMarkerCode])

maxWaitTime = 5
startTime = time.time()
while 1:
    if os.path.exists(buildCompletedMarkerPath):
        os.remove(buildCompletedMarkerPath)
        success = True
        break
    if time.time() - startTime > maxWaitTime:
        print("Build execution timed out! Check output in RoboFont to see if there were errors.")
        break

if success:
    print("Built and installed.")

# Get open documents.

openDocumentsRecordCode = """
from AppKit import *
openDocumentPaths = []
for document in NSApp().orderedDocuments():
    url = document.fileURL()
    if url is not None:
        openDocumentPaths.append(url.path())
openDocumentPaths = "\\n".join(openDocumentPaths)
f = open("{openDocumentsRecordPath}", "w")
f.write(openDocumentPaths)
f.close()
"""

if success:
    print("Gathering open paths...")

    openDocumentsRecordCode = openDocumentsRecordCode.format(
        openDocumentsRecordPath=openDocumentsRecordPath
    )

    success = False
    subprocess.call([robofont, "-c", openDocumentsRecordCode])

    maxWaitTime = 5
    startTime = time.time()
    while 1:
        if os.path.exists(openDocumentsRecordPath):
            success = True
            break
        if time.time() - startTime > maxWaitTime:
            print("Failed gathering open documents.")
            break

# Reboot RoboFont.

if success:
    print("Rebooting RoboFont...")

    f = open(openDocumentsRecordPath, "r")
    openDocumentPaths = f.read().splitlines()
    f.close()
    os.remove(openDocumentsRecordPath)

    workspace = NSWorkspace.sharedWorkspace()

    # Shut down.
    NSRunningApplication.runningApplicationsWithBundleIdentifier_("com.typemytype.robofont3")[0].forceTerminate()

    # Launch.
    workspace.launchApplication_("RoboFont")

    # Reopen the documents.
    for path in openDocumentPaths:
        workspace.openFile_withApplication_(path, "RoboFont")

    print("RoboFont has been restored.")

print("Done.")