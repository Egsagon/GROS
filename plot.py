import json
import string
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# All triggers used by the bot for the first group
triggers = [
    'né', 'ner', 'nez',
    'nai', 'nait', 'née',
    'naie', 'nées', 'nés',
    'net', 'néz', 'ney',
    'nei', 'nes', 'nais'
]

def format_string(text: str) -> str:
    '''
    Clean a string using the same method as the bot.
    '''
    
    t = text.lower()
    for char in string.punctuation: t = t.replace(char, '')
    return t.strip()

def build(user: str, tick ='H', logs = 'bot.log', viewformat = '%Hh %d/%m', dpi = 80) -> str:
    '''
    Construct a graph for a specific user.
    If user is an empty string, will construct the graph
    for all cumulated users.
    
    The tick argument specifies the datetime str*time
    precision between one x-axis unit (e.g. d, H, M, etc.).
    '''
    
    date_format = '%Y/%m/%d %H:%M:%s'.split(tick)[0] + tick
    date_args = {{'H': 'hours', 's': 'seconds', 'm': 'months', 'd': 'days'}[tick]: 1}
    
    # === Extract data from logs === #
    data = [[], []] # group A and B
    
    for line in open(logs, 'r', encoding = 'utf-8').readlines():
        
        # Parse logs
        log, *msg = line.split(': ')
        msg = format_string(': '.join(msg))
        
        # Check if log is concerning user
        if f'Replied to ${user}' in log:
            
            # Parse date
            date = line.split('[serv]')[0][1:-2]
            date = datetime.strptime(date, '%H:%M:%S %d/%m/%Y')
            
            # Append data to the correct data group
            data[not any(map(msg.endswith, triggers))] += [date]
    
    # === Generate plotable data === #
    def plotify(group: list[datetime]) -> tuple[list]:
        '''Called for each group'''
        
        # Cumulate data in a dict
        events, ticks = {}, {}
        
        for date in group:
            key = date.strftime(date_format)
            
            if key not in events.keys(): events[key] = 0
            events[key] += 1
        
        # Generate the missing ticks        
        start = datetime.strptime(min(events.keys()), date_format)
        stop  = datetime.strptime(max(events.keys()), date_format)
        step  = timedelta(**date_args)
        
        while start < stop:
            ticks[start.strftime(date_format)] = 0
            start += step
        
        # Join dicts and format their dates
        res = {datetime.strptime(k, date_format).strftime(viewformat):
            v for k, v in (ticks | events).items()}
        
        return res.keys(), res.values()

    group_a, group_b = map(plotify, data)
    
    # === Plot the data === #
    plt.clf()
    fig = plt.figure(0, frameon = False)
    fig.set_size_inches(15, 8)
    
    # Set colors
    plt.rcParams['axes.facecolor'] = '#00000000'
    plt.rcParams['text.color'] = '#fff'
    
    ax = plt.axes()
    [ax.spines[t].set_color('#fff') for t in ['bottom', 'top', 'right', 'left']]
    [t.set_color('#fff') for t in ax.xaxis.get_ticklabels()]
    [t.set_color('#fff') for t in ax.yaxis.get_ticklabels()]
    
    # Plot data
    plt.plot(*group_a, '-', color = '#F88379')
    plt.plot(*group_b, '-', color = '#DAA06D')
    
    # Set labels
    # xticks = [0, 1000]
    plt.xticks(rotation = -90)
    plt.title(user)
    
    # Save image
    path = f'graphs/{user or "all"}.png'
    plt.savefig(path, bbox_inches = 'tight', dpi = dpi)
    
    return path

# EOF
