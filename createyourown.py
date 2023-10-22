import discord
from discord.ext import commands
import openai
import os
from dotenv import load_dotenv
import aiohttp
import re
import base64
import requests
from io import BytesIO
import aiohttp
import asyncio



load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
intents.messages = True
intents.guilds = True
openai.api_key=os.getenv('API_Key')
token=os.getenv('DISCORD_TOKEN')


questions = [
    "🌟 Name your Odo: 🌟  ",
    "🌟 Describe personalities of your Odo🌟 ",
    "🌟 Preferred Bot profile picture 🌟(only png/jpg are acceptable) ",
    "Just one more step to go! \n🌟 Could you please share your email address? 🌟 "
]


user_data = {}

# Function to generate an image from OpenAI API
async def generate_image(prompt):
    # Generate image URL using OpenAI
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024"  # or whatever size you prefer
    )

    image_url = response["data"][0]["url"]
    return image_url

# Function to generate an answer from OpenAI API
async def generate_answer(prompt):
    try:
        
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=100  # adjust as needed
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error: {e}")
        return "Error generating answer."

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.event
async def on_message(message):
    example_answers = ["Odo", "Friendly, talkative, and curious.", "odo_picture.png/odo_picture.jpg","example@example.com "]
    
    # Ignore messages from bots
    if message.author.bot:
        return
    
    # Check if the bot is mentioned without mentioning others
    if bot.user.mentioned_in(message) and len(message.mentions) == 1:
        user_id = message.author.id
        user_data[user_id] = {"step": 0, "answers": []}

        await message.author.send(
            "🎉 Welcome! 🎉 \n Let's create your Odo 🤖 (an AI character, AI friend)). \n" + questions[0]
            + f"\n Example answer: '{example_answers[0]}' \n Type `auto` if you'd like me to complete the answer for you. "
        )
        #await message.author.send(f"Example answer: '{example_answers[0]}' \n Type `auto` if you'd like me to complete the answer for you. ")
        await message.channel.send(f"{message.author.mention}, I've sent you a DM with more information!")
        return
    
    user_id = message.author.id
    if user_id in user_data and user_data[user_id]["step"] < len(questions):
        if 'auto' in message.content.lower():
            # Generate the appropriate prompt for the current step
            if user_data[user_id]["step"] == 0:
                prompt = "Generate a name."
                # Show typing indicator while generating answer
                async with message.channel.typing():
                    answer = await generate_answer(prompt)

                user_data[user_id]["answers"].append(answer)
                user_data[user_id]["step"] += 1
                # print(user_data[user_id]["answers"])
                await message.author.send(f"Answer autofilled with: {answer} \n \n 🚀Moving on.🚀")

            elif user_data[user_id]["step"] == 1:
                prompt = f"Describe personalities and appearance of {user_data[user_id]['answers'][0]}: \nPlease provide an answer in five sentences."

                # Show typing indicator while generating answer
                async with message.channel.typing():
                    answer = await generate_answer(prompt)

                user_data[user_id]["answers"].append(answer)
                user_data[user_id]["step"] += 1
                # print(user_data[user_id]["answers"])
                await message.author.send(f"Answer autofilled with: {answer} \n \n 🚀Moving on.🚀")

            elif user_data[user_id]["step"] == 2:
                prompt = f"A clear and concise prompt for a avatar with the following property: {user_data[user_id]['answers'][1]} \n Make the prompt for the digital avatar's headshot profile picture for a social media platform. .jpg/.png format"
                # prompt="cute minimalistic avatar of a smiling young woman with open eyes, looking at the camera, black and white, sharp focus, monochromatic, simple clean line, notion style –q 2 –v 5 –s 750"
                prompt =await generate_answer(prompt)
                async with message.channel.typing():
                    image_url = await generate_image(prompt)

                
                user_data[user_id]["answers"].append(image_url)
                await message.author.send(f"Profile picture generated! Here it is: {image_url}")
                user_data[user_id]["step"] += 1
                # print(user_data[user_id]["answers"])
            
        else:
            if user_data[user_id]["step"] ==1:
                async with message.channel.typing():
                    answer=await generate_answer(str(user_data[user_id]["answers"][0])+"\nPlease provide an answer in five sentences.")
                user_data[user_id]["answers"].append(answer)
                user_data[user_id]["step"] += 1
                # print(user_data[user_id]["answers"])
            elif user_data[user_id]["step"] ==2:
                image_url=message.content
                if image_url.lower().endswith(('.png', '.jpg', '.jpeg')):
                    user_data[user_id]["answers"].append(image_url)
                    await message.author.send(f"Profile picture generated! Here it is: {image_url}")
                    user_data[user_id]["step"] += 1
                else:
                    await message.author.send("Invalid file format. Please upload a JPG file.")
                user_data[user_id]["answers"].append(message.content)
                user_data[user_id]["step"] += 1
            elif user_data[user_id]["step"] == 3:
                pattern = r"[^@]+@[^@]+\.[^@]+"
                if re.match(pattern, message.content):
                    # If valid, proceed to the next step
                    user_data[user_id]["answers"].append(message.content)
                    user_data[user_id]["step"] += 1
                    # print(user_data[user_id]["answers"])
                else:
                    # If invalid, ask again until a valid email is provided
                    await message.author.send("⚠️ The email you provided is invalid. Please make sure it's a correct email address.")
                    return 

            else:
                user_data[user_id]["answers"].append(message.content)
                user_data[user_id]["step"] += 1
                print(user_data[user_id]["answers"])

        
        if user_data[user_id]["step"] < len(questions)-1:
            await message.author.send(questions[user_data[user_id]["step"]])
            await message.author.send(f"Example answer: '{example_answers[user_data[user_id]['step']]}' \n Type `auto` if you'd like me to complete the answer for you. ")
            print(user_data[user_id]["answers"])
        elif user_data[user_id]["step"] == len(questions)-1:
            await message.author.send(questions[user_data[user_id]["step"]])
            print(user_data[user_id]["answers"])
        else:
            await message.author.send("Congratulations! 🎉 Now you can take your Odo home! ")
            print(user_data[user_id]["answers"])

            url = "https://testflight.apple.com/join/gaOapjan"  # Replace with your desired URL
            button = discord.ui.Button(label="Finish Setup", url=url, style=discord.ButtonStyle.link)
            # button = discord.ui.Button(label="Invite to server", url=url, style=discord.ButtonStyle.link)
            view = discord.ui.View()
            view.add_item(button)
            await message.author.send("Click below to finish setup in the app!", view=view)
        
        
        await call_api(user_id)
        
        

    if isinstance(message.channel, discord.DMChannel):
        
        if message.content.startswith('Profile'):
            user_email = message.content[len('Profile '):].strip()
            # print(user_email)

            if not user_email:
                await message.channel.send("Please provide an email after Profile.")
                return

            async with aiohttp.ClientSession() as session:
                character_data = await fetch_character_data(session, f'https://emwv7umxn9.us-east-1.awsapprunner.com/bots/user/{user_email}', user_email)
                print(character_data)

                if 'error' in character_data:
                    await message.channel.send(character_data['error'])
                else:
                    name = character_data[0]['botName']
                    personality = character_data[0]['description']
                    avatar = character_data[0]["image"]['imageUrl']
                    
                    # response = f"**Name:** {name}\n**Personality:** {personality} "
                    response = f"**Name:** {name}\n**Personality:** {personality} \n**Profile Picture:** {avatar}"
                    # print("aaa")
                    # print(avatar)
                    await message.channel.send(response)
        


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found!")
    else:
        await ctx.send("An error occurred while processing the command.")
        print(f"Error: {error}")


@bot.event
async def call_api(user_id):

    # Extract user data
    user_answers = user_data[user_id]["answers"] if user_id in user_data else None
    # print("answer")

    # Ensure the user_answers contains the expected data
    if not user_answers or len(user_answers) < 4:
        print(f"User data for user ID {user_id} is incomplete.")
        return
    
    
    # Construct the payload from the answers
    payload = {
        'userEmail': user_answers[3],  
        'botName': user_answers[0],
        'botDescription': user_answers[1],
        'isPublic': True,
        

    }
    

    url = 'https://emwv7umxn9.us-east-1.awsapprunner.com/bots/create'
    headers =  {
        'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
        # 'Content-Length' will be automatically set by the aiohttp library
    }

    async with aiohttp.ClientSession() as session:
        # print('run')
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                print(data)
                await update_image_data(user_id,data)
            else:
                print(f'Failed to call API. Status code: {response.status}. Reason: {response.text}')
                

    
    
    

async def fetch_character_data(session, url, email):
    params = {'email': email}
    print(email)
    async with session.get(url, params=params) as response:
        return await response.json()

async def update_image_data(user_id,data):
    user_answers = user_data[user_id]["answers"] if user_id in user_data else None
    pic=await get_image(user_answers[2])
    
    profpic = base64.b64encode(pic)
    profpic_str = profpic.decode('utf-8')
    print("profpic_str")
    
    # Construct the payload from the answers
    payload = {
        'base64Image': profpic_str

    }
    print("payload")
    api_url = f"https://emwv7umxn9.us-east-1.awsapprunner.com/bots/{data['bot']['id']}/replace-image"
    headers =  {
        'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
        # 'Content-Length' will be automatically set by the aiohttp library
    }

    async with aiohttp.ClientSession() as session:
        async with session.put(api_url, json=payload, headers=headers) as response:
            print('run')
            if response.status == 200:
                print(response)
                data = response
                print(data)
            else:
                print(f'Failed to call update API. Status code: {response.status}. Reason: {response.text}')
    

async def get_image(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            # Raise an exception if the GET request was unsuccessful
            if response.status != 200:
                raise aiohttp.HttpProcessingError(code=response.status, message="Failed to download image")
            
            data = await response.read()
            return data

    



bot.run(token)

