import nltk
import streamlit as st
import altair as alt
import pandas as pd
import requests
import spacy
import json
import re


def preprocess_title(data, num_top_words):
    data.fillna('', inplace=True)
    all_title_tokens = ''
    for title in data['title']:
        all_title_tokens += title + ' '
    tokens = nltk.word_tokenize(all_title_tokens.lower())
    tokens_no_stop = [w for w in tokens if w not in stopwords]
    tokenized_titles = [re.sub('[^A-Za-z]+', '', token) for token in tokens_no_stop]
    tokenized_titles = [w for w in tokenized_titles if w != '']
    freq_dict = nltk.FreqDist(w for w in tokenized_titles)
    top_tokens = pd.DataFrame(freq_dict.most_common(num_top_words), columns=['word', 'count'])
    return top_tokens

def process_search_results(data):
    df = pd.DataFrame(data['docs'])
    df['index'] = [i for i in range(len(df))]
    df.fillna('', inplace=True)
    df['author_name'] = (df['author_name'].transform(lambda x: ", ".join(map(str,x))))
    df['person'] = (df['person'].transform(lambda x: ", ".join(map(str,x))))
    df['characters num'] = [len(pers) for pers in df['person']]
    return df

def top_title_words(data, num_top_words, query_type, query):
    '''Visualize the most common words in titles.'''
    top_tokens = preprocess_title(data, num_top_words)

    c = alt.Chart(top_tokens).mark_bar().encode(
                  alt.Y('word', sort='-x'), x='count'
                  ).properties(title="Top {} words in book titles for {}: {}".format(
                  num_top_words, query_type, query), width=600)
    return c

def top_characters(data, query_type, query):
    '''Visualize the distribution of numbers of characters.'''
    c = alt.Chart(data).mark_circle(
                  opacity=0.5).encode(x='characters num', y='index',
                  tooltip=['title', 'author_name', 'characters num', 'person']
                  ).properties(
                  title='The distribution of characters in the books, {}: {}'.format(
                  query_type, query),
                  width=600,height=400)

    return c

def top_authors(data):
    authors_list = data['author_name'].value_counts().index[:5]
    df = data[data['author_name'].isin(authors_list)].copy()
    df['books found'] = df.groupby(['author_name'], as_index=True)['author_name'].transform(lambda x: x.count())
    df = df.groupby(['author_name','books found'], as_index=True).agg({'title': pd.Series.to_list})
    df = df.sort_values(by=['books found'], ascending=False).reset_index()
    df['top titles'] = [lst[:3] for lst in df['title'].values]
    authors, num_books, titles = df['author_name'], df['books found'], df['top titles']
    for i, (a, n, t) in enumerate(zip(authors, num_books, titles)):
        st.markdown('**{}. {}**'.format(i+1, a))
        st.caption('Books found: {}'.format(n))
        st.write('Top works: ', t)

def top_matches(data, query, search_space):
    if search_space=='Authors':
        st.subheader("Best matches for {} in {}:".format(query, search_space))
        if len(data['author_name'].unique()) > 2:
            top_authors(data)

    elif search_space=='Persons':
        st.subheader("Most relevant matches for {} in {}:".format(query, search_space))
        st.dataframe(data[['title','author_name', 'person']].head(10), width=600)

    elif search_space=='Subjects':
        st.subheader("Most relevant matches for {} in {}:".format(query, search_space))
        st.dataframe(data[['title','author_name']].head(10), width=600)
        st.subheader("Most popular authors for {} in {}:".format(query, search_space))
        if len(data['author_name'].unique()) > 2:
            top_authors(data)

    else:
        st.subheader("Most relevant matches for {} in {}:".format(query, search_space))
        st.dataframe(data[['title','author_name']].head(10), width=600)


@st.cache
def search(query, num_matches, field):
    params = {field: query, 'fields':'title, author_name, person', 'limit': num_matches}
    req = requests.get(url='http://openlibrary.org/search.json', params=params)
    return req.json()


def main():
    st.title('OpenLibrary search')
    st.write('This is an app to explore OpenLibrary search API using a graphical interface.')

    text_input = st.sidebar.text_input('Type in your search query')
    search_space = st.sidebar.selectbox('Search in', ('Anywhere', 'Titles',
                                        'Authors', 'Persons', 'Subjects', 'Places'))
    query = '"{}"'.format(text_input)
    num_matches = int(st.sidebar.number_input('Specify the max number of matches to analyze', min_value=100))
    num_top_words = int(st.sidebar.number_input('Specify the number of most common words to show', value=10))

    search_space_mapping = {'Anywhere': 'q',
                            'Titles': 'title',
                            'Authors': 'author',
                            'Persons': 'person',
                            'Subjects': 'subject',
                            'Places': 'place'}

    if text_input:
        query_type = search_space_mapping[search_space]
        result = search(query, num_matches, field=query_type)
        result_json = json.dumps(result)

        try:
            data = process_search_results(result)

            c_words = top_title_words(data, num_top_words, query_type, query)
            st.altair_chart(c_words)

            c_chars = top_characters(data, query_type, query)
            st.altair_chart(c_chars)

            top_matches(data, query, search_space)

            st.write()
            st.download_button('Download search results as JSON', data=result_json)

        except Exception as e:
            st.warning("Sorry, couldn't find anything matching... Try changing your search criteria")

if __name__ == '__main__':
    # load libraries' dependencies once
    nltk.download('punkt')
    nlp = spacy.load("en_core_web_sm")
    stopwords = nlp.Defaults.stop_words
    main()
