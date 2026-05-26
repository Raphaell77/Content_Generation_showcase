import googleapiclient.discovery
import json
import datetime
import time
import yt_dlp
from api.config import API_KEY, API_KEY_2
from customer_config import MAX_RESULTS


PATH_YOUTUBE_DATA = 'analysis/responses/data.json'

# api request
api_service_name = "youtube"
api_version = "v3"

youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey=API_KEY, cache_discovery=False)   # cache discovery=False ist oft stabiler


# searches yt videos to extract titels for keyword extensions: gerade verwende ich stattdessen send_http_request()
# def youtube_client() -> dict:
#     yt_video_titles = {}
#     kw = niche.get_seed_keywords()

#     for seed in kw:
#         yt_video_titles[seed] = list()


#     MAX_RESULTS = 3 # fuer nlp unbedingt deutlich hoeher stellen
#     for keyword in yt_video_titles.keys():
#         request = youtube.search().list(
#             part="snippet",
#             type="video",
#             maxResults=MAX_RESULTS,
#             q=niche.name + " " + keyword,
#             relevanceLanguage='en'
#         )
#         response = request.execute()

#         # da maxResults bugged? ich
#         if len(response["items"]) < MAX_RESULTS:
#             MAX_RESULTS = len(response["items"])

#         for i in range(MAX_RESULTS):    
#             video_title = response["items"][i]["snippet"]["title"]
#             yt_video_titles[keyword].append(video_title)

#     cleaned_titles = niche.clean_input(yt_video_titles)
            
#     return cleaned_titles



def get_video_id(merged_expandings, niche_name, max_results=MAX_RESULTS):
    # Optionen für yt-dlp konfigurieren
    ydl_opts = {
        'quiet': True,           
        'extract_flat': True,   
        'no_warnings': True
    }
    
    final_result = {}
    current_time = datetime.datetime.now().isoformat()

    # PERFORMANCE FIX: Die yt-dlp Instanz nur einmal ganz außen starten!
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for keyword, expandings in merged_expandings.items():
            query_base = f"{niche_name} {keyword}"

            final_result[keyword] = {
                "retrieved_at": current_time,
                "videos": []
            }

            for exp in expandings:
                search_string = f"ytsearch{max_results}:{query_base} {exp}"
                print(f"Searching for: {keyword} {exp}")

                try:
                    yt_result = ydl.extract_info(search_string, download=False)

                    if yt_result and 'entries' in yt_result:
                        for video in yt_result['entries']:
                            video_id = video.get('id')
                            if not video_id:
                                continue

                            video_entry = {
                                'video_id': video_id,
                                'snippet': {
                                    'title': video.get('title', ""),
                                    'description': video.get('description', "")
                                },
                                'content_details': {},
                                'statistics': {},
                                'channel': {
                                    'channel_id': video.get('channel_id', ""),
                                    'channel_title': video.get('channel', ""),
                                    # 'subscriber_count': video.get('channel_follower_count', 0), # testen ob das hier was bringt, ansonsten: get_channel_info() nutzen
                                }
                            }
                            final_result[keyword]["videos"].append(video_entry)
                            
                except Exception as e:
                    print(f"Error occured at '{search_string}': {e}")
                    
    return final_result




# searches yt videos *with* found keyword extensions from send_http_request()
def search_yt_videos(merged_expandings: dict[str, list[str]], niche_name: str, max_results=10) -> dict:
    result = {}
    
    current_time = datetime.datetime.now().isoformat() 

    for keyword, expandings in merged_expandings.items():
        query_base = f"{niche_name} {keyword} "
        
        result[keyword] = {
            "retrieved_at": current_time,
            "videos": []  # leere liste, wird dynamisch befuellt
        }
        
        for exp in expandings:
            request = youtube.search().list(
                part="snippet",
                type="video",
                maxResults=max_results,
                q=query_base + exp,
                relevanceLanguage='en'
            )
            response = request.execute()

            time.sleep(0.5)
            
            items = response.get("items", []) 
            
            # ueberspringen falls keine video id
            for elem in items:
                video_id = elem.get("id", {}).get("videoId")
                if not video_id:
                    continue
                
                snippet = elem.get("snippet", {})
                
                video_entry = {
                    "video_id": video_id,
                    "snippet": {
                        "title": snippet.get("title", ""),
                        # "description": snippet.get("description", ""), # lieber aus videos.list() holen, da dort vollständig
                        "published_at": snippet.get("publishedAt", "")
                    },
                    "content_details": {},
                    "statistics": {},
                    "channel": {
                        "channel_id": snippet.get("channelId", ""),
                        "channel_title": snippet.get("channelTitle", ""),
                        "subscriber_count": 0
                    }
                }
                result[keyword]["videos"].append(video_entry)
            
    return result


# get subscriber count
def get_video_info(data: dict) -> dict:
    for keyword, value in data.items():
        videos = value.get("videos", [])
        if not videos: continue
        
        video_ids = [v.get("video_id") for v in videos if v.get("video_id")]
        
        # batching: max 50 ids pro request
        for i in range(0, len(video_ids), 50):
            chunk = video_ids[i:i+50]   # von i bis ende, in i+50er schritten
            id_string = ",".join(chunk) # ["ID_1", "ID_2", "ID_3"] -> "ID_1,ID_2,ID_3"
            
            request = youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=id_string
            )
            response = request.execute()
            items = response.get("items", [])
            
            for item in items:
                v_id = item.get("id")
                
                for video in videos:
                    if video.get("video_id") == v_id:
                        snippet = item.get("snippet", {})
                        video["snippet"]["description"] = snippet.get("description", "")
                        
                        content_details = item.get("contentDetails", {})
                        statistics = item.get("statistics", {})
                        
                        video["content_details"] = {
                            "duration": content_details.get("duration", "PT0S")
                        }
                        video["statistics"] = {
                            "view_count": int(statistics.get("viewCount", 0)),
                            "like_count": int(statistics.get("likeCount", 0)),
                            "comment_count": int(statistics.get("commentCount", 0))
                        }
                        break # Video gefunden und geupdatet, abbrechen
                        
    return data



def get_channel_info(data: dict) -> dict:
    for keyword, value in data.items():
        videos = value.get("videos", [])
        if not videos: continue
        
        # Alle Channel-IDs extrahieren und Duplikate per set() entfernen
        channel_ids = list({v.get("channel").get("channel_id") for v in videos if v.get("channel", {}).get("channel_id")})
        
        for i in range(0, len(channel_ids), 50):
            chunk = channel_ids[i:i+50]
            id_string = ",".join(chunk)
            
            request = youtube.channels().list(
                part="statistics",
                id=id_string
            )
            response = request.execute()
            items = response.get("items", [])
            
            # Abonnentenanzahl zurück auf die Videos mappen
            for item in items:
                c_id = item.get("id")
                sub_count = int(item.get("statistics", {}).get("subscriberCount", 0))
                
                for video in videos:
                    if video.get("channel", {}).get("channel_id") == c_id:
                        video["channel"]["subscriber_count"] = sub_count
                        
    return data

