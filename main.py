'''
https://discord.com/api/oauth2/authorize?client_id=1064590959016423424&permissions=3072&scope=bot
'''

import json
import string
import discord
from collections import OrderedDict

# Settings
triggers = {'GROS': ['né', 'ner', 'nez', 'nai', 'nait', 'née', 'naie', 'nées', 'nés', 'net',
                     'néz', 'ney', 'nei', 'nes', 'nais'],
            'GARS': ['ni','ny', 'nit']}

board: dict = json.load(open('board.json'))

# Initialize client
client = discord.Client(intents = discord.Intents.all())

@client.event
async def on_ready(): print('Bot ready')

@client.event
async def on_message(msg: discord.Message) -> None:
    
    # Show scoreboard
    if msg.content.startswith('$stats'):
        
        pad = 10
        ebd = discord.Embed(title = f'Stats{pad * " "}GROS, GARS')
        
        # Sort items
        items = list(board.items())
        items.sort(key = lambda l: l[1]['GROS'] + l[1]['GARS'], reverse = 1)
        
        for author, counts in items:
            
            # TODO - Crappy, refactor
            a, b = counts.values()
            x = list(f"{f'{a}, {b}': >{pad + 18}}")
            
            for i, char in enumerate(author): x[i] = char
            x = ''.join(x)
            
            ebd.add_field(name = f'```{x}```', value = '', inline = False)
        
        return await msg.channel.send(embed = ebd)

    # Check for triggers
    for response, trgs in triggers.items():
        for trigger in trgs:
            t = msg.content.lower()
            
            for char in string.punctuation:
                t = t.replace(char, '')
            
            if t.strip().endswith(trigger):
                await msg.reply(response)
                
                # Save to scoreboard
                author = msg.author.name
                
                if author not in board.keys():
                    board[author] = {'GROS': 0, 'GARS': 0}
                
                board[author][response] += 1
                
                # Save file
                with open('board.json', 'w') as f:
                    f.write(json.dumps(board, indent = 3))

client.run(open('token').read())    
