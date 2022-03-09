from datetime import datetime as dt


def stamp2str(stamp, form='%Y-%m-%d %H:%M:%S'):
    return dt.utcfromtimestamp(stamp).strftime(form)


def str2stamp(string, form='%Y-%m-%d %H:%M:%S'):
    return dt.strptime(string, form).timestamp()
