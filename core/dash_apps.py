import dash
import dash_core_components as dcc
import dash_html_components as html
from .apps import *
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash
import environ
import datetime
import pandas
import functools

env = environ.Env()

panel = DjangoDash(name="panel",
                   )

panel.layout = html.Div([
    html.Link(
        rel='stylesheet',
        href=env('STATIC_URL') + 'bulma/css/style.min.css'
    ),
    dcc.Loading(
        type="circle",
        children=[
            html.Div(className='field', children="Luces:"),
            html.Div([
                html.Button('Light', id='light', className="button"),
                html.Div(id='light-cmd', children=''),
            ], className="row"),

            html.Div(className='container', children="Persiana:"),
            html.Div(id="persiana-panel",
                     className='field is-grouped',
                     children=[
                         html.Button('Down', id='persiana-down', className="button"),
                         html.Button('Stop', id='persiana-stop', className="button"),
                         html.Button('Up', id='persiana-up', className="button"),
                         html.Div(id='persiana-cmd', children=''),
                     ]),

            html.Div(className='row', children="HVAC"),
            html.Div(id='hvac-panel', className="field is-grouped",
                     children=[
                         html.Button('Aire Off', id='aire-off', className='button'),
                         html.Button('Aire On', id='aire-on', className='button'),
                         html.Div(id='aire-status', className='off')
                     ])
        ],
    ),
], className="container bg-light")


@panel.expanded_callback(
    dash.dependencies.Output('aire-status', 'className'),
    [dash.dependencies.Input('aire-off', 'n_clicks'),
     dash.dependencies.Input('aire-on', 'n_clicks')]
)
def hvac_off(off, on, session_state=None, dash_app_id=None, *args, **kwargs):
    if session_state is None:
        raise NotImplementedError("Cannot handle a missing session state")
    csf = session_state.get('aire_state', None)
    msg = 'unknown'
    if not csf:
        csf = dict(on=0, off=0)
        session_state['aire_state'] = csf
    else:
        if on and csf['on'] != on:
            hvac('on')
            msg = 'on'
        if off and csf['off'] != off:
            hvac('off')
            msg = 'off'

        csf['on'] = on
        csf['off'] = off
        return msg

    return


@panel.expanded_callback(
    dash.dependencies.Output('persiana-cmd', 'children'),
    [dash.dependencies.Input('persiana-up', 'n_clicks'),
     dash.dependencies.Input('persiana-stop', 'n_clicks'),
     dash.dependencies.Input('persiana-down', 'n_clicks'), ])
def persiana_callback(up, stop, down, session_state=None, dash_app_id=None, *args, **kwargs):
    if session_state is None:
        raise NotImplementedError("Cannot handle a missing session state")
    csf = session_state.get('control_state', None)
    if not csf:
        csf = dict(up=0, down=0, stop=0)
        session_state['control_state'] = csf
    else:
        if up and csf['up'] != up:
            persiana('up')
        if down and csf['down'] != down:
            persiana('down')
        if stop and csf['stop'] != stop:
            persiana('stop')

        csf['up'] = up
        csf['stop'] = stop
        csf['down'] = down
    # persiana('up')
    return


@panel.expanded_callback(
    dash.dependencies.Output('light-cmd', 'children'),
    [dash.dependencies.Input('light', 'n_clicks')])
def turn_on_light(n, dash_app_id=None, *args, **kwargs):
    if n:
        if n % 2:
            set_light(True)
            return 'Sent Light On'
        else:
            set_light(False)
            return 'Sent Light Off'
    return ''


class PlotDash():
    def __init__(self):
        app = DjangoDash(name="plots")
        
        app.layout = html.Div([
        
            html.Link(
                rel='stylesheet',
                href=env('STATIC_URL') + 'bulma/css/style.min.css'
            ),
            dcc.Loading(
                type="circle",
                children=[
                    html.Div(id='internal_state', children="IOT Dash!", style={'display': 'none'}),
                    html.Button('Reload Data', id='reload', className="button"),
                    html.Div(id='radios', children=[
                        dcc.DatePickerRange(
                            id='selector-fechas',
                            min_date_allowed=datetime.datetime(2020, 3, 1),
                            initial_visible_month=datetime.datetime.now(),
                            start_date=datetime.datetime.now() - datetime.timedelta(days=2),
                            end_date=datetime.datetime.now() + datetime.timedelta(days=2),
                            display_format='Y-MM-DD',
                        ),
                    ]),
                    dcc.Loading(
                        id="loading-2",
                        children=[html.Div([dcc.Graph(id='timeseries'), ])],
                        type="circle",
                    ),
                ])
        ])
        
        @app.callback(dash.dependencies.Output("loading-2", "children"))
        @app.expanded_callback(
            dash.dependencies.Output('timeseries', 'figure'),
            [dash.dependencies.Input('selector-fechas', 'start_date'),
             dash.dependencies.Input('selector-fechas', 'end_date'),
             dash.dependencies.Input('reload', 'n_clicks')
             ])
        def callback_color(start_date, end_date, reload, session_state=None, dash_app_id=None, *args, **kwargs):
            csf = session_state.get('app_state', None)
            if not csf:
                csf = dict(reload=0)
                session_state['app_state'] = csf
            else:
                if csf['reload'] != reload:
                    reload = True
                else:
                    reload = False

            if not end_date or not start_date:
                end_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
                start_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        
            if not end_date or not start_date:
                return None
            data = get_data(start_date, end_date, reload)
            fig = go.Figure()
            traces = [go.Scatter(y=data[(data['loc'] == 'T')]['value'],
                                 x=data[(data['loc'] == 'T')]['date'],
                                 name="Temp. In",
                                 mode='markers',
                                 ),
                      go.Scatter(y=data[(data['loc'] == 'TO')]['value'],
                                 x=data[(data['loc'] == 'TO')]['date'],
                                 name='Temp. Out',
                                 mode='markers',
                                 ),
                      go.Scatter(y=data[(data['loc'] == 'H')]['value'],
                                 x=data[(data['loc'] == 'H')]['date'],
                                 name="Hum. In",
                                 mode='markers',
                                 yaxis="y2",
                                 ),
                      go.Scatter(y=data[(data['loc'] == 'HO')]['value'],
                                 x=data[(data['loc'] == 'HO')]['date'],
                                 name='Hum. Out',
                                 mode='markers',
                                 yaxis="y2",
                                 ),
                      go.Scatter(y=data[(data['loc'] == 'P1')]['value'],
                                 x=data[(data['loc'] == 'P1')]['date'],
                                 name="Maceta 1", 
                                 mode='markers',
                                 yaxis="y3",
                                 ),
                      go.Scatter(y=data[(data['loc'] == 'P2')]['value'],
                                 x=data[(data['loc'] == 'P2')]['date'],
                                 name='Maceta 2', 
                                 mode='markers',
                                 yaxis="y3",
                                 ),
                      go.Scatter(y=data[(data['loc'] == 'P3')]['value'],
                                 x=data[(data['loc'] == 'P3')]['date'],
                                 name='Maceta 3', 
                                 mode='markers',
                                 yaxis="y3",
                                 ),
                      go.Scatter(y=data[(data['loc'] == 'NB')]['value'] * (950 / 1024) * (1 / 100) * 10,
                                 x=data[(data['loc'] == 'NB')]['date'],
                                 name="Nano Bat", 
                                 mode='markers',
                                 yaxis="y4",
                                 )
                      ]
            for trace in traces:
                fig.add_trace(trace)
            fig.update_layout(paper_bgcolor='#fff',
                              xaxis=dict(domain=[0.04, 0.96]),
                              yaxis=dict(range=[0, 60],
                                         anchor="free",
                                         title="ºC",
                                         showgrid=False,
                                         title_standoff=3),
                              yaxis2=dict(range=[0, 100],
                                          anchor="free",
                                          title="%rel",
                                          position=0.03,
                                          overlaying="y",
                                          showgrid=False,
                                          title_standoff=3,
                                          ),
                              yaxis3=dict(range=[0, 100],
                                          anchor="free",
                                          title="%",
                                          position=0.97,
                                          side="right",
                                          overlaying="y",
                                          showgrid=True,
                                          title_standoff=3,
                                          ),
                              yaxis4=dict(range=[5, 9.5],
                                          anchor="free",
                                          title="V",
                                          side="right",
                                          position=1,
                                          overlaying="y",
                                          showgrid=False,
                                          title_standoff=3,
                                          ))
        
            return fig
        

@functools.lru_cache(maxsize=1024)
def get_csv():
    data = pandas.read_csv(env('MQTT_LOG_FILE'), chunksize=1024)
    data.set_index('date')
    return data


def get_data(start_date, end_date, reload):
    # if reload:
    #     get_csv.cache_clear()
    # data = get_csv()
    # data = data[
    #     (data['date'] < end_date) &
    #     (data['date'] > start_date)
    #     ]

    data = pandas.DataFrame()
    for chunk in pandas.read_csv(env('MQTT_LOG_FILE'), chunksize=50000):
        data = data.append(
            chunk[(chunk['date'] > start_date) &
                  (chunk['date'] < end_date)
            ]
        )

    return data
