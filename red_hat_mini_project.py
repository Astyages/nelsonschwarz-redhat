# Note to task authors
# =============================================================================
# 1.
# Not to sound confrontive, but why "Import the file into a local db"? The 
# file is easily managed in memory and would need to be exported for analytics, 
# anyways. Was the intention that I could use SQL, instead of pandas, to
# realize the task?

# 2.
# Why "write functions in python to perform the following computations"? 
# Specifically, why "write functions"? If the function is specific to this data, 
# the function would just be an unnecessary wrapper for the analytics below.
# If the function is not dataset-specific, then I would need to make assumptions 
# about input data schema and column types. I guess that is fine for a live
# discussion, but less so for a bounded mini-project.

# 3. 
# In absence of functions, there is an absence of function tests. If I 
# misunderstood the instructions, or should have made certain assumptions, 
# feel free to discuss function tests when we meet. 



# LIBRARIES
# =============================================================================
import pandas as pd




# SETUP
# =============================================================================
movieMetadata = pd.read_csv('movie_metadata.csv')




# PART I
# =============================================================================
# Compute the top 10 genres in decreasing order by their profitability

# exploding genre array
movieGenres = (
    pd.DataFrame(
        movieMetadata['genres']
        .str
        .split('|')
        .reset_index(drop=True), 
        columns = ['genres']
        )
    .genres
    .apply(pd.Series)
    .reset_index(drop=True)
    )

genreAccounting = (
    pd.concat(
        [movieMetadata[['gross', 'budget']], movieGenres], 
        axis=1)
    )

genreAccounting = (
    pd.melt(
        genreAccounting, 
        id_vars=['gross', 'budget'],
        value_name='genres'
        )
    .drop('variable', axis=1)
    .dropna()
    .groupby('genres')
    .sum()
    )

# profitability: net revenue
genreAccounting['profitabilityInBillions'] = (
    (genreAccounting['gross'] - genreAccounting['budget']) / 1000000000.0
    )

# top 10 genres by profitability in billions
(
    genreAccounting
    .profitabilityInBillions
    .nlargest(10)
    .apply(lambda x: '%.3f' % x)
)

del movieGenres
del genreAccounting



# PART II
# =============================================================================
# Compute the top 10 directors or actors in decreasing order by their 
# profitability

movieStars = movieMetadata[['director_name', 'actor_1_name', 'actor_2_name', 
                            'actor_3_name', 'gross', 'budget', 'imdb_score']]

simplifyStars = (
    lambda star_type: 'actor' if star_type == 'actor_1_name' or
                                 star_type == 'actor_2_name' or
                                 star_type == 'actor_3_name' 
               else 'director'
    )

# movie star: director or actor
starsAccounting = (
    pd.melt(
        movieStars, 
        id_vars=['gross', 'budget'],
        value_vars=['director_name', 'actor_1_name', 
                    'actor_2_name', 'actor_3_name'],
        value_name='movie_star_name'
        )
    .dropna()
    .rename(index=str, columns={"variable": "movie_star_type"})
    )

starsAccounting['movie_star_type'] = starsAccounting['movie_star_type'].apply(simplifyStars)
# avoiding case differences by lowering
starsAccounting['movie_star_name'] = starsAccounting['movie_star_name'].str.lower()

starsAccounting = (
    starsAccounting
    .groupby('movie_star_name')
    .agg({
        'gross':'sum',
        'budget':'sum',
        # most frequent movie star type: director or actor
        'movie_star_type':lambda x:x.value_counts().index[0]})
    )

# profitability: net revenue
starsAccounting['profitabilityInBillions'] = (
    (starsAccounting['gross'] - starsAccounting['budget']) / 1000000000.0
    )

# top 10 movie stars by profitability in billions
(    
    starsAccounting
    .reset_index()
    .set_index(['movie_star_name', 'movie_star_type'])
    .profitabilityInBillions
    .nlargest(10)
    .apply(lambda x: '%.3f' % x)
)

del starsAccounting



# PART III
# =============================================================================
# Find the best actor-director pairs (up to 10) that have the highest 
# IMDB_ratings

movieStarsRatings = (
    movieStars[['director_name', 'actor_1_name', 'actor_2_name', 
                'actor_3_name', 'imdb_score']]
    )

movieStarsRatings = (
    pd.melt(
        movieStarsRatings, 
        id_vars=['director_name', 'imdb_score'],
        value_vars=['actor_1_name', 'actor_2_name', 'actor_3_name'],
        value_name='actor_name'
        )
    .reset_index()
    .drop(['index', 'variable'], axis=1)
    .dropna()
    )

# avoiding case differences by lowering
movieStarsRatings['director_name'] = movieStarsRatings['director_name'].str.lower()
movieStarsRatings['actor_name'] = movieStarsRatings['actor_name'].str.lower()

movieStarsRatings = (
	movieStarsRatings
	.groupby(['director_name', 'actor_name'])
	.agg({'imdb_score':'mean'})
	)

# top rated actor-director pairs
(    
    movieStarsRatings
    .imdb_score
    .nlargest(10)
)

