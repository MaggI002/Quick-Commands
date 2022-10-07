import math
from blessed import Terminal
from time import sleep
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



# Make cmd_return_func. If under class, edit somewhere around line 180 (dont forget to add class_name.cmd_return_func())


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
            o = file[i][1].replace("`", "")
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
                                switch(0, self, last_file.pop(-1))
                        if selection == -1:
                            selection = len(self.list) - 1 - self.get_comments_above(0, True)
                        else:
                            comments_above = self.get_comments_above(selection)
                            selection = selection % (len(self.list) - comments_above)

    def enter(self, string):
        part_list = string.split("`")
        out_list = list(part_list)
        temp_var = ""
        for i, part in enumerate(part_list):
            if i % 2 == 0:
                continue
            else:
                temp_var = self.edit_str(part)
                if temp_var == "esc pressed, make sure nóbǒdy ťýpë$ thIś öň accident}~€Đđ&#°↓¶ŧ":
                    out_list[i] = part
                else:
                    out_list[i] = temp_var
        s = ""
        for part in out_list:
            s += part
        if temp_var == "esc pressed, make sure nóbǒdy ťýpë$ thIś öň accident~€Đđ&#°↓¶ŧ":
            return s, "esc pressed, make sure nóbǒdy ťýpë$ thIś öň accident~€Đđ&#°↓¶ŧ"
        return s, 0

    def edit_str(self, part):
        cursor = len(part)
        edit_str_inprogress = True
        with term.fullscreen():
            with term.cbreak():
                while edit_str_inprogress:
                    display.print_enter_line(part, cursor)
                    # Check whether space is a sequence or not
                    key = term.inkey()
                    if key.is_sequence:
                        if key.name == 'KEY_BACKSPACE':
                            part = part[:(cursor - 1)] + part[cursor:]
                            cursor -= 1
                        if key.name == 'KEY_LEFT':
                            cursor -= 1
                        if key.name == 'KEY_RIGHT':
                            cursor += 1
                        if key.name == 'KEY_ENTER':
                            edit_str_inprogress = False
                        if key.name == 'KEY_ESCAPE':
                            return "esc pressed, make sure nóbǒdy ťýpë$ thIś öň accident}~€Đđ&#°↓¶ŧ"
                        if cursor > len(part):
                            cursor = len(part)
                        if cursor < 0:
                            cursor = 0
                    else:
                        sth = part[:cursor]
                        part = part[:cursor] + key + part[cursor:]
                        cursor += 1
                return part

    def display_menu(self, selection):
        comments_above = self.get_comments_above(selection)
        for i, line in enumerate(self.list):
            if i == selection + comments_above:
                display.print_line(line[0], True)
            else:
                display.print_line(line[0], False)
    
    def get_comments_above(self, selection, get_total_comments = False):
        comments_above = 0
        for i, line in enumerate(self.list):
            if line[0][0] == "#":
                comments_above += 1
            if get_total_comments == False:
                if i == selection + comments_above:
                    break
        return comments_above

    def run_action(self, selection):
        comments_above = self.get_comments_above(selection)
        selection += comments_above
        # First letter of the second item in the selected tuple
        if self.list[selection][1][0] == ":":
            switch(selection, self)
        elif self.list[selection][1][0] == ">":
            self.rewrite_line(self.list[selection][1])
            settings.load_settings()
            self.__init__(self.file)
        else:
            self.run_command(selection)
         
    def run_command(self, selection):
        print(term.clear())
        command = self.enter(self.list[selection][1])
        if command[1] == "0":
            global last_file
            switch(0, self, last_file.pop(-1))
            return
        final_command = self.check_for_reference(command[0])
        os.system(final_command)
        if settings.cmd_return == True:
            self.cmd_return_func(self.list[selection][1])

    def check_for_reference(self, line):
        line = line.replace("<working_dir>", str(CURRENT_DIR))
        return line

    def cmd_return_func(self, selection):
        display.part_buffer.clear()
        display.append_normal("\n\n\n")
        display.append_normal(f'Ran {selection}, press y to return to Quick Commands')
        display.print_part_buffer()
        with term.cbreak():
            key = term.inkey()
            if key == "y":
                switch(0, self, MAIN_MENU_FILE)
            else:
                exit()
        
    def rewrite_line(self, line, no_enter=False):
        line = line.split("<", 1)
        evaluated_ptr = line[0].strip(">")
        evaluated_ptr = evaluated_ptr.split(",")

        file = name_to_file[evaluated_ptr[0]]
        line_int = int(evaluated_ptr[1])
        original_ptr = line[0] + "<"
        str_to_enter = line[1]

        original_file = []
        write_list = []
        with open(file) as f:
            for line in f.readlines():
                original_file.append(line)
        with open(file, "w") as f:
            for i, line in enumerate(original_file):
                if (i + 1) == line_int:
                    if no_enter == False:
                        temp_var = self.enter(str_to_enter)
                    else: 
                        temp_var = str_to_enter, 0
                    write_list.append(original_ptr + "`" + temp_var[0] + "`\n")
                else:
                    write_list.append(line)
            f.writelines(write_list)
        if temp_var[1] == "esc pressed, make sure nóbǒdy ťýpë$ thIś öň accident}~€Đđ&#°↓¶ŧ":
            global last_file
            switch(0, self, last_file.pop(-1))


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

    def print_enter_line(self, part, cursor):
        print(term.clear())
        part = fold_line(part)
        if cursor > len(part) - 1:
            part += "_"
            self.append_normal(part[:cursor])
            self.append_underline(part[cursor])
        else:
            self.append_normal(part[:cursor])
            if part[cursor] == " ":
                self.append_highlited(part[cursor])
            else:
                self.append_underline(part[cursor])
            self.append_normal(part[(cursor + 1):])
        self.print_part_buffer()

    def append_with_format(self, line, format_of_str):
        if self.check_for_link(line):
            line = self.check_for_link(line)
            for i, part in enumerate(line):
                if i % 2 == 1:
                    self.append_link(part)
                else:
                    getattr(self, f'append_{format_of_str}')(part)
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

    def append_underline(self, line):
        color = f'{settings.accent_color}_underline'
        self.part_buffer.append((f'{getattr(term, color)}{line}{term.normal}'))

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
    for i in range(0, len(line), math.floor(max_width)):
        if i == 0:
            continue
        pointer = i + newlines * 2
        while line[pointer] != " ":
            pointer -= 1
        line = line[:pointer] + "\n" + line[pointer + 1:]
        newlines += 1
    return line

def fold_line(line):
    if line == "":
        return ""
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
    menu_entrys = []
    actions = []
    out = []
    with open(file) as f:
        for i, line in enumerate(f.readlines()):
            if line[0] == "#":
                menu_entrys.append(line.strip())
                actions.append("")
                comments_above += 1
            elif (i + comments_above) % 2 == 1:
                actions.append(line.strip())
            else:
                menu_entrys.append(line.strip())
    # Menu list first, coresponding actions or values second, put them in a tuple
    for i in range(len(menu_entrys)):
        t = (menu_entrys[i], actions[i])
        out.append(t)
    return out

def parse_string(string):
    string = string.split("<")
    string = str(string[1])
    if string.isdigit():
        return int(string)
    elif string in ("True", "False"):
        if string == "True":
            return True
        return False
    elif string.find("(") != -1:
        return eval(string)
    return string

def switch(selection, menu, file=None):
    if file:
        menu = Menu(file) 
    else:
            last_file.append(menu.file)
            # Get from list -> tuple (selection) -> action (second item) -> everything but the first character
            menu_name = menu.list[selection][1][1:]
            menu.__init__(name_to_file[menu_name])
            #menu = Menu(name_to_file[menu_name])

settings = Settings()
display = Display()

if settings.first_run == True:
    print("Use UP and DOWN to navigate menu (scrolling also works), ENTER to confirm and ESCAPE to return or cancel.")
    print(f"All the menus are in the form of files, found at {CURRENT_DIR}, feel free to edit any of them.")
    sleep(7)
    Menu.rewrite_line(Menu, ">options,2<0", no_enter=True)

menu = Menu(MAIN_MENU_FILE)
