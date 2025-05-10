import discord
from discord.ext import commands
# -----------------------------------------------------------------------------------------------------------------------------------------------
import urllib.request
import re
import random
# -----------------------------------------------------------------------------------------------------------------------------------------------
import pymongo
from pymongo import MongoClient
import ast
import asyncio
from discord.utils import find
import bs4
from bs4 import BeautifulSoup

from lxml import etree
# -----------------------------------------------------------------------------------------------------------------------------------------------
import requests
from requests.exceptions import ConnectionError
# -----------------------------------------------------------------------------------------------------------------------------------------------
import tmdbsimple as tmdb1
tmdb1.API_KEY = '76e5b1afa53174c3572becb4263bcbef'

from tmdbv3api import TMDb
tmdb = TMDb()
from tmdbv3api import Movie
tmdb.api_key = '76e5b1afa53174c3572becb4263bcbef'

from imdb import IMDb
ia = IMDb()
# -----------------------------------------------------------------------------------------------------------------------------------------------
prefix = "!"
client = commands.Bot(command_prefix=prefix)
# -----------------------------------------------------------------------------------------------------------------------------------------------
mongoPath = "mongodb+srv://senthu:"
mongoHostPath = "@watchlistbot.ssjho.mongodb.net/"
mongoHostEnd = "?retryWrites=true&w=majority"
mongo_url = mongoPath + urllib.parse.quote_plus(
    "Caesar@2017") + mongoHostPath + urllib.parse.quote_plus("database") + mongoHostEnd
cluster = MongoClient(mongo_url)
db = cluster["letterbox"]
collection = db["users"]
# -----------------------------------------------------------------------------------------------------------------------------------------------
emptyArr = []
textPrefix = "list"
embedname = "The Letterboxd Bot" 
embedTick = "https://i.imgur.com/hwDZGsV.png"
embedCross = "https://i.imgur.com/w1ChmUP.png"
# -----------------------------------------------------------------------------------------------------------------------------------------------
def embedRight(url, embed):
    embed.set_thumbnail(url = url) 
    embed.set_author(name=embedname, icon_url=embedTick)
def embedWrong(url, embed):
    embed.set_thumbnail(url = "https://i.imgur.com/2TGrhu2.png") 
    embed.set_author(name=embedname, icon_url=embedCross)
def argumentError(ctx,embed):
    embed.set_thumbnail(url = "https://i.imgur.com/2TGrhu2.png") 
    embed.set_author(name=embedname, icon_url=embedCross)
def get_author_name(ctx):
    target = str(ctx.author)
    target = target[:-5]
    return target
def get_author_id(ctx):
    return str(ctx.author.id)
def lb_pfp(ctx, user):
    IMGsearch = urllib.request.urlopen("https://letterboxd.com/"+user+"/")
    mybytesIMG = IMGsearch.read()
    IMGgetUser = mybytesIMG.decode("utf8")
    IMGsearch.close()
    pfpimage = re.findall(r'img src=".+?" alt=',IMGgetUser)
    imgurl = str(pfpimage[0])
    imgurl = imgurl[9:-6]
    imgurl = imgurl.replace("amp;", "")
    return imgurl
def get_movie_poster(getUser, post):
    posters = re.findall(r'srcset=".+? ',getUser)
    single = posters[0]
    single = str(single)[8:-1]
    return single
def get_movie_page(movie):
    url = "https://letterboxd.com/film/"+movie+"/"
    search = urllib.request.urlopen(url)
    mybytes = search.read()
    getUser = mybytes.decode("utf8")
    search.close()
    return getUser
def get_movie_title(getUser, movie):
    matchesTitle = re.findall(r'<meta.+?>',getUser)
    matchesString = str(matchesTitle[6]).replace('<meta property="og:title" content="',"").replace('"',"").replace('" />','').replace(" />","")
    matchesString = matchesString.replace("&#039;", '')
    matchesString = matchesString.replace('&quot;',"")
    return matchesString  
def get_movie_desc(getUser, movie):
    matchesDesc = re.findall(r'<p>.+?</p>',getUser)
    formatDesc = str(matchesDesc[0]).replace("<p>","").replace("</p>", "").replace("&#039;","'").replace('&quot;',"")
    return formatDesc
def get_movie_rating(getUser, movie):
    ratingString = "N/A"
    rating = re.findall(r'<meta.+?>',getUser)
    if len(rating) > 0:
        index = [i for i, s in enumerate(rating) if 'out of' in s]
        if len(index) > 0:
            ratingSingle = re.findall(r'".+? out',rating[index[0]])
            ratingString = str(ratingSingle[0]).replace('twitter:data2" content="',"").replace(" out", "").replace('"', "")
        else:
            ratingString = "N/A"
    else:
        ratingString = "N/A"
    return ratingString
# -----------------------------------------------------------------------------------------------------------------------------------------------
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name=prefix + "randomize" + " - " + str(len(client.guilds)) + " Servers"))
    print('Ready')
# -----------------------------------------------------------------------------------------------------------------------------------------------
@client.event
async def on_commmand_error(ctx, error):
    pass
# -----------------------------------------------------------------------------------------------------------------------------------------------
@client.event
async def on_guild_remove(guild):
    await client.change_presence(activity=discord.Game(name=prefix + "randomize" + " - " + str(len(client.guilds)) + " Servers"))
@client.event
async def on_guild_join(guild):
    await client.change_presence(activity=discord.Game(name=prefix + "randomize" + " - " + str(len(client.guilds)) + " Servers"))
# -----------------------------------------------------------------------------------------------------------------------------------------------   
@client.command()
async def randomize(ctx, *, user=None): 
    debug = False
    #=======================================================================================
    if user is None:
        result = collection.find_one({'_id': get_author_id(ctx)})['LetterboxName']
        if result is not None:
            user = result
        else:
            return
    #=======================================================================================
    if debug == False:
        user = user.replace(" ", "-")
        print(user)
        search = urllib.request.urlopen("https://letterboxd.com/"+user+"/watchlist/")
        mybytes = search.read()
        getUser = mybytes.decode("utf8")
        search.close()
    
        matches = re.findall(r'film/.+?/"',getUser)
        if str(matches) == "[]":
            embed = discord.Embed(
                title="Empty",
                description="That user has no movies in their watchlist",
                colour=discord.colour.Color.red()
            )
            embedWrong(embedCross, embed)
            await ctx.channel.send(embed=embed)
    #=======================================================================================
        else:
            numPage = re.findall(r'/page/.+?/',getUser)
            onlyNum = re.findall(r'\d+', str(numPage))
            finalPage = onlyNum[len(onlyNum)-1]
            finalArr = []
            
            ranPage = random.randint(1,int(finalPage))
            search = urllib.request.urlopen(
                "https://letterboxd.com/"+user+"/watchlist/"+"page/"+str(ranPage)+"/")
            mybytes = search.read()
            getUser = mybytes.decode("utf8")
            search.close()

            matches = re.findall(r'film/.+?/"',getUser)
            matches = list(dict.fromkeys(matches))

            imgurl = lb_pfp(ctx, user)

            for items in matches:
                finalArr.append(str(items))

            gen = random.randint(0,len(finalArr))
            Filmstring = finalArr[gen]
            SearchString = Filmstring.replace('film/', "").replace('/"', "")
            getTitleUser = get_movie_page(SearchString)
            Final = get_movie_title(getTitleUser, SearchString)

            searchposter = urllib.request.urlopen("https://letterboxd.com/film/"+SearchString+"/")
            mybytesposter = searchposter.read()
            getPoster = mybytesposter.decode("utf8")
            searchposter.close()
            posters = re.findall(r'srcset=".+? ',getPoster)
            single = posters[0]
            single = str(single)[8:-1]
           
            embed = discord.Embed(
                title="Movie: " + Final,
                url="https://letterboxd.com/film/"+SearchString+"/",
                description="From user: " + user,
                colour=discord.colour.Color.blue()
            )
            embed.set_image(url = single)
            embedRight(imgurl, embed)
            await ctx.channel.send(embed=embed)
    #=======================================================================================
# -----------------------------------------------------------------------------------------------------------------------------------------------
@randomize.error
async def randomizeError(ctx, error):
    errorS = str(error)
    
    if str(errorS) == "Command raised an exception: HTTPError: HTTP Error 401: Unauthorized":
        embed = discord.Embed( 
            title = "Error",
            description = "This user's watchlist has been privated",        
            colour=discord.colour.Color.red()
        )
        argumentError(ctx,embed)
        await ctx.channel.send(embed=embed)
    elif str(errorS) == "Command raised an exception: HTTPError: HTTP Error 404: Not Found":
        embed = discord.Embed( 
            title = "Error",
            description = "There are no users with this username on letterbox",        
            colour=discord.colour.Color.red()
        )
        argumentError(ctx,embed)
        await ctx.channel.send(embed=embed)
    elif str(errorS) == "Command raised an exception: TypeError: 'NoneType' object is not subscriptable":
        embed = discord.Embed( 
            title = "Error",
            description = "You have not set up an account. Type in **!setup <username>** to set yourself a username" + "\n" +
            "Once you do so, the randomize command needs no arguments to show from your own list",         
            colour=discord.colour.Color.red()
        )
        argumentError(ctx,embed)
        await ctx.channel.send(embed=embed)
# -----------------------------------------------------------------------------------------------------------------------------------------------
@client.command()
async def setuser(ctx, *, user):
    #=======================================================================================
    id = get_author_id(ctx)
    results = collection.find({"_id": {'$exists': id}})
    check = False
    for x in results:
        SubstringX = str(x)
        Modified = SubstringX[9:27]
        if Modified == id:
            check = True
    #=======================================================================================
    isLBacc = False
    search = urllib.request.urlopen("https://letterboxd.com/"+user+"/")
    mybytes = search.read()
    getUser = mybytes.decode("utf8")
    search.close()
    if "error message" not in getUser:
        isLBacc = True
        imgurl = lb_pfp(ctx, user)
    #=======================================================================================
    if isLBacc == True:
        if check == False:
            create_id = {"_id": id, "LetterboxName": user}
            collection.insert_one(create_id)
            embed = discord.Embed(
                title="User has been set!",
                description='Letterbox User: '+user + "\n"
                + "Discord name: " + get_author_name(ctx),
                colour=discord.colour.Color.green(),
            )
            embedRight(imgurl, embed)
            await ctx.channel.send(embed=embed)
        else:
            collection.update_one({"_id":id},{"$set":{"LetterboxName":user}})
            embed = discord.Embed(
                title="User has been set!",
                description='Letterbox User: '+user + "\n"
                + "Discord name: " + get_author_name(ctx),
                colour=discord.colour.Color.green(),
            )
            embedRight(imgurl, embed)
            await ctx.channel.send(embed=embed)
    #=======================================================================================
    else:
        await ctx.channel.send("error")
# -----------------------------------------------------------------------------------------------------------------------------------------------
@setuser.error
async def setuserError(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed( 
            title = "Error",
            description = "Missing argument! Usage is '!setuser <letterbox username>'",
            colour=discord.colour.Color.red()
            )
        argumentError(ctx,embed)
        await ctx.channel.send(embed=embed)
    else:
        embed = discord.Embed( 
            title = "Error",
            description = "- The user you have entered does not exist on letterboxd :(",         
            colour=discord.colour.Color.red()
            )
        argumentError(ctx,embed)
        await ctx.channel.send(embed=embed)
# -----------------------------------------------------------------------------------------------------------------------------------------------
@client.command()
async def account(ctx, *, user=None):
    #=======================================================================================
    if user is None:
        result = collection.find_one({'_id': get_author_id(ctx)})['LetterboxName']
        if result is not None:
            user = result
        else:
            return   
    #======================================================================================= 
    isLBacc = False
    search = urllib.request.urlopen("https://letterboxd.com/"+user+"/")
    mybytes = search.read()
    getUser = mybytes.decode("utf8")
    search.close()

    searchWL = urllib.request.urlopen("https://letterboxd.com/"+user+"/watchlist/")
    mybytesWL = searchWL.read()
    getUserWL = mybytesWL.decode("utf8")
    searchWL.close()
    #======================================================================================= 
    if "error message" not in getUser:
        isLBacc = True
        imgurl = lb_pfp(ctx, user)
    #======================================================================================= 
    if isLBacc == True:
        titles = re.findall(r'"value">.+?</span>',getUser)
        
        findWL = re.findall(r'see .+?&n',getUserWL)
        WLstr = findWL[0]
        WLstr = WLstr.replace("see ", "")
        WLstr = WLstr.replace("&n", "")
       
        def replace(array, index):
            string = str(array[index])
            string = string.replace('"value">', "")
            string = string.replace("</span>", "")
            return string

        seen = replace(titles, 0)
        Cyear = replace(titles, 1)
        lists = replace(titles, 2)
        following = replace(titles,3)
        follows = replace(titles, 4)
        embed = discord.Embed(
            title= user + "'s Profile",
            url = "https://letterboxd.com/"+user+"/",
            description = "Films watched: " + "**" + seen + "**" + "\n" +
            "This year: " + "**" + Cyear + "**" + "\n" +
            "Lists made : " + "**" + lists + "**" + "\n" +
            "Following : " + "**" + following + "**" + "\n" +
            "Followers : " + "**" + follows + "**" + "\n" +
            "Watchlist : " + "**" + WLstr + "**" + "\n",
            colour=discord.colour.Color.teal()
        ) 
        embedRight(imgurl, embed)
        await ctx.channel.send(embed=embed)
    #======================================================================================= 
# -----------------------------------------------------------------------------------------------------------------------------------------------
@account.error
async def accountError(ctx, error):
    errorS = str(error)
    if str(errorS) == "Command raised an exception: HTTPError: HTTP Error 404: Not Found":
        embed = discord.Embed( 
            title = "Error",
            description = "There are no users with this username on letterbox",        
            colour=discord.colour.Color.red()
        )
        argumentError(ctx,embed)
        await ctx.channel.send(embed=embed)
    elif str(errorS) == "Command raised an exception: TypeError: 'NoneType' object is not subscriptable":
        embed = discord.Embed( 
            title = "Error",
            description = "You have not set up an account. Type in **!setuser <username>** to set yourself a username" + "\n" +
            "Once you do so, the randomize command needs no arguments to show from your own list",         
            colour=discord.colour.Color.red()
        )
        argumentError(ctx,embed)
        await ctx.channel.send(embed=embed)
# -----------------------------------------------------------------------------------------------------------------------------------------------
@client.command(pass_context = True , aliases=['s', 'stats', 'film'])
async def f(ctx, *, Entermovie):
    #=======================================================================================
    movie = Movie()
    #=======================================================================================
    Entermovie = SearchLB(ctx, Entermovie)
    #=======================================================================================
    getUser = get_movie_page(Entermovie)
    formatTitle = get_movie_title(getUser, Entermovie)
    #=======================================================================================
    directorArray = []
    matches = re.findall(r'/director/.+?/">',getUser)
    
    for items in matches:
        item = str(items)
        item = item.replace("/director/", "").replace('/">',"").replace("-", " ")
        item = item.title()
        directorArray.append(item)

    directorText = ""
    directorString = ""
    if len(directorArray) == 0:
        directorString = "N/A"
        directorText = "Director"
    else:
        directorString = str(directorArray).replace("[","").replace("]","").replace(",",", ").replace("'",'')
        directorString = ''.join(i for i in directorString if not i.isdigit())
        if len(directorArray)>1:
            directorText = "Directors"
        else:
            directorText = "Director"
    #=======================================================================================
    trailerText = ""
    trailerLink = ""
    trailer = re.findall(r'data-track-category="Trailer".+?">',getUser)
    if len(trailer) == 0:
        trailerText = "N/A"
    else:
        trailerText = "Trailer"
        trailerLink = str(trailer[0])
        trailerLink = trailerLink.replace('data-track-category="Trailer" href="//www.youtube.com/embed/', '')
        trailerLink = trailerLink.replace('?rel=0&amp;wmode=transparent">', '')
    #=======================================================================================
    posterURL = get_movie_poster(getUser, Entermovie)
    ratingString = get_movie_rating(getUser, Entermovie)
    if ratingString == "N/A":
        Percentage = "N/A"
    else:
        Percentage = (float(ratingString)/5)*100
        Percentage = ("%.0f" % Percentage)
        Percentage = Percentage + "%"
    #=======================================================================================
    tmbdID = re.findall(r'data-tmdb-id=".+?">',getUser)
    searchID = str(tmbdID[0])
    searchID = searchID.replace('data-tmdb-id="','').replace('">','')

    movie = tmdb1.Movies(searchID)
    response = movie.info()
    get = str(response)
    RunTime = re.findall(r'runtime.+?,',get)
    RunTime = str(RunTime).replace("runtime': ","").replace(",","").replace('["',"").replace('"]',"")
    
    Hours = int(RunTime)//60
    Minutes = int(RunTime) % 60
    TimeString = str(Hours) + "hr " + str(Minutes) + "mins" 
    if TimeString == "0hr 0mins":
        TimeString = "N/A"
    else:
        TimeString = TimeString
    #=======================================================================================
    Budget = re.findall(r'budget.+?,',get)
    Budget = str(Budget).replace("budget': ","").replace(",","").replace('["',"").replace('"]',"")
    Budget = f"{int(Budget):,d}"
    Budget = "$" + str(Budget)
    if Budget == "$0":
        Budget = "N/A"
    else:
        Budget= Budget

    BO = re.findall(r'revenue.+?,',get)
    BO = str(BO).replace("revenue': ","").replace(",","").replace('["',"").replace('"]',"")
    BO = f"{int(BO):,d}"
    BO = "$" + str(BO)
    if BO == "$0":
        BO = "N/A"
    else:
        BO= BO
    #=======================================================================================
    Backdrop = re.findall(r'backdrop_path.+?,',get)
    Backdrop = str(Backdrop[0]).replace("backdrop_path': ","").replace(",","").replace('["',"").replace('"]',"").replace("}","")
    Backdrop = Backdrop[2:-1]
    Backdrop = "https://image.tmdb.org/t/p/original/" + str(Backdrop)
    #=======================================================================================
    embed = discord.Embed(
        title = formatTitle,
        url = "https://letterboxd.com/film/"+Entermovie+"/",
        description = "**"+directorText+":**" + " "+ directorString + "\n"+
        "**Letterboxd Rating:**" + " " + ratingString + " (" + str(Percentage) + ")" + "\n"+
        "**Runtime:**" + " " + TimeString + "\n" +
        "-----------------------------------"+ "\n" + 
        "**Budget:**" + " " + Budget + "\n" +
        "**Box Office:**" + " " + BO + "\n" +
        "-----------------------------------",
        colour=discord.colour.Color.blue()
    )
    if trailerText == "Trailer":
        embed.add_field(name = "⠀", value = "**Trailer:** [Click here](https://www.youtube.com/watch?v="+trailerLink+")")
    else:
        embed.add_field(name = "⠀", value = "**Trailer:** " + trailerText)

    embed.set_image(url = Backdrop)
    embed.set_thumbnail(url =posterURL) 
    embed.set_author(name=embedname, icon_url=embedTick)
    await ctx.channel.send(embed=embed)
# -----------------------------------------------------------------------------------------------------------------------------------------------
@f.error
async def f(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed( 
            title = "Error",
            description = "Missing argument! Usage is " + prefix + "f <Movie Name>'",
            colour=discord.colour.Color.red()
            )
        argumentError(ctx,embed)
        await ctx.channel.send(embed=embed)
    else:
        embed = discord.Embed( 
            title = "Error",
            description = "No movie was found",         
            colour=discord.colour.Color.red()
            )
        argumentError(ctx,embed)
        await ctx.channel.send(embed=embed)
# -----------------------------------------------------------------------------------------------------------------------------------------------
def SearchLB(ctx, movie):
    import urllib.request
    movie = movie.replace(" ", "+")
    fp = urllib.request.urlopen("https://letterboxd.com/search/films/"+movie+"/")
    mybytes = fp.read()
    mystr = mybytes.decode("utf8")
    posters = re.findall(r'/film/.+?/',mystr)
    fp.close()
    if len(posters) == 0:
        return(False)
    
    else:
        FirstSearch = str(posters[0])
        FirstSearch = FirstSearch.replace("/film/", "")
        FirstSearch = FirstSearch[:-1]
        return(FirstSearch)
# -----------------------------------------------------------------------------------------------------------------------------------------------
def SearchLBCast(ctx, body):
    import urllib.request
    body = body.replace(" ", "+")
    fp = urllib.request.urlopen("https://letterboxd.com/search/cast-crew/"+body+"/")
    mybytes = fp.read()
    mystr = mybytes.decode("utf8")
    posters = re.findall(r'/actor/.+?/',mystr)
    fp.close()
    if len(posters) == 0:
        return(False)
    
    else:
        FirstSearch = str(posters[0])
        FirstSearch = FirstSearch.replace("/actor/", "")
        FirstSearch = FirstSearch[:-1]
        return(FirstSearch)
# -----------------------------------------------------------------------------------------------------------------------------------------------
@client.command()
async def diary(ctx,*, user):
    if user is None:
        result = collection.find_one({'_id': get_author_id(ctx)})['LetterboxName']
        if result is not None:
            user = result
        else:
            return   
    #======================================================================================= 
    isLBacc = True
    search = urllib.request.urlopen("https://letterboxd.com/"+user+"/films/diary/")
    mybytes = search.read()
    getUser = mybytes.decode("utf8")
    search.close()
    #======================================================================================= 
    
    #======================================================================================= 
    if isLBacc == True:
        watched1 = re.findall(r'data-film-name=".+?"',getUser)
        
       
        mylist = list(dict.fromkeys(watched1))
        print(mylist)
        Delete = ['&','#']
        mylist = [a for a in mylist if not 
          any(b in Delete for b in str(a))] 
        if len(mylist) >= 5:
            first = str(mylist[0]).replace("data-film-name=", "").replace('"', '')
            second = str(mylist[1]).replace("data-film-name=", "").replace('"', '')
            third = str(mylist[2]).replace("data-film-name=", "").replace('"', '')
            fourth = str(mylist[3]).replace("data-film-name=", "").replace('"', '')
            fifth = str(mylist[4]).replace("data-film-name=", "").replace('"', '')

            embed = discord.Embed(
                title="Diary for User: " + user,
                url = "https://letterboxd.com/"+user+"/films/diary/",
                description=first + "\n" + second + "\n" + third + "\n" + fourth + "\n" + fifth,
                colour=discord.colour.Color.green()
            )
            embedRight(lb_pfp(ctx, user), embed)
  
            await ctx.channel.send(embed=embed)
        elif len(mylist) == 4:
            first = str(mylist[0]).replace("data-film-name=", "").replace('"', '')
            second = str(mylist[1]).replace("data-film-name=", "").replace('"', '')
            third = str(mylist[2]).replace("data-film-name=", "").replace('"', '')
            fourth = str(mylist[3]).replace("data-film-name=", "").replace('"', '')
            embed = discord.Embed(
                title="Diary for User: " + user,
                url = "https://letterboxd.com/"+user+"/films/diary/",
                description=first + "\n" + second + "\n" + third + "\n" + fourth,
                colour=discord.colour.Color.green()
            )
            embedRight(lb_pfp(ctx, user), embed)
  
            await ctx.channel.send(embed=embed)
        
        elif len(mylist) == 3:
            first = str(mylist[0]).replace("data-film-name=", "").replace('"', '')
            second = str(mylist[1]).replace("data-film-name=", "").replace('"', '')
            third = str(mylist[2]).replace("data-film-name=", "").replace('"', '')
            embed = discord.Embed(
                title="Diary for User: " + user,
                url = "https://letterboxd.com/"+user+"/films/diary/",
                description=first + "\n" + second + "\n" + third,
                colour=discord.colour.Color.green()
            )
            embedRight(lb_pfp(ctx, user), embed)
  
            await ctx.channel.send(embed=embed)
        
        elif len(mylist) == 2:
            first = str(mylist[0]).replace("data-film-name=", "").replace('"', '')
            second = str(mylist[1]).replace("data-film-name=", "").replace('"', '')
            embed = discord.Embed(
                title="Diary for User: " + user,
                url = "https://letterboxd.com/"+user+"/films/diary/",
                description=first + "\n" + second,
                colour=discord.colour.Color.green()
            )
            embedRight(lb_pfp(ctx, user), embed)
  
            await ctx.channel.send(embed=embed)

        elif len(mylist) == 1:
            first = str(mylist[0]).replace("data-film-name=", "").replace('"', '')
            embed = discord.Embed(
                title="Diary for User: " + User,
                url = "https://letterboxd.com/"+user+"/films/diary/",
                description=first,
                colour=discord.colour.Color.green()
            )
            embedRight(lb_pfp(ctx, user), embed)
  
            await ctx.channel.send(embed=embed)

        else:
            embed = discord.Embed(
                title="Diary empty",
                description= "There appears to be nothing in this user's diary",
                colour=discord.colour.Color.dark_blue()
            )
            embedRight(lb_pfp(ctx, user), embed)
  
            await ctx.channel.send(embed=embed)
# -----------------------------------------------------------------------------------------------------------------------------------------------   
client.run('NzQ1MjQ1NzAwMDY5MjYxMzcz.Xzu-JA.VWYhVJ98Lzbjnu6QvfrhyYkp-uQ')
# -----------------------------------------------------------------------------------------------------------------------------------------------
