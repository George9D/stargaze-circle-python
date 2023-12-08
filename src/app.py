import base64
from pathlib import Path
from dash import Dash, dcc, html, ctx, DiskcacheManager, CeleryManager
from dash.dependencies import Input, Output, State
import diskcache
import dash_bootstrap_components as dbc
from PIL import Image
from io import BytesIO
import requests
import os

import functions as f

if 'REDIS_URL' in os.environ:
    # Use Redis & Celery if REDIS_URL set as an env variable
    from celery import Celery
    celery_app = Celery(__name__, broker=os.environ['REDIS_URL'], backend=os.environ['REDIS_URL'])
    background_callback_manager = CeleryManager(celery_app)

else:
    # Diskcache for non-production apps when developing locally
    import diskcache
    cache = diskcache.Cache("./cache")
    background_callback_manager = DiskcacheManager(cache)

app = Dash(__name__, prevent_initial_callbacks=True, background_callback_manager=background_callback_manager)
server = app.server

app.config.suppress_callback_exceptions = True
app.title = "Stargaze Circles"


filepath = "image.jpg"

colorpicker = html.Div(
    [
        dbc.Input(
            type="color",
            id="colorpicker",
            value="#FFFFFF",
            style={"height": 50, 'background-color': 'transparent', 'display': 'inline-block'}
        ),
    #], style={'display': 'inline-block', 'margin-right': '5px', 'width': '250px'}
    ], style={'display': 'inline-block', 'margin-right': '5px'}
)


app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Row([
                html.Div([
                    dbc.Row([
                        dbc.Input(id="sg-wallet",
                                  debounce=True,
                                  placeholder=f"Enter your Stargaze address or name here",
                                  autofocus=True,
                                  autocomplete='off',
                                  # required=True,
                                  # className="input",
                                  style={'color': 'white', 'background-color': 'black',
                                         'border': 'solid rgba(158,202,225,0.3) 1px !important',
                                         'box-shadow': '0.1rem 0.01rem 0.3rem rgb(92,92,100),'
                                                       '-0.1rem -0.01rem 0.3rem rgb(92,92,100)'},
                                  ),
                    ], style={'margin-bottom': 10}),
                    dbc.Row([
                        dbc.Button(
                            children=["Generate Stargaze Circle"],
                            id="generate-circle-btn",
                            className="m-1",
                            color="primary",
                            n_clicks=0,
                        ),
                    ], justify="center")
                ], style={'width': '450px'})
            ], justify="center", style={'margin-top': '100px'}),
            dbc.Row([
                html.Div([
                    dbc.Collapse(
                        children=[
                            dbc.Card([
                                dbc.CardImg(src="assets/stars-fx-a.jpg", top=True, id='image-display', bottom=True, style={'height': '500px'}),
                            ],
                                style={'margin-bottom': '20px', 'backgroundColor': "black"}
                            ),
                            dbc.Row([
                                html.Div([
                                    dbc.Row([
                                        colorpicker
                                    ], justify="center")
                                ], style={'width': '200px'}),
                                html.Div([
                                    dbc.Row([
                                        dbc.Button(
                                            children=["Download"],
                                            id="download-btn",
                                            download="stargaze_circle.png",
                                            className="m-1",
                                            color="primary",
                                            n_clicks=0,
                                        ),
                                    ], justify="center")
                                ], style={'width': '200px'})
                            ], justify="around", style={'margin-top': '15px'}),

                        ],
                        id="collapse",
                        is_open=False,
                    ),
                ],
                    style={
                        'margin-top': 20,
                        'margin-bottom': 20,
                        'width': '510px'
                    }
                ),
            ], justify="center", style={'margin-top': '10px'}),
        ], align="center"),

    ], justify="center", style={'position': 'absolute', "height": "90vh", 'width': '100%'}),

    dbc.Row([
                html.Footer([
                    dbc.Col([
                        html.P(children=['Built by the community for the community.'],
                               className="text-secondary"
                               ),
                    ], width=4, className="text-start"),
                    dbc.Col([
                        html.P(
                            html.A(
                                href="https://www.stargaze.zone/",
                                children=[
                                    html.Img(
                                        alt="Link to stargaze.zone",
                                        src="assets/stargaze_star_gradient.svg",
                                        height="40px"
                                    )
                                ],
                                target="_blank"
                            )
                        )
                    ], width=4),
                    dbc.Col([
                        html.P(children=['Created by ',
                                         html.A(
                                             href="https://twitter.com/George9D",
                                             children=[
                                                 "George9D"
                                             ],
                                             target="_blank",
                                             className="text-secondary text-decoration-underline"
                                         ),
                                         ], className="text-secondary"
                               ),
                    ], width=4, className="text-end", id="footer")
                ],
                    className="text-inverse text-center pt-2 hstack",
                    style={'position': 'fixed', 'bottom': 0, 'background-color': 'black'},
                ),
            ], align="bottom", justify="around"),

    dcc.Store(id='image-store', data=''),
    dcc.Store(id='layer-config-store', data=''),
    dcc.Store(id='bg-color-store', data=''),

    dcc.Download(id="download-image")

], fluid=True, style={"height": "100vh",
                      'position': 'absolute',
                      'background-image': 'url(assets/stars1.jpeg)',
                      'background-repreat': 'no-repeat',
                      'background-position': 'right top',
                      })


"""@app.callback(
    Output('layer-config-store', 'data'),
    Input('header', 'children')
)
def get_layers(children):
    layers = main.get_layer_config()
    return layers"""


app.clientside_callback(
    """
    function(color) {
        return {"color": color}
    }
    """,
    Output("bg-color-store", "data"),
    Input("colorpicker", "value"),
)



@app.callback(
    output=[
    Output('image-store', 'data'),
    #Output('layer-config-store', 'data'),
    Output("collapse", "is_open")
    ],
    inputs=[
    Input('generate-circle-btn', 'n_clicks'),
    #Input('change-bg-btn', 'n_clicks'),
    ],
    state=[
    State('bg-color-store', 'data'),
    State('image-store', 'data'),
    #State('layer-config-store', 'data'),
    State('sg-wallet', 'value')],
    background=True,
    running=[
        (Output("generate-circle-btn", "disabled"), True, False),
        #(Output("change-bg-btn", "disabled"), True, False),
        (Output("download-btn", "disabled"), True, False),
        (Output("generate-circle-btn", "children"), [dbc.Spinner(size="sm"), " Generating..."], ["Generate Stargaze Circles"]),
    ],
)
def update_image(n_clicks, bg_color_data, current_image_data, wallet):

    if ctx.triggered_id == "generate-circle-btn":
        layers = f.get_layer_config(wallet)
        image_data = f.create_image(layers, None)
    elif ctx.triggered_id == "change-bg-btn":
        layers = f.get_layer_config(wallet)

        if bg_color_data:
            bg_color = bg_color_data['color']
        else:
            bg_color = 'rgba(255, 255, 255, 1)'

        image_data = f.create_image(layers, bg_color)
    else:
        current_image_bytes = base64.b64decode(current_image_data.split(',')[1])
        current_img = Image.open(BytesIO(current_image_bytes)).convert('RGBA')

        # Create a new image with the selected background color
        new_img = Image.new(mode='RGBA', size=current_img.size, color=bg_color_data['color'])

        # Composite the original image onto the new image
        result_img = Image.alpha_composite(new_img, current_img)

        # Save the resulting image to a BytesIO object
        image_data = BytesIO()
        result_img.save(image_data, format='PNG')

        # Save the resulting image to a file
        result_img.save(filepath, "PNG")

    # Convert the BytesIO image data to base64 for storage in the dcc.Store
    encoded_image = f"data:image/png;base64,{base64.b64encode(image_data.getvalue()).decode()}"



    return [encoded_image, True]


@app.callback(
    Output('image-display', 'src'),
    [Input('image-store', 'data')]
)
def display_image(encoded_image):
    print("display_image")
    if not encoded_image:
        print("None")
        return None

    return encoded_image


@app.callback(
    Output('download-btn', 'href'),
    Input('image-store', 'data')
)
def update_download_button(image_data):
    if not image_data:
        return ''

    # Convert the base64 image data to bytes
    image_bytes = base64.b64decode(image_data.split(',')[1])

    # Create a BytesIO object
    image_io = BytesIO(image_bytes)

    return f'data:application/octet-stream;base64,{base64.b64encode(image_io.getvalue()).decode()}'


"""@app.callback(
    Output("download-image", "data"),
    Input("download-btn", "n_clicks"),
    State('image-store', 'data'),
    prevent_initial_call=True,
)
def func(n_clicks, image_data):
    if n_clicks and image_data:
        # Convert the base64 image data to bytes
        image_bytes = base64.b64decode(image_data.split(',')[1])

        # Create a BytesIO object
        image_io = BytesIO(image_bytes)

        return {'base64': False, "content": f'data:application/octet-stream;base64,{base64.b64encode(image_io.getvalue()).decode()}', "filename": "sg_circles.png"}
"""

if __name__ == '__main__':
    app.run_server(debug=True)

"""
 dbc.Row([
                                html.Div([
                                    dbc.Row([
                                        dbc.Button(
                                            children=["Download"],
                                            id="download-btn",
                                            download="stargaze_circle.png",
                                            className="m-1",
                                            color="primary",
                                            n_clicks=0,
                                        ),
                                    ], justify="center")
                                ], style={'width': '450px'})
                            ], justify="center", style={'margin-top': '15px'}),
"""

"""
                            dbc.Row([
                                html.Div(
                                    [
                                        dbc.Input(
                                            type="color",
                                            id="colorpicker",
                                            value="#FFFFFF",
                                            style={"width": 180, "height": 50, 'background-color': 'transparent', 'display': 'inline-block'} ,#'border-color': '#db2c74'
                                        ),
                                    ], style={'display': 'inline-block', 'margin-right': '5px', 'width': '180px'}
                                ),
                                html.Div([
                                    dbc.Button(
                                        children=["Change BG Color"],
                                        id="bg-change-btn",
                                        href="src/circles.png",
                                        download="stargaze_circle.png",
                                        className="m-1",
                                        color="primary",
                                        n_clicks=0)
                                ], style={'width': '200px',
                                           'margin-left': '15px',
                                           'display': 'inline-block'}
                                )
                            ], justify="center"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button(
                                        children=["Download"],
                                        id="download-btn",
                                        href="src/circles.png",
                                        download="stargaze_circle.png",
                                        className="m-1",
                                        color="primary",
                                        n_clicks=0,
                                        style={'width': '200px'}
                                    )
                                ], align="center", xs=6, sm=6, md=6, lg=6, xl=6, xxl=6)
                            ])
"""

"""
import base64
from pathlib import Path

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_daq as daq

from PIL import Image
from io import BytesIO
import requests

import main

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1(id="header", children=["Image Background Color Changer"]),

    html.Label("Choose Background Color:"),
    daq.ColorPicker(
        id='color-picker',
        label='Color Picker',
        value=dict(hex='#119DFF')
    ),

    dcc.Store(id='image-store', data=''),
    dcc.Store(id='layer-config-store', data=''),

    html.Div([
        html.Img(id='image-display'),
    ], style={'margin-top': 20})
])


def create_image():
    image_data = main.main()
    return image_data

@app.callback(
    Output('image-store', 'data'),
    Input('color-picker', 'value'),
    State('image-store', 'data'),
    State('layer-config-store', 'data')
)
def update_image(background_color, current_image_data, layers):
    # Check if an image is already loaded
    if not current_image_data:
        #layers = main.get_layer_config()
        #image_data = main.create_image(layers, "rgba(255, 255, 255, 1)")
        image_data = create_image()
    else:
        current_image_bytes = base64.b64decode(current_image_data.split(',')[1])  # Decode base64
        # print(current_image_bytes)
        current_img = Image.open(BytesIO(current_image_bytes)).convert('RGBA')

        # Create a new image with the selected background color
        new_img = Image.new(mode='RGBA', size=current_img.size, color=background_color['hex'])
        #new_img.paste(current_img.convert('RGBA'), (0, 0), current_img.convert('RGBA'))

        # Set the alpha channel of the original image to 255 (fully opaque)
        current_img_with_alpha = current_img.copy()
        current_img_with_alpha.putalpha(255)

        # Paste the original image onto the new image with the desired background color
        new_img.paste(current_img_with_alpha, (0, 0), current_img_with_alpha)


        new_img.save("circles.png", "PNG")

        # Save the new image to a BytesIO object
        image_data = BytesIO()
        new_img.save(image_data, format='PNG')

    # Convert the BytesIO image data to base64 for storage in the dcc.Store
    encoded_image = f"data:image/png;base64,{base64.b64encode(image_data.getvalue()).decode()}"

    return encoded_image, layers
"""