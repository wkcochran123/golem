class Noop:
    """
    NOOP

    Tell the robot to do nothing
    """

    def __init__(self):
        pass

    @staticmethod
    def action(command,goal_id):
        pass

    @staticmethod
    def get_token():
        "noop"

    @staticmethod
    def context_description():
        return """
        goal

        The goal command is used to manage the goals of the robot.  The goals are assigned
        a goal id by the robot and the goal id is used in robot commands to understand which
        commands are working towards which goal.

        A goal must have some desired deliverable that can be evaluated. A good goal has three
        distinct parts:
            Deliverable:     This is the thing that must be created for the user.
            Next Step:       This is what needs to happen next, ideally a simple command.
            Next Step Test:  A script that verifies that the goal has been achieved.

        So, in order to set a goal, it is important to understand exactly what these three
        pieces are and make sure they are described in the goal.  The goal command has three
        different modes: new, next_step, and complete.  When the user asks for something,
        create a goal using the goal new.  As you make progress, you can indicate the progress
        by goal next_step.  Finally, when you believe the goal is complete, calling
        goal complete will resolve the goal.  Here are the commands in detail:


            goal new <test_script> <goal>

        Add a goal to the list of goals that need to be accomplished. This includes a link
        to a test_script that is in your file list.  

        For instance, suppose the user would like you to make a "Hello, world!" program.  
        This would require an integration test that verified the output program did, indeed, 
        print "Hello, world!".  You could write the test in a file called hello_world_test.py.
        Putting this all together, you would issue the following command to the robot:

            robot [2025-07-10 22:08:29]> goal new hello_world_test.py Deliverable: hello_world.py application that writes Hello, World! to the console. Next Step: write the python code. Next Step Test: verify the python code outputs the answer ||| Writing a computer program for the user.

        This will place a goal in the robot's telemetry that you can make progress against.
        Let's assume this is goal id 6, for the sake of example.
        Once you have engaged the robot and you believe you have accomplished the current
        step, you can try to advance the goal using the next_step command:

            goal next_step <goal_id> <next_test_script> <next step information>

        In our example, this means determining what to do after the first step.  In this case,
        you need to inform the user that their software is written and all tests pass.
        But, since there isn't really a way for you to test if you said this or not, you
        can have a noop test (you still have to implement it, by the way).  You can do this 
        with the following command:

            goal next_step 6 noop.py Next Step: tell user that you have succeeded in testing the script Next Step Test: No test on speaking, so noop is fine. ||| Update progress on the goal.

        This command will run the test from the previous (hello_world_test.py) NOT
        noop.py.  If hello_world_test.py fails, you will get a prompt that explains the
        failure and you will have to fix it.

        Finally, once you have informed the user of the code, you can use the complete command
        to mark the goal as done:

            goal complete 6

        A test succeeds if and only if the only output of the test is on stdout and it is:
            
            All tests pass.

        If the output of the test is not this, the robot considers it failed and will not
        let you make progress or complete the goal.
        """

