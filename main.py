# Cheat Codes:
#   > Level10 - The game starts at level 10
#   > StopKey - Enables a 'stop key' which stops the shape from falling
#   > SlowGame - Causes the shapes to fall slower
# Screen Resolution: 1600x900

# Imports modules needed for the program
from tkinter import *
from tkinter import messagebox
import tkinter.ttk as ttk
from random import choice
import sys
import os
import pickle

# Define global variables for the dimensions of the game window.
WIDTH = 300
HEIGHT = 500


class Shape:
    """ Allows the user to move the shape around the screen
        Allows the shape to collide with existing shapes on the canvas """
    def __init__(self, canvas):
        """ Defines values which are used in the 'Shape' class """
        # A tuple of possible in-game shapes
        self.start_point = (WIDTH / 2) - (20 / 2)
        self.shape_options = (
            ("o-block", "yellow", (1, 1), (1, 0), (0, 1), (0, 0)),
            ("i-block", "lightblue", (1, 1), (0, 1), (2, 1), (3, 1)),
            ("l-block", "orange", (1, 1), (0, 1), (2, 0), (2, 1)),
            ("j-block", "blue", (1, 1), (0, 1), (0, 0), (2, 1)),
            ("s-block", "green", (1, 1), (0, 1), (1, 0), (2, 0)),
            ("z-block", "red", (1, 1), (1, 0), (0, 0), (2, 1)),
            ("t-block", "purple", (1, 1), (0, 1), (1, 0), (2, 1))
        )
        self.shape = choice(self.shape_options)
        self.colour = self.shape[1]
        self.canvas = canvas
        # Each shape is built with multiple 'boxes'
        self.boxes = []

        for point in self.shape[2:6]:
            box = self.canvas.create_rectangle(
                point[0] * 20 + self.start_point,           # x1
                point[1] * 20,                              # y1
                point[0] * 20 + 20 + self.start_point,      # x2
                point[1] * 20 + 20,                         # y2
                fill=self.colour, tag="box")
            self.boxes.append(box)

    def check_move_shape(self, x, y, shape_grid):
        """ Checks if the shape can be moved to a new point on the canvas """
        for box in self.boxes:
            if not self.check_move_box(box, x, y, shape_grid):
                return False
        return True

    def check_move_box(self, box, x, y, shape_grid):
        """ Checks if each box in the shape can be moved to a new point"""
        coordinates = self.canvas.coords(box)
        coordinates = [value / 20 for value in coordinates]

        # False if the box's new y-coordinate exceeds the bottom of the canvas
        if coordinates[3] + y > len(shape_grid):
            return False
        # Returns false if the box's new x-coordinate is less than 0
        if coordinates[0] + x < 0:
            return False
        # False if the box's new x-coordinate exceeds the width of the canvas.
        if coordinates[2] + x > len(shape_grid[0]):
            return False
        # False if there is already a box in the current box's new coordinates
        if shape_grid[int(coordinates[1] + y)][int(coordinates[0] + x)] != 0:
            return False
        return True

    def get_shape_coordinates(self):
        """ Returns the coordinates of the shape's boxes from the canvas """
        new_shape = []
        for box in self.boxes:
            coordinates = self.canvas.coords(box)
            new_shape.append(coordinates)
        return new_shape

    def move(self, x, y, shape_grid):
        """ Checks if the shape can move to a valid point before moving it """
        if not self.check_move_shape(x, y, shape_grid):
            return False
        else:
            for box in self.boxes:
                self.canvas.move(box, x * 20, y * 20)
            return True

    def rotate(self, shape_grid):
        """ Rotates the shape 90 degrees clockwise """
        centre = self.canvas.coords(self.boxes[0])

        def get_rotation_coordinates(square):
            coordinates = self.canvas.coords(square)

            # translate the rotation to the origin
            x_difference = coordinates[0] - centre[0]
            y_difference = coordinates[1] - centre[1]

            # formula for rotation: x = xcos(angle) - ysin(angle)
            #                       y = xsin(angle) + ycos(angle)
            # since cos(90) = 0 and sin(90) = 1 this can be simplified to:
            #                       x = - y
            #                       y = x
            new_x = - y_difference
            new_y = x_difference

            # undo the translation to the origin
            new_x = new_x - x_difference
            new_y = new_y - y_difference

            return (new_x / 20), (new_y / 20)

        if self.shape[0] != "o-block":
            # Check if every box can move to the new rotation coordinates
            for box in self.boxes:
                x_move, y_move = get_rotation_coordinates(box)
                if not self.check_move_box(box, x_move, y_move, shape_grid):
                    return False

            # Move each box to it's new coordinates
            for box in self.boxes:
                x_move, y_move = get_rotation_coordinates(box)
                self.canvas.move(box, x_move * 20, y_move * 20)


class Game:
    """ Contains the main game loop """
    def __init__(self, master, game_save):
        """ Defines values which are used in the Game class """
        self.master = master
        self.master.configure(borderwidth=0)
        # Sets the keybinds and cheats to user set values
        self.keybinds = game_save[0]
        self.cheats = game_save[1]
        # The score is set to the value found in the saved game
        self.score = game_save[2]
        # If the user entered the 'Level10' cheat code
        # the game starts at level 10
        if "Level10" in self.cheats and self.score == 0:
            self.level = 10
        else:
            self.level = game_save[3]

        # If the user entered the 'SlowGame' cheat code
        # the game starts slower.
        if "SlowGame" in self.cheats:
            self.speed = 1000
        else:
            self.speed = 500
        self.counter = 1
        self.game_paused = False
        # Shapes are added to the shape grid when they stop moving
        # which is how collisions are detected.
        self.shape_grid = []
        for i in range(int(HEIGHT / 20)):
            self.shape_grid.append([0] * int(WIDTH / 20))

        self.v_statistics = StringVar()
        self.v_statistics.set("Level: 1, Score: 0")
        self.l_statistics = Label(self.master, textvariable=self.v_statistics, font="Calibri 20 bold")
        self.l_statistics.configure(background="black", foreground="white")
        self.l_statistics.pack()

        self.canvas = Canvas(self.master, width=WIDTH, height=HEIGHT)
        self.canvas.configure(background="black")
        self.canvas.pack(expand=True, side="top")
        self.initial_shape = True
        # A list of shapes is saved when the user saves their game
        self.idle_shapes = game_save[4]
        if len(self.idle_shapes) != 0:
            # Iterate through the contents of the list of saved shapes and draw them to the screen.
            for shape in self.idle_shapes:
                for box in shape[1]:
                    self.canvas.create_rectangle(box[0], box[1], box[2], box[3], fill=shape[2])
                    self.shape_grid[int(box[1] / 20)][int(box[0] / 20)] = 1

        # Draws a pause button to the screen.
        self.b_pause = Button(self.canvas, text="||", font="Calibri 10 bold", anchor=W)
        self.b_pause.configure(background="white", foreground="black")
        self.b_pause["command"] = self.pause_game
        self.b_pause_window = self.canvas.create_window(10, 10, anchor=NW, window=self.b_pause)

        self.master.bind("<Key>", self.handle_events)
        self.game_loop()

    def handle_events(self, event):
        """ Handles key inputs from the user """
        # Key input's will not be checked if the game is currently paused
        if not self.game_paused:
            # Movement keys
            if event.keysym == self.keybinds[0]:
                self.current_shape.move(-1, 0, self.shape_grid)
            elif event.keysym == self.keybinds[1]:
                self.current_shape.move(1, 0, self.shape_grid)
            elif event.keysym == self.keybinds[2]:
                self.current_shape.rotate(self.shape_grid)
            elif event.keysym == self.keybinds[3]:
                self.current_shape.move(0, 1, self.shape_grid)
        else:
            # Stop key
            if event.keysym == self.keybinds[4]:
                if "StopKey" in self.cheats:
                    self.toggle_stop()
        # Boss Key
        if event.keysym == self.keybinds[5]:
            self.boss_clicked()

    def toggle_stop(self):
        """ If the user has entered the "StopKey" cheat, a key can be used to stop the game """
        # Pauses the game without showing the pause menu
        if not self.game_paused:
            self.game_paused = True
        else:
            self.game_paused = False
            self.canvas.after(self.speed, self.game_loop)

    def pause_game(self):
        """ Shows a pause menu when the user clicks the pause button, where the user can Resume or Quit """
        self.game_paused = True
        self.pause_frame = Frame(self.canvas)
        self.pause_window = self.canvas.create_window((WIDTH / 2, HEIGHT / 2), window=self.pause_frame, anchor="center")

        self.l_pause = Label(self.pause_frame, text="PAUSED", font="Calibri 20 bold")
        self.l_pause.configure(background="black", foreground="white", borderwidth=0)
        self.l_pause.pack(padx=10, pady=10)

        self.e_enter = Entry(self.pause_frame, background="white")
        self.e_enter.insert(END, "Enter your name:")
        self.e_enter.pack(padx=10, pady=10)

        self.b_save = Button(self.pause_frame, text="Save & Quit")
        self.b_save["command"] = self.save_game
        self.b_save.configure(background="white", foreground="black", width=10)
        self.b_save.pack(padx=10, pady=10)

        self.b_quit = Button(self.pause_frame, text="Quit")
        self.b_quit.configure(background="white", foreground="black", width=10)
        self.b_quit["command"] = sys.exit
        self.b_quit.pack(padx=10, pady=10)

        self.b_resume = Button(self.pause_frame, text="Resume")
        self.b_resume.configure(background="white", foreground="black", width=10)
        self.b_resume["command"] = self.resume_game
        self.b_resume.pack(padx=10, pady=10)

    def save_game(self):
        """ Allows the user to save and quit, storing the game details which can be loaded when run in the future """
        new_save = [self.keybinds, self.cheats, self.score, self.level, self.idle_shapes]

        # Only saves the game if there are not 5 games already saved
        # - Similar to old, retro video games
        games_saved = len([file for file in os.listdir("SavedGames")])
        if games_saved < 5:
            new_save.append(self.e_enter.get())
            for shape in new_save[4]:
                if type(shape[1]) != list:
                    shape[1] = shape[1].get_shape_coordinates()
            directory = r"SavedGames\game" + str(games_saved + 1) + ".txt"
            # Pickle is used to add the data to a text file, so it can be written to and read from as a list.
            with open(directory, "wb") as file:
                pickle.dump(new_save, file)
            messagebox.showinfo("Success!", "Game Saved Successfully!")
            sys.exit(0)
        else:
            messagebox.showerror("Error!", "Already 5 games saved! Delete a Game to save some more!")
            sys.exit(0)

    def resume_game(self):
        """ Called when the user clicks 'Resume' on the pause menu """
        self.canvas.delete(self.pause_window)
        self.game_paused = False
        self.canvas.after(self.speed, self.game_loop)

    def boss_clicked(self):
        """ Called when the user clicks the boss key """
        if not self.game_paused:
            self.game_paused = True
            # Removes current widgets on the screen 
            self.l_statistics.pack_forget()
            self.canvas.pack_forget()

            # Places the 'boss key' image on the screen
            self.photo = PhotoImage(file="boss_image.gif")
            self.l_image = Label(self.master, image=self.photo, borderwidth=0)
            self.l_image.image = self.photo
            self.l_image.pack(fill="both", expand=True)

        elif self.game_paused:
            # Removes the boss key image and places the game back on the screen
            self.l_image.pack_forget()
            self.l_statistics.pack()
            self.canvas.pack(expand=True, side="top")
            self.game_paused = False
            self.canvas.after(self.speed, self.game_loop)

    def check_complete_lines(self):
        """ Called when a shape is placed on the bottom of the screen """
        # Adds the shape's coordinates to the shape_grid 
        current_coordinates = self.current_shape.get_shape_coordinates()
        new_coordinates = []
        for box in current_coordinates:
            current_x = int(box[2] / 20)
            current_y = int(box[3] / 20)
            new_coordinates.append([current_x, current_y])
        current_coordinates = new_coordinates

        for coordinates in current_coordinates:
            self.shape_grid[int(coordinates[1] - 1)][int(coordinates[0] - 1)] = 1

        # Iterates through the contents of shape_grid to see if there are any complete lines
        complete_row = []
        for row in self.shape_grid:
            if 0 not in row:
                row_y = (self.shape_grid.index(row) * 20)
                complete_row.append([row, row_y])

        # Deletes shapes on any lines that are complete 
        all_boxes = self.canvas.find_withtag("box")
        for row in complete_row:
            for box in all_boxes:
                if self.canvas.coords(box)[1] == row[1]:
                    self.canvas.delete(box)

            # Moves the rest of the shapes down
            all_boxes = self.canvas.find_withtag("box")
            for box in all_boxes:
                if self.canvas.coords(box)[1] < row[1]:
                    self.canvas.move(box, 0, 20)

            # Updates the contents of shape_grid
            self.shape_grid.remove(row[0])
            self.shape_grid.insert(0, [0] * int(WIDTH / 20))
        
        # Returns the number of complete rows so the game can be updated
        return len(complete_row)

    def game_loop(self):
        """ Main game loop which is run until the user loses the game """
        # Displays the first shape on the screen
        if self.initial_shape:
            self.current_shape = Shape(self.canvas)
            self.initial_shape = False

        # Checks whether the current shape is at the bottom of the screen
        if not self.current_shape.move(0, 1, self.shape_grid):
            self.idle_shapes.append([self.counter, self.current_shape, self.current_shape.shape[1]])
            # Updates score and counter values 
            self.score += 1 * (self.level + 1)
            complete_rows = self.check_complete_lines()
            self.counter += 1
            self.score += (self.level + 1) ** 2 * complete_rows
            # Creates a new shape
            self.current_shape = Shape(self.canvas)
            # Checks whether the current shape can fall to a valid position on the shape grid.
            if not self.current_shape.check_move_shape(0, 1, self.shape_grid):
                self.game_over()

        if self.counter == 5:
            # Updates level value 
            self.level += 1
            self.speed -= 20
            self.counter = 1

        if not self.game_paused:
            # Runs the game loop again if the game isn't paused
            self.canvas.after(self.speed, self.game_loop)

        # Updates the level and score label
        self.v_statistics.set("Level: %d, Score: %d" % (self.level, self.score))

    def game_over(self):
        """ Called when the user loses the game """
        self.game_paused = True
        # Removes the game canvas and switches frame to the "GameOver" frame.
        self.l_statistics.pack_forget()
        self.canvas.pack_forget()
        GameOver(self.master, self.score, self.level)


class Template:
    """ A parent class for GUI windows which allow them to be created more easily """
    def __init__(self, master, header):
        """Contains common attributes which will be shared by every frame"""
        self.master = master
        self.master.option_add('*Font', 'Calibri 14')
        self.master.option_add('*Background', '#90E3F7')
        self.master.option_add('*Foreground', 'black')
        self.master.option_add('*Label.Font', 'Calibri 14')
        self.master.option_add('*Label.Borderwidth', '1')
        self.master.option_add('*Label.Relief', 'solid')
        self.master.config(borderwidth=20, background="#D4F2F9")
        self.master.title("Tetris")

        self.main_frame = Frame(self.master)
        self.main_frame.config(padx=10, pady=10)
        self.main_frame.pack(expand=True)

        self.v_title = StringVar()
        self.v_title.set(header)
        self.l_title = Label(self.main_frame, textvariable=self.v_title, font="Calibri 18 bold")
        self.l_title.configure(background="#2D64A5", foreground="white")
        self.l_title.grid(pady=10, sticky="nsew", row=0, column=0, columnspan=10)

    def switch_frame(self, frame):
        self.main_frame.forget()
        frame(self.master)


class MainMenu(Template):
    """ Allows the user to easily navigate to other parts of the program """
    def __init__(self, master):
        """ Defines variables which are needed on the Main Menu """
        super().__init__(master, 'Tetris')
        self.master = master
        # Sets the size of the window to the screen resolution.
        self.master.geometry('1600x900+0+0')

        # Keeps a list of frames so the user can easily switch to them using buttons
        page_names = ["New Game", "Load Game", "Instructions", "View Leaderboard"]
        pages = [Options, LoadGame, Instructions, ViewLeaderboard]
        buttons = {}

        for i in range(len(page_names)):
            buttons[page_names[i]] = Button(self.main_frame, text=page_names[i], background="white")
            buttons[page_names[i]]["command"] = lambda frame=pages[i]: self.switch_frame(frame)
            buttons[page_names[i]].grid(row=i + 1, column=0, padx=10, pady=10, sticky="ew")
        buttons["Exit"] = Button(self.main_frame, text="Exit", background="white")
        buttons["Exit"]["command"] = sys.exit
        buttons["Exit"].grid(row=5, column=0, padx=10, pady=10, sticky="ew")

        # Displays an image on the main menu
        # https://upload.wikimedia.org/wikipedia/en/thumb/7/7d/Tetris_NES_cover_art.jpg/220px-Tetris_NES_cover_art.jpg
        self.photo = PhotoImage(file="cover.gif")
        self.l_image = Label(self.main_frame, image=self.photo)
        self.l_image.image = self.photo
        self.l_image.grid(row=1, column=1, rowspan=5)


class Options(Template):
    """ Allows the user to change the options of the game before starting """
    def __init__(self, master):
        """ Defines variables which are needed on the options frame """
        super().__init__(master, 'Options')
        self.master = master

        self.l_keybinds = Label(self.main_frame, text="Keybinds", borderwidth=0, font="Calibri 18 bold")
        self.l_keybinds.grid(row=1, column=0, columnspan=2)
        
        self.text = ["Move Left", "Move Right", "Rotate", "Fall", "Stop", "Boss Key"]
        self.default_binds = ["a", "d", "w", "s", "space", "q"]
        self.labels = {}
        # A list of all possible keybinds which the user can set game functions to.
        self.drop_options = [
            "space",
            "period",
            "comma",
            "semicolon",
            "backslash",
            "Left", "Right", "Down", "Up",
            "a", "b", "c", "d", "e", "f", "g", "h", "i", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v",
            "w", "x", "y", "z",
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"
        ]
        # A list of variables which store the contents of the drop menus.
        self.drop_entry = [StringVar(self.main_frame),
                           StringVar(self.main_frame),
                           StringVar(self.main_frame),
                           StringVar(self.main_frame),
                           StringVar(self.main_frame),
                           StringVar(self.main_frame)]
        self.drop_menus = {}

        # A for loop is used to efficiently create widgets.
        for i in range(len(self.text)):
            self.labels[self.text[i]] = Label(self.main_frame, text=self.text[i], borderwidth=0)
            self.labels[self.text[i]].grid(row=i + 2, column=0, padx=10, pady=10)
            # Creates drop menus, a dictionary is used to ensure that new drop menus are made
            self.drop_entry[i].set(self.default_binds[i])
            self.drop_menus[self.text[i]] = OptionMenu(self.main_frame, self.drop_entry[i], *self.drop_options)
            self.drop_menus[self.text[i]].configure(width=10, background="white")
            self.drop_menus[self.text[i]]["menu"].configure(background="white")
            self.drop_menus[self.text[i]].grid(row=i + 2, column=1, padx=10, pady=10)

        # List of cheat codes the user enters
        self.cheats = []
        # List of valid cheat codes
        self.cheat_codes = ["Level10", "StopKey", "SlowGame"]

        # Create the widgets needed to allow the user to enter cheat codes
        self.l_cheats = Label(self.main_frame, text="Cheats", borderwidth=0, font="Calibri 18 bold")
        self.l_cheats.grid(row=1, column=2, columnspan=2, padx=10, pady=10)

        self.l_cheats = Label(self.main_frame, text="Enter Cheat Code", borderwidth=0)
        self.l_cheats.grid(row=2, column=2, padx=10, pady=10)
        self.e_cheats = Entry(self.main_frame, background="white", width=15)
        self.e_cheats.grid(row=2, column=3, padx=10, pady=10)

        self.b_submit = Button(self.main_frame, text="Submit Cheat", background="white", width=15)
        self.b_submit["command"] = self.submit_cheat
        self.b_submit.grid(row=3, column=2, columnspan=2, padx=10, pady=10)

        # A button which allows the user to go back to the main menu
        self.b_back = Button(self.main_frame, text="Back", background="white", width=15)
        self.b_back["command"] = lambda frame=MainMenu: self.switch_frame(frame)
        self.b_back.grid(row=7, column=2, padx=10, pady=10, sticky="w")

        # A button which allows the user to start the game 
        self.b_start = Button(self.main_frame, text="Start Game", background="white", width=15)
        self.b_start["command"] = self.start_game
        self.b_start.grid(row=7, column=3, padx=10, pady=10, sticky="w")

    def submit_cheat(self):
        """ Called when the user clicks "submit" after entering a cheat code """
        cheat_entered = self.e_cheats.get()

        # Checks whether the user's input is a valid cheat code
        if cheat_entered in self.cheat_codes:
            # Checks whether the user has already entered the cheat code
            if cheat_entered in self.cheats:
                messagebox.showerror("Error!", "Cheat already entered")
            else:
                self.cheats.append(cheat_entered)
                messagebox.showinfo("Cheat Added", "Cheat Added! Score will not be added to the leaderboard!")
        else:
            messagebox.showerror("Error!", "Invalid Cheat Code!")

    def start_game(self):
        """ Called when the user clicks 'Start Game' on the options menu """
        temp_list = []
        same_item = False
        # Checks whethter the user has entered the same keybind for multiple game functions
        for item in self.drop_entry:
            temp_list.append(item.get())
            if temp_list.count(item.get()) > 1:
                same_item = True

        if same_item:
            messagebox.showerror("Error!", "Please do not enter the same keybinds!")
            for i in range(len(self.drop_entry)):
                self.drop_entry[i].set(self.default_binds[i])
        else:
            # If all keybinds are different, the game is started
            keybinds = [entry.get() for entry in self.drop_entry]
            self.master.configure(background="black")
            self.main_frame.pack_forget()
            # Since a new game is being started, default values for score and level are passed in as parameters.
            new_game = [keybinds, self.cheats, 0, 0, [], None]
            Game(self.master, new_game)


class LoadGame(Template):
    """ Allows the user to load and continue an existing game save """
    def __init__(self, master):
        """ Defines variables which are needed on the Load Game page"""
        super().__init__(master, 'Load Game')
        self.master = master

        # Labels and buttons are added to a list so they are not overwritten with each iteration of the for loop
        self.name_labels = []
        self.score_labels = []
        self.load_buttons = []
        self.delete_buttons = []
        self.game_saves = []
        number_saved = len([file for file in os.listdir("SavedGames")])
        # Create buttons to load / delete game saves
        for i in range(number_saved):
            directory = r"SavedGames\game" + str(i + 1) + ".txt"
            with open(directory, "rb") as file:
                self.saved_data = pickle.load(file)
            self.game_saves.append(self.saved_data)

            self.l_name = Label(self.main_frame, text=str(self.saved_data[5]))
            self.l_name.grid(row=i + 1, column=0, padx=10, pady=10)
            self.name_labels.append(self.l_name)

            self.l_score = Label(self.main_frame,
                                 text="Score: " + str(self.saved_data[2]) + " Level: " + str(self.saved_data[3]))
            self.l_score.grid(row=i + 1, column=1, padx=10, pady=10)
            self.score_labels.append(self.l_score)

            self.b_load = Button(self.main_frame, text="Load")
            self.b_load.configure(background="white", foreground="black")
            self.b_load["command"] = lambda index=i: self.load_save(index)
            self.b_load.grid(row=i + 1, column=2, padx=10, pady=10)
            self.load_buttons.append(self.b_load)

            self.b_delete = Button(self.main_frame, text="Delete")
            self.b_delete.configure(background="white", foreground="black")
            self.b_delete["command"] = lambda index=i: self.delete_save(index)
            self.b_delete.grid(row=i + 1, column=3, padx=10, pady=10)
            self.delete_buttons.append(self.b_delete)

        if number_saved == 0:
            self.l_nosaved = Label(self.main_frame, text="There are no saved games")
            self.l_nosaved.grid(row=1, padx=10, pady=10)

        self.b_back = Button(self.main_frame, text="Back", background="white", width=15)
        self.b_back["command"] = lambda frame=MainMenu: self.switch_frame(frame)
        self.b_back.grid(row=number_saved + 2, column=0, columnspan=3, padx=10, pady=10)

    def delete_save(self, index):
        """ Removes the game .txt file when the user wishes to delete a game """
        directory = r"SavedGames\game" + str(index + 1) + ".txt"
        os.remove(directory)
        messagebox.showinfo("Success!", "Saved Game has been deleted!")
        self.switch_frame(self.main_frame)

    def load_save(self, index):
        """ Loads a different game depending on which 'Load' button the user clicks on """
        self.master.configure(background="black")
        self.main_frame.pack_forget()
        Game(self.master, self.game_saves[index])


class Instructions(Template):
    """ Displays instrcutions for the game """
    def __init__(self, master):
        """ Defines variables which are needed on the Instructons page """
        super().__init__(master, 'Instructions')
        self.master = master

        self.instruction_list = [
            "Bring down blocks from the top of the screen. You can move the blocks around or rotate them.",
            "Your objective is to get all of the blocks to fill the empty space in a line at the bottom of the screen",
            "Your game is over if your pieces reach the top of the screen.",
            "Press the boss key to flip to an image that shows that you're really doing work!"]

        # The contents this variable updates to a new instruction when the user clicks on the next or previous button 
        self.v_instructions = StringVar()
        self.v_instructions.set(self.instruction_list[0])
        self.l_instructions = Message(self.main_frame, textvariable=self.v_instructions)
        self.l_instructions.config(justify="center")
        self.l_instructions.grid(row=1, columnspan=3, padx=10, pady=10)

        self.b_previous = Button(self.main_frame, text="<", background="white")
        self.b_previous["command"] = lambda increment=-1: self.switch_message(increment)
        self.b_previous.grid(row=2, column=0)

        self.b_back = Button(self.main_frame, text="Back", background="white", width=15)
        self.b_back["command"] = lambda frame=MainMenu: self.switch_frame(frame)
        self.b_back.grid(padx=10, pady=10, row=2, column=1, sticky="ew")

        self.b_next = Button(self.main_frame, text=">", background="white")
        self.b_next["command"] = lambda increment=1: self.switch_message(increment)
        self.b_next.grid(row=2, column=2)

    def switch_message(self, increment):
        """ Changes the current instruction when the user clicks the '<' or '>' button """
        current_message = self.instruction_list.index(self.v_instructions.get())
        current_message += increment
        # If the user clicks 'back' on the first instruction the last instruction is displayed
        if current_message < 0:
            current_message = len(self.instruction_list) - 1
        # If the user clicks 'next' on the last instruction the first instruciton is displayed
        elif current_message > len(self.instruction_list) - 1:
            current_message = 0

        self.v_instructions.set(self.instruction_list[current_message])


class ViewLeaderboard(Template):
    """ Allows the user to view the 5 best scores and levels achieved from previous runs of the game """
    def __init__(self, master):
        """ Defines variables which are needed on the Leaderboard page """
        super().__init__(master, 'Leaderboard')

        # Defines the font of the treeview and sets the text to lie in the center.
        style = ttk.Style()
        style.configure("mystyle.Treeview", font=("Calibri", 13), rowheight=30)
        style.configure("mystyle.Treeview.Heading", font=("Calibri", 14, "bold"))
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])
        # Creates the column headers for the treeview
        self.leaderboard_tree = ttk.Treeview(self.main_frame, style="mystyle.Treeview")
        self.leaderboard_tree["columns"] = ("one", "two")
        self.leaderboard_tree.heading("#0", text="Initials", anchor=CENTER)
        self.leaderboard_tree.column("#0", width=100, stretch=YES, anchor=CENTER)
        self.leaderboard_tree.heading("one", text="Score", anchor=CENTER)
        self.leaderboard_tree.column("one", width=100, stretch=YES, anchor=CENTER)
        self.leaderboard_tree.heading("two", text="Level", anchor=CENTER)
        self.leaderboard_tree.column("two", width=100, stretch=YES, anchor=CENTER)
        self.leaderboard_tree.grid(row=1, column=0, columnspan=2, sticky="ew")

        b_back = Button(self.main_frame, text="Back", background="white", width=15)
        b_back["command"] = lambda frame=MainMenu: self.switch_frame(frame)
        b_back.grid(padx=10, pady=10, row=2, column=1, sticky="w")

        # Reads the contents of the leaderboard text file and adds them to the treeview 
        with open("leaderboard.txt", "rb") as file:
            self.leaderboard_contents = pickle.load(file)
        for entry in reversed(self.leaderboard_contents):
            self.leaderboard_tree.insert("", "0", text=entry[0], values=(entry[1:]))


class GameOver(Template):
    """ Window is dislpayed when the user loses the game,
    if the user scores high enough, they are prompted to enter their initials and add their score to the leaderboard"""
    def __init__(self, master, score, level):
        """ Defines variables which are needed on the Game Over page """
        super().__init__(master, 'Game Over')
        self.master = master
        self.score = score
        self.level = level

        self.v_statistics = StringVar()
        self.v_statistics.set("Score: " + str(self.score) + "          Level: " + str(self.level))
        self.l_statistics = Label(self.main_frame, textvariable=self.v_statistics, borderwidth=0)
        self.l_statistics.grid(row=1, columnspan=2, pady=10)

        # Reads the contents of the leaderboard file and adds the scores to a list
        with open("leaderboard.txt", "rb") as file:
            self.leaderboard_contents = pickle.load(file)

        if len(self.leaderboard_contents) > 0:
            self.highest_scores = [entry[1] for entry in self.leaderboard_contents]
        else:
            self.highest_scores = [0] * 5

        # Prompts the user to enter their initials if their score was higher than the lowest score on the leaderboard
        if self.score > min(self.highest_scores):
            self.l_congratulations = Label(self.main_frame,
                                           text="Congratulations! Your score can be added to the leaderboard!",
                                           borderwidth=0)
            self.l_congratulations.grid(row=2, columnspan=2, pady=10)
            self.l_prompt = Label(self.main_frame, text="Please enter your initials:", borderwidth=0)
            self.l_prompt.grid(row=3, columnspan=2, pady=10)
            self.e_initials = Entry(self.main_frame, background="white", width=5)
            self.e_initials.grid(row=4, padx=10, pady=10)
            self.b_add = Button(self.main_frame, text="Add to Leaderboard")
            self.b_add.configure(background="white", foreground="black")
            self.b_add["command"] = lambda score=self.score, level=self.level, initials=self.e_initials: self.add_leaderboard(score, level, initials)
            self.b_add.grid(row=4, column=1, padx=10, pady=10)
        else:
            # Tells the user their score was not high enough to be put on the leaderboard
            self.l_fail = Label(self.main_frame, text="Better luck next time!", borderwidth=0)
            self.l_fail.grid(row=2, columnspan=2, pady=10)
            self.b_back = Button(self.main_frame, text="Back to Main Menu")
            self.b_back.configure(background="white", foreground="black")
            self.b_back["command"] = lambda frame=MainMenu: self.switch_frame(frame)
            self.b_back.grid(row=3, columnspan=2, pady=10)

    def add_leaderboard(self, score, level, initials):
        """ Adds the user's score to the leaderboard, and deletes the lowest entry """
        # Checks whether the user entered 3 characters.
        if len(initials.get()) != 3:
            messagebox.showerror("Error!", "Please enter 3 initials!")
            initials.set("")
        else:
            self.leaderboard_contents.append([initials.get(), score, level])
            self.leaderboard_contents = sorted(self.leaderboard_contents, key=lambda x: x[1], reverse=True)
            self.leaderboard_contents = self.leaderboard_contents[:5]
            with open("leaderboard.txt", "wb") as file:
                pickle.dump(self.leaderboard_contents, file)
            messagebox.showinfo("Success!", "Score added to the leaderboards!")
            self.switch_frame(MainMenu)


def main():
    root = Tk()
    app = MainMenu(root)
    root.mainloop()

if __name__ == "__main__":
    main()
