from database import SessionLocal
from models import User
from security import hash_password   # ⚠️ change if needed


def seed():
    db = SessionLocal()

    try:
        if not db.query(User).filter(User.email == "elizabeth@example.com").first():
            admin = User(
                email="elizabeth@example.com",
                hashed_password=hash_password("Victor123!"),
                role="admin",
            )
            db.add(admin)

        if not db.query(User).filter(User.email == "user@example.com").first():
            user = User(
                email="user@example.com",
                hashed_password=hash_password("User123!"),
                role="user",
            )
            db.add(user)

        db.commit()
        print("✅ Users seeded successfully")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
