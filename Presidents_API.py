from io import BytesIO
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi import HTTPException, status
import pandas as pd
import cv2 as cv

data = pd.read_csv('presidents.csv', dtype={'term_end_year': pd.Int16Dtype()})

app = FastAPI()

@app.get('/')
def root():
    return {'Introduction': 'This API helps you gather some information about the US presidents'}

@app.get('/presidents')
def print_pres_list():
    presidents_intro = data[['name', 'order', 'term_begin_year', 'term_end_year', 'political_party']]
    return presidents_intro.to_dict(orient='records')

@app.get('/presidents/{family}')
def print_pres_info(family: str):
    if not family.capitalize() in data['last_name'].values:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Enter the last name of a US president')
    wanted_presidents = data[data['last_name']==family.capitalize()] # returns a DataFrame. Bcs of Cleveland and possibly Trump
    presidents = []
    for _, pres in wanted_presidents.iterrows():
        presidents.append({ 'Order': pres['order'],
                            'Full Name': pres['name'],
                            'Term': f"{pres['term_begin_year']}-{pres['term_end_year']}",
                            'Party': pres['political_party'],
                            'Vice president(s)': pres['vice_president']})
    return presidents

@app.get('/presidents/{family}/image')
def print_img(family):
    if not family.capitalize() in data['last_name'].values:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Enter the last name of a US president')
    img = cv.imread(f'Images/{family}.jpg')
    _, enImg = cv.imencode('.png',img)
    return StreamingResponse(BytesIO(enImg.tobytes()),media_type='image/png')