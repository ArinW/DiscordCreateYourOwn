import discord
from discord.ext import commands
import aiohttp
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import os


load_dotenv()
TOKEN=os.getenv('TOKEN')

# Define the required intents
intents = discord.Intents.default()
intents.message_content = True  # Enables the message content intent
intents.presences = True  # Optionally enable presence updates (if needed)
intents.members = True 

bot = commands.Bot(command_prefix="/", intents=intents)  # Changed prefix to "/"

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    print(bot.user.name)


@bot.event
async def on_message(message):
    # print(bot.user.name)
    # Check if message is from the bot itself or if it's not in the target channel
    target_channel_id = 1166560391497777262  # Replace with your target channel's ID
    print(message.channel.id)
    if message.author == bot.user or message.channel.id != target_channel_id:
        return
    
    if message.content.startswith('Invitebot'):
        email = message.content.split()[-1]  # Get the email part of the command
        print(email)
        # Fetch character data
        async with aiohttp.ClientSession() as session:
            character_data = await fetch_character_data(session, f'https://tky4ccw9mr.us-east-1.awsapprunner.com/bots/user/{email}', email)
            
            name = character_data[0]['botName']
            avatar = character_data[0]["image"]['imageUrl']
            avatar = await fetch_and_resize_image(avatar)

                
            permissions = discord.Permissions.all()

            # Change bot's username
            await bot.user.edit(username=name)
            print(f'Bot username changed to: {bot.user.name}')

            # Changing bot's avatar
            await bot.user.edit(avatar=avatar.read())

            # Use the bot ID in the URL
            invite_url = discord.utils.oauth_url(client_id=bot.user.id, permissions=permissions)
            print(f'Invite URL: {invite_url}')

            target_channel = bot.get_channel(target_channel_id)
            await target_channel.send(f"You can invite me to your server now {invite_url}")
            


async def fetch_character_data(session, url, email):
    params = {'email': email}
    print(email)
    async with session.get(url, params=params) as response:
        return await response.json()

async def fetch_and_resize_image(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            image_data = await response.read()

    # Open the image using Pillow
    image = Image.open(BytesIO(image_data))

    # Resize the image to 128x128 pixels
    image = image.resize((128, 128))

    # Save the resized image to a BytesIO object
    byte_data = BytesIO()
    image.save(byte_data, format="PNG")
    byte_data.seek(0)  # Seek back to the beginning of the BytesIO object

    return byte_data

bot.run(TOKEN)
