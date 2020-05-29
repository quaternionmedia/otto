from typing import List
from fastapi import FastAPI
from pydantic import BaseModel, AnyUrl
from fastapi.responses import HTMLResponse
import render
import os

class Video_Request(BaseModel):
    name: str
    logo: AnyUrl
    address: str
    phone: str
    hours: str
    website: str #AnyUrl
    initial: str
    bullets: str
    optional: str
    videos: str #List[AnyUrl] = []
    audios: str #List[AnyUrl] = []
    media: str #List[AnyUrl] = []
    call: str
    closing: str
    fontcolor: str
    themecolor: str
    font: str

app = FastAPI()

@app.post('/render')
async def process():#vid_request: Video_Request):
    # v = render.Otto(Video_Request.json())
    v = render.Otto()
    # file = await v.render()
    v.render()
    return {'status': True }
    # return StreamingResponse(fake_video_streamer())


@app.get("/")
async def main():
    content = """
<body>
<form action="/render" enctype="multipart/form-data" method="post">
Name: <input name="name" type="text"><br>
Logo: <input name="logo" type="text"><br>
Address: <input name="address" type="text"><br>
Phone: <input name="phone" type="text"><br>
Hours: <input name="hours" type="text"><br>
Website: <input name="website" type="text"><br>
Initial: <input name="initial" type="text"><br>
Bullets: <input name="bullets" type="text"><br>
Optional: <input name="optional" type="text"><br>
Video: <input name="videos" type="text"><br>
Audio: <input name="audios" type="text"><br>
Media: <input name="media" type="text"><br>
Call: <input name="call" type="text"><br>
Closing: <input name="closing" type="text"><br>
Font Color: <input name="fontcolor" type="text"><br>
Theme Color: <input name="themecolor" type="text"><br>
Font: <input name="font" type="text"><br>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)

# app.mount("/", StaticFiles(directory='dist', html=True), name="static")

if __name__ == '__main__':
    run(app, host='0.0.0.0', port=8000)
