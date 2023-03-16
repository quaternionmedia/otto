"""Otto.main

The primary app.

This initializes the main FastAPI `app` and attaches all routes to it.
"""
from fastapi import FastAPI
from otto.preview import previewAPI
from otto import templates
from otto import __version__

app = FastAPI()
"""# The main app"""
app.include_router(previewAPI, prefix='/preview', tags=['preview'])


@app.get('/')
def version() -> dict:
    """# Version

    Return version information
    Args:

    Returns: JSON with version number
        otto (str): version number

            {
                'otto': 'SEMANTIC.VERSION.NUMBER'
            }
    """
    return {'otto': __version__}


@app.get('/templates')
async def getTemplates() -> list:
    """# Get templates
    Returns a list of template names currently loaded and available."""
    return [t for t in dir(templates) if t.islower() and t[0] != '_']


if __name__ == '__main__':
    from uvicorn import run

    run(app, host='0.0.0.0', port=9000)
