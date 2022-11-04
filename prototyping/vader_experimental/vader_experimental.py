from SharedConnectors import dbConnection
from nltk.sentiment.vader import SentimentIntensityAnalyzer


def test_secret_VADER_slow_and_bad():
    dbLink:dbConnection._connection = dbConnection.get_db_connection()
    VADERAnalyzer = SentimentIntensityAnalyzer()

    grab_unVADERed_tweets_query = dbConnection.query_select_unVADERed_tweets
    update_tweet_with_VADER_scores = dbConnection.query_update_tweet_with_VADER_scores_NegNeuPosCompID
    # update_temp_table = 'INSERT INTO tempVader VALUES %s'
    # https://stackoverflow.com/questions/1262786/mysql-update-query-based-on-select-query

    # merge_temp_and_tweets = 'UPDATE tweets AS destinationTable INNER JOIN tempVADER AS sourceTable ON destinationTable.id = sourceTable.id SET destinationTable.VADERcompound = sourceTable.compound, destinationTable.VADERneg = sourceTable.nega, destinationTable.VADERneu = sourceTable.neu, destinationTable.VADERpos = sourceTable.pos'
    # update_duplicate_trickery = 'INSERT INTO tweets(id, VADERneg, VADERneu, VADERpos, VADERcompound) VALUES %s AS new(newid, nega, neu, pos, compound) ON DUPLICATE KEY UPDATE VADERneg = nega, VADERneu = neu, VADERpos = pos, VADERcompound = compound'
    # ^ nega not neg. Huh. Weird.
    # Nah, need to have defaults for non-nulls such as author_id. Just do a temporary table and move data over.
    with dbLink.cursor() as dbCursor:
        dbCursor.execute(grab_unVADERed_tweets_query)
        tweetsPlusID = dbCursor.fetchall()

    updateTuple = []

    for tweet in tweetsPlusID:
        sentimentScores = VADERAnalyzer.polarity_scores(tweet[1])
        # print(tweet[0], tweet[1], 'Neg: ', sentimentScores['neg'], 'Neutral: ', sentimentScores['neu'], 'Pos: ', sentimentScores['pos'], 'Compound: ', sentimentScores['compound'])
        updateTuple.append((sentimentScores['neg'],sentimentScores['neu'],sentimentScores['pos'],sentimentScores['compound'],tweet[0]))

    tupleString = ','.join(map(str,updateTuple))
    # updateString = update_temp_table % tupleString
    # print(tupleString[0:200])
    # print(VADERAnalyzer.polarity_scores(tweetsPlusID[0][1]),VADERAnalyzer.polarity_scores(tweetsPlusID[1][1]))
    if(True):
        with dbLink.cursor() as dbCursor:
            dbCursor.executemany(update_tweet_with_VADER_scores,updateTuple)
            # dbCursor.execute(update_duplicate_trickery,(tupleString,))
            # dbCursor.execute(updateString)
            print(dbCursor.fetchall())
            # dbCursor.execute(merge_temp_and_tweets)
            dbCursor.execute(dbConnection.query_select_idAndScore_where_ID,((tweetsPlusID[0][0]),))
            print(dbCursor.fetchall())
            print(VADERAnalyzer.polarity_scores(tweetsPlusID[0][1]))
        # dbLink.commit()
        dbLink.rollback()


def test_secret_VADER():
    dbLink:dbConnection._connection = dbConnection.get_db_connection()
    VADERAnalyzer = SentimentIntensityAnalyzer()

    grab_unVADERed_tweets_query = dbConnection.query_select_unVADERed_tweets
    # update_tweet_with_VADER_scores = 'UPDATE tweets SET VADERneg = %s, VADERneu = %s, VADERpos = %s, VADERcompound = %s WHERE id = %s'
    update_temp_table = dbConnection.query_insert_into_temp_table_TupleList_IDNegNeuPosComp
    # https://stackoverflow.com/questions/1262786/mysql-update-query-based-on-select-query

    merge_temp_and_tweets = dbConnection.query_merge_temp_and_tweets
    # update_duplicate_trickery = 'INSERT INTO tweets(id, VADERneg, VADERneu, VADERpos, VADERcompound) VALUES %s AS new(newid, nega, neu, pos, compound) ON DUPLICATE KEY UPDATE VADERneg = nega, VADERneu = neu, VADERpos = pos, VADERcompound = compound'
    # ^ nega not neg. Huh. Weird.
    # Nah, need to have defaults for non-nulls such as author_id. Just do a temporary table and move data over.
    with dbLink.cursor() as dbCursor:
        dbCursor.execute(grab_unVADERed_tweets_query)
        tweetsPlusID = dbCursor.fetchall()

    updateTuple = []

    for tweet in tweetsPlusID:
        sentimentScores = VADERAnalyzer.polarity_scores(tweet[1])
        # print(tweet[0], tweet[1], 'Neg: ', sentimentScores['neg'], 'Neutral: ', sentimentScores['neu'], 'Pos: ', sentimentScores['pos'], 'Compound: ', sentimentScores['compound'])
        updateTuple.append((tweet[0],sentimentScores['neg'],sentimentScores['neu'],sentimentScores['pos'],sentimentScores['compound']))

    tupleString = ','.join(map(str,updateTuple))
    updateString = update_temp_table % tupleString
    # print(tupleString[0:200])
    # print(VADERAnalyzer.polarity_scores(tweetsPlusID[0][1]),VADERAnalyzer.polarity_scores(tweetsPlusID[1][1]))
    if(True):
        with dbLink.cursor() as dbCursor:
            # dbCursor.executemany(update_tweet_with_VADER_scores,updateTuple)
            # dbCursor.execute(update_duplicate_trickery,(tupleString,))
            dbCursor.execute(updateString)
            print(dbCursor.fetchall())
            dbCursor.execute(merge_temp_and_tweets)
            dbCursor.execute(dbConnection.query_delete_rows_in_temporary_table)
            print(dbCursor.fetchall())
            dbCursor.execute(dbConnection.query_select_idAndScore_where_ID,((tweetsPlusID[0][0]),))
            print(dbCursor.fetchall())
            print(VADERAnalyzer.polarity_scores(tweetsPlusID[0][1]))
        # dbLink.commit()