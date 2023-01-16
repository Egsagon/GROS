'''
https://discord.com/api/oauth2/authorize?client_id=1064590959016423424&permissions=3072&scope=bot
'''

import json
import string
import discord

# Settings
triggers = {'GROS': ['né', 'ner', 'nez', 'nai', 'nait', 'née', 'naie', 'nées', 'nés', 'net',
                     'néz', 'ney', 'nei', 'nes', 'nais'],
            'GARS': ['ni','ny', 'nit']}

board = json.load(open('board.json'))

# Initialize client
client = discord.Client(intents = discord.Intents.all())

@client.event
async def on_ready(): print('Bot ready')

@client.event
async def on_message(msg: discord.Message) -> None:
    
    # Show scoreboard
    if msg.content.startswith('$stats'):
        
        ebd = discord.Embed(
            title = 'Stats' + f'''name {f"{0} | {0}": >100}'''
        )
        
        for author, counts in board.items():
            
            ebd.add_field(
                name = author + f'''{f"{counts['GROS']} | {counts['GARS']}": >100}''',
                value = '',
                inline = True
            )
        
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