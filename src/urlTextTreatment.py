
import re
import urllib.request

# source for the following characters specifications : https://stackoverflow.com/questions/1547899/which-characters-make-a-url-invalid/13500078#13500078
disallowed_in_url = [" ", "<", ">", "#", '"']#, "%"]
unwise_in_url     = ["{", "}", "|", "\\", "^", "[", "]", "`"]
reserved_in_url   = [";", "/", "?", ":", "@", "&", "=", "+", "$", ","]
NOT_ALLOWED_IN_URL = disallowed_in_url + ["\\", "\n"]

def findAllOccurrences(text, substringList):
    assert type(substringList)==type([]), "substringList must be of type list"
    assert len(substringList)>=1, "No element given in substringList"
    matchesPositions = []
    for substring in substringList:
        matches = re.finditer(substring, text)
        for match in matches:
            if match.start() not in matchesPositions:   # Don't consider 'xxx' as a new position if 'xxxY' already considered
                matchesPositions.append(match.start())
    return matchesPositions

def splitPositions(text, positionsList):
    finalText = []
    currentPos = 0
    for pos in positionsList:
        finalText.append(text[currentPos:pos])
        currentPos = pos
        if pos==positionsList[-1]:
            finalText.append(text[currentPos:len(text)])
    return finalText

def keepUrlOnlyLine(text):
    stopCharacter = NOT_ALLOWED_IN_URL
    listIndex = []
    for char in stopCharacter:
        if char in text: listIndex.append(text.index(char))
    listIndex = sorted(listIndex)
    # Case : if no stop character -> go until end of line, return full text
    # assert len(listIndex)>=1, "No stop character found"
    if len(listIndex)==0: return text
    return text[:listIndex[0]]

def keepUrlOnlyArray(array):
    substringToDetect = ['http://', 'https://']
    toDelete = []
    for element in array:
        toKeep=False
        for substring in substringToDetect:
            if substring in element: toKeep=True
        if not toKeep:
            toDelete.append(element)
    for element in toDelete:
        array.remove(element)
    return array

def getAllUrlsFromDescrption(text, removeDuplicates=True):
    splitedText = splitPositions(text, findAllOccurrences(text, ['http', 'https']))
    onlyWithUrl = keepUrlOnlyArray(splitedText)
    for i in range(len(onlyWithUrl)):
        onlyWithUrl[i] = keepUrlOnlyLine(onlyWithUrl[i])
    if removeDuplicates:
        # First : consider that 'www.test.com/mypage/' is equal to 'www.test.com/mypage'
        for i in range(len(onlyWithUrl)):
            if onlyWithUrl[i][-1]=='/': onlyWithUrl[i] = onlyWithUrl[i][:-1]
        # Then remove duplicates :
        onlyWithUrl = list(dict.fromkeys(onlyWithUrl))
    return onlyWithUrl


def getShortUrl(url):
    """
    TO BE IMPROVED
    Until now, it doesn't do any difference between 'youtube' (which can be a source) and 'youtube/channel' (which is not)
    """
    url = url.replace('https', '').replace('http', '').replace('://', '')
    if '/' in url: return url[:url.index('/')]
    else: return url


# TEST EXAMPLE
if __name__=='__main__':
    import json
    from youtubeFunctions import youtubeExtractDetails

    # text = youtubeExtractDetails("https://www.youtube.com/watch?v=DcswgkK0emM")[VIDEO_DESC]
    text = """Les actus du jour, résumées et expliquées ! 
Pour vous abonner à notre chaîne principale (reportages, interviews etc.) : https://www.youtube.com/c/hugodecrypte2/videos

🤗 Sur Instagram, du contenu exclusif et des résumés d'actu en moins d'1 minute : @HugoDecrypte http://instagram.com/hugodecrypte/

🍿 La même chose, mais pour la culture (ciné/séries, musique) : https://instagram.com/hugodecrypte.pop

⚽️ Et pour le sport : https://instagram.com/hugodecrypte.sport
 
🐦 Mon Twitter (moins de résumés d’actu, + de tweets persos) : http://twitter.com/HugoTravers

🎙 Sur Twitch, du live  ! Au menu : de l’actualité, de la culture et du jeu https://www.twitch.tv/hugodecrypte

🎧 Les actus du jour en podcast : https://open.spotify.com/show/6y1PloEyNsCNJH9vHias4T?si=pz8U9CGkTCO_IGSEnMVxVw (également disponible sur Apple Podcast, Spotify, Deezer, etc)

SOMMAIRE
00:00 Intro
00:52  Union de la gauche
03:44 Tabac en Nouvelle-Zélande
06:50 France présidente de l'UE
09:30 Boycott des JO
10:10 Yannick Agnel en GAV
10:57 Mariage gay à Tokyo

UNION DE LA GAUCHE

https://www.liberation.fr/politique/elections/de-jean-luc-melenchon-a-arnaud-montebourg-lunion-de-la-gauche-en-question-20211208_A3RWCD5TUFDCDCYAWB3MG7BSEI/

https://www.leparisien.fr/elections/presidentielle/presidentielle-il-faut-organiser-une-primaire-de-la-gauche-reclame-anne-hidalgo-08-12-2021-B4AWNRLNJBA4TBVIECUUK5JIC4.php

https://www.lemonde.fr/election-presidentielle-2022/article/2021/12/09/yannick-jadot-et-fabien-roussel-rejettent-la-primaire-a-gauche-proposee-par-anne-hidalgo_6105305_6059010.html

NOUVELLE-ZÉLANDE 

https://www.bbc.com/news/world-asia-59589775

https://edition.cnn.com/2021/12/09/asia/new-zealand-outlaw-smoking-intl-hnk/index.html

https://www.lefigaro.fr/flash-actu/la-nouvelle-zelande-envisage-d-interdire-progressivement-la-vente-de-tabac-20211209

https://www.leparisien.fr/societe/tabac-la-nouvelle-zelande-veut-interdire-la-cigarette-a-toute-une-generation-09-12-2021-IDNCZKWJFRELZDBCZ6XD5HLARA.php

MACRON UNION EUROPÉENNE 

https://www.france24.com/fr/europe/20211209-pr%C3%A9sidence-fran%C3%A7aise-de-l-ue-un-effet-d-aubaine-pour-emmanuel-macron

https://www.courrierinternational.com/article/vu-despagne-la-presidence-francaise-de-lunion-europeenne-un-tremplin-pour-macron

FRANCE JO DE PEKIN

https://www.leparisien.fr/sports/JO/jo-dhiver-2022-les-pays-qui-boycottent-diplomatiquement-les-jeux-en-paieront-le-prix-avertit-pekin-09-12-2021-OWL7ZFAV7JHS3FXKROGWBHJRW4.php

https://www.huffingtonpost.fr/entry/la-france-ne-boycottera-pas-les-jo-dhiver-a-pekin_fr_61b1cc0fe4b0b50268a17a00

MARIAGE GAY TOKYO

https://www.liberation.fr/international/le-mariage-gay-va-enfin-etre-reconnu-a-tokyo-20211208_5YM3FC765ZHUNCHHH3MQH4CCRY/

https://www.letemps.ch/societe/ville-tokyo-reconnaitra-unions-meme-sexe-dici-2023

Écriture : Blanche Vathonne - Paul Bonnaud - Manon de Cabarrus - Hugo Travers 
Montage : Leo Henry"""
    urls = getAllUrlsFromDescrption(text)
    print(json.dumps(urls, indent=1))
