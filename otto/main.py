from fastapi import FastAPI
from otto.preview import previewAPI
from otto import templates
from otto import __version__

app = FastAPI()

app.include_router(previewAPI, prefix='/preview', tags=['preview'])


@app.get('/')
def hello() -> dict:
    return {'otto': __version__}


@app.get('/templates')
async def getTemplates() -> list:
    """# Get templates
    Returns a list of template names currently loaded and available."""
    return [t for t in dir(templates) if t.islower() and t[0] != '_']


if __name__ == '__main__':
    from uvicorn import run

    run(app, host='0.0.0.0', port=9000)
