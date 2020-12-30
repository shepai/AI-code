from AI import AI
import discord

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)
        self.bots={}
        
    async def on_message(self, message):
        #Assign a bot to each person
        if message.author == self.user:
            return
        if str(message.channel)=="shep-v0010":
            self.bots[message.author]=self.bots.get(message.author,[AI()])
            cleverBot=self.bots[message.author][0] #get current bot
            await message.channel.send("@"+message.author.name+" "+cleverBot.chat(message.content))
            
client = MyClient()
client.run('tag')

#NzkxMz
#GHGND
#Y2NDAy
#ODkxND
#Q4MzYw
#.X-OHZQ
#.Tr21o5q
#All6dFLB
#NsjJ3dPY8Oik
