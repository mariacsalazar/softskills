from clean import *

def main():
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(os.path.dirname(abspath))
    print(dname)
    os.chdir(dname)

    translator = Translator()
    original_data=download_kaggle()
    null_checks(original_data)
    translated_data=translate_database(original_data)
    df=extract_soft_skills(translated_data,'description')


if __name__ == "__main__":
    main()

    
