
from datetime import datetime, timedelta

date_format = '%Y-%m-%d'


def extract_timeperiod(request):
    data = request.data.keys()
    if 'startdate' in data and 'enddate' in data:
        return (datetime.strptime(request.data['startdate'], date_format), datetime.strptime(request.data['enddate'], date_format))
    elif 'startdate' in data:
        return (datetime.strptime(request.data['startdate'], date_format), datetime.now())
    else:
        default_timeperiod = 365
        enddate = datetime.now()
        startdate = enddate - timedelta(days=default_timeperiod)
        return (startdate, enddate)
