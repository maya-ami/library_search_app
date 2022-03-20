# OpenLibrary Search App
# Installation
Below are the instructions to install an app that automates data extraction and analysis from OpenLibrary.
Built and tested on Windows 10 and macOS Monterey.  


## 1. Install dependencies
- Python 3.7
- Some environment management system
In case of using Anaconda, use the command `conda create -n test_env python=3.7` to create a new environment. Then enter it, using `conda activate test_env`
- Some Python libraries for data analysis and data visualization
`pip install -r requirements.txt`


## 2. Start the app
In the terminal, run the command `streamlit run app.py`.
The app is now available locally at http://localhost:8501/

Alternatively, you may play with the app deployed in the cloud at https://share.streamlit.io/maya-ami/open_library_search/app.py  


## 3. Usage

The usage is fairly straightforward. As the user opens the app web page, they see a sidebar menu which contains:
- a text input cell where they can type in their search query;
- a select menu where they can specify what kind of search they want to do: generic ('Anywhere') or more specific, e.g. look for authors or books on a certain subject.
- a numeric input cell where they can specify the desired number of matches to be analysed. The default value is 100.
- a numeric input cell where they can specify the number of most frequent words appearing in the matched book titles. This number will be used to generate a plot. The default value is 10.

If the app received a non-null result from OpenLibrary, it will process the data, do some analysis and show the user:
- For virtually all searches:
  - a countplot of the most common words appearing in the matched book titles
  - a chart of the distribution of the number of characters in the matched books.
  - a table of most relevant matches Title - Author.

- For searches in "Authors" and "Subjects":
  - a list of 5 matched authors with most number of books in a descending order. For each author, there will also be a list of their top books.

As the app received the response from OpenLibrary, the raw results for the query can be downloaded as a JSON file by clicking on the button "Download search results as JSON".


## 4. Future work

Some ideas I didn't have enough time to implement:
- allow users to specify the language they are interested in. E.g., search only for books with the character 'Bella' that are written in English.
- automatically identify language of the matched book titles in order to remove the corresponding stopwords. This would improve the quality of further text analysis.
- allow users to create more complex queries. For example, search for books where the subject is Christmas and the place is London.
- some books have the field "time". It might be an interesting feature to add to the app as it would allow to explore books about a particular time period and do some research, e.g. to analyse most common words in titles and most frequent subjects, find authors with most works on that period, etc.
