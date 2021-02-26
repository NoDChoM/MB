import discord #디스코드 메인 모듈
from discord import permissions  #디스코드 권한 모듈
from discord.ext import commands  #디스코드 명령어 모듈
from discord.utils import get  #디스코드 수집 모듈
from discord.ext.commands import Bot  #디스코드 봇 관련 모듈
from discord import Member  #디스코드 멤버 모듈
import datetime #날자 모듈
from youtube_search import YoutubeSearch #유튜브 검색 결과 수집 모듈
import json #string을 json 형태로 바꿔주는 모듈
import asyncio #비동기 모듈
from discord import FFmpegPCMAudio
import youtube_dl

import os #각종 경로 찾기


youtube_dl.utils.bug_reports_message = lambda: ''

GuildSongInfo = dict()

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

TimeoutLog = dict()
t = open(os.path.dirname( os.path.abspath( __file__ ) )+"/token.txt","r",encoding="utf-8")
token = t.read().split()[0]
activity = discord.Activity(type=discord.ActivityType.listening, name="노래")
bot = commands.Bot(command_prefix='!',status=discord.Status.online,activity=activity)
print("토큰 :",token)

@bot.event
async def on_ready():
    print(f"[{datetime.datetime.now().strftime('%H:%M')}] 봇 준비완료!")



class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        # self.thumbnail = data.get('thumbnails')[1]['url']
        # self.channel = data.get('uploader')
        # self.views = data.get('view_count')
        # self.time = data.get('duration')
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()
    
    #@commands.command()
    async def play(self, ctx, *, query=""):
        """url만 지원, 파일 다운후 실행"""


        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                embed=discord.Embed(description='오류: 음성채널에 들어가있지 않습니다.', color=0xFF0000)
                await ctx.channel.send(embed=embed)
                return
        elif ctx.voice_client.is_playing():
            embed=discord.Embed(description='오류: 노래가 재생중 입니다.', color=0xFF0000)
            await ctx.channel.send(embed=embed)
            return


        if len(query) > 0:
            if not "//www.youtube.com/watch?v=" in query:
                try: results = json.loads(YoutubeSearch(query, max_results=5).to_json())
                except:
                    try: results = json.loads(YoutubeSearch(query, max_results=5).to_json())
                    except: pass
                if len(results['videos']) == 0:
                    try: results = json.loads(YoutubeSearch(query, max_results=5).to_json())
                    except:
                        try: results = json.loads(YoutubeSearch(query, max_results=5).to_json())
                        except: pass
                    if not len(results['videos']):
                        embed = discord.Embed(title="검색결과가 없습니다.",
                                                description=f"'`{query}`' 에 대한 검색결과가 없습니다.",
                                                color=0xFF0000)
                        await ctx.channel.send(embed=embed)
                        return
                embed = discord.Embed(title="노래를 선택해 주세요.",
                                        color=0xFF8C00)
                for i in range(len(results['videos'])):
                    try:
                        embed.add_field(name = f"[{i+1}] {results['videos'][i]['title']}", value = f"채널명: `{results['videos'][i]['channel']}`ㅤㅤ길이: `{results['videos'][i]['duration']}`ㅤㅤ조회수: `{results['videos'][i]['views'][4:]}`", inline=False)
                    except:
                        try:
                            embed.add_field(name = f"[{i+1}] {results['videos'][i]['title']}", value = f"채널명: `{results['videos'][i]['channel']}`ㅤㅤ길이: `{results['videos'][i]['duration']}`ㅤㅤ조회수: `{results['videos'][i]['views'][4:]}`", inline=False)
                        except:
                            pass

                embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
                Emsg = await ctx.channel.send(embed=embed)
                Emoji_L = ["❌"]
                if (len(results['videos']) >= 1):
                    await Emsg.add_reaction("1️⃣")
                    Emoji_L.append("1️⃣")
                if (len(results['videos']) >= 2):
                    await Emsg.add_reaction("2️⃣")
                    Emoji_L.append("2️⃣")
                if (len(results['videos']) >= 3):
                    await Emsg.add_reaction("3️⃣")
                    Emoji_L.append("3️⃣")
                if (len(results['videos']) >= 4):
                    await Emsg.add_reaction("4️⃣")
                    Emoji_L.append("4️⃣")
                if (len(results['videos']) >= 5):
                    await Emsg.add_reaction("5️⃣")
                    Emoji_L.append("5️⃣")
                await Emsg.add_reaction("❌")

                def check(reaction, user):
                    return reaction.message.id == Emsg.id
                    
                try:
                    TimeoutLog[Emsg.id] = datetime.datetime.now() + datetime.timedelta(seconds=20)
                    while True:
                        if TimeoutLog[Emsg.id] > datetime.datetime.now():
                            reaction, user = await bot.wait_for('reaction_add', timeout=(TimeoutLog[Emsg.id]-datetime.datetime.now()).total_seconds(), check=check)
                            if user.id == ctx.author.id:
                                if str(reaction.emoji) in Emoji_L:
                                    break
                                else:
                                    await Emsg.remove_reaction(reaction.emoji, user)
                            else:
                                if user.id != bot.user.id:
                                    await Emsg.remove_reaction(reaction.emoji, user)

                        else:
                            del TimeoutLog[Emsg.id]
                            embed=discord.Embed(description=f'⛔ 시간이 초과되었습니다.', color=0xFF0000)
                            await Emsg.channel.send(embed=embed)
                            break
                    if str(reaction.emoji) != "❌" :
                        for E in reaction.emoji:
                            try:
                                await Emsg.delete()
                                embed = discord.Embed(title="노래가 선택되었습니다.",
                                                        color=0xFF0000)
                                try:
                                    embed.set_thumbnail(url=results['videos'][int(E)-1]['thumbnails'][1])
                                except:
                                    try:
                                        embed.set_thumbnail(url=results['videos'][int(E)-1]['thumbnails'][1])
                                    except:
                                        pass
                                embed.add_field(name="제목 : `" + results['videos'][int(E)-1]['title'] + "`", value=f"채널명: `{results['videos'][int(E)-1]['channel']}`ㅤㅤ길이: `{results['videos'][int(E)-1]['duration']}`ㅤㅤ조회수: `{results['videos'][int(E)-1]['views'][4:]}`", inline=False)
                                embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
                                await ctx.channel.send(embed=embed)

                                embed_ = discord.Embed(title="현재 재생중인 곡 정보.",
                                                        color=0xFF0000)
                                try:
                                    embed_.set_thumbnail(url=results['videos'][int(E)-1]['thumbnails'][1])
                                except:
                                    try:
                                        embed_.set_thumbnail(url=results['videos'][int(E)-1]['thumbnails'][1])
                                    except:
                                        pass
                                embed_.add_field(name="제목 : `" + results['videos'][int(E)-1]['title'] + "`", value=f"채널명: `{results['videos'][int(E)-1]['channel']}`ㅤㅤ길이: `{results['videos'][int(E)-1]['duration']}`ㅤㅤ조회수: `{results['videos'][int(E)-1]['views'][4:]}`", inline=False)
                                GuildSongInfo[ctx.guild.id] = embed_


                                async with ctx.typing():
                                    player = await YTDLSource.from_url("https://www.youtube.com" + results['videos'][int(E)-1]['url_suffix'], loop=self.bot.loop)
                                    ctx.voice_client.play(player, after=lambda e: print('오류 발생 : %s' % e) if e else None)

                                break
                            except ValueError:
                                pass
                    else:
                        await Emsg.delete()
                        embed = discord.Embed(title="취소되었습니다.", color=0xFF0000)
                        await ctx.voice_client.disconnect()
                        await ctx.channel.send(embed=embed)

                except asyncio.exceptions.TimeoutError:
                    embed=discord.Embed(description=f'⛔ 시간이 초과되었습니다.', color=0xFF0000)
                    await Emsg.channel.send(embed=embed)

            else:
                GuildSongInfo[ctx.guild.id] = "https://www.youtube.com" + results['videos'][int(E)-1]['url_suffix']
                async with ctx.typing():
                    player = await YTDLSource.from_url(url, loop=self.bot.loop)
                    ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
                    embed = discord.Embed(title="노래가 선택되었습니다.", color=0xFF0000)
                    try:
                        embed.set_thumbnail(url=player.thumbnail)
                    except:
                        try:
                            embed.set_thumbnail(url=player.thumbnail)
                        except:
                            pass
                    embed.add_field(name="제목 : `" + player.title + "`", value=f"채널명: `{player.channel}`ㅤㅤ길이: `{player.time}`ㅤㅤ조회수: `{player.views}`", inline=False)
                    ctx.channel.send(embed=embed)


    @commands.command()
    async def stream(self, ctx, *, query=""):
        """url만 지원, 파일 다운후 실행"""


        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                embed=discord.Embed(description='오류: 음성채널에 들어가있지 않습니다.', color=0xFF0000)
                await ctx.channel.send(embed=embed)
                return
        elif ctx.voice_client.is_playing():
            embed=discord.Embed(description='오류: 노래가 재생중 입니다.', color=0xFF0000)
            await ctx.channel.send(embed=embed)
            return


        if len(query) > 0:
            if not "//www.youtube.com/watch?v=" in query:
                try: results = json.loads(YoutubeSearch(query, max_results=5).to_json())
                except:
                    try: results = json.loads(YoutubeSearch(query, max_results=5).to_json())
                    except: pass
                if len(results['videos']) == 0:
                    try: results = json.loads(YoutubeSearch(query, max_results=5).to_json())
                    except:
                        try: results = json.loads(YoutubeSearch(query, max_results=5).to_json())
                        except: pass
                    if not len(results['videos']):
                        embed = discord.Embed(title="검색결과가 없습니다.",
                                                description=f"'`{query}`' 에 대한 검색결과가 없습니다.",
                                                color=0xFF0000)
                        await ctx.channel.send(embed=embed)
                        return
                embed = discord.Embed(title="노래를 선택해 주세요.",
                                        color=0xFF8C00)
                for i in range(len(results['videos'])):
                    embed.add_field(name = f"[{i+1}] {results['videos'][i]['title']}", value = f"채널명: `{results['videos'][i]['channel']}`ㅤㅤ길이: `{results['videos'][i]['duration']}`ㅤㅤ조회수: `{results['videos'][i]['views'][4:]}`", inline=False)
                embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
                Emsg = await ctx.channel.send(embed=embed)
                Emoji_L = ["❌"]
                if (len(results['videos']) >= 1):
                    await Emsg.add_reaction("1️⃣")
                    Emoji_L.append("1️⃣")
                if (len(results['videos']) >= 2):
                    await Emsg.add_reaction("2️⃣")
                    Emoji_L.append("2️⃣")
                if (len(results['videos']) >= 3):
                    await Emsg.add_reaction("3️⃣")
                    Emoji_L.append("3️⃣")
                if (len(results['videos']) >= 4):
                    await Emsg.add_reaction("4️⃣")
                    Emoji_L.append("4️⃣")
                if (len(results['videos']) >= 5):
                    await Emsg.add_reaction("5️⃣")
                    Emoji_L.append("5️⃣")
                await Emsg.add_reaction("❌")

                def check(reaction, user):
                    return reaction.message.id == Emsg.id
                    
                try:
                    TimeoutLog[Emsg.id] = datetime.datetime.now() + datetime.timedelta(seconds=20)
                    while True:
                        if TimeoutLog[Emsg.id] > datetime.datetime.now():
                            reaction, user = await bot.wait_for('reaction_add', timeout=(TimeoutLog[Emsg.id]-datetime.datetime.now()).total_seconds(), check=check)
                            if user.id == ctx.author.id:
                                if str(reaction.emoji) in Emoji_L:
                                    break
                                else:
                                    await Emsg.remove_reaction(reaction.emoji, user)
                            else:
                                if user.id != bot.user.id:
                                    await Emsg.remove_reaction(reaction.emoji, user)

                        else:
                            del TimeoutLog[Emsg.id]
                            embed=discord.Embed(description=f'⛔ 시간이 초과되었습니다.', color=0xFF0000)
                            await Emsg.channel.send(embed=embed)
                            break
                    if str(reaction.emoji) != "❌" :
                        for E in reaction.emoji:
                            try:
                                await Emsg.delete()
                                embed = discord.Embed(title="노래가 선택되었습니다.",
                                                        color=0xFF0000)
                                try:
                                    embed.set_thumbnail(url=results['videos'][int(E)-1]['thumbnails'][1])
                                except:
                                    try:
                                        embed.set_thumbnail(url=results['videos'][int(E)-1]['thumbnails'][1])
                                    except:
                                        pass
                                embed.add_field(name="제목 : `" + results['videos'][int(E)-1]['title'] + "`", value=f"채널명: `{results['videos'][int(E)-1]['channel']}`ㅤㅤ길이: `{results['videos'][int(E)-1]['duration']}`ㅤㅤ조회수: `{results['videos'][int(E)-1]['views'][4:]}`", inline=False)
                                embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
                                await ctx.channel.send(embed=embed)

                                embed_ = discord.Embed(title="현재 재생중인 곡 정보.",
                                                        color=0xFF0000)
                                try:
                                    embed_.set_thumbnail(url=results['videos'][int(E)-1]['thumbnails'][1])
                                except:
                                    try:
                                        embed_.set_thumbnail(url=results['videos'][int(E)-1]['thumbnails'][1])
                                    except:
                                        pass
                                embed_.add_field(name="제목 : `" + results['videos'][int(E)-1]['title'] + "`", value=f"채널명: `{results['videos'][int(E)-1]['channel']}`ㅤㅤ길이: `{results['videos'][int(E)-1]['duration']}`ㅤㅤ조회수: `{results['videos'][int(E)-1]['views'][4:]}`", inline=False)
                                GuildSongInfo[ctx.guild.id] = embed_

                                async with ctx.typing():
                                    player = await YTDLSource.from_url("https://www.youtube.com" + results['videos'][int(E)-1]['url_suffix'], loop=self.bot.loop, stream=True)
                                    ctx.voice_client.play(player, after=lambda e: print('오류 발생 : %s' % e) if e else None)

                                break
                            except ValueError:
                                pass
                    else:
                        await Emsg.delete()
                        embed = discord.Embed(title="취소되었습니다.", color=0xFF0000)
                        await ctx.channel.send(embed=embed)

                except asyncio.exceptions.TimeoutError:
                    embed=discord.Embed(description=f'⛔ 시간이 초과되었습니다.', color=0xFF0000)
                    await Emsg.channel.send(embed=embed)

            else:
                GuildSongInfo[ctx.guild.id] = "https://www.youtube.com" + results['videos'][int(E)-1]['url_suffix']
                async with ctx.typing():
                    player = await YTDLSource.from_url(url, loop=self.bot.loop)
                    ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
                    embed = discord.Embed(title="노래가 선택되었습니다.", color=0xFF0000)
                    try:
                        embed.set_thumbnail(url=player.thumbnail)
                    except:
                        try:
                            embed.set_thumbnail(url=player.thumbnail)
                        except:
                            pass
                    embed.add_field(name="제목 : `" + player.title + "`", value=f"채널명: `{player.channel}`ㅤㅤ길이: `{player.time}`ㅤㅤ조회수: `{player.views}`", inline=False)
                    ctx.channel.send(embed=embed)

    @commands.command()
    async def leave(self, ctx):
        """Stops and disconnects the bot from voice"""
        await ctx.voice_client.disconnect()

    @commands.command()
    async def pause(self, ctx):

        vc = ctx.voice_client
        if vc:
            if not vc.is_paused():
                vc.pause()
                embed = discord.Embed(title="노래가 일시중지 되었습니다.", color=0xFF0000)
            else:
                embed = discord.Embed(title="노래가 이미 일시중지 되어있습니다.", color=0xFF0000)
        else:
            embed = discord.Embed(title="현재 노래가 재생중이지 않습니다.", color=0xFF0000)
        await ctx.channel.send(embed=embed)

    @commands.command()
    async def unpause(self, ctx):
        vc = ctx.voice_client
        if vc:
            if vc.is_paused():
                vc.resume()
                embed = discord.Embed(title="노래가 재생됩니다.", color=0xFF0000)
            else:
                embed = discord.Embed(title="노래가 일시정지 되어있지 않습니다.", color=0xFF0000)
        else:
            embed = discord.Embed(title="현재 노래가 재생중이지 않습니다.", color=0xFF0000)
        await ctx.channel.send(embed=embed)

    @commands.command()
    async def song(self, ctx):
        if ctx.voice_client.is_playing():
            await ctx.channel.send(embed=GuildSongInfo[ctx.guild.id])

        else:
            embed=discord.Embed(description='현재 노래가 재생중이지 않습니다.', color=0xFF0000)
            await Emsg.channel.send(embed=embed)

    @commands.command()
    async def volume(self, ctx):
        embed=discord.Embed(description="음성채널에서 프로필을 오클릭하여 조절해주세요.", color=0xFF0000)
        await ctx.channel.send(embed=embed)

bot.add_cog(Music(bot))

token = os.environ["BOT_TOKEN"]
bot.run(token)
