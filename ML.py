import pandas as pd
from sklearn.ensemble import RandomForestRegressor


def predict_likeability(dataframe,item):
    y=dataframe.liked
    features=["release_date","explicit","duration","popularity","acousticness","energy","instrumentalness","liveness","loudness","speechiness","tempo","valence","danceability"]
    item=item[features]
    x=dataframe[features]
    model = RandomForestRegressor(random_state=1)
    model.fit(x,y)
    predictions=model.predict(item)
    return predictions




