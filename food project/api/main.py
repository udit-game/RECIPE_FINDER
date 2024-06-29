import time

from fastapi import FastAPI, File, UploadFile, HTTPException
import uvicorn
import numpy as np
from io import BytesIO
from PIL import Image
import tensorflow as tf
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add this middleware to enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],  # Add any other origins as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# sentiment
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import re




def clean_text(text):
    # Remove unwanted characters, punctuation, numbers, and special symbols
    cleaned_text = re.sub(r'[^a-zA-Z]', ' ', text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    clean = re.compile('<.*?>')
    cleaned_text = re.sub(clean, '', cleaned_text)
    cleaned_text = cleaned_text.strip()
    return cleaned_text


MODEL2 = f"cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(MODEL2)
model = AutoModelForSequenceClassification.from_pretrained(MODEL2)


@app.post("/predict_sentiment/")
async def predict_sentiment(text: str):
    try:
        text = clean_text(text)
        text = text.lower()
        text = tokenizer(text, return_tensors='pt')
        score = model(**text)[0][0].detach().numpy()
        if score[0] > score[1]:
            if score[0] > score[2]:
                sentiment = "negative"
            else:
                sentiment = "positive"
        else:
            if score[1] > score[2]:
                sentiment = "neutral"
            else:
                sentiment = "positive"

        return {"sentiment": sentiment}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


# **********************************************************************************
MODEL = tf.keras.models.load_model("/Users/uditjha/PycharmProjects/Project 3/food project/Models/class")
# C:\Users\mayan\OneDrive\Desktop\food project\Models\class
CLASS_NAMES = ["Chocolate Cake", "Donuts", "Burger", "Pizza"]


@app.get("/ping")
async def ping():
    return "hello"


def read_file_as_image(data) -> np.ndarray:
    size = (256, 256)
    image = np.array(Image.open(BytesIO(data)).resize(size))
    return image


@app.post("/predict")
async def predict(
        file: UploadFile = File(...)
):
    # bytes = await file.read()
    image = read_file_as_image(await file.read())
    img_batch = np.expand_dims(image, 0)

    predictions = MODEL.predict(img_batch)

    predicted_class = CLASS_NAMES[np.argmax(predictions[0])]
    confidence = np.max(predictions[0])
    time.sleep(2.5)
    return {
        'status': 200,
        'class': predicted_class,
        'confidence': float(confidence)
    }


if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8000)
