import random
from faker import Faker

from models import SessionLocal, User, Post, Comment


def generate_data(num_users=10, num_posts=20, num_comments=50):
    session = SessionLocal()
    fake = Faker()
    data_format = "%Y-%m-%d %H:%M:%S"

    word_pool = ["fantastic", "amazing", "interesting", "boring", "great", "insightful", "random", "valuable",
                 "opinion", "discussion"]

    users = []
    for _ in range(num_users):
        user = User(
            name=fake.name(),
            email=fake.email(),
            is_active=True,
            created_at=fake.date_time_between(start_date="-2y", end_date="now")
        )
        session.add(user)
        users.append(user)
    session.commit()

    posts = []
    for _ in range(num_posts):
        user = random.choice(users)
        post = Post(
            title=f"{fake.word().capitalize()} {random.choice(word_pool)}",
            content=fake.text(),
            user=user,
            created_at=fake.date_time_between(start_date=user.created_at, end_date="now")
        )
        session.add(post)
        posts.append(post)
    session.commit()

    for _ in range(num_comments):
        user = random.choice(users)
        post = random.choice(posts)
        comment = Comment(
            content=fake.sentence(),
            user=user,
            post=post,
            created_at=fake.date_time_between(start_date=post.created_at, end_date="now")
        )
        session.add(comment)

    session.commit()
    session.close()
    print("Data generation complete!")


if __name__ == "__main__":
    generate_data()
    print("Dodano przykładowe dane do bazy!")
