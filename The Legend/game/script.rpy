# You can place the script of your game in this file.

# Declare images below this line, using the image statement.
# eg. image eileen happy = "eileen_happy.png"
#what_color="##FFc0cb

init:

    python:
        import math

        class Shaker(object):
        
            anchors = {
                'top' : 0.0,
                'center' : 0.5,
                'bottom' : 1.0,
                'left' : 0.0,
                'right' : 1.0,
                }
        
            def __init__(self, start, child, dist):
                if start is None:
                    start = child.get_placement()
                #
                self.start = [ self.anchors.get(i, i) for i in start ]  # central position
                self.dist = dist    # maximum distance, in pixels, from the starting point
                self.child = child
                
            def __call__(self, t, sizes):
                # Float to integer... turns floating point numbers to
                # integers.                
                def fti(x, r):
                    if x is None:
                        x = 0
                    if isinstance(x, float):
                        return int(x * r)
                    else:
                        return x

                xpos, ypos, xanchor, yanchor = [ fti(a, b) for a, b in zip(self.start, sizes) ]

                xpos = xpos - xanchor
                ypos = ypos - yanchor
                
                nx = xpos + (1.0-t) * self.dist * (renpy.random.random()*2-1)
                ny = ypos + (1.0-t) * self.dist * (renpy.random.random()*2-1)

                return (int(nx), int(ny), 0, 0)
        
        def _Shake(start, time, child=None, dist=100.0, **properties):

            move = Shaker(start, child, dist=dist)
        
            return renpy.display.layout.Motion(move,
                          time,
                          child,
                          add_sizes=True,
                          **properties)

        Shake = renpy.curry(_Shake)

# Image definitions for snow particles:
image snow_small = Transform("snowflake1.png")
image snow_normal = "snowflake2.png"
image snow_large = Transform("snowflake3.png")
# Definition for Snowing UDD:
image snowing = Fixed(
    Snowing("snow_small", interval=(0.1, 0.15), speed=(5.5, 7.5), slow_start=(7, (0.2, 0.3))),
    Snowing("snow_normal", interval=(0.15, 0.25), speed=(3.5, 4.5), slow_start=(7, (0.4, 0.5))),
    Snowing("snow_large", interval=(0.25, 0.35), speed=(2.5, 3.5), slow_start=(5, (0.5, 0.6))))
# This bit is required for the Snowing effect:
transform particle(d, delay, startpos, endpos, speed):
    subpixel True
    pause delay
    rotate 0
    d
    pos startpos
    linear speed pos endpos rotate 360

init python:
    class Snowing(renpy.Displayable, NoRollback):
        def __init__(self, d, interval=(0.2, 0.3), start_pos=((-200, config.screen_width), 0), end_pos=({"offset": (100, 200)}, config.screen_height), speed=4.0, slow_start=False, transform=particle, **kwargs):
            """Creates a 'stream' of displayable...
           
            @params:
            -d: Anything that can shown in Ren'Py.
            -interval: Time to wait before adding a new particle. Expects a tuple with two floats.
            -start_pos: x, y starting positions. This expects a tuple of two elements containing either a tuple or an int each.
            -end_pos: x, y end positions. Same rule as above but in addition a dict can be used, in such a case:
                *empty dict will result in straight movement
                *a dict containing an "offset" key will offset the ending position by the value. Expects an int or a tuple of two ints. Default is (100, 200) and attempts to simulate a slight wind to the right (east).
            -speed: A time before particle eaches the end_pos. Expects float or a tuple of floats.
            -slow_start: If not the default False, this will expect a tuple of (time, (new_interval_min, new_interval_max)):
                *This will override the normal interval when the Displayable is first shown for the "time" seconds with the new_interval.
            -transform: ATL function to use for the particles.
               
            The idea behind the design is to enable large amounts of the same displayable guided by instructions from a specified ATL function to
            reach end_pos from start_pos in speed amount of seconds (randomized if needs be). For any rotation, "fluff" or any additional effects different ATL funcs with parallel can be used to achieve the desired effect.
            """
            super(Snowing, self).__init__(**kwargs)
            self.d = renpy.easy.displayable(d)
            self.interval = interval
            self.start_pos = start_pos
            self.end_pos = end_pos
            self.speed = speed
            self.slow_start = slow_start
            self.transform = transform
           
            self.next = 0
            self.shown = {}
       
        def render(self, width, height, st, at):
               
            rp = store.renpy
               
            if not st:
                self.next = 0
                self.shown = {}
               
            render = rp.Render(width, height)
           
            if self.next <= st:
                speed = rp.random.uniform(self.speed[0], self.speed[1])  if isinstance(self.speed, (list, tuple)) else self.speed
                   
                posx = self.start_pos[0]
                posx = rp.random.randint(posx[0], posx[1]) if isinstance(posx, (list, tuple)) else posx
               
                posy = self.start_pos[1]
                posy = rp.random.randint(posy[0], posy[1]) if isinstance(posy, (list, tuple)) else posy
               
                endposx = self.end_pos[0]
                if isinstance(endposx, dict):
                    offset = endposx.get("offset", 0)
                    endposx = posx + rp.random.randint(offset[0], offset[1]) if isinstance(offset, (list, tuple)) else offset
                else:
                    endposx = rp.random.randint(endposx[0], endposx[1]) if isinstance(endposx, (list, tuple)) else endposx
               
                endposy = self.end_pos[1]
                if isinstance(endposy, dict):
                    offset = endposy.get("offset", 0)
                    endposy = posy + randint.randint(offset[0], offset[1]) if isinstance(offset, (list, tuple)) else offset
                else:
                    endposy = rp.random.randint(endposy[0], endposy[1]) if isinstance(endposy, (list, tuple)) else endposy
               
                self.shown[st + speed] = self.transform(self.d, st, (posx, posy), (endposx, endposy), speed)
                if self.slow_start and st < self.slow_start[0]:
                    interval = self.slow_start[1]
                    self.next = st + rp.random.uniform(interval[0], interval[1])
                else:
                    self.next = st + rp.random.uniform(self.interval[0], self.interval[1])
           
            for d in self.shown.keys():
                if d < st:
                    del(self.shown[d])
                else:
                    d = self.shown[d]
                    render.blit(d.render(width, height, st, at), (d.xpos, d.ypos))
                   
            rp.redraw(self, 0)
           
            return render
           
        def visit(self):
            return [self.d]
#image for mainmenu
image nature = "06.jpg"
image MAD = "MADCG.jpg"
define flash = Fade(0.1, 0.0, 0.5, color="#FFFFFF")
define fadein = Fade(3, 0.0, 1.5)
image white = "white.jpg"
image black = "black.jpg"  
image ravine = "06.jpg"
image daylight= "01.jpg"
image Aura = "Aura.jpg"
image DA = "DAH.jpg"
image DAR = "DAR.jpg"
image AB = "AuraB.jpg"
image AA = "AuraAngry.jpg"
image AR = "AuraRage.jpg"
image alexis = "Alexis.webp"
image Alexis = "Alexis.png"
image AlexR = "AlexisA.jpg"
image AlexD = "AlexisD.jpg"
image OMG = "AlexisOMG.jpg"
image AS = "AlexisS.jpg"
image ZionCG = "ZionCG.jpg"
image Fire = "FireCG.jpg"
image ZionFire = "ZionCG1.jpg"
image Box1 = "Box1.jpg"
image Marcus = "Marcus.jpg"
image AF = "AF.jpg"
image Apron = "Apron.jpg"
image DAF = "DAF.jpg"
image dance = "Dance!.jpg"
image horror = "Horror!.jpg"
image AM = "MarcusA.jpg" 
image MH = "MarcusH.jpg"
image MS = "MarcusS.jpg"
image MFS = "MFS.jpg"
image really = "Really.jpg"
image walk = "walk.jpg"
image dinner = "dinner.jpg"
image Box = "Box2.jpg"
image AuraCG = "AuraCG.jpg"
image AuraShock = "Aurashock.jpg"
image AuraMad = "AuraMadCG.jpg"
image beach = "beach.jpg"
image kitchen = "kitchen_day.jpg"
image singing = "singing.jpg"
image praying = "praying.jpg"
image eating = "eating.jpg"
image talking = "talking.jpg"
image CS = "CS.jpg"
image freedom = "freedom.jpg"
image ZionFire1 = im.Grayscale("ZionCG1.jpg")
image nap = "nap.jpg"
image faint = "fainting.jpg"
define shake = Shake((0, 0, 0, 0), 1.0, dist=30)
image light = Movie(channel="light", play="light.webm", mask="light.webm")
image grab = "grab.jpg"
image collide = "collide.jpg"
image collide2 = "collide2.jpg"
image drown = "Drown.jpg"
image doctor = "Doctor.jpg"
image chair = "chair.jpg"
image OP = "Opening.jpg"
image OPN = "Opening1.jpg"
image astral = "Astral.jpg"
image odd = "odd.jpg"
image ha = "hahaha.jpg"
image DAI = "DAI.jpg"
image DC = "DAC.jpg"
image monster = "monster.jpg"
image choke = "choke.jpg"
image yell = "yell.jpg"
image facepalm = "facepalm.jpg"
image sense = "sense.jpg"
image PM = "M11.jpg"
image haha = "hahaha.jpg"
image weak = "weak.jpg"
image escape = "escape.jpg"
image skeptic = "1Gm8vWP.webp"
image cmon = "2cBOCyX.jpg"
image sigh = "8sXkz9e.jpg"
image evil = "JNEekgO.webp"
#image why = "Rll3Jqo.webp"
# Declare characters used by this game.
define z = Character('Zion', color="#000000", outlines=[(1, "#39637F", 0, 0)], who_size = 30, window_background="ZionT.png", what_color="#000000")
define m = Character('Marcus', color="#FFFFFF", outlines=[(1, "#39637F", 0, 0)],  window_background="orange.png", what_color="#FFb448", who_size = 30)
define a = Character('Alexis', color="#FFFFFF", outlines=[(1, "#39637F", 0, 0)],  window_background="pink.png", what_color="#FFc0cb", who_size = 30)
define u = Character('???', color="#000000", outlines=[(1, "#39637F", 0, 0)], who_size = 30, window_background="AuraT.png", what_color="#000000")
define d = Character('???', color="#000000", outlines=[(1, "#39637F", 0, 0)], who_size = 30, window_background="Daura.png", what_color="#ff0000")
define p = Character(kind=nvl,  what_xalign=0.5, window_xalign=0.5, what_text_align=0.5, what_italic=True)


init:
    style nvl_window:
        background None
init:
    style nvl_vbox:
        xfill True
# The game starts here.
label splashscreen:
    scene black
    with Pause(1)

    show text "This kinetic novel is best enjoyed with stereo headphones in a relaxed enviroment." with dissolve
    with Pause(3)
    
    show text "In order to navigate between scenes, tap the left side of the screen to go back and tap the right side of the screen to move forward. Hold the muti-window button to get to the menu." with dissolve
    with Pause(7.5)

    hide text with dissolve
    with Pause(0.5)


    return
label start:
    stop music 
    scene black with dissolve
    play sound "Snow4D.ogg" loop fadein 10
    play music "Prologue.ogg" fadein 10
    p "People say that there is no such place as Heaven." 
    p "It's just an asinine fairy tale from millennia ago."
    p "Our arbitrary existence is nothing, but a brief crack of light between two eternities of outer darkness."
    show light
    #Pause the webm at the end
    p "In spite of that, why do I feel so compelled to achieve salvation?"
    "A voice called to him."
    #p "The wind blows in my eyes, fogging up my glasses."
    #p "Walking in my church attire through a foot of snow..."
    #p "A voice calls to me as I wipe my glasses with my tie."
    hide light
    nvl clear
    voice "Spirit.ogg"
    #auto voice this line
    centered "{i}{b}{cps=4}“Press forward to Heavenly Father's kingdom!”"
    stop sound fadeout 4
    nvl clear
    $ renpy.pause(3, hard=True)
    show snowing with Dissolve(1.5)
    show text "{color=#ADD8E6}{font=Quicksand-Regular.otf}{size=+70}Detroit.exe" with dissolve
    $ renpy.pause ()
    #size 20 for regular but size 30 for dash quicksand
    show text "{color=#ADD8E6}{size=+20}{b}Chapter 1: Choosing The Right" with dissolve
    $ renpy.pause ()
    hide text with dissolve
    with Pause(1)
    hide snowing
    with fadein
    stop music fadeout 1.5
    centered "{font=ratio.ttf} {size=+10}10:16 P.M.\n8 hours until school begins" 
    scene OP with fadein:
        size (1280, 800)
    "“Alexis, how much you want to bet that I can astral project?”"
    a "“Marcus frankly I don’t care.”"
    m "“I can fly to the—“"
    #I am missing this important line!
    a "“Marcus, we’re going to school in the morning!" 
    a "Why are we even talking about this?”" 
    m "“Well Alexis, you wanted to know what I was doing…”" 
    a "“Alright, for the safety of my sanity, go ahead and ‘astral project.’”" 
    "Marcus relaxes his tender muscles and removes the breastplates of his body. "
    "He stretches repeatedly and Alexis rolls her eyes. Flat on his back, he stares at the ceiling."
    "The body naturally goes to sleep, however he can still open his big mouth." 
    a "“Are you done?”" 
    m "“Well, I am in waking sleep paralysis.”" 
    #missing line
    m "“I can only communicate for a limited time until my head goes to sleep as well.”"
    a "“Goodnight. I have honors biochemistry.”"  
    m "“Weak sauce. I’d love to see you in AP metaphysics.”" 
    "Alexis gives him the infamous straight face." 
    play music "track04.ogg" fadein 0.5
    scene OPN with dissolve:
        size (1280, 800)
    m "Every day, in every way I am getting sexier and sexier." 
    m "Wow, my body feels numb and heavy now."
    scene astral with dissolve:
        size (1280, 800)
    m "Am I floating? Crap! Where am I?"
    "He can walk on the fresh clean river; he can fly as high as the automobiles."
    "He, himself, is the limit of the experience." 
    "He flies to the clouds, without knowing what is up there."
    play sound "choir.ogg" loop
    m "What is that noise? It sounds like singing."
    #line missing
    #not sure if I could use Within Temptation song without asking for permission,
    "“{cps=5}{i}Sanctus Espiritus! Sanctus Espiritus!{/i}{/cps}”" #Make italic
    "There are beautiful angels from an immense kingdom and the moon is gone." 
    "The violet and cloudless sky flies over him." 
    "All he can see is the choir of angels and… "
    stop sound
    scene Fire with flash:
        size (1280, 800)
    m "“Is that fire?”"
    "The fire gains strength from the song."
    "“Sanctus Espiritus! Sanctus Espiritus! Sanctus Espiritus!”"
    "The fire spreads around the kingdom, making a perfect pentagram." 
    "Marcus flies over the angels and attempts to see what is happening in the fiery pentagram." 
    "Horror strikes his poor heart; he can feel his heartbeat pumping more and more"
    m "“I should leave, but why does my heart feel like it will fly out my chest?”"
    scene ZionFire with dissolve:
        size (1280, 800)
    m "“Who’s that? I like his wavy hair, but he should stay away from the fire.”"
    "The young man appears from the fiery pentagram as he it was its source."
    "The man stares at Marcus; through the young man’s glasses, he can see nothing but holiness and cleanliness of The Spirit."
    "Marcus becomes paralyzed by the look of his eyes." 
    "Marcus, now hovering over the angels’ choir in a heavenly body within the sky, attempts to think about his body at the apartment with Alexis, just as the young man walks to him… "
    stop music
    a "“MARCUS!”"
    scene MAD with flash:
        size (1280, 800)
    m "“WHAAAA— What do you want?”"
    a "“Finally, you’re awake. Its 8:00 AM.”"
    voice "16.ogg"
    m "“Crap, forget about breakfast; we have to go!”"
    play music "city_ambience.ogg"
    scene black
    "After school, at the immense campus of their high school…The sun rises, over the beautiful river."
    "The city is shiny, sleek, and eco-friendly."
    "The mild wind passes by, almost relaxing except— "
    scene walk:
        size (1280, 800)
    a "“For the love of my day, please shut up Marcus.”"
    m "“How come you cannot understand that was frightening."
    voice "18.ogg"
    m "{i}Sanctus Espiritus! Sanctus Espiritus!{/i}”"#Italics!
    a "“Look, I have to say. ‘It was just a dream.’”"
    m "“What do you call a dream, when you are aware that you’re dreaming?”"
    "Alexis and Marcus walk from campus, arguing about the dream. They continue walking up to the people mover; while there Marcus looks at his high school from above. "
    #CG flying people mover or remove this conversation entirely...............
    "The school is big as a university, holding only a max population of three thousand students."
    "The people mover stops around M. L. King Boulevard; they walk off seeing their high school from the sidewalk below. A thousand feet below their feet."
    a "“Wow, our school looks awesome from the geofront,”"
    m "“I wonder how our rival’s school looks like, although they are in the aquafront.”"
    "Marcus’s curiosity bugs him throughout the walk back home. The surface sky is a clear blue, a lot better than the geofront." 
    "The sounds of flying 2-person self driving automobiles, fueled by clean renewable energy."
    "The din of the city is low, as usual. Nevertheless, something feels quite off."
    show ZionCG with fadein:
        size (1280, 800)
        #zoom 1.0
    #Zoom in on Zion's face like in Fate/Stay Night
    m "Who’s that?"
    #missing line
    "There is a young man on the glass sidewalk against the aerospace building in downtown. Marcus walks to him and drops his book bag worriedly."
    "“Hello, what are you doing here?”"
    "The young man on the glass sidewalk questions Marcus."
    voice "22.ogg"
    m "“Are you okay?" 
    #voice "23.ogg"
    m "You were just sleeping there on the sidewalk I assumed that you needed help?”"
    "“No, thanks for it anyway—"
    m "“Sorry.”"
    "Marcus now feeling put off by the young man’s last statement."
    "“You’re blocking the sun, God’s gift to man”"
    "“God?” Marcus and Alexis simultaneously."
    #play the voices along different channels
    #such as "God" for sound channel and my channel
    stop music
    play music "Esoragoto.ogg"
    voice "start_fa6ea1b9.ogg"
    "“Yes,{cps=12} God, our{i} Heavenly Father{/i}, the creator of all that is and will be.”"
    hide ZionCG
    play sound "GettingUp.ogg"
    scene talking with dissolve:
        size (1280, 800) 
    #I will need a  CG of Marcus (perplexed), Alexis (perplexed), and Zion talking with pride. The wind blows, lifting his jacket gently."
    "The young man stands up from the glass sidewalk with absolute dignity, wearing a black tie with a silky smooth shirt."
    "Marcus and Alexis remain perplexed." 
    "The suit he is wearing is clean as his black shoes, for an African American he is quite light skinned and has wavy hair"
    "“My name is Zion, and I am a missionary of our Heavenly Father.”"
    voice "27.ogg"
    m "{cps=11}He cannot be.... he looks like the guy from... the dream." 
    voice "28.ogg"
    m "{cps=11}I can feel something. His eyes.... "
    "Marcus skin begins to crawl as he looks at Zion in the eyes."
    z "“What are your names?”"
    a "“My name is Alexis Jackson, and this nutcase friend of mine is Marcus Webster."
    a "So, what were you talking about, God? He created all that is?”"
    z "“In a sense,{w} yes…{w=2} I can substantiate my claim.”"
    "Zion confidently brings out a dense old book from his black book bag."
    "Alexis holds the book, eyeing at it from all sides. She gives Marcus the book; he reads the introduction."
    m "“What am I reading?”" 
    z "“My scriptures.”"
    z "“May I read the beginning of everything for you two?”"
    a "“Sure.”"
    "The trio walks to Marcus’s apartment a little way off from the aquafront. Zion begins to illustrate creation itself."
    scene black
    stop music 
    play music "Alaje.ogg" fadein 1
    #Seed of life in CG, but add the length, width, and depth to help illustrate.
    z "“In the beginning there was darkness, a void if you would imagine. Then God expanded his awareness 360 degrees.”"
    a "“Zion, why did God do that?”"
    z "“Well…In physics, a void is basically no matter, therefore no energy.”"
    #THE SCRIPTURES. THIS SCENE SHOULD BE LONGER. 
    z "“At the edge of His awareness, He spoke 'Let there be light!'”"
    a "“I am assuming that is where length, width, proportion, and depth were created.”"
    m "“All I see is the Venn diagram, but call it whatever you like.”"
    z "“The next day of creation, you have the Tripod of Life aka Borromean Rings.  However, I like to call it the Holy Trinity. God created a firmament between the waters. Above it was called sky and below the oceans.”"
    voice "32.ogg"
    m "Is he serious?" 
    voice "33.ogg"
    m "I cannot tell if he is just trolling us or he actually believes in the crap he says."
    z "“God puts lights in the firmament, to separate light from darkness and to mark days, seasons and years.”"
    a "“Interesting, I have learned that this is not a textbook, however a narrative.”"
    voice "34.ogg"
    m "A presumptuously sketchy narrative at best. I wonder what Alexis is thinking regarding all of this."
    z "“One half of all of creation is completed.”"
    z "“God called the dry land Earth; and the gathering together of the waters called the Seas: and God saw that it was good.”"
    z "“Moreover, God said, let the earth bring forth grass, the herb yielding seed, and the fruit tree yielding fruit after his kind, whose seed is in it, upon the earth: and it was so.”"
    z "“And the earth brought forth grass and herb yielding seed after his kind, and the tree yielding fruit, whose seed was in it, after his kind: and God saw that it was good.”"
    a "I do not know what to think about this, but that is is not how the Earth formed at all."
    m "For a homeless bum, why is he so clean?" 
    m "Better yet, how is he so clean?"
    z "“God later created two lights in the sky; one is the moon to rule the stars. The other is the Sun to rule the day.”"
    "Zion summarizes as they walk down to the apartment."
    a "“God created the sun, moon, and the stars after all the plants?”"
    voice "38.ogg"
    m "Huh... never thought about that."
    #FIND THIS LINE
    m "Go Alexis! Default skepticism at work."
    z "Yes he did."
    "Before Alexis counters Zion, Marcus pats her back."
    voice "41.ogg"
    m "There is a time and place for everything, especially argumentation."
    stop music fadeout 1
    z "“What does you guys think? Heavenly Father said it; therefore, it is so.”"
    scene odd:
        size (1280, 800)
    a "“Home sweet home, guys”"
    z "“Woah, your place is fancy.”"
    z "“The apartment complex rotates?”"
    m "“Indeed, at 30 degrees per hour.”"
    "Zion just stands all amazed at the apartment complex."
    m "“Zion come in, already.”" 
    z "“Oh okay Marcus!”"
    "The trio enters the building."
    scene black
    #CG for inside of the building
    show alexis at right with dissolve
    show MFS at left with dissolve
    m "“This is where I live, over there is the MT”"
    z "“So what is a MT?”"
    a "“Stands for Matter Transporter”" 
    a "He's never heard of a MT before?" 
    a "Where is this guy from?" 
    "Zion slowly walks in one of the spots. Marcus and Alexis set the coordinates. The universe around Zion feels void, as he sees parts of his body fade away."
    z "“Why am I disintegrating? I feel sick... ”"
    voice "45.ogg"
    m "“Relax!" 
    voice "46.ogg"
    m "It's science, we’re going to be safe.”"
    m "For a homeless person, he is quite sheltered...."
    #missing line
    "The trio dematerializes atom by atom, at the speed of light." 
    "Zion opens his eyes and looks the same as if nothing happened." 
    "They are in a stylish red hallway; Marcus finds his apartment 2 doors down from the MT, and there is a pad next to the door."
    "Marcus touches the pad and the door opens soundlessly."
    voice "48.ogg"
    #insert BG here
    m "“Now let us get to the meaning of this meeting.”"
    play music "DatGroove.ogg"
    m "“Alexis, is that your music playing?”"
    a "“I like it”"
    a "“It’s a lot better than that stupid rap song.”"
    m "“Hey that rap song is awesome.”"
    #Missing line
    z "“What rap song?”" 
    a "“No Zion!”"
    hide MFS
    show MH onlayer middle at left:
        linear 1 xalign 0.5
    hide alexis
    show alexis onlayer middle at right
    stop music
    voice "51.ogg"
    m "“Computer, give me a beat.”"
    play music "rap01.ogg"
    show rap_lights:
        alpha 0.1
    $ camera_move(-347, -440, 1100, 0, 20)
    voice "52.ogg"
    m "“{cps=4}I was getting my report card the other day and noticed something...”"
    voice "2.ogg"
    m "“{cps=6}'Look at all those B’s on my report card' I said to myself.”"
    voice "right.ogg"
    m "“{cps=9}'This ain't right' I said.”"
    voice "1.ogg"
    m "“{cps=10}I walked into his little office after school and told them to...”"
    hide MH onlayer middle
    show dance onlayer middle:
        ypos 1.09 yanchor 1.0 xalign 0.5
        linear 0.3896103896103896 rotate 10
        linear 0.3896103896103896 rotate 0
        repeat
    show alexis onlayer middle:
        linear 0.3 xpos 1.3
    hide rap_lights
    show rap_lights2:
        alpha 0.3
    play music "rap2.ogg"
    $ camera_move(0, 0, 0, 0, 0.15)
    #ATL the dancing with him moving back and fourth, flip the sprite, and virbate. 
    voice "4.ogg"
    m "{font=comic.ttf} {size=+15} “THROW SOME A's ON IT!”"
    $ camera_moves( ( (0, 300, 500, 0, 0.3896103896103896, 'linear'), (0, 0, 0, 0, 0.7792207792207792, 'linear') ), loop=True)
    voice "58.ogg"
    m "{font=comic.ttf}“THROW SOME A's ON THAT REPORT CARD!”"
    hide alexis onlayer middle
    show cmon onlayer middle at right
    show dance flipped onlayer middle:
        ypos 1.20 xpos 0.72 rotate 26
        linear 0.05 rotate 29
        linear 0.05 rotate 26
        repeat
    $camera_move(5418, 1709, 1000, 10, 0)
    voice "Line_1_2.ogg"
    m "{font=comic.ttf} {size=+15} “Honor Roll niggas”"
    show dance onlayer middle:
        ypos 1.09 xpos 0.65
        parallel:
            linear 0.1948051948051948 rotate -15
            linear 0.1948051948051948 rotate 15
            linear 0.1948051948051948 rotate -15
            linear 0.1948051948051948 rotate 15
            rotate -15
            linear 0.1948051948051948 rotate 15
            linear 0.1948051948051948 rotate -15
            linear 0.1948051948051948 rotate 15
            linear 0.1948051948051948 rotate -15
            rotate 15
            repeat
        parallel:
            linear 0.7792207792207792 xpos 0.25
            "dance flipped"
            linear 0.7792207792207792 xpos 0.75
            "dance"
            repeat
    $ camera_move(0, 0, 0, 0, 0)
    $ camera_moves( ( (0, 0, 200, 0, 0.3896103896103896, 'linear'), (0, 0, 0, 0, 0.7792207792207792, 'linear') ), loop=True)
    "Marcus runs around"
    voice "As.ogg"
    m "{font=comic.ttf} {size=+15} “THROW SOME A's ON IT!”" 
    voice "58.ogg"
    m "{font=comic.ttf} {size=+15} “THROW SOME A's ON THAT REPORT CARD!”"
    voice "Line_1_1.ogg"
    m "{font=comic.ttf} {size=+15}  “Valedictorian and salutatorian niggas here in dis club”" 
    "Zion just stands there dumbfounded and Alexis facepalms herself."
    voice "As.ogg"
    m "{font=comic.ttf} {size=+15} “THROW SOME A's ON IT”"
    voice "61.ogg"
    m "{font=comic.ttf} {size=+15} “THROW SOME A's ON THAT REPORT CARD”"
    voice "pimps.ogg"
    m "{font=comic.ttf}“Welcome to the Ivy League pimps!”"
    show dance onlayer middle:
        ypos 1.1 rotate -10 xalign 0.5
        parallel:
            linear 0.1948051948051948 rotate 22
            linear 0.1948051948051948 rotate -10
            repeat
    $ camera_move(0, 0, 0, 0, 0.15)
    a "“Computer, stop music.”"
    stop music
    show rap_lights2:
        linear 0.5 alpha 0.0
    hide OMG onlayer middle
    hide dance onlayer middle
    show really at center with dissolve
    m "“Hey! Don't ruin the fun Alexis”"
    hide cmon onlayer middle
    show AlexR at right
    a "“Why Marcus? Why?" 
    a "Can't you see that he is NOT having fun?”"
    a "“Zion, I apologize for his actions; I surely hope you are not surely offended.”"
    z "“I forgive you”" 
    m "“Skip you both!" 
    m "Yall know that rap was awesome.”"
    "Alexis rolls her eyes"
    a "“Marcus, would it kill you to act as if you have some rationality, Mr. Philosopher!”"
    m "“Why don't you go comb a hairy ball, Alexis?”"
    "{font=ratio.ttf}{size=+10} 4:15 PM"
    z "“Marcus you have a lovely apartment here.”"
    hide really
    show marcus at left with dissolve
    m "“Thanks Zion, at least someone appreciates my style and décor.”"
    "Alexis rolls her eyes yet again."
    hide AlexR with dissolve
    show Alexis at right
    #Zion at center facing alexis
    a "“Zion, where did you come from?" 
    a "Let me play something relaxing.”"
    play music "ThornsOfOmarV2.ogg" fadein 2
    z "“Well, that’s what I am trying to find out. I like how this sounds.”"
    a "“That just means that you have a good taste in music. Hehehehe“"
    "Marcus tilts his head in curiosity."
    m "“What's your last name?”" 
    m "This song does sound good."
    z "“Ummm....err.... I do not know... ”"
    hide marcus with dissolve
    show MS at left 
    a "“Excuse me, do you suffer from amnesia?”"
    #Zion's partner had a pod malfuction and died inside. 
    z "“All I remember is waking up in a pod next to this bag I have with me today. My companion was nothing more than just a skeleton"
    hide MS
    hide Alexis
    scene Box with fadein:
        size (1280, 800)
    "Zion opens the bag and it contains a golden box. Marcus and Alexis survey the box."
    a "“Do you know how to open the box?”"
    z "“Nope, but I see a mini microphone on the side of it.”"
    m "“Oh, Zion you will have to say something to open it.”"
    scene Box1:
        size (1280, 800)
    a "“What a deep philosophical insight.”"
    m "“Oh shut up, woman.”"
    scene black
    show Alexis at right with dissolve
    show MH at left with dissolve
    a "“Anyway Zion, what do you plan on doing here?”"
    z "“Honestly, I want to spread the word of Christ and His teachings unto all men and women worthy.”"
    #hide zion
    hide Alexis
    hide MH
    show marcus at center with dissolve
    show AlexR at right with dissolve
    "Marcus begins to whisper to Alexis and walks her to the window."
    m "“What do you think{i} Christ{/i} is?”"
    a "“You are the philosopher." 
    a "Do you know of any religious teachings?”"
    m "“Alexis, I do not even know what religious means.”"
    #show zion at left
    z "“What are you two talking about over there?”"
    hide AlexR with dissolve
    hide marcus
    show MH at right with dissolve
    #Zion at center
    m "“Hey, Zion did you know that these three windows are not actual windows?”"
    z "“Really Marcus?”"
    m "“The one on the right is the game console." 
    m "The middle is the 4D television and finally on the left is my computer screen.”"
    z "“That’s amazing, how do they work?”"
    m "“Just touch it.”"
    a "“We should get on your computer Marcus.”"
    z "“Good Idea. There could be scriptures on the internet you guys can learn.”"
    hide MH
    show horror at right
    m "Oh crap, I think I am starting to remember something.... But what was it?"
    m "“I am not sure about that—"
    "Marcus mutters nervously; Alexis rush to the computer and wake it up."
    hide horror
    stop music fadeout 2
    "Zion gasps and his heart skip a beat, the world of holiness that Zion has begins to dim."
    " The sun sets marking dusk, Marcus freezes in his place."
    " Alexis is simply disappointed at him, there is a dead horrifying silence between the trio."
    z "“{cps=1}...”"
    show sigh with dissolve
    a "“{cps=1}...”"
    hide sigh with dissolve
    show horror with dissolve
    m "“{cps=1}...”"
    #Break
    "The large screen displays a paused lascivious video. Alexis turns to Marcus and shakes her head in his immense fail."
    hide horror
    show AlexR at center with dissolve
    #change back to "why" after figuring out webp
    show PM at right with dissolve
    a "“{cps=5}Marcus... {w} tell me why?”" 
    #modify CPS after voice acting for release.........maybe......
    m "“{cps=14}Ok, ok, Alexis... {/cps}"
    m "I forgot.”"
    "The tension between Marcus and Alexis is enough for Zion to—"
    z "“I believe I should leave, thanks for having me over.”"
    a "“Zion. Marcus did not mean to offend you in any kind of way." 
    a "Maybe it is my fault for actually meeting in this ratchet place.”"
    z "“Well… I guess I can stay, however please turn off the computer.”"
    m "“Computer off.”"
    z "I cannot feel the Holy Ghost at this moment. This is not a good sign. Am I choosing the right?"
    "Marcus pulls the shades over the windows. Alexis and Zion stay in the living room until he returns. "
    z "However, they seem to be good people. If I turn my back now, how will they come unto Christ?"
    m "“For the last time Alexis, I forgot." 
    m "If I knew that Zion was coming, the computer would have been off already.”"
    a "Sigh...“How do you forget such a thing?" 
    a "I mean really....Really... and it was your idea to bring him to the computer in the first place!”"
    z "Oh I have an idea!"
    z "“Alexis, can you turn on the computer? I want to play a song.”"
    a "“Sure.”"
    m "“...Alexis...”"
    a "“Computer on. I hope you find something good on the internet.”"
    z "“Oh I will.” If I can remember, it should be on this website.... oh wait... hmmm."
    m "“Are you willing to cut me some slack?”"
    a "“It's a miracle that he is staying. At the very least, you should cook something.”"
    m "She's right. That was irresponsible on my part."
    m "“Okay, I am going to cook him something right now for dinner .”"
    hide PM with dissolve
    hide why
    show Alexis
    a "“Thank you for understanding me.”"
    a "Sometimes, I wonder why in the world am I still living with this guy." 
    a "I cannot wait till I move out with my boo."
    play music "God.ogg" 
    m "“What is he playing?”" 
    m "I do not feel too well right now."
    scene faint with dissolve:
        size (1280, 800)
    a "“Zion? I see you found something....”" 
    a "My legs feel weak.... "
    a "I do not think I can..."
    with vpunch
    play sound "fall.mp3"
    scene black with vpunch 
    #Marcus and Alexis falling to the ground in agony CG
    z "{cps=8} {font=Georgia.ttf} “I am a child of god and he has sent me here, has given me an earthy home with parents kind and dear. Lead me, guide me, and walk beside me. Help me find the way. Teach me all that I must do to live with him someday.”"
    scene singing with dissolve:
        size (1280, 800)
    z "{cps=8} {font=Georgia.ttf}“I am a child of God, and so my needs are great. Help me to understand his words before it grows to late. Lead me, guide me, and walk beside me. Help me find the way. Teach me all that I must do to live with him someday.”" 
    scene faint with dissolve:
        size (1280, 800)
    #This needs to be a new CG, where she is already on the ground.
    pause 2.0
    a "Why does my heart ache so much?" 
    a "My body feels heavy."
    a "I can barely get up." 
    scene nap with fadein:
        size (1280, 800)
    pause 2.0
    m "“Alexis. Are you alright?”"
    m "Owww. I walk over to her on the floor with my apron on." 
    m "The water begins to boil."
    scene singing:
        size (1280, 800)
    z "{cps=8} {font=Georgia.ttf}“I am a child of God.  if I but learn to do his will, I'll live with him once more. Lead me, guide me, and walk beside me. Help me find the way. Teach me all that I must do to live with him someday.”"
    #Back in fourth with ATL pans and zoom.
   
      
    
    
    
    
    
    #A CG of Marcus struggling to carry Alexis to the reclining chair in sheer agony
    scene black
    a "What is this song?" 
    a"“I am fine Marcus," 
    a "but you should be more concerned with owwww.... my heart burns like fire..”"
    m "I got her." 
    m "“Here, I am going to pick you up and put you in my reclining chair.”" 
    m "I can barely walk with this seething pain in my heart."
    scene singing with dissolve:
        size (1280, 800)
    z "{cps=8} {font=Georgia.ttf}“I am a child of God. His promises are sure. Celestial glory shall be mine if I can but endure. Lead me, guide me, and walk beside me. Help me find the way. Teach me all that I must do to live with him someday.”"
    stop music fadeout 2 
    m "Is the song over?" 
    a "Why was I in so much pain just now...?"
    "Marcus walks back to the kitchen to pour some macaroni into the boiling pot. He puts the lid on the pot and grabs some cheese from the fridge."
    z "I feel so much better right now. I can feel the spirit now." 
    scene kitchen with wiperight
    show apron with dissolve
    m "Crap, I am all out of cheese. Think of something, me."
    #missing line
    hide apron
    scene black with wipeleft
    show alexis at right with dissolve
    a "“Why are you serving the Lord?"
    a "Let me put on another song.”"
    play music "PleasureMix.ogg" fadein 1
    z "“It's my duty and it's my way of paying Him back?”"
    a "“It's a guy? The Lord is a man?”"
    z "“Yes, He created us in His image.”"
    a "“Really? Why would He do that?”"
    z  "“Because, He loves us so very much.”"
    a "“No, I mean why would He have an human appearance."
    a "If He could be anything, why be human?”"
    a "What makes the {i}Homo Sapiens{/i} species so ideal for a {i}Lord{/i}?”"
    z "“I do not know Alexis.”"
    hide skeptic
    scene kitchen with slideright
    show apron
    m "Okay, I pour some water into another pot while the marconi gets softer." 
    m "Time to grab some carrots and potatoes."
    #misssing line
    m "Shoot, I might as well grab some onion. " 
    m "I boil all three of these bad boys right now with some sea salt." 
    scene black with slideleft
    a "“What do you know?”"
    z "“That I have to continue my mission to serve for the Lord, and that everyone is a child of God.”"
    show AS at right with dissolve
    a "“We are children of this Lord?”"
    z "“We all are. You just don't know how much the Lord loves you, and that's why I am here.”"
    z "“There are no coincidences. It's all part of His plan.”"
    hide AS
    scene kitchen with pushright
    show apron with dissolve
    m "I take out the potatoes, onions, and carrots from the pot."
    m "I throw them into my blender along with some paprika, a cap full of lemon juice, and a half cup of raw cashews."
    play sound "Blender.ogg" loop
    m "Coconut milk? Why not?" 
    m "I finally have a use for these nutritional yeast flakes Cheyenne gave me." 
    m "Throw them all into the blender!"
    hide apron
    scene black with pushleft
    show AS at right with dissolve
    a "“Huh... I never met a religious person before.”"
    z "“Hehehe...{w=1}wait, {w=2} what?”"
    a "“Yeah I never met a religious person before.”"
    z "“How is that possible? Granted I have not seen any churches or any places of worship since I arrived into this city six months ago.” This is really bizarre."
    a "“I am not entirely sure as to what you're getting at with this Lord." 
    a "What do you want from Marcus and....”"
    hide AS
    show AlexR at right 
    a "“Marcus turn that damn blender off! I can barely hear him.”"
    stop sound fadeout 1
    hide AlexR
    scene kitchen with slideawayright
    show apron
    m "She does not have to yell."
    hide apron
    show yell
    m "“Don't make me drop this apron and smack the asian out of you. ”"
    m "I drain the macaroni and pour the stuff from the blender." 
    m "It looks like cheese... so yeah.."
    scene black with slideawayleft
    show AlexR
    a "This fool must be insane."
    a "“You would hate it if I came in the kitchen right now.”"
    show yell at left
    m "“Shut up and eat!”" 
    m "I hand her and Zion a bowl."
    hide AlexR
    show alexis at right with dissolve
    play sound "Sit.ogg"
    scene eating with fadein:
        size (1280, 800)
    a "“Oh”"
    a "What did he make?"
    a "This does NOT look like mac and cheese. But whatever, I am hungry. "
    z "“Thanks Marcus. ”" 
    z "Mmm. This smells wonderful. However, I do not think this how mac and chesse is supposed to smell."
    a "“This is not mac and cheese.”"
    m "“Well, yeah, I did not buy any cheese." 
    m "Do you feel accomplished for pointing out that fact?”"
    z "I kneel down."
    #ATL on Zion down
    
    
    
    
    
    
    scene praying with fadein:
        size (1280, 800)
    z "Dear most gracious Heavenly Father, thank you for the opportunity to be with Alexis and Marcus. Thank you for food that will nourish our bodies and minds. In the name of Jesus Christ, amen."
    scene black with dissolve
    a "I look at Zion arising from the floor. “What were you doing?”"
    z "“I was praying,”"
    m "“What's praying?”"
    z "“It's when you communicate to Heavenly Father directly.”"
    a "“What were you discussing with the Lord?”"
    z "“I was thanking him for the food.”"
    #I seriously need a BG for the apartment or I can CGs of their perspectives.
    hide Alexis
    show AlexD at right
    with vpunch 
    show choke at left
    m "Crap, I almost choked on my food."
    a "“That's rude of you, Zion. I expected better."
    a "How can you thank the Lord for the food that Marcus has prepared?”"
    z "“What? If it was not for the Lord, we would be here.”"
    a "“However, who prepared the food?”"
    z "“But....”"
    m "“Answer the question, who prepared the food? In other words, who should you really be thanking?”"
    z "“I acknowledge that you prepared the food, Marcus. So thank you, nevertheless, the Lord made everything possible.”"
    #Table slam sound by Marcus.
    stop music
    hide choke 
    show AM at left with dissolve
    m "“What did God, Heavenly Father, The Lord or whatever do?”"
    a "“How disrespectful of you Zion.”"
    z "“It's not disrespectful.”"
    m "“How are you going to thank someone else for the food that I bought, prepared, cooked, and served for you?”"
    z "“Without God, you would not been able to have this dinner.”"
    m "“Zion, I don’t know who this God is. Neverthe-less he has NOTHING on me.”"
    a "“Zion, please stop”"
    m "“Why are you insisting that this god, have something to do with everything that is me?”"
    z "“That is who He is, we are all His children.”"
    m "“Well, this child has a couple of words for him!”"
    m "“If He is so damn awesome, why does he need YOU to spread His teachings?”" 
    m "“He can just beam the knowledge into our heads!”" 
    z "“I know he exists in my heart!”"
    m "“There is no place for your sentimentality in an argument.”"
    a "These boys are just going at it.... I am just going to sit here and enjoy my mac and whatever he used to make this sauce."
    z "“Shut up!”"
    m "Hehehe, this guy is sure passionate about this God thingy of his."
    z "“Why do you guys reject God?”"
    a "“We do not reject we are only skeptical of his existence.”"
    m "“You do not even clearly define what God, Heavenly whatever does...." 
    m "Much less give a reason for us to believe in Him.”"
    z "Sigh, what I am doing arguing with them? I am just going my food and relax." 
    z "I just invited The Spirit and now The Spirit does not want to stay."
    m "“I apologize for how I been behaving today Alexis”"
    a "Sigh, “Don't worry about it. Hehehe.”" 
    a "I cannot hold it against Marcus anymore; it has been a strange day for both of us"
    m "“I am just upset today, Alexis. I don’t know why I feel this way.”" 
    "I sit back on my chair. Some Friday this turned out to be."
    m "“{cps=8}Ever since that dream last night—“"
    scene ZionFire1 with flash:
        size (1280, 800) crop (0, 150, 400, 300)
        linear 1 crop (0, 0, 800, 600)
    #Fix after prerelease!
    scene black with fadein 
    #flashback sound
    z "Dream? {w=1}“Hey Marcus,{w=2} can you explain that dream to me?”"
    m "“Sure, there was a choir of angels, a boy, and a fiery pentagram.”"
    z "“Did the boy have a {b}black book{/b} in his hand?”"
    show horror 
    play music "esoragoto.ogg"
    m "“How did you.... {w=1.5} know?”"
    m "Aww man, I can feel my skin crawling."
    show Alexis at right
    a "“Looks like we have an investigation on our hands, hehehehe.”"
    m "“No we don’t Alexis, {w=2}I’m pretty sure it’s a—"
    hide horror
    show really
    m "{w=1.5}Screw it, we're going into the wire!”"
    z "Wire?"
    "Walking out the living room, Alexis grabs two black and white headbands."    
    z "“What’s going on?”"
    m "“Alexis are the headbands done charging?”"
    a "“Yes they are.”"
    "Marcus and Alexis turns off the lights." 
    z "“Hey guys, what are you doing?”"
    a "“Here, put on this headband Zion."
    a "I will explain when we get there.”"
    "Marcus's wrist displays a holographic user interface."
    #Click and fainting sounds
    hide really
    "Marcus falls unconscious on the the sofa as Zion puts on the headband."
    hide Alexis
    #show scary looking Alexis as she gets closer and closer
    z "Why did Marcus just collapse over there? Seriously, what is happening here?"
    z "Alexis, why are you smiling so evil-like? She gets closer and closer. I do not feel comfortable around her right now."
    stop music fadeout 3
    z "No wait, {w=1} stop... {w=2} She presses on the button on my headband..."
    # ATL affect goes here of them entering the wire.
    
    
    
    
    
    #dramatic music goes here
    #lots of scary, bloody, gory images
    #lots of sounds of beating in the forest
    # lots of shaking ATL 
    scene nature with fadein:
        size (1280, 800) 
    "Meanwhile in the wire."
    play sound "Scary.flac" 
    show DAR with dissolve
    #sound engineer the music
    d "“…{cps=3} Where....am...I?”"
    #static noise
    "She looks at her static hand."
    d "“…{cps=4} How did I get here?”"
    "She looks around the forest and sees a cloud shaped that spells out Marcus's name."
    d "“{cps=5}Marcus...”"
    scene drown with flash :
        size (1280, 800) crop (0, 150, 400, 300)
        linear 1 crop (0, 0, 800, 600)
    pause 1
    scene nature:
        size (1280, 800)
    show DAR
    d "“…{cps=4}GRRHHHHH”"
    with vpunch
    with hpunch
    # show scientists covered in blood
    scene doctor with flash:
        size (1280, 800) crop (0, 0, 400, 300)
        linear 1 crop (0, 0, 800, 600)
    # a broken chucky doll (NOT ACTUAL CHUCKY!!! JUST A BROKEN DOLL THAT LOOKS LIKE CHUCKY WITH BLACK HAIR)
    scene nature:
        size (1280, 800)
    show DAR
    d "“{cps=6}AAAAAAARRRRRGGGHHH!”"
    with shake
    # show toddler dark aura's broken reflection in the mirror with blood dripping on her face.
    scene chair with flash:
        size (1280, 800) crop (150, 150, 400, 300)
        linear 1 crop (0, 0, 800, 600)
    pause 1 
    scene haha with flash :
        size (1280, 800)
    pause 1
    # show even more firy destruction with her friends from the view of the wire pod. 
    #Violent ATL goes here!
    scene nature:
        size (1280, 800)
    show DC
    scene AuraCG with fadein:
        size (1280, 800)
        #yalign 0.0
        #linear 5.0 yalign -1.0
    #ATL pan up 
    
    
    
    
    
    "Inside the body of the young woman lies another woman."
    play sound "Girl.ogg"
    u "“…Sigh... ”"
    #cyber sound effect
    with shake
    u "“Huh?!”"
    play music "escape.wav"
    scene AuraShock with dissolve:
        size (1280, 800)
    u "“What the...”"
    scene nature:
        size (1280, 800)
    show DAI
    d "“EEEYYYAAAAAAAAAAHHHHHHHHHHAHAHAHAHAHA!”"
    hide DAI
    scene AuraShock with dissolve:
        size (1280, 800)
    u "“What the crap is going on?”"
    scene AuraMad with dissolve:
        size (1280, 800)
    u "“ARGG! SET ME FREE!”"
    hide AA
    #Get a different sound effect!!!
    scene freedom with flash:
        size (1280, 800)
    play sound "Chain.wav"
    #Flash then atl on her face, zoom out from her face
   
    "The light skin girl breaks from her binds."
    "As she travels around the body she sees--"
    scene monster:
        size (1280, 800)
    #monster roar sound effect
    #she's flying around until she encounters monsters.
    u "“Well, great.”"
    #"The monsters attack her one by one."
    scene nature:
        size (1280, 800)
    show DA
    hide AA
    d "“…Oh hi sis.”"
    d "“Since you're free now, do you think you can reach me and keep that promise?”"
    hide DA
    scene weak with flash:
        size (1280, 800) crop (0, 0, 400, 300)
        linear 0.5 crop (0, 0, 800, 600)
    scene CS:
        size (1280, 800)
    show AA
    #"I got no time for this."
    u "She's located in the head." 
    u "If I keep this pace I will make it in no time."
    #"The light skinned girl defeats the monsters and moves on."
    play sound "whoosh.wav"
    scene escape:
        size (1280, 800)
    pause 1
    stop music
    #She smashes them and keeps on moving
    scene beach with fadein
    play sound "beach.mp3"  
    z "“AAAHHHHHH!!!”"
    show MH with dissolve
    m "“You can stop screaming now.”"
    z "“Where am I?”"
    m "“The artificial fourth dimension aka the wire. This is where people go to manifest whatever their heart's desire.”"
    m "“Anything that you can think of manifests here.”"
    z "“Artificial fourth dimension, what the natural fourth dimension?”"
    m "“That's the astral plane, only accessible to those that can astral project.”"
    z "“That's where you saw me in surrounded by fire in the shape of the pentagram. How do we investigate this dream?”"
    hide MH with dissolve
    show marcus with dissolve
    m "“I am going to recreate the dream, and you can help understand the meaning behind it.”"
    z "“Go ahead, and should Alexis be here already?”"
    hide marcus with dissolve
    show sense with dissolve
    m "“...” Something does not seem right here."
    z "“Marcus...”"
    hide sense with dissolve
    m "I fly up to see the forest."
    m "“Zion, get inside the forest, someone else is using up the memory in this virtual plane.”"
    stop sound fadeout 2
    scene CS with fadein:
        size (1280, 800)
    play music "fightscene.ogg"
    show AA at left
    u "“Oh…I found you.”"
    show DA at right
    d "“Ahh~ so you're ready to play with me sister.”"
    d "“You're hoping to take back your body, to have it your way?”"
    d "“My apologies, but I am afraid that I can't let you do that.”"
    u "“…I am not taking 'no' for an answer! I'm taking my body back now!”"
    d "“…Wait,  you think you're going to force me from you?”"
    u "“…I will never know unless I try sis.”"
    d "“Well then, take back your body and fulfill your wish!”"
    "A fierce battle explodes between the twin sisters, the light-skinned girl flies and attempts to sock the other girl." 
    "The black-skinned girl catches her fist, as throws her head into a nerve. Getting back up to clash fists with her sister."
        
    hide AA
    hide DA
    #scene grab
    #$ camera_move(0, 130, 0, 0, 1)
#        show A onlayer l1
#        show B onlayer l2
#        show B onlayer l3
#        'Start motion'
#        'It takes 1 second to move a camera to (0, 130, 0)'
#        $ camera_move(0, 130, 0, 0, 1)
#        'It takes 5 seconds to move a camera to (-70, 130, 1000)'
#        $ camera_move(-70, 130, 1000, 0, 5)
#        'A camera moves to (0, 0, 0) at the moment'
#        $ camera_move(0, 0, 0)
#        'It takes 1 second to rotate a camera to 360 degrees'
#        $ camera_move(0, 0, 0, 360, 1)
#        'reset motion'
#        $ camera_reset()
#        'end'

    show AF at left
    show DAF at center with dissolve
    with flash and  vpunch 
    play sound "Smash.ogg"
    with flash and  hpunch 
    play sound "Smash.ogg"
    with flash and vpunch
    play sound "Smash.ogg"
    with flash and hpunch 
    play sound "Smash.ogg"
    with flash and vpunch 
    play sound "Smash.ogg"
    with flash and hpunch
    play sound "Smash.ogg"
    with flash and vpunch
    play sound "Smash.ogg"
    with flash and hpunch
    hide AF 
    hide DAF
    show grab onlayer backdrop:
        xalign 0.5 yalign 0.5 zoom 2.18
    show grab onlayer backdrop at Shake((-1045, -525, 0, 0), 0.5, dist=20)
    $ camera_move(-4290, -2880, 3800, 20, 0)
    $ camera_move(0, 0, 0, 0, 0.5)
    d "“Why do you keep trying, you’ll inevitably fail honey.”"
    u "“I made a promise to her that we will be together forever”" 
    "The light skinned woman, head-butts her own sister."
    with flash and hpunch
    play sound "Slam.ogg" 
    "Then slams her head midair, the black skinned woman gaining momentum returns to ram her sister." 
    play sound "Pound.ogg"
    with flash and vpunch
    play sound "Pound.ogg"
    with flash and hpunch
    "The light-skinned woman slaps her in the jaw; black skinned woman retaliates by punching her in the eyes."
    #slap sound not shatter
    play sound "Shatter.ogg"
    with hpunch
    "While the light-skinned woman is knocked out, she grabs her legs and repeatedly face-plants her on the nerves. "
    hide grab onlayer backdrop
    play sound "Grip.ogg"
    play sound "Pound.ogg"
    play sound "Slam.ogg"
    play sound "Smash.ogg"
    with flash and Shake((0, 0, 0, 0), 1.0, dist=15)
    play sound "Pound.ogg"
    play sound "Slam.ogg"
    play sound "Smash.ogg"
    with flash and Shake((0, 0, 0, 0), 1.0, dist=30)
    play sound "Pound.ogg"
    play sound "Slam.ogg"
    play sound "Smash.ogg"
    with flash and Shake((0, 0, 0, 0), 1.0, dist=45)
    "The light-skinned woman wakes, and she tosses her with great force to the nerve."
    play sound "Grab.ogg"
    with flash 
    play sound "Smash.ogg" 
    with Shake((0, 0, 0, 0), 1.0, dist=60)
    play sound "Fire.ogg"
    hide AF
    hide DAF
    show AB at left with dissolve
    show DA at center with dissolve
    d "“You still have faith in that promise?”" 
    d "“Everything you fought for has been a lie." 
    d "You refuse to believe me, although we are fundamentally the same. “"
    u "“IF I knew it was a lie, why would I keep fighting for it?”"
    d "“Because you’re hopeless!" 
    d "You’d have nothing left if it was a lie,so you assume it has to be the truth.”"
    hide AB
    show AR at left with dissolve
    u "“YOU LIAR!!!”"
    d "“Well…Let me show you the truth!”"
    hide AR
    hide DA
    with flash
    play sound "Pound.ogg"
    play sound "Slam.ogg"
    play sound "Smash.ogg"
    with Shake((0, 0, 0, 0), 1.0, dist=75) 
    "The dark skinned girl throws her sister one last time."
    #electricity and static noises
    scene daylight with dissolve:
        size (1280, 800)
    stop music fadeout 2.5
    show aura
    u "“I am...{cps=3} back to normal”"
    #show ghost onlayer middle at left:
        #linear 1 xalign 0.5
    #Ghost Dark Aura goes here
    d "“You wish, I still have control and it looks like we have some company.”"
    hide ghost with dissolve
    z "“Hello!”"
    #clear her background
    u "“*Gasp*”"
    # wind blowing sound effect
    "The wind blows silently."
    "There are trees outside the field of grass; the brightest thing in the sky is the moon."
    u "“Hello mister, where did you get that ring from?”"
    z "“I wish I knew.”"
    u "...{i}Wish{/i}..."
    hide aura
    show marcus at left with dissolve
    #zion at right
    m "“Hey Zion, who is this girl?”"
    #aura looks dazed sprite
    z "“I do not know.”"
    m "“Is she high?”"
    z "“I do not know what it means to be high.”"
    play sound "snap.mp3"
    "Marcus snaps his fingers."
    show aura
    hide marcus
    u "“Huh.”"
    hide aura
    show AM
    m "“Now that I have your attention, what are you doing here?”"
    hide AM
    show aura
    u "“Ummm,....”"
    hide aura
    show AM
    m "“Better yet, how are you even here? This server is encrypted.”"
    #Aura looks scared
    #virtual disappear sound
    show aura
    hide AM
    u "“Uhh....”"
    hide aura with dissolve
    "The young girl runs off and disappears."
    hide AM
    show Alexis at right with dissolve 
    a "“Hey guys, what I missed?”"
    show facepalm at center
    m "“{cps=3}...”"
    z "“{cps=3}...”"
    $ persistent.ending = "one"
    #Marcus and Zion are facepalm
    #show Zion straight face at left
    #Marcus and Zion give Alexis the staight face
    call credits from _call_credits
    #cue credits music 
    return
    label credits:
    $ credits_speed = 25 #scrolling speed in seconds
    play music "Roboskater.mp3"
    scene black #replace this with a fancy background
    with dissolve
    show theend:
        yanchor 0.5 ypos 0.5
        xanchor 0.5 xpos 0.5
    with dissolve
    with Pause(3)
    hide theend
    show cred at Move((0.5, 5.0), (0.5, 0.0), credits_speed, repeat=False, bounce=False, xanchor="center", yanchor="bottom")
    with Pause(credits_speed)
    show thanks:
        yanchor 0.5 ypos 0.5
        xanchor 0.5 xpos 0.5
    with dissolve
    with Pause(3)
    hide thanks
    show support:
        yanchor 0.5 ypos 0.5
        xanchor 0.5 xpos 0.5
    with dissolve
    with Pause(5)
    return
#VAs need to be credited differently.
init python:
    credits = ('Created by', 'Lightworker'), ('Sprites', 'EkanubaTheKittyCat'), ('CGs', 'ell'), ('GUI','ds-sans'), ('Programming 3D Camera and ATL', 'Belgerum'), ('Programming Android', 'Ayano'), ('Audio', 'Audionautix.com'), ('Audio', 'Freesounds.org'), ('Other Backgrounds', 'Uncle Mugen'), ('"Icarus" Main menu theme', 'Abigail Benans-Hillard') 
    credits_s = "{size=80}Credits\n\n"
    c1 = ''
    for c in credits:
        if not c1==c[0]:
            credits_s += "\n{size=40}" + c[0] + "\n"
        credits_s += "{size=60}" + c[1] + "\n"
        c1=c[0]
    credits_s += "\n{size=40}Engine\n{size=60}Ren'py\n6.99.11" #Don't forget to set this to your Ren'py version
   
init:
#    image cred = Text(credits_s, font="myfont.ttf", text_align=0.5) #use this if you want to use special fonts
    image cred = Text(credits_s, text_align=0.5)
    image theend = Text("{size=90}{color=#ADD8E6} {font=Quicksand_Dash.otf} To be continued...", text_align=0.5)
    image thanks = Text("{size=80}{color=#ADD8E6} {font=Quicksand-BoldItalic.otf} Thanks for reading!", text_align=0.5)
    image support = Text("{size=59}If you want to see Chapter 2, please donate and share this with others.", text_align=0.5)