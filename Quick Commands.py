from blessed import Terminal
import os
import time
#from rich import print

APP_NAME = "Quick Commands"

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
term = Terminal()
CMD_FILE = CURRENT_DIR + "/commands.conf"
EDITOR_FILE = CURRENT_DIR + "/editors.conf"
OPTIONS_FILE = CURRENT_DIR + "/options.conf"

# Menu entrys
MAIN_MENU = ["Run a command", "Edit commands", "Options", "Help", "Exit"]
cmdMenu = []
commands = []
EDIT_CMD_MENU = ["Commands are located in the same directory as this file, {}\nThe config file has one line as a description of the command and the line right after it as the command. It skips comments.\nTo add a comment, put a hash symbol at the begining of the line. Must be before a description or after a command.\nTo add a space to fill in into the command (for example for an URL), add a description into the command of what to enter surrounded with backticks like this: `This is a description of what to enter`\nWhen using a terminal application supporting hyperlinks, dollar signs can be used to add them to a description or a comment with the folowing syntax: [dollar sign]text,URL[dollar sign]\nIf your terminal application does not support them, you can disable hyperlinks in the settings, which will also p URL\n$Click me!,https://bit.ly/3uTw3UC$\nYou might not have some of the editors listed here, please pick one that you have and want to use. If you do not have any of these editors, you can edit editor list found in the same directory, same syntax applies.\nPress ENTER to select an editor\nPress ESC to cancel".format(CMD_FILE)]
editorsMenu = []
editCommands = []
options = []
optionsValues = []
HELP = ["Use UP and DOWN to change your selection, ENTER to confirm and ESC to return or exit."]

MENU_LIST = {0:cmdMenu, 1:EDIT_CMD_MENU, 2:options, 3:HELP, 4:"Exit"}


# Defining global variables
lastMenu = MAIN_MENU

term.fullscreen()

def fold_text(selectedMenu):
    maxWidth = round((term.width/4)*3+2)
    if term.width < 37:
        print("Your console window is not wide enough. This application might have some problems running.")
        exit()
    for i, s in enumerate(selectedMenu):
        if len(s) * 2 > maxWidth and s.find("\n") != -1:
            s = s.split("\n")
            s = fold_text(s)
            st2 = ""
            for st in s:
                st += "\n"
                st2 += st
            s = st2
        elif len(s) > maxWidth:
            i2 = 0
            while s[maxWidth - i2] != " ":
                i2 += 1
            s = s[0:(maxWidth - i2)] + "\n" + s[(maxWidth - i2 + 1):len(s)]
            if len(s) > maxWidth:
                s = s.split("\n")
                s = fold_text(s)
                st2 = ""
                for st in s:
                    st2 += st
            s = st2
        else:
            s += "\n"
        selectedMenu[i] = s
        s = ""
    return selectedMenu

# Import from config files
def import_conf():
    # Import cmdMenu and commands
    commentsAbove = 0
    with open(CMD_FILE) as f:
        for i, line in enumerate(f.readlines()):
            if line.find("#") != -1:
                cmdMenu.append(line.strip())
                commentsAbove += 1
            elif (i - commentsAbove) % 2 == 1:
                commands.append(line.strip())
            else:
                cmdMenu.append(line.strip())
    # Import editCommands and editorsMenu
    commentsAbove = 0
    with open(EDITOR_FILE) as f:
        for i, line in enumerate(f.readlines()):
            if line.find("#") != -1:
                editorsMenu.append(line.strip())
                commentsAbove += 1
            elif (i - commentsAbove) % 2 == 1:
                editCommands.append(line.strip())
            else:
                editorsMenu.append(line.strip())
    # Import options and optionsValues
    with open(OPTIONS_FILE) as f:
        for i, line in enumerate(f.readlines()):
            if line.find("#") != -1:
                options.append(line.strip())
                commentsAbove += 1
            elif (i - commentsAbove) % 2 == 1:
                optionsValues.append(line.strip())
            else:
                options.append(line.strip())
    return commands, cmdMenu, editCommands, editorsMenu

commands, cmdMenu, editCommands, editorsMenu = import_conf()


# Function for displaying a menu
def display_menu(selection, selectedMenu):
    maxWidth = round((term.width/4)*3+2)
    selectNotFound = True
    commentsAbove = 0
    commentsTotal = 0
    for s in selectedMenu:
        if len(s) > maxWidth and s.find("\n") != -1:
            selectedMenu = fold_text(selectedMenu)
    print(term.clear())
    for (i, name) in enumerate(selectedMenu):
        if name.find("#") != -1:
            name = name.replace("#", "    ")
            if name.find("$") != -1:
                name = name.split("$")
                for i, part in enumerate(name):
                    if i % 2 == 1:
                        part = part.split(",")
                        print(f'{term.underline_on_teal}{term.link(part[1],part[0])}{term.normal}', end ="")
                    else:
                        print('{t.bold_teal}{title}{t.normal}'.format(t=term, title=part), end ="")
                print()
            else:
                print('{t.bold_teal}{title}{t.normal}'.format(t=term, title=name))
                commentsTotal += 1
            if selectNotFound:
                commentsAbove += 1
        elif i - commentsAbove == selection:
            if name.find("$") != -1:
                name = name.split("$")
                for i, part in enumerate(name):
                    if i % 2 == 1:
                        part = part.split(",")
                        print(f'{term.underline_teal_on_white}{term.link(part[1],part[0])}{term.normal}', end ="")
                    else:
                        print('{t.bold_on_teal}{title}{t.normal}'.format(t=term, title=part), end ="")
                print()
            else:
                print('{t.bold_on_teal}{title}{t.normal}'.format(t=term, title=name))
                selectNotFound = False
        else:
            if name.find("$") != -1:
                name = name.split("$")
                for i, part in enumerate(name):
                    if i % 2 == 1:
                        part = part.split(",")
                        print(f'{term.underline}{term.link(part[1], part[0])}{term.normal}', end ="")
                    else:
                        print('{t.normal}{title}{t.normal}'.format(t=term, title=part), end ="")
                print()
            else:
                print('{t.normal}{title}'.format(t=term, title=name))
    return commentsAbove, commentsTotal


# Run selection 
def run_selection(selection, commentsAbove, selectedMenu):
    if selectedMenu == cmdMenu or selectedMenu == editorsMenu:
        print(term.turquoise_reverse('Running {}'.format(selectedMenu[selection + commentsAbove])))
        if selectedMenu == cmdMenu:
            st = commands[selection]
            if "`" in st:
                while "`" in st:
                    st = enter(st)
                os.system(st)
            else:
                os.system(commands[selection])
        else:
            os.system(editCommands[selection])
            print(term.turquoise("\nPress ENTER to go back to {}\n".format(APP_NAME), "Press an arrow key or TAB to exit {}".format(APP_NAME)))
            time.sleep(0.5)
            selection_inprogress = True
            with term.cbreak():
                while selection_inprogress:
                    key = term.inkey()
                    if key.is_sequence:
                        if key.name == "KEY_ENTER":
                            selection_inprogress = False
                            menu(MAIN_MENU)
                        else:
                            print(term.clear())
                            exit()
    elif selectedMenu == HELP:
        menu(MAIN_MENU)
    elif selectedMenu == EDIT_CMD_MENU:
        menu(editorsMenu)
    elif selectedMenu == options:
        s1 = ""
        s2 = ""
        s3 = ""
        with open(OPTIONS_FILE, "r") as f:
            for i, line in enumerate(f.readlines()):
                if i < selection * 2 + 1:
                    s1 += line
                elif i > selection * 2 + 1:
                    s3 += line
                else:
                    s2 = line.strip("\n")
        s2 = ("`" + enter(s2) + "`") + "\n"
        with open(OPTIONS_FILE, "w") as f:
            f.write(s1 + s2 + s3)
        menu(options)


# Function for entering stuff
def enter(enteredStr):
    st = ""
    enteredStr = enteredStr.split("`", 2)
    exitStr = enteredStr[1]
    cursor = len(enteredStr[1])
    selection_inprogress = True
    display_text(enteredStr, cursor)
    with term.cbreak():
        while selection_inprogress:
            key = term.inkey()
            if key.is_sequence:
                if key.name == "KEY_BACKSPACE":
                    if len(enteredStr[1]) > 0:
                        enteredStr[1] = enteredStr[1][0:cursor - 1] + enteredStr[1][cursor:len(enteredStr)]
                        cursor -= 1
                if key.name == "KEY_ENTER":
                    selection_inprogress = False
                if key.name == "KEY_ESCAPE":
                    return(exitStr)
                    exit()
                if key.name == "KEY_LEFT":
                    cursor -= 1
                if key.name == "KEY_RIGHT":
                    cursor += 1
            elif key:
                if cursor == len(enteredStr[1]):
                    enteredStr[1] = enteredStr[1] + key
                else:
                    enteredStr[1] = enteredStr[1][0:cursor] + key + enteredStr[1][-(len(enteredStr[1]) - cursor):]
                cursor += 1
            cursor = cursor % (len(enteredStr[1])+1)
            display_text(enteredStr, cursor)
    for value in enteredStr:
        st += value
    enteredStr = st
    print(term.clear())
    return enteredStr
    
def display_text(enteredStr, cursor):
    print(term.clear())
    if cursor == len(enteredStr[1]):
        print(term.teal(enteredStr[1]) + "_")
    else:
        for i, char in enumerate(enteredStr[1]):
            if i == cursor:
                print(term.teal_reverse(enteredStr[1][i]), end="")            
            else:    
                print(term.teal(enteredStr[1][i]), end="")

# Menu function
def menu(selectedMenu):
    global lastMenu
    commentsTotal = 0
    commentsAbove = 0
    selection = 0
    selection_inprogress = True
    with term.cbreak():
        while selection_inprogress:
            commentsAbove, commentsTotal = display_menu(selection, selectedMenu)
            key = term.inkey()
            if key.is_sequence:
                if key.name == 'KEY_TAB':
                    selection += 1
                if key.name == 'KEY_DOWN':
                    selection += 1
                if key.name == 'KEY_UP':
                    selection -= 1
                if key.name == 'KEY_ENTER':
                    selection_inprogress = False
                    if selectedMenu == MAIN_MENU:
                        if MENU_LIST[selection] == "Exit":
                            print(term.clear())
                            print(term.turquoise("Exiting"))
                            exit()
                        else:
                            lastMenu = selectedMenu
                            menu(MENU_LIST[selection])
                    else:
                        print(term.clear())
                        if selectedMenu != options:
                            lastMenu = selectedMenu
                        run_selection(selection, commentsAbove, selectedMenu)
                        exit()
                if key.name == "KEY_ESCAPE":
                    if selectedMenu == MAIN_MENU:
                        print(term.clear())
                        exit()
                    else:
                        menu(lastMenu)
            elif key:
                print("got {0}.".format(key))
            if selection == -1:
                selection = selection % (len(selectedMenu) - commentsTotal)
            else:
                selection = selection % (len(selectedMenu) - commentsAbove)
menu(MAIN_MENU)
