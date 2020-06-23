
from datetime import datetime, timedelta

date_format = '%Y-%m-%d'


def extract_timeperiod(request):
    """
    Generated start_date and end_date.
    """
    data = request.data.keys()

    if 'start_date' in data and 'end_date' in data:
        start_date = datetime.strptime(request.data['start_date'], date_format)
        end_date = datetime.strptime(request.data['end_date'], date_format)
    elif 'start_date' in data:
        start_date = datetime.strptime(request.data['start_date'], date_format)
        end_date = datetime.now()
    else:
        default_timeperiod = 7
        end_date = datetime.now()
        start_date = end_date - timedelta(days=default_timeperiod)

    print((start_date, end_date))
    return (start_date, end_date)
