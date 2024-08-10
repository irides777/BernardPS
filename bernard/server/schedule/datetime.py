import dspy

trainset = [
    dspy.Example(current_weekday='Sat', relative_weekday_or_date='下下周五', date_delta='13'),
    dspy.Example(current_weekday='Wed', relative_weekday_or_date='这周天', date_delta='4'),
    dspy.Example(current_weekday='Mon', relative_weekday_or_date='大后天', date_delta='3'),
    dspy.Example(current_weekday='Sun', relative_weekday_or_date='下个周一', date_delta='1'),
    dspy.Example(current_weekday='Fri', relative_weekday_or_date='周天', date_delta='2'),
    dspy.Example(current_weekday='Tue', relative_weekday_or_date='周五', date_delta='3'),
    dspy.Example(current_weekday='Sat', relative_weekday_or_date='下周六', date_delta='7'),
    dspy.Example(current_weekday='Thu', relative_weekday_or_date='下周二', date_delta='5'),
]
trainset = [i.with_inputs("current_weekday", "relative_weekday_or_date") for i in trainset]

def validate_answer(example, pred, trace=None):
    return example.date_delta == pred.date_delta
class WeekdayCalSig(dspy.Signature):
    current_weekday = dspy.InputField(desc="Current weekday in ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']")
    relative_weekday_or_date = dspy.InputField(desc="Relative weekday or date, like 'next Monday', '下下周五', 'day after tomorrow', '大后天'.")
    date_delta = dspy.OutputField(desc="An integer, Number of days between current date and relative weekday or date. NO EXPLANATION NEEDED.")

relative_date_cal = dspy.ChainOfThought(WeekdayCalSig)
relative_date_cal.load('/home/irides/project/secretary/bernard/server/schedule/model.json')
