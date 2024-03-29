from io import BytesIO
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi import HTTPException, status
import pandas as pd
import cv2 as cv

data = pd.read_csv('presidents.csv', dtype={'term_end_year': pd.Int16Dtype(), 'assassinated':pd.BooleanDtype(), 'good_to_know':pd.StringDtype()})

app = FastAPI()

@app.get('/')
def root():
    return {'Introduction': 'This API helps you gather some information about the US presidents'}

@app.get('/presidents')
def print_pres_list():
    presidents_intro = data[['name', 'order', 'term_begin_year', 'term_end_year', 'assassinated', 'political_party']]
    return presidents_intro.to_dict(orient='records')

@app.get('/presidents/{family}')
def print_pres_info(family: str):
    if not family.capitalize() in data['last_name'].values:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Enter the last name of a US president')
    wanted_presidents = data[data['last_name']==family.capitalize()] # returns a DataFrame. Bcs same last names
    presidents = []
    for _, pres in wanted_presidents.iterrows():
        presidents.append({ 'Order': pres['order'],
                            'Full Name': pres['name'],
                            'Term': f"{pres['term_begin_year']}-{pres['term_end_year']}",
                            'Assassinated': pres['assassinated'],
                            'Party': pres['political_party'],
                            'Vice president(s)': pres['vice_president'],
                            'Good to know': pres['good_to_know']})
    return presidents

@app.get('/presidents/{family}/image')
def print_img(family):
    family = family.capitalize()
    try:
        img = cv.imread(f'images/{family}.jpg')
        _, enImg = cv.imencode('.png',img)
        return StreamingResponse(BytesIO(enImg.tobytes()),media_type='image/png')
    except:
        wp = data[data['last_name']==family] # wp stands for Wanted President
        if len(wp) == 0:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Enter the last name of a US president')
        if len(wp) == 2:
            raise HTTPException(
                                status.HTTP_400_BAD_REQUEST, 
                                f"There are 2 presidents with this last name. For {wp.iloc[0]['name']} enter '{family}1' and for {wp.iloc[1]['name']} enter '{family}2'")
            
