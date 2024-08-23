import os
import json
import discord
import logging
import asyncio
from dotenv import load_dotenv
from scraper import Instagram

intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

load_dotenv()
token = os.environ.get('TOKEN')
bot_username = os.environ.get('USERNAME')
bot_password = os.environ.get('PASSWORD')

user_file = 'users.json'
follower_file = 'followers.json'

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    
@client.event
async def on_message(message):
    with open(user_file, 'r') as file:
        user_data = json.load(file)
    discord_user = str(message.author.id)

    if message.author == client.user:
        return
    
    if message.content.startswith('.hello'):
        await handle_hello(message)
    
    elif message.content.startswith('.login'):
        await handle_login(message, user_data, discord_user)

    elif message.content.startswith('.notify'):
        await handle_notify(message, user_data, discord_user)

    elif message.content.startswith('.unfollowers'):
        await handle_unfollowers(message, user_data, discord_user)

    elif message.content.startswith('.logout'):
        await handle_logout(message, user_data, discord_user)

    elif message.content.startswith('.'):
        await message.channel.send('Invalid command. Please use ".hello" to see the list of available commands.')

async def handle_hello(message):
    # await message.channel.send('Hello! My name is TweevilBot, I am here to help you find the tweevils that have unfollowed you. \n\n'
    #                            'I can help you with the following commands: \n '
    #                            '**.login** <username>\n Login with your Instagram account \n\n '
    #                            '**.notify**\nGet weekly notifications of who has unfollowed you. Use ".notify off" to stop notifications\n\n '
    #                            '**.unfollowers**\nSee who has unfollowed you \n\n' 
    #                            '**.logout**\n Remove your Instagram account from our service')
    embed = discord.Embed(
            title="Hello!\n",
            description="My name is TweevilBot, I am here to help you find the tweevils that have unfollowed you.\n\n\n",
            color=0x0066CC99  # Embed color (in this case, green)
    )
    embed.set_footer(text="Here are the commands our bot offers:\n")
    embed.add_field(name=".login <username>", value="Login with your Instagram account\n", inline=False)
    embed.add_field(name=".unfollowers", value="See who has unfollowed you\n", inline=False)
    embed.add_field(name=".notify", value="Get weekly notifications of who has unfollowed you. Use **.notify off** to stop notifications\n", inline=False)
    embed.add_field(name=".logout", value="Remove your Instagram account from our service\n\n\n", inline=False)
    embed.set_footer(text=".hello to see the list of available commands.")
    await message.channel.send(embed=embed)

async def handle_login(message, user_data, discord_user):
    logging.basicConfig(level=logging.INFO)
    if len(message.content.split()) == 1:
        await message.channel.send('Please enter your Instagram username in the following format: \n'
                               '"**.login username**"')
        return
    else:
        insta_handle = str(message.content.split()[1])

    # Check if the user is already in the file
    if discord_user in user_data:
        await message.channel.send('You are already logged in!')
        return
    else:
        await message.channel.send('Logging in... this will take a few minutes.')

        try:
            followers = await retrieve_current_followers(insta_handle)
            logging.info(f"Successfully retrieved followers for {insta_handle}")
        except Exception as e:
            logging.error(f"Error retrieving followers for {insta_handle}: {e}")
            await message.channel.send('Error logging in. Please try again.')
            return

        new_user_data = {"instagram": insta_handle,
                            "notifications": False,
                            "followers": followers}
        user_data[discord_user] = new_user_data

        # Add the user to the file
        with open(user_file, 'w') as file:
            json.dump(user_data, file, indent=4)
        await message.channel.send('You have successfully logged in!')

async def handle_notify(message, user_data, discord_user):
    if message.content == '.notify':
        await message.channel.send('You will now receive weekly notifications of who has unfollowed you.')
        user_data[discord_user]['notifications'] = True
        with open(user_file, 'w') as file:
            json.dump(user_data, file)
    elif message.content == '.notify off':
        await message.channel.send('You will no longer receive notifications of who has unfollowed you.')
        user_data[discord_user]['notifications'] = False
        with open(user_file, 'w') as file:
            json.dump(user_data, file)
    else:
        await message.channel.send('Invalid command. Please use ".notify" to turn on notifications or ".notify off" to turn them off.')

async def handle_unfollowers(message, user_data, discord_user):
    if discord_user not in user_data:
        await message.channel.send('You need to login first. Use "**.login <username>**" to login.')
    else:
        await message.channel.send('Checking for unfollowers... this will take a few minutes.')
        insta_handle = user_data[discord_user]['instagram']
        followers = retrieve_current_followers(insta_handle)
        unfollowers = list(set(user_data[discord_user]['followers']) - set(followers))
        user_data[discord_user]['followers'] = followers

        with open(user_file, 'w') as file:
            json.dump(user_data, file, indent=4)

        if len(unfollowers) == 0:
            await message.channel.send('You have no unfollowers!')
        elif user_data[discord_user]['notifications'] == True:
            user_to_mention = await client.fetch_user(discord_user)
            await message.channel.send(f'{user_to_mention.mention} {unfollowers} has unfollowed you!')
        else:
            await message.channel.send(f'You have {len(unfollowers)} unfollowers: {unfollowers}')

async def handle_logout(message, user_data, discord_user):
    if discord_user not in user_data:
        await message.channel.send('You need to login first. Use "**.login <username>**" to login.')
    else:
        user_data.pop(discord_user)
        with open(user_file, 'w') as file:
            json.dump(user_data, file, indent=4)
        await message.channel.send('You have successfully logged out!')

async def retrieve_current_followers(insta_handle: str):
    insta = Instagram(bot_username, bot_password)
    await insta.login()
    await insta.get_followers([insta_handle])

    with open(follower_file, 'r') as file:
        follower_data = json.load(file)
    return follower_data[insta_handle]
        
client.run(token)