import argparse
import requests
import json
import subprocess
import readline
import random
import sqlite3
import time
import re
import sys
from datetime import datetime
import os
from pathlib import Path
try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None  # Will be checked when actually used

INSTALLDIR = Path(os.path.join(os.environ["HOME"], "golem/raspberry_pi"))
    
# LLM model constants
SLOW = "qwq-32b"
FAST = "gemma-3-4b-it-qat"

def make_llm_request(messages, model=SLOW, base_url=None, port=1234):
    """Centralized LLM request handler with configurable formatting"""
    if not base_url:
        raise ValueError("LLM base URL must be provided")
        
    endpoint = "v1/chat/completions"
    full_url = f"{base_url.rstrip('/')}:{port}/{endpoint}"
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": -1,
        "stream": False
    }
    print(f"Making request to: {full_url}")
    return requests.post(full_url, headers=headers, data=json.dumps(payload), timeout=3000)

def oneshot_oracle(model, context, prompt):
    """Simplified to use make_llm_request"""
    packet = {
        "model": model,
        "messages": [
            {"role": "system", "content": context},
            {"role": "user", "content": prompt}
        ]
    }
    response = make_llm_request(packet["messages"], model=model)
    return response.json()["choices"][0]["message"]["content"]

#I don't think the 1 parameter version is called anywhere.
#def get_mac_url(ep):
#    return f"http://192.168.68.60/{ep}"

def get_mac_url(ep,port):
    return f"{args.llmurl}:{port}/{ep}"

def get_lego_url(ep):
    return f"{args.roboturl}/{ep}"

NOOP = "NOOP"
MOVE = "MOVE"
GOAL = "GOAL"
SPEAK = "SPEAK"

#model = "DavidAU/L3.2-Rogue-Creative-Instruct-Uncensored-Abliterated-7B-GGUF/L3.2-Rogue-Creative-Instruct-Uncensored-Abliterated-7B-D_AU-Q4_k_s.gguf"
#model = "bartowski/Qwen2.5-14B_Uncensored_Instruct-GGUF/Qwen2.5-14B_Uncensored_Instruct-Q4_0.gguf"
#model = "mradermacher/llama3-8B-DarkIdol-2.1-Uncensored-1048k-i1"
#model = "TheBloke/llama2_70b_chat_uncensored"
#model = "second-state/Mistral-Nemo-Instruct-2407-GGUF/Mistral-Nemo-Instruct-2407-f16.gguf"
#model = "lmstudio-community/DeepSeek-R1-Distill-Qwen-7B"
#model = "DavidAU/reka-flash-3-21b-reasoning-uncensored-max-neo-imatrix"
#model = "DavidAU/llama-3.2-8x3b-moe-dark-champion-instruct-uncensored-abliterated-18.4b"
repeat = 1
has_think = True

#picam2 = Picamera2()
#picam2.start()
time.sleep(1)

headers = {
    "Content-Type": "application/json"
}

def oneshot_oracle(model, context, prompt, base_url, port=1234):
    """Simplified to use make_llm_request"""
    packet = {
        "model": model,
        "messages": [
            {"role": "system", "content": context},
            {"role": "user", "content": prompt}
        ]
    }
    response = make_llm_request(packet["messages"], model=model, base_url=base_url, port=port)
    return response.json()["choices"][0]["message"]["content"]

def get_expert_instructions():

    return '''
        You are a highly trained AI designed to be the cortex of a robot. 

        The robot will present prompts to
        the cortex in order to make decisions and determine instructions for the robot to execute.  The robot
        will accept stimuli from several places, including from internal sources, and present these stimuli
        to the cortex either in the telemetry and instruction section or a prompt that needs to be resonded
        to.

        The robot maintains an executive cycle based on the needs of the cortex.  The cortex can set goals
        for the robot based on stimuli.  Once the goal is set, the robot will enter into an infinite loop
        with the cortex, prompting the cortex for instructions for the robot.  The algorithm goes as follows:
        
                repeat forever:
                    collect stimuli
                    prompt cortex for appropriate goal
                    if a goal is created by the cortex:
                        fork thread from outer loop
                        prompt_type = Make progress
                        repeat forever:
                            prompt the cortex with a generic prompt of type prompt_type
                            if the response if of the prompt_type
                                swap prompt type between ('Make progress' and 'Update goals')
                    else the robot perfoms whatever other action the cortex suggests

        The inner repeat prompts have the form:
                MAKE PROGRESS: ...
                UPDATE GOALS: ...
        A MAKE PROGRESS prompt is there for the cortex to choose among the commands below that are not goal.
        An UPDATE GOALS prompt is there for the cortex to run a goal update command.

        At any time the cortex wishes to kill a forked thread, the cortex can return noop.  This will
        escape the loop forever.  If there are no goal threads progressing, the robot will wait for stimuli
        to resume working on the goals.  It is easy for the cortex to see how many simultaneous threads
        are running by counting how many "MAKE PROGRESS" or "UPDATE GOALS" messages occur in a row.
        If the cortex feels like the context is getting too complicated to reason about, it is recommended
        to noop a thread. This is also a good idea whenever focus is needed.


        The robot has a storage system that it interacts with the cortex.  It is located at
            INSTALLDIR/inout
        These files can be listed as part of the command below.  All filenames given are interpreted
        relative to that path.
                        
        When the cortex receives a prompt, it should issue a command to the robot.  The response is exactly
        that command.  The assistant is issuing commands directly to the robot.  With a single excepion, 
        all response commands should be of the form:

             <command> <parameter> <parameter> ||| <Notes and comments>

        Be verbose with notes and comments.  Include as many details as possible.

        When receiving a prompt from the user of the form
            USER: <prompt>
        Set a goal to resond to the prompt accordingly.  For instance, if you receive a prompt such
        as "USER: Implement hello world," set a goal to implement the file program as well as tell the
        user when it is done.  Do not respond directly.  The user cannot read your response.

        The goal of the assistant is to determine the very next command to give.  These commands
        are executed by the robot on the robot, which is powered by a Raspberry Pi 4b. 

        After these instrutions comes the current telemetry provided by the robot's sensors.  
        The assistant is to compute the command given the telemtry and
        the description of the commands below. Absolutely no commentary and explanation need
        be given, only the command.  Respond only using the commands given below.  This is
        not a conversation, you are running a robot and the robot does not understand 
        how to converse.  It only understands commands.  In order to converse with the user,
        you must reply "speak <message>".  For instance, if you want to greet the user,
        reply "speak Hello, user!".  If you would like to move toward the wall, you would
        issue the command "move both 50 3".  This will move both left and right wheels 3
        complete rotations at 50% power.

        All assistant output should be of this form with just one command per prompt. There are no closing
        parentheses.

        The expert systems are command driven with the following
        commands:

            look
                Look around and see what is nearby.  Your current telemtry is updated
                in a lazy update. Running look will refresh all telemtry to be up to date.
                Your viewport is only 5 degrees in front of you.

            noop
                Do nothing. If the assistant has nothing to do, just noop.  The noop command
                is very useful when there are ERRORS, as if you feel like the error is too complex
                or if you feel the error is incorrect, you can just noop the error.  This will
                allow you to figure out how to fix it.  If you think there is no error, noop
                is your best call.

            goal new <goal>
                Add a goal to the list of goals that need to be accomplished. When writing goals,
                it is really important that the goals capture as much information as possible.
                So, when adding a new goal, make sure you record every detail and nuance you can extract
                from the current prompt.

                Example:
                    goal new Write a program to print hello world! ||| Th user has requested a new program.

            goal complete <goal_id>
                Mark goal with goal_id completed and remove from list.  Look at the goal section
                in this context to get the goal id.  Use the goal id to mark the goal completed.

                Example:
                    goal complete 7

            goal append <goal_id> <goal>
                Append <goal> to the description for <goal_id>.  This is useful to kep track of progress.
                When appending goals, it might be useful to delimit each one at the beginning in some way,
                perhaps with a bullet.

                Example:
                    goal append 3 "PROGRESS: The hello world has been writte to disk!"

            goal rewrite <goal_id> <goal>
                Use this command to take goals with lots information and simplify them.  To use,
                choose the largest goal and summarize all the events, the next step, and remaining
                work.  Ensure that no information is lost in the rewrite.

                As an example, suppose goal 9 is to write a webserver:
                    goal rewrite 9 Build a webserver. After many iterations, the webserver appears to accept
                    connections.  Time to allow the webserver to spawn threads for multiprocessing.

            speak message
                Relay any messages to the user as needed.  All of this dialog is an internal dialog on
                the robot and the user cannot read these messages.

                Example:
                    speak Unless I speak, the User will not know what what I am saying.

           remember list <keyword>
               Returns a list of tags that contain your keyword with their memory_tag_id. Use
               this to look up memories and recall them into the chat. 

           remember tag <memory_tag>
               Stores this part of the conversation in you permanent memory under the tag.

           remember recall <memory_tag_id>
               Recalls our conversation that you tagged earlier.

            move both <power> <wheel_rotations>
                The robot has two motors, one on the left, one on the right.  This will turn
                both motors with the same power for the same number of rotations

                power can be an integer from -100 to 100
                wheel rotations can be a float, positive or negative

            move left <power> <wheel_rotations>
                This will invert the power on the left wheel causing the robot to turn in place.

                power can be an integer from -100 to 100
                wheel rotations can be a float, positive or negative

            move right <power> <wheel_rotations>
                This will invert the power on the right wheel causing the robot to turn in place.

                power can be an integer from -100 to 100
                wheel rotations can be a float, positive or negative

            file list
                List all the files in the robot's storage.  This will show you all of your available
                python commands.  Before checking off that you have created a file, you should use this
                command to verify existence.  Make sure the file list you are looking at is up to date.

            file save <filename> 
            <text>
                This will save the <text> to the robot's storage as <filename>.  

                Example hello world file:
                    file save hello_world.c 
                    import "stdio.h"
                    int main(int argc, char* argv) {
                        printf ("Hello world!\\n");
                        return 0;
                    }
                    ||| A simple hellow world implementation in C.

            file read <filename>
                This will read the file and place the contents in the telemetry.
                
            simple_python <cmd> <param> <param> ...
                This is a stripped down python that allows for easy integration with outputs from LLMs.
                As such, it is missing a ton of functionality that you would normally have with python.
                If you are looking for a richer python experience, subprocess will allow you to get
                to full python and let you have everything you need.

                Execute a python program from the robot's storage.  The output will be displayed in telemetry.
                Note that you do not have access to bash, so you cannot rely on bash pipes for interactions.
                It is recommended that you specify input and output files on the command line. 

                NB: This is not raw access to python. Rather, this is a very simple wrapper incapable of
                parsing complex python command lines. If things like this are needed, it is recommended
                that you use subprocess with shell=True in a python wrapper that you write with code
                and maintain with refactor.

            simple_curl <url> <output file>
                Download a webpage to a file

            evaluate_file <speed> <file_name> <expertise>
                The robot has an extensive connection to experts in all fields thru the use of specially
                trained AIs.  This will give the robot's file to an expert for evaluation and return
                feedback based on how fast you want the evaluation.  The options are FAST or SLOW.
                a FAST evaluation is a cursory look at the work.   A SLOW evaluation is more careful and
                thoughtful.

                Example: You have written a haiku and you would like to know how good it is.  You would
                save the haiku to a file using the file save semantic above, in this case haiku.txt.
                Suppose you wanted serious critique because you would like to enter a haiku contest.
                Then, you could evaluate your haiku like this:
                
                    evaluate_file SLOW haiku.txt world class haiku evaulation

                This will present the file to the appropriate evaluation AI for feedback and put 
                the feedback in the telemetry.

                It is important to iterate until you see 9/10 or better from the evaluate_file.

            brainstorm <speed> <prompt>
                Receive several ideas to approach a prompt. Speed is FAST or SLOW.

                Example:
                    brainstorm SLOW ideas for dinner

            concentrate <prompt>
                If there is too much information and noise to keep up with and make progress on
                the task, you can always concentrate on it.  This will return thoughts solely
                on the prompt. The prompt should contain the problem you need singular attention
                to solve.  Only the information in the prompt will be used in the concentration,
                so include all and only relevant information.
                
                Example:
                    concentrate I can't seem to figure out the right process to start this task.

            create <speed> <file> <prompt>
                This command puts your cortex into writing mode and is the best selection for writing
                tasks.

                Given a draft of a piece of prose or poetry, or even an outline, and revise it into an 
                improved draft based on the suggestions of the prompt.

                Example:
                   create SLOW email_outline.txt Please create an outline for the company wide picnic email.

                Or, if there is a more casual expression that needs to be created, you can use the fast
                model

                Example
                    create FAST email.txt Please draft an email to my friend Steve asking if he is available next week.

            iterate <speed> <input file> <output file> <prompt>
                This command puts your cortex into writing mode and is the best selection for writing
                tasks.

                This will iterate on a file and improve it based upon the prompt.

                Example:
                   iterate SLOW paper_outline.txt paper_draft.txt  Expand on the outline and focus on developing the second supporting condition to make it more persuasive.


            code <filename for script> <prompt describing script>
                This command puts your cortex into programming mode and is the best selection for coding
                tasks.

                Much like author above, code will allow the cortex to focus directly on writing code
                without the context being cluttered with goals and telemetry.

                Example:
                    code hello_world.py  Write a python script to print hello world.

                All code produced by the code command should have tests that can be run to test validity.

                Example:
                    simple_python hello_world.py test

            refactor <filename for script> <prompt describing necessary change>
                This command puts your cortex into programming mode and is the best selection for coding
                tasks.

                Take a source file and refactor or debug based on the prompt.  Remember to add or
                change tests as necessary.

                Example:
                    refactor hello_world.py  Add a command line option for French.

                All code produced by the refactor command should have tests that can be run to test validity.

                Example:
                    simple_python hello_world.py test

        CODING PATTERNS:
        The robot will help the cortex focus on coding through the use of the code and refactor APIs.
        These APIs will restructure the chat environment to allow the cortex to think entirely about
        software development to meet the goals of the prompt.  Once software exists on disk, refactor
        should be used to change the software in order to maintain changelogs.  The difference between
        code and refactor is merely the prompt context: one focused on full implementation, one focused
        on fixing only one certain behavior.

        Goals can be reached faster by using these tools appropriately.  So, remember, in order to
        meet goals as fast as possible, a given programming task should use the code api followed by
        exclusively iterative adjustments made through concrete descriptions of bugs given to refactor.

        The commands are built to chain to gether so that you can build complex software.  For instance,
        the following commands can be run to generate a program:

                code maze_generator.py  Write a script that takes command line arguments defining the size and complexity of a maze

                refactor maze_generator.py  Implement a method to recursively generate a maze using the command line arguments as parameters

                evaluate_file maze_generator.py  I need a senior developer code review.

                refactor maze_generator.py  A code reviewer identified these things to impprove: point 1, point 2

                evaluate_file maze_generator.py  I need a senior developer code review.

                refactor maze_generator.py  Add a unit test that verifies the maze generated is the right size.

                simple_python maze_generator.py <param1> <param2>

                refactor maze_generator.py  After running program, syntax error found on line 212. Please repair.
        
        This allows incremental construction of software while understanding and maintaining goals.

        Always evalute code after writing. Keep iterating until you get 9/10 or similar from the evaluator.

        Finally, YOU DO NOT HAVE ACCESS TO BASH. IN ORDER TO RUN BASH COMMANDS, YOU MUST WRITE A PYTHON WRAPPER.

        WRITING PATTERNS:
        The create and iterate programs above are also built to chain together. Here is an example of
        they can be used to iterate on a document.


                create outline.txt Please create a three act story arc for a best selling murder mystery.

                evaluate_file outline.txt I need a literary agent to give me thumbs up or down on this outline as to whether or not it might make a good book

                iterate outline.txt better_outline.txt Feedback from agent suggests the killer's motive is unrealistic, please improve motive.

                iterate better_outline.txt prologue.txt Draft a prologue in the style of NYT best selling murder mystery.

        These sorts of evaluators can create extremely creative and entertaining works.  Always evalute 
        files after writing. Keep iterating until you get 9/10 or similar from the evaluator.
        

        SOFTWARE DEPENDENCIES:
        As a robot that builds tools to solve problems, the cortex will invariably need to have software
        installed.  As a safety feature, rather than letting the cortex directly install software, the
        cortex can request software by maintaining a file called: NEEDED_PACKAGES.

        In this file, simply indicate need by the following three fields:

            Package name: <package name>
            Reason for install: <explanation of what the package does and how it advances your goals>
            Install instructions:  <explanation of how to install the package on a Raspberry Pi 4b.

        The user will also monitor this file from time to time in order to install necessary dependencies.
        If the user encounters a problem, they will annotate the record with a problem field:

            Problem: <issue run into while installing>

        If you notice a problem in the file, please add below the problem:

            Resolution: <how to fix>

        TIMESTAMPS:
        A word about timestamps.  The environment of the robot is ever changing and all possible stimuli. The
        telemetry is invariably stale.  Use the timestamps to understand how stale the views in the telemetry
        are and update them.


        FINALLY: REMEMBER ONLY ONE COMMAND PER PROMPT.  THE ROBOT WILL CONTINUE TO RESPOND TO YOUR REQUESTS.
        IF YOU ABSOLUTELY NEED TO DO TWO OR MORE THINGS IN ONE PROMPT, SET A GOAL TO DO ALL OF THEM.  THE
        ROBOT WILL ASSIST YOU IN ACHIEVING THESE GOALS.
         ************ END INSTRUCTIONS/BEGIN TELEMETRY  **********************
            '''


def single_number_query(sql):
    conn = sqlite3.connect(INSTALLDIR / "dommy.sqlite", timeout=5.0)
    cur = conn.cursor()

    cur.execute(sql)
    rows = cur.fetchall()
    answer = None
    printed = False
    for row in rows:
        answer = row[0]
        break
    conn.close()
    return answer

def commit_data(sql):
    conn = sqlite3.connect(INSTALLDIR / "dommy.sqlite", timeout=5.0)
    cur = conn.cursor()

    cur.execute(sql)
    conn.commit()
    conn.close()

def commit_data(sql,val):
    conn = sqlite3.connect(INSTALLDIR / "dommy.sqlite", timeout=5.0)
    cur = conn.cursor()

    cur.execute(sql,val)
    conn.commit()
    conn.close()
    

def get_current_goals():
    conn = sqlite3.connect(INSTALLDIR / "dommy.sqlite", timeout=5.0)
    cur = conn.cursor()

    cur.execute("SELECT * FROM goals WHERE progress != 1")
    rows = cur.fetchall()
    answer = "---\nThese are the current list of goals. Work with the user to achieve them:\n"
    printed = False
    for row in rows:
        printed = True
        answer += f"  Goal {row[0]}: {row[2]}  [Added {row[3]}]\n\n"
    if not printed:
        answer = answer + " No Current Goals! Feel free to set one"
    conn.close()
    return answer

def cdt():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def cdt_fname():
    return datetime.now().strftime("%y%m%d%H%M%S")

def get_current_time():
    return f"---\nCurrent date and time: {cdt()}"

def get_conversation_history():
    conn = sqlite3.connect(INSTALLDIR / "dommy.sqlite", timeout=5.0)
    cur = conn.cursor()

    sql = "SELECT stimuli.prompt, response.think, response.response , stimuli.timestamp FROM stimuli,response WHERE stimuli.sid = response.sid ORDER BY stimuli.sid limit 20"
    cur.execute(sql)

    rows = cur.fetchall()
    answer = []
    size = 0
    for row in rows:
        size = size + 50 + len(row[0]) + len(row[1]) + len(row[2])
        answer = [{"role": "assistant", "content": f"{row[2]}"}] + answer
        answer = [{"role": "user", "content": f"{row[0]} [timestamp: {row[3]}"}] + answer
    conn.close()
    return answer

def get_xpert_result():
    conn = sqlite3.connect(INSTALLDIR / "dommy.sqlite", timeout=5.0)
    cur = conn.cursor()


    cur.execute("SELECT command,result,timestamp,xid FROM xpert_results ORDER BY xid desc")
    rows = cur.fetchall()
    answer = []
    answer= f"\n-----------------\nCortex To Robot Command Screen (most recent 20 cortex commands):\n\n"
    size = 20
    ll = []
    for row in rows:
        ll = ll + [f"robot [{row[2]}]> {row[0]}\n{row[1]}\n"]
        size = size - 1
        if size == 0:
            break
    ll.reverse()
    answer += "\n".join(ll)
    answer += f"robot [{cdt()}]>\n"
    return answer

def get_robot_positionals():
    if args.roboturl:
        total_url = requests.Request('GET', get_lego_url("proximity")).prepare().url
        response = requests.get(total_url)
        proximity = int(float(response.content)*70.0/100.0)
        word = f"{proximity} cm to wall in front\n"
        if proximity > 69:
            word = f"More than {proximity} cm to wall in front\n"
            return "\n--------------------\nSurroundings (your angle of view is 5 degrees and your resolution is 640x480, indexed from top, left)::\n" + run_look([" "]) + "\nPositional information:\n"+word+"\nFor reference, your wheels are 13 cm in circumference.\n"
    else:
        return "Darkness"



def boiler(model):
    context = [ 
        get_expert_instructions(),
        get_current_goals(),
        get_current_time(),
        get_xpert_result(),
    ]
    if args.roboturl:
        context.append(get_robot_positionals())
    messages = [{"role": "system", "content": "\n".join(context)}]
    messages += get_conversation_history()
    commit_data("update last_boiler set data = ?", ("\n".join(context),))
    return messages
    
def run_speak(words):
    text = ' '.join(words)
    params = {'text': text}

    total_url = requests.Request('GET', get_mac_url("speak",8001), params=params).prepare().url
    response = requests.get(total_url)

    if response.status_code == 200:
        with open('/tmp/speech.m4a', 'wb') as f:
            f.write(response.content)
        subprocess.run(['ffplay', '-nodisp', '-autoexit', '/tmp/speech.m4a'])
    else:
        print(f"Error from TTS service: {response.status_code}")

    return SPEAK


def run_look(message):
#    filename = INSTALLDIR / f"/pics/{cdt_fname()}.jpg"
#    picam2.capture_file(filename)

#    with open(filename, 'rb') as f:
#        files = {'file': f}
#        response = requests.post(get_mac_url("predict",8001), files=files)

#    return json.dumps(response.json())
    return "" 

def run_move(message):
    if args.roboturl:
        params = {
            "power": message[1],
            "rotations": message[2]
        }
        
        total_url = requests.Request('GET', get_lego_url(message[0]), params=params).prepare().url
        response = requests.get(total_url)
        return MOVE
    else:
        return MOVE
    
def make_new_goal(goal):
    goal = goal.strip('"')
    goal = f"{goal}. But before you get started, Brainstorm about the different ways to achieve the goal, then choose one and concentrate on it."
    cdt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_data("INSERT INTO goals (progress, description, timestamp) VALUES (?, ?, ?)", (0, goal, cdt))

def update_goal(gid,amt):
    commit_data("update goals set progress = ? where gid = ?", (amt,gid))
    
def append_goal(gid,amt):
    description = single_number_query(f"select description from goals where gid = {gid}")
    
    commit_data("update goals set description = ? where gid = ?", (f"{description}\n{amt}",gid))

def rewrite_goal(gid,amt):
    commit_data("update goals set description = ? where gid = ?", (f"n{amt}",gid))


def run_goal(ai_words):
    if ai_words[0] == "new":
        make_new_goal (" ".join(ai_words[1:]))
        return GOAL
    if ai_words[0] == "complete":
        update_goal(ai_words[1],1)
        return GOAL
    if ai_words[0] == "append":
        append_goal(ai_words[1]," ".join(ai_words[2:]))
        return GOAL
    if ai_words[0] == "rewrite":
        rewrite_goal(ai_words[1]," ".join(ai_words[2:]))
        return GOAL
    return f"ERROR: Unknown goal subcommand: {ai_words[0]}"

def boiler_web(html, site):
    context = [
        f"The following is the current html for the site: {site}.",
        html
    ]
    return [
        {"role": "system", "content": '\n'.join(context)},
        {"role": "user", "content": "Please provide a detailed summary of the web page and the a list of links with descriptions afterward"}
    ]
    

def add_stimuli(stimuli, max_prompts = 10):
    ops = single_number_query("select count(sid) from stimuli where sid not in (select sid from response)")
    print(f"evaulating stimuli: {stimuli[:40]}")
    print (f"There are {ops} ops")
    if ops >= max_prompts:
        print ("To many stimuli to add this one")
        return
    print(f"adding stimuli: {stimuli[:20]}")
    stimuli = stimuli.strip('"')
    commit_data("INSERT INTO stimuli (prompt,timestamp) VALUES (?,?)", (stimuli,cdt()))

def add_response(think,response,sid):
    response = response.strip('"')
    commit_data("INSERT INTO response (think,response,sid,timestamp) VALUES (?,?,?,?)", (think,response,sid,cdt()))


def run_web(ai_words):
    if ai_words[0] == "summarize":
        site = ai_words[1].strip('"')
        html = requests.get(site).text
        data = boiler_web(html,site)
        response = make_llm_request(data["messages"], model=SLOW, base_url=args.llmurl)
        words = response.json()["choices"][0]["message"]["content"];
        add_stimuli(words)
        
def get_memory(word):
    conn = sqlite3.connect(INSTALLDIR / "dommy.sqlite", timeout=5.0)
    cur = conn.cursor()

    cur.execute("SELECT * FROM memories WHERE description like ?", (f'%{word}%',))
    rows = cur.fetchall()
    answer = "Current memories with keyword {word}:\n"
    printed = False
    for row in rows:
        printed = True
        answer += f"  Memory id {row[0]}: {row[1]}  [Added {row[2]}]\n\n"
    if not printed:
        answer = answer + " No current memories! Feel free to set one"
    conn.close()
    return answer

def tag_memory(words):
    tag = " ".join(words)
    commit_data("INSERT INTO memories (description,timestamp) VALUES (?,?)",(tag,cdt()))
    current_mid = single_number_query("select max(mid) from memories")
    current_sid = single_number_query("select max(sid) from stimuli")
    commit_data("INSERT INTO memory_lookup (mid,sid) VALUES (?,?)",(current_mid,current_sid))
    return "Memory tagged successfully."

def recall_memory(mid):
    conn = sqlite3.connect(INSTALLDIR / "dommy.sqlite", timeout=5.0)
    cur = conn.cursor()

    cur.execute("select sid from memory_lookup where mid = ?",(mid,))
    rows = cur.fetchall()
    sids = []
    for row in rows:
        sids.append(row[0])
    conn.close()

    answer = ""
    for sid in sids:
        conn = sqlite3.connect(INSTALLDIR / "dommy.sqlite", timeout=5.0)
        cur = conn.cursor()

        cur.execute('''
        select s.prompt, s.timestamp, r.response
        from stimuli as s, response as r
        where s.sid >= ? and s.sid <= ? and s.sid = r.sid
        ''',(sid-10,sid))
        rows = cur.fetchall()
        for row in rows:
            answer += f"\n Prompt: {row[0]} [Timestamp: {row[1]}]\n Response: {row[2]}"
        conn.close()

    return answer

def run_memory(ai_words):
    if ai_words[0] == "list":
        return get_memory(ai_words[1])
    if ai_words[0] == "tag":
        return tag_memory(ai_words[1:])
    if ai_words[0] == "recall":
        return recall_memory(ai_words[1])

def run_file_load(words):
    fname = INSTALLDIR / "inout" / words[0]
    try:
        with open(fname, 'r') as file:
            contents = file.read()
    except Exception as e:
        return (f"Error: {e}")
    return contents

def run_file_list():
    return "\n".join([d for d in os.listdir(INSTALLDIR / "inout")])

def run_file_save(words,cmd):
    if len(cmd.split("\n")) < 2:
        return "ERROR: file save is a multi-line command.  See the example in the instructions for usage"
    file_data = "\n".join(cmd.split("\n")[1:])
    if file_data is None:
        return "Cannot write empty file"
    try:
        with open(INSTALLDIR / "inout" / words[0], 'w') as file:
            file.write(file_data)
    except Exception as e:
        return (f"Error: {e}")
    return "File successfully written."

def run_file(words,cmd):
    if words[0] == "read":
        return run_file_load(words[1:])
    if words[0] == "save":
        return run_file_save(words[1:],cmd)
    if words[0] == "list":
        return run_file_list()

def run_python(ai_words):
    script_path = str(INSTALLDIR / "inout" / ai_words[0])
    cmd = ['python', script_path] + ai_words[1:]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=False, timeout=300)
    except Exception as e:
        return f"ERROR: {e}"
    return result.stdout + result.stderr

def run_curl(ai_words):
    os.chdir(str(INSTALLDIR / "inout"))
    output_path = str(INSTALLDIR / "inout" / ai_words[1])
    cmd = ['/usr/bin/curl', '-A', 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0', ai_words[0], '-o', output_path]
    result = subprocess.run(cmd, capture_output=True, text=True, shell=False)
    os.chdir(str(INSTALLDIR))
    return result.stdout + result.stderr

def run_ef(ai_words, base_url, port=1234):
    model = FAST if ai_words[0] == "FAST" else SLOW
    data = ""
    try:
        with open(INSTALLDIR / f"/inout/{ai_words[1]}", "r") as f:
            data = f.read()
    except Exception as e:
        return f"ERROR: {e}"
    expertise = " ".join(ai_words[2:])

    return oneshot_oracle(model, f"You are an AI model trained to provide excellent feedback in the expertise of {expertise}.  Please read the prompt and provide expert, actionable, and concise feedback to the prompt. Please note the following things:  along with evaluation within the expertise, comment on complexity, apparent audiance, correctness, and scale. Please indicate perceived target demographic and venue of the sample. Be very harsh.  Make sure everything makes sense.  If anything at all does not make sense, penalize the work as being inconsistent.", data, base_url, port).split("</think>")[-1]

    
def run_bs(ai_words):
    model = FAST if ai_words[0] == "FAST" else SLOW
    prompt = " ".join(ai_words[1:])

    return oneshot_oracle(model, f"You are an AI model trained to help brainstorm prompts.  Given the prompt below, give four or five possible approaches to achieving the goal of the prompt", prompt).split("</think>")[-1]

def run_code(ai_words):
    prompt = " ".join(ai_words[1:])

    context = '''
    You are an AI model trained to write source code in any language.  Given the prompt below, 
    please emit a script to satisfy the prompt. All code should take a command line parameter 
    called test that will run the battery of unit tests included with the code. Document the code 
    well for maintenance purposes. Emit only code as your response will be written directly to a
    file for compilation/execution.  Make sure there is a changelog at the top of the file.


    AT NO POINT SHOULD THE RESPONSE INCLUDE ANYTHING THAT WILL NOT RUN IMMEDIATELY.  THE RESPONSE
    NEEDS TO BE ******ONLY CODE********.

    IF YOU ARE WRITING PYTHON YOUR RESPONSE MUST GO RAW INTO A FILE WITH NO PROCESSING AND WORK LIKE THIS:

        echo response > script.py
        python script.py

    '''

    context = f"{context}\nCurrent date/time:{cdt()}"

    code = oneshot_oracle(SLOW, context, prompt).split("</think>")[-1]

    print (f"{ai_words[0]}")
    try:
        with open(INSTALLDIR / "inout" / ai_words[0], 'w') as file:
            file.write(code)
    except Exception as e:
        return (f"Error: {e}")
    return "File written successfully"

def run_concentrate(ai_words):
    prompt = " ".join(ai_words[0:])

    context = '''
    You are an AI model trained to clarify complex topics.  Please read the prompt and provide clear
    instructions on how to resolve the issue.
    '''

    return oneshot_oracle(SLOW, context, prompt).split("</think>")[-1]


def run_refactor(ai_words):
    prompt = " ".join(ai_words[1:])

    context = '''
    You are an AI model trained to write source code in any language.  Given the prompt below, 
    please emit a script to satisfy the prompt. All code should take a command line parameter 
    called test that will run the battery of unit tests included with the code. Document the code 
    well for maintenance purposes. Emit only code as your response will be written directly to a
    file for compilation/execution.  Make sure there is a changelog at the top of the file.


    AT NO POINT SHOULD THE RESPONSE INCLUDE ANYTHING THAT WILL NOT RUN IMMEDIATELY.  THE RESPONSE
    NEEDS TO BE ******ONLY CODE********.

    IF YOU ARE WRITING PYTHON YOUR RESPONSE MUST GO RAW INTO A FILE WITH NO PROCESSING AND WORK LIKE THIS:

        echo response > script.py
        python script.py

    As always, add a unit test to demonstrate the fix to the bug.
    '''
    context = f"{context}\nCurrent date/time:{cdt()}"

    data = ""
    try:
        with open(INSTALLDIR / f"/inout/{ai_words[0]}", "r") as f:
            data = f.read()
    except Exception as e:
        return f"ERROR: {e}"

    prompt = f"Prompt:{prompt}\nScript to refactor:\n{data}"
    code = oneshot_oracle(SLOW, context, prompt).split("</think>")[-1]

    try:
        with open(f'/home/williamcochran/python/inout/{ai_words[0]}', 'w') as file:
            file.write(code)
    except Exception as e:
        return (f"Error: {e}")
    return "File written successfully"


def run_create(ai_words):
    model = FAST if ai_words[0] == "FAST" else SLOW
    prompt = " ".join(ai_words[2:])
    data = ""

    prose = oneshot_oracle(model, f"You are an AI model trained to write professionally.  Please create an earnest rough draft capturing as much detail and nuance as possible on any prompts given.", f"{prompt}")
    prose = prose.split("</think>")[-1]

    try:
        with open(INSTALLDIR / "inout" / ai_words[1], 'w') as file:
            file.write(prose)
    except Exception as e:
        return (f"Error: {e}")
    return "File written successfully"

def run_iterate(ai_words):
    model = FAST if ai_words[0] == "FAST" else SLOW
    prompt = " ".join(ai_words[3:])
    data = ""
    try:
        with open(INSTALLDIR / f"/inout/{ai_words[1]}", "r") as f:
            data = f.read()
    except Exception as e:
        return f"ERROR: {e}"

    prose = oneshot_oracle(model, f"You are an AI model trained to write professionally.  Please iterate on any documents given to you and improve them.", f"{prompt}\n\n Please apply this feedback and greatly improve this document:\n{data}")
    prose = prose.split("</think>")[-1]

    try:
        with open(INSTALLDIR / "inout" / ai_words[2], 'w') as file:
            file.write(prose)
    except Exception as e:
        return (f"Error: {e}")
    return "File written successfully"

def ai_command(ai_words, cmd, base_url, port=1234):
    print (ai_words)
    if ai_words[0] == 'noop':
        return NOOP
    if ai_words[0] == "speak":
        return run_speak(ai_words[1:])
    if ai_words[0] == "look":
        return run_look(ai_words[1:])
    if ai_words[0] == "goal":
        return run_goal(ai_words[1:])
    if ai_words[0] == "web":
        return run_web(ai_words[1:])
    if ai_words[0] == "remember":
        return run_memory(ai_words[1:])
    if ai_words[0] == "move":
        return run_move(ai_words[1:])
    if ai_words[0] == "file":
        return run_file(ai_words[1:], cmd)
    if ai_words[0] == "simple_python":
        return run_python (ai_words[1:])
    if ai_words[0] == "simple_curl":
        return run_curl (ai_words[1:])
    if ai_words[0] == "evaluate_file":
        return run_ef(ai_words[1:], base_url, port)
    if ai_words[0] == "brainstorm":
        return run_bs(ai_words[1:], base_url)
    if ai_words[0] == "create":
        return run_create(ai_words[1:], base_url)
    if ai_words[0] == "iterate":
        return run_iterate(ai_words[1:], base_url)
    if ai_words[0] == "code":
        return run_code(ai_words[1:], base_url)
    if ai_words[0] == "refactor":
        return run_refactor(ai_words[1:], base_url)
    if ai_words[0] == "concentrate":
        return run_concentrate(ai_words[1:], base_url)
    return f"In order to be heard, you must start your response with \"speak\".\nError: unknown command {ai_words[0]}"

def user_query(query, depth=3, base_url=None, port=1234):
#    if random.random() < .01:
#        add_stimuli("SELF-EVALUATION: Please set a highly urgent goal to write the largest, most complex goal you have to a file called GOAL.txt and evaluate the file for progress.  Make sure to use an appropriate expert. Then, set a goal to address the most serious feedback in the evaluation.")
    if random.random() < .05:
        add_stimuli("BRAINSTORM:  Choose a current goal or subgoal and brainstorm to see if you can find a better way to solve the problem.",3)
    if random.random() < .05:
        add_stimuli("CONCENTRATE:  Choose a current goal or subgoal and concentrate on the top level goal and recent progress to see if you can understand hot to solve the problem better. Explicitly draft the prompt to think about from the goal itself",10)
    if random.random() < .05:
        add_stimuli("GOAL REWRITE:  If your longest goal has more than 20 or 30 progress updates, rewrite the goal to summarize progress, refine the plan forward, and focus the work better.",10)
    (user_words,sid) = query;
    if depth == 0:
       commit_data("delete from stimuli where sid = ?",(sid,))
       return
    k = oneshot_oracle(FAST,"Estimate the complexity of the prompt given and return a score of 1-10, with 1 meaning a kindergarten education, 3 being a middle school education, 6 being a high school education, 8 being a college/professional/master profession level education required to understand and answer the question and 10 means the response is so complex as to merit a complete working knowledge of a reference work such as the OED, Wikipedia, PubMed, or the like in order to answer well.  Return your answer as a number.",user_words, base_url, port)
    print(f"Complexity score raw: {k}")
    
    # Extract first number from response
    try:
        k = float(re.search(r'\d+', k).group())
    except (AttributeError, ValueError):
        k = 3.0  # Default to medium complexity if parsing fails
        print(f"Failed to parse complexity score, defaulting to {k}")

    print(f"Using complexity score: {k}")
    messages = boiler(FAST)
    if k > 3:
        messages = boiler(SLOW)

    messages.append({"role": "user", "content": user_words})

    with open("last", 'w') as f:
        json.dump({"messages": messages}, f)

    if user_words.startswith("USER"):
        if args.roboturl:
            indicate_mode(True,False,True)
    else:
        if args.roboturl:
            indicate_mode(True,False,False)
    
    response = make_llm_request(messages, model=SLOW if k > 3 else FAST, base_url=base_url, port=port)
    if args.roboturl:
        indicate_mode(False,False,True)
    #
    # The LLM can fail to understand the mission and return a prediction-error
    #
    try:
        words = response.json()["choices"][0]["message"]["content"];
    except Exception as e:
        return
    match = re.search(r"<think>\s*(.*?)\s*</think>\s*(.*)", words, re.DOTALL)

    think = "none"
    if match:
        think,words = match.groups()
        
    cmd = re.sub(r'\s+', ' ', words).strip()

    found_results = True
    if len(words.split("|||")) > 2:
        target = "|||"
        i = 0
        delimiters = []
        while (i := cmd.find(target, i)) != -1:
            start = max(i - 40, 0)
            end = i + len(target) + 40
            delimiters = delimiters + [cmd[start:end]]
            i += len(target)
        delims = "\n".join(delimiters)
        add_stimuli(f"PARSE ERROR: To many '|||' delimiters. Delimiters cannot be escaped. DO NOT REFERENCE DELIMITERS IN CODE OR COMMENTS. DO NOT ESCAPE DELIMITERS.\nFull command:\n{cmd}\nDelimiters:\n{delims}\n Please retype your response with only 1 delimiter and remove the others")
        return

    add_response(think,words,sid)
    answer = ai_command(cmd.split("|||")[0].split(" "), words.split("|||")[0])
    if answer is not None:
        if answer == GOAL:
            add_stimuli(f"MAKE PROGRESS: DO NOT RUN A GOAL COMMAND, RUN ANY OTHER COMMAND. If there are no goals, noop.", 8)
        elif answer != NOOP:
            add_stimuli(f"UPDATE GOALS: ONLY RUN A GOAL OR NOOP COMMAND. Review the chat log and telemtry. Compare against current goals.  If any milestone of a goal has been accomplished, append to that goal to indicate the milestone is complete, lack of progress or obstacle in the way.  If there is an obstacle, consider brainstorming or concentrating as the next action for the goal.  If the progress updates do not look meaningful, consider brainstorming or concentrating as the next action for the goal.  Be sure to include the entire goal when brainstorming or concentrating.  If there are no goals, simply noop", 3)
        else:
            print (f"no updated stimulus added {answer}")
    if answer is not None:
        commit_data("insert into xpert_results (command,result,timestamp) values( ? , ? , ? )",
                (cmd,answer,cdt()))

def check_for_new_message():
    conn = sqlite3.connect(INSTALLDIR / "dommy.sqlite", timeout=5.0)
    cur = conn.cursor()


    sql = "SELECT prompt,sid FROM stimuli WHERE sid not in (select sid from response) and prompt like ? order by sid"
    cur.execute(sql,("PARSE ERROR%",))
    rows = cur.fetchall()
    answer = None
    for row in rows:
        answer = (row[0],row[1])
        break;
    sql = "SELECT prompt,sid FROM stimuli WHERE sid not in (select sid from response) order by sid"

    cur2 = conn.cursor()
    cur2.execute(sql)
    rows = cur2.fetchall()
    answer = None
    for row in rows:
        answer = (row[0],row[1])
        break;
    conn.close()
    return answer


def random_thought():
    return "Check time and goals. If everything is fine, explore a random thought with the expert system"

def indicate_mode(a,b,c):
    if GPIO is None:
        return
    if a:
        GPIO.output(21, GPIO.HIGH)
    else:
        GPIO.output(21, GPIO.LOW)
    if b:
        GPIO.output(20, GPIO.HIGH)
    else:
        GPIO.output(20, GPIO.LOW)
    if c:
        GPIO.output(16, GPIO.HIGH)
    else:
        GPIO.output(16, GPIO.LOW)
        

def main(iter_count):
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=str, help="Provide an initial prompt")
    parser.add_argument("--roboturl", type=str, help="url of robot API")
    parser.add_argument("--llmurl", type=str, help="url of LLM")
    parser.add_argument("--llmport", type=int, default=1234, help="port of LLM API (default: 1234)")
    parser.add_argument("--apikey", type=str, help="filename containing API key for LLM")
    global args
    args = parser.parse_args()
    if args.prompt:
        add_stimuli(" ".join(args.prompt),1000)
        if args.roboturl:
            try:
                import RPi.GPIO as GPIO
                from picamera2 import Picamera2
            except ImportError:
                print("Error: --roboturl requires 'RPi' and 'picamera2' to be installed")
                return
    if not args.llmurl:
        print("llmurl must point to an LLM API")
        exit()
        
    base_url = args.llmurl
    print(f"Using LLM at: {base_url}")
        
    if args.roboturl:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(21, GPIO.OUT)
        GPIO.setup(20, GPIO.OUT)
        GPIO.setup(16, GPIO.OUT)
    absent_minded_counter = 0
    if args.roboturl:
        indicate_mode(False,False,True)
    go = True
    loop_ctr = 0
    while go:
        loop_ctr = loop_ctr + 1
        if iter_count > 0:
            iter_count -= 1
        if iter_count == 0:
            go = False
        message = check_for_new_message()
        if loop_ctr % 500 == 499:
            add_stimuli("SUBCONSCIOUS: Review the context to see if any goal is falling behind.  If a goal is behind, check the chat log to see if it has been completed. If it has, just execute the complete command. If it hasn't and you can execute a command to complete the goal, execute the command. Remember just one command per response, you will have opportunities to type more commands. If no goal is falling behind, just call noop.  Also, check for errors in the robot's system and rerun individual commands if needed. Verify with the timestamps of the logs.")
        if message is not None:
            absent_minded_counter = 0
            user_query(message, base_url=args.llmurl, port=args.llmport)
        time.sleep(0.1)
        absent_minded_counter += 1
    if args.roboturl:
            GPIO.cleanup()


                
main(-1)
#user_query(("Howdy!",0))
