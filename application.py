from flask import Flask, render_template, request 
from flask_cors import CORS, cross_origin
import requests as req
import re
import logging

from datetime import datetime as dt
from datetime import timedelta as td

logging.basicConfig(filename="scrapper.log" , level=logging.INFO)

application = Flask(__name__)
app = application

@app.route("/", methods = ['GET'])
@cross_origin()
def homepage():
    return render_template("index.html")

@app.route("/ytVids" , methods = ['POST' , 'GET'])
@cross_origin()
def index():
    if request.method == 'POST':
        try:           
            youtube_url = 'https://www.youtube.com'
            
            header={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}

            today = dt.now()
            result = { 'hou': lambda x: today - td(hours=x), 
                       'day': lambda x: today - td(days=x), 
                       'wee': lambda x: today - td(weeks=x),
                       'mon': lambda x: today - td(days=x*30),
                       'yea' :lambda x: today - td(days=x*365),
                    }
                    
            channel_name = request.form['content'].replace(" ","")
            vid_count = int(request.form['v_count'])

            video_channel_url = f"{youtube_url}/@{channel_name}/videos"
            response = req.get(video_channel_url, headers=header, cookies={'CONSENT':'YES+1'})
           
            if response.ok:
                data = response.text

                videourls = re.findall('"videoRenderer":{"videoId":".*?"', data)
                thumbs = re.findall('"thumbnail":{"thumbnails":\[{"url":".*?"', data)
                titles = re.findall('"title":{"runs":\[{"text":".*?"', data)
                published = re.findall('"publishedTimeText":{"simpleText":".*?"', data)
                views = re.findall('"shortViewCountText":{"accessibility":{"accessibilityData":{"label":".*?"', data)
             
                filename = channel_name + ".csv"
                fw = open(filename, "w", encoding="utf-8")
                cols = "No, Video URL, Thumbnail, Video Title, Views, Publish Date \n"
                fw.write(cols)
                
                videos_list = list()
                for n in range(vid_count):
                    videoId = youtube_url+'/watch?v='+ videourls[n].split(":")[-1].replace('"','')
                    thumb = thumbs[n].split('"')[-2].split('?')[0]
                    title = titles[n].split('"')[-2]
                    view = views[n].split('"')[-2]

                    when = published[n].split('"')[-2]
                    num, val, ago = when.split()
                    publish = result[val[:3]](int(num))

                    publish = publish.strftime("%d %b %Y")
                    fw.write(f"{(n+1)}, {videoId}, {thumb}, {title}, {view}, {publish} \n")
                    detail = {"No": (n+1), "Video URL": videoId, "Thumbnail": thumb, "Video Title": title, 
                              "Views": view, "Publish Date": publish}

                    videos_list.append(detail)

                logging.info("Final Search Result: {}".format(videos_list))
                
                if not fw.closed:
                    fw.close() 
                
                return render_template('result.html', videos=videos_list, channel=channel_name)
            else:
                return "Please check the channel name. Something is wrong."
        except Exception as e:
            logging.info(e)            
            return 'Exception: Something is wrong.' 
    else:
        return render_template('index.html')


if __name__=="__main__":
    app.run(host="0.0.0.0", port=8000)
