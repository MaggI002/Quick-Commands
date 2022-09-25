import math
from blessed import Terminal
import os

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
term = Terminal()

MAIN_MENU_FILE = CURRENT_DIR + "/m-menu.txt"
COMMANDS_FILE = CURRENT_DIR + "/commands.conf"
EDITORS_FILE = CURRENT_DIR + "/editors.conf"
EDIT_INFO_FILE = CURRENT_DIR + "/edit-info.txt"
OPTIONS_FILE = CURRENT_DIR + "/options.conf"
HELP_MENU_FILE = CURRENT_DIR + "/help.txt"


last_file = []
name_to_file = {"main_menu":MAIN_MENU_FILE, "commands":COMMANDS_FILE, "edit_info":EDIT_INFO_FILE, "editors":EDITORS_FILE, "options":OPTIONS_FILE, "help_menu":HELP_MENU_FILE}


# I do not think there is currently a way to write to options, check this whole section before making anything tho

# run_command does not work, make cmd_return_func. If under class, edit somewhere around line 122 (add class_name.)


class Settings:
    def __init__(self):
        self.first_run = False
        self.cmd_return = False
        self.text_color = ""
        self.accent_color = ""
        self.max_width_formula = 0
        # Remember to change settings_to_add a few lines down
        
        self.load_settings()
    
    def load_settings(self):
        settings_to_add = [self.first_run, self.cmd_return, self.text_color, self.accent_color, self.max_width_formula]
        file = load_file(OPTIONS_FILE)
        for i, val in enumerate(settings_to_add):
            # The next variable is the option in the file without the backticks
            o = file[i][1].strip("`")
            settings_to_add[i] = parse_string(o)
        self.first_run, self.cmd_return, self.text_color, self.accent_color, self.max_width_formula = settings_to_add

class Menu:
    def __init__(self, file):
        # self.file might be useful for debug, 
        # can add an option to show this at the bottom of the screen for better nav
        self.file = file
        self.list = load_file(self.file)
        self.select()

    def select(self):
        selection = 0
        selection_inprogress = True
        with term.fullscreen():
            with term.cbreak():
                while selection_inprogress:
                    print(term.clear())
                    self.display_menu(selection)
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
                            self.run_action(selection)
                        if key.name == "KEY_ESCAPE":
                            selection_inprogress = False
                            if self.file == MAIN_MENU_FILE:
                                print(term.clear())
                                exit()
                            else:
                                global last_file
                                self.switch(0, last_file.pop(-1))
                        selection = selection % (len(self.list) - 1)
                
    def display_menu(self, selection):
        comments_above = self.get_comments_above(selection)
        for i, line in enumerate(self.list):
            if i == selection + comments_above:
                display.print_line(line[0], True)
            else:
                display.print_line(line[0], False)
    
    def get_comments_above(self, selection):
        comments_above = 0
        for i, line in enumerate(self.list):
            if line[0][0] == "#":
                comments_above += 1
            if i == selection + comments_above:
                break
        return comments_above

    def run_action(self, selection):
        comments_above = self.get_comments_above(selection)
        selection += comments_above
        # First letter of the second item in the selected tuple
        if self.list[selection][1][0] == ":":
            self.switch(selection)
        else:
            self.run_command(selection)

    def switch(self, selection, file=None):
        global last_file
        if file:
            self = Menu(file) 
        else:
                last_file.append(self.file)
                # Get from list -> tuple (selection) -> action (second item) -> everything but the first character
                menu_name = self.list[selection][1][1:]
                self = Menu(name_to_file[menu_name])
         
    def run_command(self, selection):
        os.system(self.list[selection][1])
        if settings.cmd_return == True:
            # cmd_return_func is WIP, does not work
            cmd_return_func(self.list[selection][1])

# A Display object is never created, for now refering to "display" (chceck in Menu -> display_menu())
# Make an enter_or_something() function for displaying the stuff to fill in when running a command or editing options, consider addind this to menu, not sure
class Display:
    def __init__(self):
        self.part_buffer = []

    def print_line(self, line, is_selected):
        line = fold_line(line)
        if line[0] == "#":
            line = "    " + line[1:]
            self.append_with_format(line, "comment")
        elif is_selected:
            self.append_with_format(line, "highlited")
        else:
            self.append_with_format(line, "normal")
        self.print_part_buffer()

    def append_with_format(self, line, format_of_str):
        if self.check_for_link(line):
            line = self.check_for_link(line)
            for i, part in enumerate(line):
                if i % 2 == 1:
                    self.append_link(part)
                else:
                    getattr(self, f'append_{format_of_str}')(line)
        else:
            getattr(self, f'append_{format_of_str}')(line)

    def check_for_link(self, line):
        out = []
        if line.find("$") != -1:
            list_from_line = line.split("$")
            for i, part in enumerate(list_from_line):
                if i % 2 == 1:
                    part = part.split(",")
                    tuple_of_link = (part[0], part[1])
                    out.append(tuple_of_link)
                else:
                    out.append(part)
            return out
        else:
            return False
            
    # when working check if you need two or one bracket after *.append
    def append_normal(self, line):
        self.part_buffer.append((f'{getattr(term, settings.text_color)}{line}{term.normal}'))
    
    def append_highlited(self, line):
        color = f'bold_{settings.text_color}_on_{settings.accent_color}'
        self.part_buffer.append((f'{getattr(term, color)}{line}{term.normal}'))

    def append_link(self, tuple_of_link):
        self.part_buffer.append(term.link(tuple_of_link[1], tuple_of_link[0]))

    def append_comment(self, line):
        self.part_buffer.append((f'{getattr(term, settings.accent_color)}{line}{term.normal}'))

    def print_part_buffer(self):
        for i in self.part_buffer:
            print(i, end="")
        print()
        self.part_buffer.clear()

def fold_anywhere(line):
    max_width = term.width
    for i in range(math.floor((len(line) / max_width))):
        line = line[:(max_width * (i + 1) + (i * len("\n")))] + "\n" + line[(max_width * (i + 1) + (i * len("\n"))):]
    return line + "\n"

def fold_at_space(line):
    max_width = settings.max_width_formula
    newlines = 0
    sth = range(0, len(line), math.floor(max_width))
    for i in range(0, len(line), math.floor(max_width)):
        if i == 0:
            continue
        pointer = i + newlines * 2
        sth = line[pointer]
        while line[pointer] != " ":
            pointer -= 1
        line = line[:pointer] + "\n" + line[pointer + 1:]
        newlines += 1
    return line

def fold_line(line):
    max_width = settings.max_width_formula

    # Get length of longest word
    longest_word_len = line.split()
    longest_word_len = sorted(longest_word_len, key=len)
    longest_word_len = len(longest_word_len[-1])

    if max_width < longest_word_len:
        line = fold_anywhere(line)
        return line
    elif max_width < len(line):
        line = fold_at_space(line)
        return line
    else:
        return line

def load_file(file):
    comments_above = 0
    menu = []
    actions = []
    out = []
    with open(file) as f:
        for i, line in enumerate(f.readlines()):
            if line.find("#") != -1:
                menu.append(line.strip())
                actions.append("")
                comments_above += 1
            elif (i + comments_above) % 2 == 1:
                actions.append(line.strip())
            else:
                menu.append(line.strip())
    # Menu list first, coresponding actions or values second, put them in a tuple
    for i in range(len(menu)):
        t = (menu[i], actions[i])
        out.append(t)
    return out

def parse_string(string):
    if string.isdigit():
        return int(string)
    elif string in ("True", "False"):
        if string == "True":
            return True
        return False
    elif string.find("(") != -1:
        return eval(string)
    return string



settings = Settings()
display = Display()
menu = Menu(MAIN_MENU_FILE)
