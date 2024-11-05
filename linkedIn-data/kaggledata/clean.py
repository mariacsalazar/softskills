import numpy as np 
import pandas as pd 
import os
import kagglehub
from googletrans import Translator
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from pathlib import Path
from google.cloud import translate_v2 as translate


nltk.download('punkt')
nltk.download('stopwords')


def download_kaggle():
    path = kagglehub.dataset_download("terencicp/eu-entry-level-data-analyst-linkedin-jobs")
    print("Path to dataset files:", path)
    df = pd.read_csv(f"{path}/eu_entry_level_data_analyst_linkedin_jobs_sample.csv")
    print(f"df is loaded")
    return df

def null_checks(df):
    key_columns = ['job_title', 'description', 'linkedin_skills']
    missing_values = df[key_columns].isnull().sum()
    print("Missing values in key columns:",missing_values)
    return None
    

def translate_text(text):
    
    try:
        # Translate text to English
        translated = translator.translate(text, dest='en')
        return translated.text
    except Exception as e:
        print(f"Error translating text: {e}")
        return text
    

def make_checkpoint_dir():
    
    datestring = "data"
    Path(datestring).mkdir(parents=True, exist_ok=True)
    return datestring

def translate_database(df):

    make_checkpoint_dir()
    columns_to_translate = ['job_title', 'description', 'linkedin_skills']
    for column in columns_to_translate:
        df[column] = df[column].apply(translate_text)

    df.to_csv('data/translated_data.csv', index=False)
    print("Translation complete. Translated data saved to 'translated_data.csv'.")
    return df

def soft_skills(text):
    
    soft_skills_keywords = [
    "communication", "teamwork", "adaptability", "problem solving", 
    "creativity", "work ethic", "attention to detail", "leadership", 
    "emotional intelligence", "collaboration", "flexibility", 
    "conflict resolution", "decision making", "empathy"]
    words = word_tokenize(text.lower())
    
    words = [word for word in words if word.isalpha() and word not in stopwords.words('english')]
    
    found_skills = [skill for skill in soft_skills_keywords if skill in words]
    return found_skills

def extract_soft_skills(df,variable):
    df['soft_skills'] = df[variable].apply(soft_skills)
    df.to_csv('data/translated_data_ss.csv', index=False)
    print("Soft skills have been extracted and saved to 'translated_data_ss.csv'.")







