from pymongo import MongoClient
import os
import numpy as np
import plotly
import plotly.graph_objs as go
import json

client = MongoClient(os.environ["MONGODB_CLIENT"])
db = client.flickr

os.environ["MAPBOX_TOKEN"] = os.environ["MAPBOX_TOKEN"]


def load_gals():
    gals = list(db.galleries.find({}, {"photos": 0}))
    return gals


def get_gal_rows(width):
    gals = list(db.galleries.find({}, {"photos": 0}))
    rows = []
    frames = []
    idx = 1
    for gal in gals:
        if (idx / width) != (idx // width):
            frames.append(
                {
                    "caption": gal["title"] + " - " + str(gal["count_photos"]),
                    "thumb": gal["primary"],
                    "kk6gpv_link": "/gallery/" + gal["id"],
                },
            )
            idx += 1
        else:
            frames.append(
                {
                    "caption": gal["title"] + " - " + str(gal["count_photos"]),
                    "thumb": gal["primary"],
                    "kk6gpv_link": "/gallery/" + gal["id"],
                },
            )
            rows.append(frames)
            frames = []
            idx = 1
    rows.append(frames)
    return rows


def get_photo_rows(id, width):
    gal = list(db.galleries.find({"id": id}))[0]
    rows = []
    frames = []
    lats = []
    lons = []
    idx = 1
    for phid in gal["photos"]:
        if (idx / width) != (idx // width):
            frames.append(
                {
                    "thumb": gal["photos"][phid]["thumb"],
                    "kk6gpv_link": "/photo/" + phid,
                },
            )
            try:
                lats.append(float(gal["photos"][phid]["latitude"]))
                lons.append(float(gal["photos"][phid]["longitude"]))
            except Exception:
                pass
            idx += 1
        else:
            frames.append(
                {
                    "thumb": gal["photos"][phid]["thumb"],
                    "kk6gpv_link": "/photo/" + phid,
                },
            )
            try:
                lats.append(float(gal["photos"][phid]["latitude"]))
                lons.append(float(gal["photos"][phid]["longitude"]))
            except Exception:
                pass
            rows.append(frames)
            frames = []
            idx = 1
    rows.append(frames)

    lat_c = np.array(lats).mean()
    lon_c = np.array(lons).mean()

    data = [
        go.Scattermapbox(
            lat=lats,
            lon=lons,
            mode="markers",
            marker=dict(size=10, color="#2EF4F1",),
        )
    ]
    layout = go.Layout(
        autosize=True,
        font=dict(family="Roboto Mono"),
        showlegend=False,
        hovermode="closest",
        hoverlabel=dict(font=dict(family="Roboto Mono")),
        uirevision=True,
        margin=dict(r=0, t=0, b=0, l=0, pad=0),
        mapbox=dict(
            bearing=0,
            center=dict(lat=lat_c, lon=lon_c),
            accesstoken=os.environ["MAPBOX_TOKEN"],
            style="mapbox://styles/areed145/ck3j3ab8d0bx31dsp37rshufu",
            pitch=0,
            zoom=4,
        ),
    )

    graphjson = json.dumps(
        dict(data=data, layout=layout), cls=plotly.utils.PlotlyJSONEncoder
    )
    return (
        rows,
        graphjson,
        gal["title"],
        gal["count_photos"],
        gal["count_views"],
    )


def get_photo(id):
    image = list(db.photos.find({"id": id}))[0]
    image.pop("_id")
    try:
        lat_c = float(image["location"]["latitude"])
        lon_c = float(image["location"]["longitude"])
        data = [
            go.Scattermapbox(
                lat=[lat_c],
                lon=[lon_c],
                mode="markers",
                marker=dict(size=10, color="#2EF4F1",),
            )
        ]
        layout = go.Layout(
            autosize=True,
            font=dict(family="Roboto Mono"),
            showlegend=False,
            hovermode="closest",
            hoverlabel=dict(font=dict(family="Roboto Mono")),
            uirevision=True,
            margin=dict(r=0, t=0, b=0, l=0, pad=0),
            mapbox=dict(
                bearing=0,
                center=dict(lat=lat_c, lon=lon_c),
                accesstoken=os.environ["MAPBOX_TOKEN"],
                style="mapbox://styles/areed145/ck3j3ab8d0bx31dsp37rshufu",
                pitch=0,
                zoom=13,
            ),
        )

        graphjson = json.dumps(
            dict(data=data, layout=layout), cls=plotly.utils.PlotlyJSONEncoder
        )
    except Exception:
        graphjson = None
    return image, graphjson
