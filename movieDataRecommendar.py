# let's import the basic Libraries
# for data visualization
import numpy as np
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
import warnings

warnings.filterwarnings("ignore")


# read data file
def read_data():
    data = pd.read_csv('moviedata/movie_metadata.csv')

    # get rid of all columns that are useless
    data = data.drop(['color',
                      'director_facebook_likes',
                      'actor_3_facebook_likes',
                      'actor_1_facebook_likes',
                      'cast_total_facebook_likes',
                      'actor_2_facebook_likes',
                      'facenumber_in_poster',
                      'content_rating',
                      'country',
                      'movie_imdb_link',
                      'aspect_ratio',
                      'plot_keywords',
                      ],
                     axis=1)

    # is 'not a number' in data and get rid of it
    data = data[~np.isnan(data['gross'])]
    data = data[~np.isnan(data['budget'])]

    # fill any place it has null value as unknown
    data['actor_2_name'].fillna('Unknown Actor', inplace=True)
    data['actor_3_name'].fillna('Unknown Actor', inplace=True)

    data = data[data.isnull().sum(axis=1) <= 2]

    # change big numbers into ex. 1 Million
    data['gross'] = data['gross'] / 1000000
    data['budget'] = data['budget'] / 1000000

    # profit column
    data['Profit'] = data['gross'] - data['budget']

    # drop duplicate movie titles
    data.drop_duplicates(subset=None, keep='first', inplace=True)

    data['Moviegenres'] = data['genres'].str.split('|')
    data['Genre1'] = data['Moviegenres'].apply(lambda x: x[0])

    # Some movies have only one genre. In such cases, assign the same genre to 'genre_2' as well
    data['Genre2'] = data['Moviegenres'].apply(lambda x: x[1] if len(x) > 1 else x[0])
    data['Genre3'] = data['Moviegenres'].apply(lambda x: x[2] if len(x) > 2 else x[0])
    data['Genre4'] = data['Moviegenres'].apply(lambda x: x[3] if len(x) > 3 else x[0])
    return data


# recommend data on actor
def movie_with_actor(data, actor):
    a = data[['movie_title', 'imdb_score']][data['actor_1_name'] == actor]
    b = data[['movie_title', 'imdb_score']][data['actor_2_name'] == actor]
    c = data[['movie_title', 'imdb_score']][data['actor_3_name'] == actor]
    a = a.append(b)
    a = a.append(c)
    a = a.sort_values(by='imdb_score', ascending=False)
    return a.head(15)


def movie_with_genre(data, genre):
    a = data[['movie_title', 'imdb_score']][data['actor_1_name'] == genre]
    b = data[['movie_title', 'imdb_score']][data['actor_2_name'] == genre]
    c = data[['movie_title', 'imdb_score']][data['actor_3_name'] == genre]
    a = a.append(b)
    a = a.append(c)
    a = a.sort_values(by='imdb_score', ascending=False)
    return a.head(15)


def movie_with_movie(data, movie):
    # split genres into array
    a = data['genres'].str.split('|')

    # make into array with True and False
    te = TransactionEncoder()
    x = te.fit(a).transform(a)
    x = pd.DataFrame(x, columns=te.columns_)

    # make into array with only 1 and 0
    genres = x.astype('int')

    # put movie titles
    genres.insert(0, 'movie_title', data['movie_title'])

    # make the movie titles a index
    genres = genres.set_index('movie_title')

    # make into sparse matrix
    y = genres.transpose()

    # no idea what's going on here/had to search up on google
    movie = y[movie + '\xa0']
    similar_movies = y.corrwith(movie)
    similar_movies = similar_movies.sort_values(ascending=False)
    similar_movies = similar_movies.iloc[1:]
    similar_movies = similar_movies.head(25)
    return similar_movies


def main():
    data = read_data()

    print('1.) Search movie based on actor\n'
          '2.) Search movie based on genre\n'
          '3.) Search movie based on another movie')
    user_input = input('What movies do you want recommended: ')

    if user_input == '1':
        actor = input('Actor Name: ')
        a = movie_with_actor(data, actor)
        print(a)
    elif user_input == '2':
        genre = input('Genre: ')
        a = movie_with_genre(data, genre)
        print(a)
    elif user_input == '3':
        movie = input('Movie: ')
        a = movie_with_movie(data, movie)
        for i in range(len(a)):
            if not pd.isna(a[i]):
                print(a['movie_title'] + a[i])
    else:
        print('L + ratio + no maidens')


main()
