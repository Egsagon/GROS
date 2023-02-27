import os
import json
import plot
import string
import discord
import datetime
import platform
import threading
from numerize import numerize

logs = open('bot.log', 'a', encoding = 'utf-8')

# Settings
triggers = {'GROS': ['né', 'ner', 'nez', 'nai', 'nait', 'née', 'naie', 'nées', 'nés', 'net',
                     'néz', 'ney', 'nei', 'nes', 'nais'],
            'GARS': ['ni','ny', 'nit', 'nis', 'nig', 'nie']}

board: dict = json.load(open('board.json'))

# Initialize client
client = discord.Client(intents = discord.Intents.all())

def debug(text: str, inst: str = 'serv') -> None:
    
    ortext = text
    global logs
    
    # Print message
    text = text.split()
    for i, word in enumerate(text):
        if word[0] == '$':
            text[i] = f'\033[92m{word}\033[0m'.replace('$', '')
    text = ' '.join(text)
    # print(f'[\033[35m{inst.upper(): ^6}\033[0m] {text}')
    print(f'[\033[35m{inst.upper()}\033[0m] {text}')
    
    # Save to logs
    now = datetime.datetime.now()
    raw = now.strftime('%H:%M:%S %d/%m/%Y')
    logs.write(f'[{raw}] [{inst}] -> {ortext}\n')
    logs.flush()

@client.event
async def on_ready():
    os.system('cls' if platform.system() == 'Windows' else 'clear')
    debug('Bot started')

nrz = lambda int_: numerize.numerize(int_).lower()

@client.event
async def on_message(msg: discord.Message) -> None:
    
    try:
        # Show scoreboard
        if msg.content.startswith('$stats'):
                        
            res = '```json\n' # will color digits
            length = 20
            
            # Sort items
            items = [(a, list(c.values())) for a, c in board.items()]
            items = [(a, (*c, sum(c))) for a, c in items]
            
            # items.sort(key = lambda l: sum(l[1]), reverse = 1)
            items.sort(key = lambda l: l[1][-1], reverse = 1)
            
            # Get totals
            total_a = sum([c[0] for _, c in items])
            total_b = sum([c[1] for _, c in items])
            
            items = [(a, list(map(nrz, c))) for a, c in items]
            
            values = [str(c[0]) for _, c in items]
            values_b = [str(c[1]) for _, c in items]
            values.sort(key = len, reverse = 1)
            values_b.sort(key = len, reverse = 1)
            max_len_a = len(values[0])
            max_len_b = len(values_b[0])
            
            # Ensure there is place for titles
            max_len_a = max(4, max_len_a)
            max_len_b = max(4, max_len_b)
            
            # Set title
            items.insert(0, (' LEADERBOARD ', (' né ', ' ni ', ' sum ')))
            
            for i, (author, (a, b, s)) in enumerate(items):
                
                # Scoreboard length
                if i > 10: break
                
                # Remove weird author chars
                if i:
                    for char in author:
                        if char not in string.printable or not char.strip():
                            author = author.replace(char, '')
                
                if i:		res += f'{i: >2}. {author: <{length}} ┃ {a: <{max_len_a}} ┃ {b: <{max_len_b}} ┃ {s}\n'
                else:		res += f' ┏━━{author:━^{length}}━┳━{a:━<{max_len_a}}━┳━{b:━<{max_len_b}}━┳━{s}━┓\n'
                if i == 10:	res += f' ┗━━{"":━<{length}}━┻━{"":━<{max_len_a}}━┻━{"":━<{max_len_b}}━┻━━━━━━━┛\n'
                
            res += f'\nTOTAL: {nrz(total_a)} (né) + {nrz(total_b)} (ni) = {nrz(total_a + total_b)}'
            await msg.reply(f'{res}```')
            
            # Generate graph
            graph = plot.build('', dpi = 50)
            
            with open(graph, 'rb') as f:
                await msg.reply(file = discord.File(f))
            
            return debug(f'Sending scoreboard for ${msg.author.name} on ${msg.guild.name}', 'NE_STAT')
        
        # Show json scoreboard
        if msg.content.startswith('$jstats'):
            raw = json.dumps(board, indent = 2)
            
            try:
                await msg.author.send(f'```json\n{raw}```')
                await msg.reply('Sent.')
                
            except:
                await msg.reply('Ouvre tes mp grocon')
            
            debug(f'Send json stats to ${msg.author}', 'NE_STAT')
        
        # Show user stats
        if msg.content.startswith('$mstats'):
            stats = board[msg.author.name]
            
            wds = msg.content.split()
			
            if len(wds) == 2:
                kwargs = eval(wds)
            else:
                kwargs = {}
            
            graph = plot.build(msg.author.name, **kwargs)
            
            await msg.reply(f'Stats de {msg.author.name}:\n> GROS ↣ {stats["GROS"]}\n> GARS ↣ {stats["GARS"]}')
            
            with open(graph, 'rb') as f:
                await msg.channel.send(file = discord.File(f))
            
            debug(f'Sent graph to ${msg.author.name}', 'NE_grph')
        
        # Check for triggers
        t = msg.content.lower()
        for char in string.punctuation:
            t = t.replace(char, '')
        t = t.strip()
        
        #for emoji in msg.guild.emojis:
        #    print(emoji.name, emoji.id)
        
        for response, trgs in triggers.items():
            for trigger in trgs:
                
                if t.endswith(trigger):
                    
                    if isinstance(msg.channel, discord.channel.DMChannel):
                        debug(f'${msg.author.name} attempted to dm')
                        return await msg.reply('PATATE')
                    
                    await msg.reply('**' + response + '**')
                    
                    # Save to scoreboard
                    author = msg.author.name
                    
                    if author not in board.keys():
                        board[author] = {'GROS': 0, 'GARS': 0}
                    
                    board[author][response] += 1
                    
                    # Save file
                    with open('board.json', 'w') as f:
                        f.write(json.dumps(board, indent = 3))
                    
                    debug(f'Replied to ${author} on ${msg.guild.name}: {msg.content}')
    
    except Exception as e:
        # debug(f'Raised exception: {type(e)}', 'err')
        raise e

# Run server status as thread
# def run_status(): import mc_status_bot
# threading.Thread(target = run_status).start()

client.run(open('token').read(), log_handler = None)

debug('Bot down')
logs.close()

# EOF
