### GROS

Random discord bot

## Dependencies

- discord
- numerize
- matplotlib

Install: `pip install discord numerize matplotlib`

## Usage

For the bot to connect, you must enter the token of a discord bot
into the `token` file.
Along with the triggers, following commands are available:

```jsonc
$stats  // Provide an overall leaderboard of the users that triggered the most
$mstats // Provide secific statistics for a specific user
$jstats // Provide all statistics as a json file
```

For the first 2 commands, the bot will also generate a graph showing the
evolution of the triggering rate.

## Notes

- Bot is rate limited (1 msg per second)
- There is no limitation on the size of the graph data, which means that more data = more time + less readable
- Bot needs all intents
