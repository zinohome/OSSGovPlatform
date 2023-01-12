import datetime

def transform(awx_time: str):
    time = datetime.datetime.strptime(awx_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    return time.strftime("%Y-%m-%d %H:%M:%S")

def handelDatetime(awx_time: str,format:str):
    time = datetime.datetime.strptime(awx_time, format)
    return time.strftime("%Y-%m-%d %H:%M:%S")

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")