# -*- coding: utf-8 -*-
# GhidraDeepSeekDecomprove.py
# A Ghidra plugin to improve decompiled code readability by re-writing it (Using DeepSeek) in a better way, Along with renaming/assigning variables based on their usage.

#@author Zeyad Azima (https://zeyadazima.com/)
#@category Decompiler
#@keybinding Ctrl+Shift+D+A
#@menupath Tools.Decompiler.DeepSeek Code Improvement
#@toolbar 💣
#@runtime Jython

import json
import os
import random
from ghidra.util.task import ConsoleTaskMonitor
from ghidra.app.decompiler import DecompInterface
from ghidra.program.model.listing import FunctionManager
from ghidra.util import Msg
from javax.swing import JOptionPane, JTextArea, JScrollPane, JButton, JPanel, JFrame, JTextField
from java.awt import BorderLayout, GridLayout
from java.awt.datatransfer import StringSelection
from java.awt.Toolkit import getDefaultToolkit

# DeepSeek Chat API configuration
deepSeekChatApiUrl = "https://api.deepseek.com/v1/chat/completions"
deepSeekApiKey = "your_deepseek_api"

# Default output folder
defaultOutputFolder = "C:\\GhidraDeepSeek"

def sendToDeepSeekChat(code, addComments):
    """
    Sends the decompiled code to DeepSeek Chat for variable renaming.
    If addComments is True, instructs DeepSeek to add comments to explain the code.
    Only returns the improved code.
    """
    headers = {
        "Authorization": "Bearer " + deepSeekApiKey,  # Use string concatenation instead of f-strings
        "Content-Type": "application/json"
    }
    systemMessage = "You are a helpful assistant that improves the readability of decompiled code. Rename variables based on their usage. Do not modify function names and do not add any Explanation section. Only Return the improved code."
    if addComments:
        systemMessage += " Add comments to explain each code block."
    
    payload = {
        "model": "deepseek-coder",  # Use the appropriate model for code improvements
        "messages": [
            {
                "role": "system",
                "content": systemMessage
            },
            {
                "role": "user",
                "content": "Improve the readability of the following code by renaming variables based on their usage. Do not modify function names." + (
                    " Add comments to explain each code block." if addComments else ""
                ) + " Only return the improved code:\n\n" + code
            }
        ]
    }
    try:
        import urllib2  # Python 2.x library for HTTP requests
        req = urllib2.Request(deepSeekChatApiUrl, json.dumps(payload), headers)
        response = urllib2.urlopen(req)
        if response.getcode() == 200:
            responseData = json.loads(response.read())
            return responseData["choices"][0]["message"]["content"]
        else:
            Msg.error(None, "Error: {} - {}".format(response.getcode(), response.read()))
            return code
    except Exception as e:
        Msg.error(None, "Error sending request to DeepSeek Chat: {}".format(e))
        return code

def getDecompiledCode(function):
    """
    Extracts the decompiled code for a given function.
    """
    decompiler = DecompInterface()
    decompiler.openProgram(currentProgram)
    decompileResults = decompiler.decompileFunction(function, 30, ConsoleTaskMonitor())
    if decompileResults.decompileCompleted():
        return decompileResults.getDecompiledFunction().getC()
    else:
        Msg.error(None, "Decompilation failed for function: {}".format(function.getName()))
        return None

def generateUniqueFileName(outputFolder, functionName):
    """
    Generates a unique file name in the format {functionName}_{random_9_digit_number}_imp.c.
    Ensures the file does not already exist in the output folder.
    """
    while True:
        # Generate a random 9-digit number
        randomNumber = random.randint(100000000, 999999999)
        # Construct the file name
        fileName = "{}_{}_imp.c".format(functionName, randomNumber)
        filePath = os.path.join(outputFolder, fileName)
        # Check if the file already exists
        if not os.path.exists(filePath):
            return filePath

def saveImprovedCode(outputFolder, fileName, improvedCode):
    """
    Saves the improved code to a file in the specified output folder.
    """
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)  # Create the output folder if it doesn't exist

    # Save the improved code to the file
    outputFile = os.path.join(outputFolder, fileName)
    with open(outputFile, "w") as file:
        file.write(improvedCode)
    Msg.info(None, "Improved code saved to: {}".format(outputFile))

def getSortedFunctions():
    """
    Retrieves all functions in the current program, sorts them by name, and returns a list of (name, address).
    """
    functionList = []
    func = getFirstFunction()
    while func is not None:
        functionName = func.getName()
        functionAddress = func.getEntryPoint().toString()
        functionList.append((functionName, functionAddress))
        func = getFunctionAfter(func)
    
    # Sort the functions by name
    functionList.sort(key=lambda x: x[0])  # Sort by function name
    return functionList

def displayCodePopup(code):
    """
    Displays the improved code in a popup window with a Copy button and a Close button.
    """
    # Create the popup window
    frame = JFrame("Improved Code")
    frame.setSize(600, 400)
    frame.setLayout(BorderLayout())

    # Create a text area to display the code
    textArea = JTextArea(code)
    textArea.setEditable(False)
    scrollPane = JScrollPane(textArea)
    frame.add(scrollPane, BorderLayout.CENTER)

    # Create a panel for the buttons
    buttonPanel = JPanel()
    buttonPanel.setLayout(GridLayout(1, 2))

    # Add a Copy button
    copyButton = JButton("Copy", actionPerformed=lambda e: copyToClipboard(code))
    buttonPanel.add(copyButton)

    # Add a Close button
    closeButton = JButton("Close", actionPerformed=lambda e: frame.dispose())
    buttonPanel.add(closeButton)

    # Add the button panel to the frame
    frame.add(buttonPanel, BorderLayout.SOUTH)

    # Add a footer to the frame
    footer = JTextArea("By: Zeyad Azima\nWebsite: zeyadazima.com")
    footer.setEditable(False)
    frame.add(footer, BorderLayout.NORTH)

    # Display the frame
    frame.setVisible(True)

def copyToClipboard(text):
    """
    Copies the given text to the clipboard.
    """
    clipboard = getDefaultToolkit().getSystemClipboard()
    clipboard.setContents(StringSelection(text), None)
    Msg.info(None, "Code copied to clipboard.")

def askFileName(defaultName):
    """
    Asks the user if they want to name the file or use the default name.
    """
    response = JOptionPane.showInputDialog(
        None,
        "Enter a file name or use the default name:",
        "Save File",
        JOptionPane.QUESTION_MESSAGE,
        None,
        None,
        defaultName
    )
    return response if response else defaultName

def askAddComments():
    """
    Asks the user if they want to add comments to explain the code.
    """
    response = JOptionPane.showConfirmDialog(
        None,
        "Do you want to add comments to explain the code?",
        "Add Comments",
        JOptionPane.YES_NO_OPTION
    )
    return response == JOptionPane.YES_OPTION

def removeMarkers(code):
    """
    Removes the first and last lines of the response from DeepSeek (``` markers).
    """
    lines = code.splitlines()
    if len(lines) >= 2:
        return "\n".join(lines[1:-1])  # Remove the first and last lines
    return code

def improveDecompiledCode():
    """
    Improves the readability of decompiled code for a selected function in the current program.
    Only renames variables and returns the improved code.
    """
    # Prompt the user for the output folder path
    outputFolder = askString("Output Folder", "Enter the folder path to save improved code (default: C:\\GhidraDeepSeek):")
    if not outputFolder:
        outputFolder = defaultOutputFolder  # Use the default output folder if no path is provided

    # Get the sorted list of functions
    functionList = getSortedFunctions()
    if not functionList:
        Msg.error(None, "No functions found in the current program. Please analyze the binary first.")
        return

    # Prepare the list of choices for the dialog
    choices = []
    for functionName, functionAddress in functionList:
        choices.append(functionName + " @ " + functionAddress)

    # Display a dialog for the user to select one function
    selectedChoice = askChoice(
        "Select Function",  # Title of the dialog
        "Choose a function to improve:",  # Message displayed above the choices
        choices,  # List of choices (function names and addresses)
        choices[0]  # Default selection (first function in the list)
    )
    if not selectedChoice:
        Msg.error(None, "No function selected. Exiting.")
        return

    # Extract the function name and address from the selected choice
    functionName, functionAddress = selectedChoice.split(" @ ")
    functionManager = currentProgram.getFunctionManager()
    function = functionManager.getFunctionAt(currentProgram.getAddressFactory().getAddress(functionAddress))
    if function:
        decompiledCode = getDecompiledCode(function)
        if decompiledCode:
            Msg.info(None, "Original code for {}:\n{}\n".format(functionName, decompiledCode))

            # Ask the user if they want to add comments
            addComments = askAddComments()

            # Send the code to DeepSeek for improvement
            improvedCode = sendToDeepSeekChat(decompiledCode, addComments)
            Msg.info(None, "Improved code for {}:\n{}\n".format(functionName, improvedCode))

            # Remove the first and last lines (``` markers) from the improved code
            improvedCode = removeMarkers(improvedCode)

            # Ask the user if they want to name the file or use the default name
            defaultName = "{}_{}_imp.c".format(functionName, random.randint(100000000, 999999999))
            fileName = askFileName(defaultName)

            # Save the improved code to the specified file
            saveImprovedCode(outputFolder, fileName, improvedCode)

            # Display the improved code in a popup window
            displayCodePopup(improvedCode)
    else:
        Msg.error(None, "Function not found: {} @ {}".format(functionName, functionAddress))

# Run the plugin
improveDecompiledCode()
