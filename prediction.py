# Reference: https://fedoramagazine.org/create-containerized-machine-learning-model/

import pickle
import time

db = None


# initialize an in memory dictionary that serves as a simple database
def init_db() -> None:
    global db
    with open("top_n_movie_ids.pkl", "rb") as fp:
        db = pickle.load(fp)


# given a user id, recommend a list of comma seperated movie ids
def recommend(user_id: str) -> str:
    global db
    if db is None:
        init_db()

    # simulates a 200ms delay
    time.sleep(0.2)

    return ",".join(db[user_id])


if __name__ == "__main__":
    print(recommend("610"))