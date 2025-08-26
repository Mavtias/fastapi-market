import os
import random
from faker import Faker
from sqlalchemy.orm import Session
from app import models, database

fake = Faker()

countries = ["austria", "france", "germany", "italy", "spain"]
categories = ["mobiles", "electronics", "real estate", "vehicles"]


def reset_fake_data(db: Session):
    """Elimina solo los usuarios y productos marcados como fake."""
    deleted_products = db.query(models.Product).filter(models.Product.is_fake == True).delete(synchronize_session=False)
    deleted_users = db.query(models.User).filter(models.User.is_fake == True).delete(synchronize_session=False)
    db.commit()
    print(f"Productos Faker eliminados: {deleted_products} ✅")
    print(f"Usuarios Faker eliminados: {deleted_users} ✅")

def create_fake_users(db: Session, n=30):
    for _ in range(n):
        user = models.User(
            firstname=fake.first_name(),
            lastname=fake.last_name(),
            email=fake.unique.email(),
            address=fake.address(),
            country=random.choice(countries),
            city=fake.city(),
            hashed_password="fakehashed123",
            is_fake=True  # 👈 marcar como Faker
        )
        db.add(user)
    db.commit()
    print(f"{n} usuarios Faker creados ✅")

def create_fake_products(db: Session, n=50):
    users = db.query(models.User).filter(models.User.is_fake == True).all()
    if not users:
        print("No hay usuarios Faker en la base de datos. Primero crea usuarios Faker.")
        return
    
    fake_images_dir = "app/assets/img/uploads"
    fake_images = [f for f in os.listdir(fake_images_dir) if f.endswith(".jpg")]
    for _ in range(n):
        product = models.Product(
            title=fake.word().capitalize(),
            description=fake.sentence(nb_words=200),
            price=round(random.uniform(10, 1000), 2),
            category=random.choice(categories),
            image_url=f"/assets/img/uploads/{random.choice(fake_images)}" if fake_images else "/assets/img/uploads/no-image.png",
            owner_id=random.choice(users).id,
            is_fake=True  # 👈 marcar como Faker
        )
        db.add(product)
    db.commit()
    print(f"{n} productos Faker creados ✅")

def populate_db():
    db: Session = next(database.get_db())
    reset_fake_data(db)
    create_fake_users(db, n=30)
    create_fake_products(db, n=50)

if __name__ == "__main__":
    populate_db()
