import requests
import os
from PIL import Image

base_url = "https://api.mangadex.org"
title = "Usuzumi no Hate"
title = input("Which manga would you like to download (title)?")

#Searching for manga by title
r_manga = requests.get(
    f"{base_url}/manga",
    params={"title": title}
)

print("Mangas found:")
for i, manga in enumerate(r_manga.json()["data"]):
    try:
        print(f"{i}. {manga["attributes"]["title"]["en"]}")
    except:
        print("No english title available")

if len(r_manga.json()["data"]) > 1:
    manga_choice = int(input("Select manga to download (index):"))
else:
    manga_choice = 0

manga = r_manga.json()["data"][manga_choice]
manga_title = manga["attributes"]["title"]["en"]

print(f"Downloading {manga_title}")


r_chaps = requests.get(
    f"{base_url}/manga/{manga["id"]}/feed",
    params = {"translatedLanguage[]": ["en"]}
)
print(".")
print(".")
print(".")
for i, chapter in enumerate(r_chaps.json()["data"]):
    print(f"Chapter {i+1}:")
    #GETting chapter data & page ids
    r_img = requests.get(f"{base_url}/at-home/server/{chapter["id"]}")

    r_json = r_img.json()   
    host = r_json["baseUrl"]
    chapter_hash = r_json["chapter"]["hash"]
    data = r_json["chapter"]["data"]
    data_saver = r_json["chapter"]["dataSaver"]
    
    print("got image references")

    # Making a folder to store the images in.
    three_digit_i = ("00"+str(i+1))[-3:]
    folder_path = f"mangas/{manga_title}"
    chapter_path = folder_path + f"/{three_digit_i}_{chapter["attributes"]["title"]}"
    os.makedirs(chapter_path, exist_ok=True)
    
    print("made folder for images")

    #downloading page images
    for page in data:
        r = requests.get(f"{host}/data/{chapter_hash}/{page}")

        with open(f"{chapter_path}/{page}", mode="wb") as f:
            f.write(r.content)
            f.close()

    print("downloaded pages")

    #converting images to pdf
    images = [
        Image.open(f"{chapter_path}/{page}")
        for page in data
    ]

    pdf_path = chapter_path + ".pdf"
        
    images[0].save(
        pdf_path, "PDF" ,resolution=100.0, save_all=True, append_images=images[1:]
    )
    print("converted into pdf")

    for page in data:
        os.remove(f"{chapter_path}/{page}")
    os.rmdir(chapter_path)


    print(f"Succesfully downloaded chapter {i+1} to {chapter_path}")
    print()
