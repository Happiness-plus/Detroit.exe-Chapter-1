# This file is in the public domain. Feel free to modify it as a basis
# for your own screens.

# Note that many of these screens may be given additional arguments in the
# future. The use of **kwargs in the parameter list ensures your code will
# work in the future.

image arotate:
    "gui/logo.png"
    rotate 0
    linear 60.0 rotate 360
    repeat

##############################################################################
# Say
#
# Screen that's used to display adv-mode dialogue.
# http://www.renpy.org/doc/html/screen_special.html#say
screen say(who, what, side_image=None, two_window=False):

    # Decide if we want to use the one-window or two-window variant.
    if not two_window:

        # The one window variant.
        window:
            id "window"

            has vbox:
                style "say_vbox"

            if who:
                text who id "who"

            text what id "what"

    else:

        # The two window variant.
        vbox:
            style "say_two_window_vbox"

            if who:
                window:
                    style "say_who_window"

                    text who:
                        id "who"

            window:
                id "window"

                has vbox:
                    style "say_vbox"

                text what id "what"

    # If there's a side image, display it above the text.
    if side_image:
        add side_image
    else:
        add SideImage() xalign 0.0 yalign 1.0

    # Use the quick menu.
    use quick_menu


##############################################################################
# Choice
#
# Screen that's used to display in-game menus.
# http://www.renpy.org/doc/html/screen_special.html#choice

screen choice(items):

    window:
        style "menu_window"
        xalign 0.5
        yalign 0.5

        vbox:
            style "menu"
            spacing 2

            for caption, action, chosen in items:

                if action:

                    button:
                        action action
                        style "menu_choice_button"

                        text caption style "menu_choice"

                else:
                    text caption style "menu_caption"

init -2:
    $ config.narrator_menu = True

    style menu_window is default

    style menu_choice is button_text:
        clear

    style menu_choice_button is button:
        xminimum int(config.screen_width * 0.75)
        xmaximum int(config.screen_width * 0.75)


##############################################################################
# Input
#
# Screen that's used to display renpy.input()
# http://www.renpy.org/doc/html/screen_special.html#input

screen input(prompt):

    window style "input_window":
        has vbox

        text prompt style "input_prompt"
        input id "input" style "input_text"

    use quick_menu

##############################################################################
# Nvl
#
# Screen used for nvl-mode dialogue and menus.
# http://www.renpy.org/doc/html/screen_special.html#nvl

screen nvl(dialogue, items=None):

    window:
        style "nvl_window"

        has vbox:
            style "nvl_vbox"

        # Display dialogue.
        for who, what, who_id, what_id, window_id in dialogue:
            window:
                id window_id

                has hbox:
                    spacing 10

                if who is not None:
                    text who id who_id

                text what id what_id

        # Display a menu, if given.
        if items:

            vbox:
                id "menu"

                for caption, action, chosen in items:

                    if action:

                        button:
                            style "nvl_menu_choice_button"
                            action action

                            text caption style "nvl_menu_choice"

                    else:

                        text caption style "nvl_dialogue"

    add SideImage() xalign 0.0 yalign 1.0

    use quick_menu

##############################################################################
# Main Menu
#
# Screen that's used to display the main menu, when Ren'Py first starts
# http://www.renpy.org/doc/html/screen_special.html#main-menu

screen main_menu():

    # This ensures that any other menu screen is replaced.
    tag menu
    python:
        renpy.music.play("Main.ogg")
    add "gui/background.png"
    add "arotate" xpos 641 ypos 171 xanchor 0.5 yanchor 0.5
    add "gui/logo2.png"
    if persistent.ending == "one":
        add "gui/chapter2.png"

    imagemap:
        ground "gui/ground1.png"
        hover "gui/hover1.png"
    
        hotspot (33, 611, 201, 97) action Start()
        hotspot (246, 614, 209, 96) action ShowMenu('load')
        hotspot (465, 614, 308, 98) action ShowMenu('preferences')
        hotspot (785, 615, 268, 95) action ShowMenu('credits')
        hotspot (1064, 615, 182, 97) action Quit(confirm=False)

    

##############################################################################
# Navigation
#
# Screen that's included in other screens to display the game menu
# navigation and background.
# http://www.renpy.org/doc/html/screen_special.html#navigation
screen navigation():

    # The background of the game menu.
    window:
        style "gm_root"

    # The various buttons.
    frame:
        style_group "gm_nav"
        xalign .98
        yalign .98

        has vbox

        textbutton _("Return") action Return()
        textbutton _("Preferences") action ShowMenu("preferences")
        textbutton _("Save Game") action ShowMenu("save")
        textbutton _("Load Game") action ShowMenu("load")
        textbutton _("Main Menu") action MainMenu()
        textbutton _("Help") action Help()
        textbutton _("Quit") action Quit()

init -2:

    # Make all game menu navigation buttons the same size.
    style gm_nav_button:
        size_group "gm_nav"


##############################################################################
# Save, Load
#
# Screens that allow the user to save and load the game.
# http://www.renpy.org/doc/html/screen_special.html#save
# http://www.renpy.org/doc/html/screen_special.html#load

# Since saving and loading are so similar, we combine them into
# a single screen, file_picker. We then use the file_picker screen
# from simple load and save screens.

init -2 python: #we initialize x and y, so the load_save_slot screen below works at startup
    x=0
    y=0
screen load_save_slot:
    $ file_text = "% s\n  %s" % (FileTime(number, empty="No Save Present."), FileSaveName(number))
    add FileScreenshot(number) xpos x+20 ypos y+15
    text file_text xpos x+190 ypos y+20 size 26 
  

screen save:
    tag menu # This ensures that any other menu screen is replaced.
    add "gui/save_bg.png" 
    use file_picker 
    
screen load: 
    tag menu 
    add "gui/load_bg.png"
    use file_picker
   
    
screen file_picker:
    # Buttons for selecting the save/load page:
    
    imagemap:
        ground "gui/ground3.png"
        hover "gui/hover3.png"
        
        hotspot (84, 625, 169, 64) action FilePage("auto")
        hotspot (271, 626, 193, 69) action FilePage("quick")
        hotspot (480, 626, 50, 63) action FilePage(1)
        hotspot (558, 629, 56, 59) action FilePage(2)
        hotspot (636, 629, 55, 59) action FilePage(3)
        hotspot (713, 627, 58, 61) action FilePage(4)
        hotspot (790, 627, 59, 63) action FilePage(5)
        hotspot (893, 257, 347, 84) action Return()
        hotspot (887, 507, 355, 83) action ShowMenu("preferences")
        hotspot (893, 340, 346, 84) action ShowMenu("save")
        hotspot (895, 423, 350, 84) action ShowMenu("load")
        hotspot (893, 590, 349, 88) action MainMenu()
        
    $ y=178 # ypos for the first save slot
    for i in range(0, 3):
        imagebutton auto "gui/box_%s.png" xpos 101 ypos y focus_mask True action FileAction(i)
        use load_save_slot(number=i, x=101, y=y) 
        $ y+=150
    

        

##############################################################################
# Preferences
#
# Screen that allows the user to change the preferences.
# http://www.renpy.org/doc/html/screen_special.html#prefereces

screen preferences():

    tag menu

    # Include the navigation.
    add "gui/options_bg.png"
    
    imagemap:
        ground "gui/ground2.png"
        hover "gui/hover2.png"
        
        hotspot (85, 256, 210, 48) action Preference('display', 'window')
        hotspot (315, 253, 103, 53) action Preference('display', 'fullscreen')
        hotspot (232, 392, 172, 44) action Preference('transitions', 'none')
        hotspot (91, 392, 139, 45) action Preference('transitions', 'all')
        hotspot (703, 393, 109, 44) action Preference('after choices', 'stop')
        hotspot (495, 394, 175, 43) action Preference('after choices', 'skip')
        hotspot (612, 256, 209, 51) action Preference('skip', 'seen')
        hotspot (489, 256, 87, 50) action Preference('skip', 'all')
        hotspot (893, 257, 347, 84) action Return()
        hotspot (887, 507, 355, 83) action ShowMenu("preferences")
        hotspot (893, 340, 346, 84) action ShowMenu("save")
        hotspot (895, 423, 350, 84) action ShowMenu("load")
        hotspot (893, 590, 349, 88) action MainMenu()
        
    frame xpos 301 ypos 448:
        style_group "pref"
        has vbox
        bar value Preference("music volume")
    frame xpos 301 ypos 500:
        style_group "pref"
        has vbox
        bar value Preference("sound volume")
    frame xpos 301 ypos 550:
        style_group "pref"
        has vbox
        bar value Preference("voice volume")
    frame xpos 301 ypos 601:
        style_group "pref"
        has vbox
        bar value Preference("text speed")
    frame xpos 301 ypos 652:
        style_group "pref"
        has vbox
        bar value Preference("auto-forward time")
      
init -2 python: 
    # Styling for the bar sliders:
    # Aleema's Customizing Menus tutorial: http://lemmasoft.renai.us/forums/viewtopic.php?f=51&t=9812
    # Bar style properties documentation: http://www.renpy.org/doc/html/style.html#bar-style-properties
    style.pref_frame.background = None
    style.pref_slider.left_bar = "gui/bar_full.png"
    style.pref_slider.right_bar = "gui/bar_empty.png"
    style.pref_slider.thumb = None
    style.pref_slider.xmaximum = 557
    style.pref_slider.ymaximum = 50



    # Put the navigation columns in a three-wide grid.
    
##############################################################################
# Yes/No Prompt
#
# Screen that asks the user a yes or no question.
# http://www.renpy.org/doc/html/screen_special.html#yesno-prompt

screen yesno_prompt:
    modal True 
    add "gui/yn_bg.png"
    imagemap:
        ground "gui/ground4.png"
        hover "gui/hover4.png"
        
        hotspot (484, 433, 136, 79) action yes_action
        hotspot (696, 437, 104, 74) action no_action
    
    if message == layout.ARE_YOU_SURE:
        add "gui/yn_menu.png"
    elif message == layout.DELETE_SAVE:
        add "gui/yn_delete.png"
    elif message == layout.OVERWRITE_SAVE:
        add "gui/yn_overwrite.png"
    elif message == layout.LOADING:
        add "gui/yn_load.png"
    elif message == layout.QUIT:
        add "gui/yn_quit.png"
    elif message == layout.MAIN_MENU:
        add "gui/yn_menu.png"


##############################################################################
# Quick Menu
#
# A screen that's included by the default say screen, and adds quick access to
# several useful functions.
screen quick_menu():

    # Add an in-game quick menu.
    hbox:
        style_group "quick"

        xalign 0.5
        yalign 0.98

        textbutton _("Back") action Rollback()
        textbutton _("Save") action ShowMenu('save')
        textbutton _("Q.Save") action QuickSave()
        textbutton _("Q.Load") action QuickLoad()
        textbutton _("Skip") action Skip()
        textbutton _("F.Skip") action Skip(fast=True, confirm=True)
        textbutton _("Auto") action Preference("auto-forward", "toggle")
        textbutton _("Prefs") action ShowMenu('preferences')

init -2:
    style quick_button:
        is default
        background None
        xpadding 5

    style quick_button_text:
        is default
        size 14
        idle_color "#39637F"
        hover_color "#ccc"
        selected_idle_color "#cc08"
        selected_hover_color "#cc0"
        insensitive_color "#4448"

