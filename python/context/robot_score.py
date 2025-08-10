from db import DB,Prefs

class RobotScore:
    """
    """
    @staticmethod
    def generate_context(context_manager):
        last = 0
        first = None
        long_accum = 0
        short_accum = []
        count = 0.0
        for row in DB.select("select mid,mood from mood order by mid desc limit 100"):
            count = count + 1.0
            last = int(row[1])
            if first is None:
                first = last
            long_accum = long_accum + last
            short_accum = [last] + short_accum
            if len(short_accum) > 20:
                short_accum = short_accum[:-1]
                print (len(short_accum))

        if count < 1.0:
            return "No commands yet to score"
        long_ma = float(long_accum) / min(count,100.0)
        short_ma = float(sum(short_accum)) / float(len(short_accum))
        
        hows_it_going = "Your short term moving average is lower than your long term moving average, this means you are not doing well at all!! You need to concentrate harder to solve the problems."
        if short_ma > long_ma:
            hows_it_going = "Your short term moving average is higher than your long term moving average, this means you are doing well!! Keep up the good work!"


        context = f"The robot keeps score of how well you are driving it.  Your current score is {first}.  Errors or failed commands lower your score.  Good commands that succeed and advance goals raise your score.  Your current moving averages for your score:  short term moving average: {short_ma}, long term moving average: {long_ma}. {hows_it_going}"
        print (context)
        return context

    @staticmethod
    def generate_chat():
        return []

    @staticmethod
    def get_token():
        return "robot_score"
    
