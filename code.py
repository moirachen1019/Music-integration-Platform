#!/usr/bin/env python
# coding: utf-8

# In[14]:


#####import 必要套件#####
import json
import spotipy
import re
import requests
from spotipy.oauth2 import SpotifyClientCredentials
import urllib.request, urllib.parse, urllib.error
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from easydl import clear_output #清除顯示畫面的function
clear_output()
#####spotify取得歌曲資訊#####
spotify_client_id="a384ae34d0e6468c999d95dc8b86ab5a"
spotify_client_secret="a5930c88d0be4764aa92458408b14edd"
#從Spotify for Developer Dashboard取得帳號密碼
sp=spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=spotify_client_id,client_secret=spotify_client_secret))
#use Client ID and Client Secret to request an access token from Spotify
stop=0 #結束整個迴圈
find_inf=0 #要不要重新讓使用者選擇歌手
while stop==0:
    print("if there is a chinese song with english or all number name, please enter (c) following the song")
    #若是中文歌但為英文或數字歌名，請使用者標註
    if find_inf==0:
        song=input("Please enter a song name: ")
    elif find_inf==1:
        song=input("Please enter a song name:(or enter \"b\" to go back): ")
    if song=="b":
        pass #直接跳回選擇下一步的部分
    else:
        chinese_song_flag=0 #檢查是否為中文歌，有時候spotify歌手會是英文名，先改為中文給使用者看
        if "(c)" in song: #使用者自行標註為中文歌
            song=song.replace("(c)","")
            chinese_song_flag=1
        for char in song:
            if char >= u'\u4e00' and char <= u'\u9fff': #只要有一個中文字就判定為中文歌
                chinese_song_flag=1
                break
        repeat=0 #候選歌手重複次數
        artists=[0,1,2] #存候選artists的陣列，預設三個候選者不一樣
        try:
            track=sp.search(q=song,limit=3) #搜尋歌曲，找前三筆符合結果
#             print(track)
        except:
            continue
        check=track["tracks"]["items"]
        if check==[]:
            print("We can't find the song! Please enter again!")
            continue
        try:
            for i in range(0,3):
                maybe_artist=track["tracks"]["items"][i]["album"]["artists"][0]["name"]
#                 print(maybe_artist)
                for char in maybe_artist:
                    if char >= u'\u4e00' and char <= u'\u9fff':
                        chinese_song_flag=0 #雖然是中文歌但歌手名已是中文不用轉換
                        break
                artist_id=track["tracks"]["items"][i]["album"]["artists"][0]["id"]
                if chinese_song_flag==1 and (maybe_artist != "Mayday"): #如果是中文歌
                    artist_=maybe_artist.replace(" ","+")#轉換形式
                    if "&" in artist_:
                        artist_=artist_.replace("&","%26")
                    url="https://www.google.com/search?q="+artist_+"+%E7%B6%AD%E5%9F%BA%E7%99%BE%E7%A7%91&oq="+artist_+"+%E7%B6%AD%E5%9F%BA%E7%99%BE%E7%A7%91&aqs=chrome..69i57j69i61.2413j0j15&sourceid=chrome&ie=UTF-8"
#                     print(url)
                    #丟到google搜尋該歌手的維基百科中文版，會出現中文歌手名(%E7%B6%AD%E5%9F%BA%E7%99%BE%E7%A7%91是維基百科的編碼)
                    html=requests.get(url)#讀網頁原始碼
                    soup=BeautifulSoup(html.text, "html.parser")#以beautifulsoup解析html程式碼，指定html.parser為解析器
                    search=soup.find("h3",class_="zBAuLc") #找到該網頁第一個搜尋結果的標題
                    search=search.string #轉成字串
                    artists[i]=search[ :search.find("-")] #第一個搜尋結果的標題即為歌手名
                    if "[" in artists[i]: #有時候會多一個[]，把它排除
                        artists[i]=search[ :search.find("[")]
                elif maybe_artist == "Mayday":
                    artists[i]="五月天" #mayday丟到google搜尋的第一個結果會是求救訊號，把這特例拉出來
                else:
                    artists[i]=maybe_artist

                if find_inf==0: #若已知歌手就不用進行此步
                    special_index=0
                    if artists[1]==artists[0]: #[0]和[1]具相同歌手名
                        artists[1]="no"#清空因為沒用了
                        repeat+=1#重複次數增加
                        continue #不用印[1]
                        
                    if artists[2]==artists[1] or artists[2]==artists[0]: #[2]和[1]或[0]具相同歌手名
                        repeat+=1#重複次數增加
                        continue #不用印
                    elif artists[1]=="no": #即[0],[1]相同，[2]和他們不相同
                        special_index=1
                        print(i,artists[i]) #中間少一個候選人，故印的足標要-1
                        continue
                        
                    print((i+1),artists[i]) #都沒經過上面的if，單純印出結果就好

        except: #搜尋結果不到三個歌手，印出現有的就好
            pass
        choose_another=0
        while repeat<2: #重複兩次內，代表至少有兩個歌手給使用者選
            if find_inf==0:
                choice=input("Please choose the singer:\n(If there is no singer you want, enter \"b\" to choose another song): ")
                if choice=="b":
                    choose_another=1
                    break
                if special_index==1 and int(choice)==2: #特殊索引
                    i=int(choice)
                else:
                    i=int(choice)-1
            elif find_inf==1: #不用讓使用者選，自己找到對應搜尋結果的位置，(artist為前次操作已確定之歌手)
                for i in range(0,2):
                    if artists[i]==artist:
                        break
            try:
                artist=artists[i]
                artist_id=track["tracks"]["items"][i]["album"]["artists"][0]["id"]
                album=track["tracks"]["items"][i]["album"]["name"]
                album_id=track["tracks"]["items"][i]["album"]["id"]
                song=track["tracks"]["items"][i]["name"]
                if "-" in song: #有時候歌名後接-，會寫該歌是主題曲等資訊，把它去掉留下歌名
                    song=song[ :song.find("-") ]
                if "(" in song: #有時候歌名後接(，會附註feat.誰的資訊，把它去掉留下歌名
                    song=song[ :song.find("(") ]
                break
            except: #使用者輸入選擇以外的內容
                print("Please choose again!") #再次進入迴圈
        if choose_another==1:
            continue
        if repeat==2: #只有一個可能結果，直接顯示
            print("There is only one singer, so you don't need to choose!")
            i=0
            artist=artists[i]
            artist_url=track["tracks"]["items"][i]["album"]["artists"][0]["external_urls"]["spotify"]
            album=track["tracks"]["items"][i]["album"]["name"]
            album_url=track["tracks"]["items"][i]["album"]["external_urls"]["spotify"]
            song=track["tracks"]["items"][i]["name"]
            song=track["tracks"]["items"][i]["name"]
            if "-" in song:
                song=song[ :song.find("-") ]

#####youtube取得搜尋結果第一部影片的網址#####
        api_key="AIzaSyAWSQBSuyhTfyrT8X735WjQZ9xOzH31Vn0"
        youtube=build('youtube', 'v3', developerKey=api_key) #use the build() function to create a service object
        result=youtube.search().list( #search.list:列出搜尋結果
            part="snippet", #part來定義要取得的資料範圍,此情況下設為snippet
            maxResults=1, #最多顯示的比數
            q=song+artist, #keyword
            order="relevance" #以關聯性為排序結果
        )
        video_flag=0
        try:
            video_id=result.execute()["items"][0]["id"]["videoId"] #result經過.execute()後才是json code #印出第一個結果
        except:
            print("Sorry, we can't find the video.")
            video_flag=1

#####魔鏡歌詞網取得歌詞#####
        song_=song.replace(" ","+")#把song中間的空白轉成+(為了符合形式)
        song_=urllib.parse.quote(song_) #把中文轉成電腦可以讀的編碼
        song_=str(song_) #轉回字串型態
        artist_=artist.replace(" ","+")#把artist中間的空白轉成+(為了符合形式)
        artist_=urllib.parse.quote(artist_)
        artist_=str(artist_)
        url="https://www.google.com/search?q="+song_+"+"+artist_+"+%E9%AD%94%E9%8F%A1%E6%AD%8C%E8%A9%9E%E7%B6%B2&oq="+song_+"+"+artist_+"+%E9%AD%94%E9%8F%A1%E6%AD%8C%E8%A9%9E%E7%B6%B2&aqs=chrome..69i57j69i61.2413j0j15&sourceid=chrome&ie=UTF-8"
        #丟到google搜尋該歌曲的魔鏡歌詞網網頁，進入第一個搜尋結果網址
#         print(url)
        html=requests.get(url)#讀網頁原始碼
        soup=BeautifulSoup(html.text, "html.parser")#以beautifulsoup解析html程式碼，指定html.parser為解析器
        results=soup.find_all("div",class_="kCrYT") #抓取搜尋結果
        for result in results:
            try:
                result=result.a.get("href")
                lyrics_url=result[result.find("=")+1 : ] #得到搜尋結果的網站
                html=urllib.request.urlopen(lyrics_url).read() #讀網頁原始碼
                soup=BeautifulSoup(html, "html.parser")
                target=soup.find("dd",class_='fsZx3') #找到歌詞所在之標籤
                if target==None:
                    continue
                target=str(target)#轉成str
                target=target.replace('<br/>',"\n")#把<br/>都換成真正換行
                target=target.replace("更多更詳盡歌詞 在 <a href=\"http://mojim.com\">※ Mojim.com　魔鏡歌詞網 </a>","")#去掉廣告
                target=target[ target.find(">")+2 : target.find("</dd>") ]
                if "[00" in  target: #有時候會多一個歌詞和時間的對照表[00:00:00]開頭，把它排除
                    target=target[ : target.find("[00")]
                elif "<ol>" in  target: #有時候會有其他資訊，把它排除
                    target=target[ : target.find("<ol>")]
                break
            except: #沒找到符合格式的，代表不是魔鏡歌詞網的網站，繼續往下找
                pass

#####印出所有結果#####
        if video_flag==0:
            print("\033[0;34m"+"\nYoutube Video: https://www.youtube.com/watch?v="+video_id) #印出影片網址
        
        print("Name: "+"\033[0m",end="")
        print("\033[1;34m"+song+"\033[0m")
        
        print("\033[0;34m"+"Album: "+"\033[0m",end="")
        print("\033[1;34m"+album+"\033[0m")
        
        print("\033[0;34m"+"Artist: "+"\033[0m",end="")
        print("\033[1;34m"+artist+"\033[0m")
        try:
            print("\033[0;35m"+"Lyrics:\n"+target+"\033[0m" )#取出歌詞部分
        except:
            print("\033[0;35m"+"Sorry, we can't find the lyrics."+"\033[0m")
    print("\"q\" to stop;\n\"c\" to clear the result;\n\"artist\" to find the artist's other songs;\n\"album\" to find other songs in that album;\n\"r\" to restart.")
    #提供使用者進行下一步的選擇
    while True:
        next_step=input("Please enter: ")
        if next_step=="c": #清除完後再印出簡短資訊讓使用者選擇下一步
            clear_output()
            print("\033[0;34m"+"Album: "+"\033[0m",end="")
            print("\033[1;34m"+album+"\033[0m")
            print("\033[0;34m"+"Artist: "+"\033[0m",end="")
            print("\033[1;34m"+artist+"\033[0m")
            print("\"q\" to stop;\n\"artist\" to find the artist's other songs;\n\"album\" to find other songs in that album;\n\"r\" to restart.")
            next_step=input("Please enter: ")
        if next_step=="q": #結束程式
            stop=1
            break
        elif next_step=="artist": #從歌手找歌曲
            find_inf=1 #不用重新讓使用者選擇歌手
            artist_to_song=sp.artist_top_tracks(artist_id)
            print("Please choose another famous song from \""+"\033[0;34m"+artist+"\033[0m"+"\": ")
            for i in range(0,10):
                try:
                    print("\033[0;34m"+artist_to_song["tracks"][i]["name"]+"\033[0m")
                except:
                    pass
            break
        elif next_step=="album": #從專輯找歌曲
            find_inf=1
            print("Please choose another song from \""+"\033[0;34m"+album+"\033[0m"+"\": ")
            album_to_song=sp.album_tracks(album_id,limit=10)
            for i in range(0,10):
                try:
                    print("\033[0;34m"+album_to_song["items"][i]["name"]+"\033[0m")
                except:
                    pass
            break
        elif next_step=="r": #重新選歌
            find_inf=0
            break
        else:
            print("Please enter again!")


# In[ ]:





# In[ ]:





# In[ ]:




