from typing import List
from fastapi import FastAPI, Request
from pydantic import BaseModel, AnyUrl
from fastapi.responses import HTMLResponse
import render
import os, json

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
async def process(request: Request):#vid_request: Video_Request):
    form = json.loads(json.dumps((await request.form()), default=lambda o: o.__dict__, indent=4))['_dict']
    print(form)
    v = render.Otto(data=form)
    # v = render.Otto()
    # file = await v.render()
    v.render()
    return {'status': True }
    # return StreamingResponse(fake_video_streamer())


@app.get("/")
async def main():
    content = """
<body>
<form action="/render" enctype="multipart/form-data" method="post">
Name: <input name="NAME" type="text"><br>
Logo: <input name="LOGO" type="text"><br>
Address: <input name="ADDRESS" type="text"><br>
Phone: <input name="PHONE" type="text"><br>
Hours: <input name="HOURS" type="text"><br>
Website: <input name="WEBSITE" type="text"><br>
Initial: <input name="INITIAL" type="text"><br>
Bullets: <input name="BULLETS" type="text"><br>
Optional: <input name="OPTIONAL" type="text"><br>
Video: <input name="VIDEOS" type="text"><br>
Audio: <input name="AUDIOS" type="text"><br>
Media: <input name="MEDIA" type="text"><br>
Call: <input name="CALL" type="text"><br>
Closing: <input name="CLOSING" type="text"><br>
Font Color: <input name="FONTCOLOR" type="text"><br>
Theme Color: <input name="THEMECOLOR" type="text"><br>
Font: <input name="FONT" type="text"><br>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)

# app.mount("/", StaticFiles(directory='dist', html=True), name="static")

if __name__ == '__main__':
    run(app, host='0.0.0.0', port=8000)
