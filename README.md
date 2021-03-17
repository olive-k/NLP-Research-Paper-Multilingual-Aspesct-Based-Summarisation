#### Multilingual multi-domain aspect based summarisation

In order to successfully run this code, please follow the steps given below:

1. Create your virtual environment (if you're using a venv)
2. Create a directory called 'data'. 

        Within the 'data' directory, create 2 more directories: 'domains' and 'qid'
            Within 'domains', cretae another directory called 'animals'
            This is where all the scraped data files will be saved (one json file per Wikipedia page)

            Within the 'qid' directory, place the .csv file containing all the page_titles for the 'animals' domain.
            This is the file that you downloaded from Wikidata after running the query for 'animal'
            
3. In scraper.py, 

    In line 12 change the argument of cachedStopWords = stopwords.words("english"), to whatever language you're building.
    
    Come to the 'main' block. Change lang = 'en' to whatever lang you are building (eg: 'de', 'fr', etc.)

4. Run scraper.py