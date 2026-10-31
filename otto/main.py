"""Otto.main

The primary app.

This initializes the main FastAPI `app` and attaches all routes to it.
"""

from fastapi import FastAPI

from otto import __version__, templates
from otto.preview import previewAPI

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
    Returns the names of the templates an Edl may use: `templates.TEMPLATES`.

    This listed the lowercase names in the module's namespace, which offered
    imports (concatenate_videoclips, ct, defaults) as templates and left out
    the two current ones, textBox and makeColor, for having capitals."""
    return list(templates.TEMPLATES)


if __name__ == '__main__':
    from uvicorn import run

    run(app, host='0.0.0.0', port=9000)
