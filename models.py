from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class User(db.Model):
    """User in the system."""
    # User
    # -
    # id PK int
    # username string
    # first_name string
    # last_name string
    # email string
    # region NULL string

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    first_name = db.Column(
        db.Text,
        nullable = False
    )

    last_name = db.Column(
        db.Text,
        nullable = False
    )

    region = db.Column(
        db.Text
    )

    password = db.Column(
        db.Text,
        nullable=False
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, email, password, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.
        If can't find matching user or password is wrong, returns False.
        If user is found an password is correct,
        returns user instance.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

####################################################

# LightLevel
# -
# id PK int
# description string

# SoilType
# -
# id PK int
# description string

# SoilMoisture
# -
# id PK int
# description string

# GrowingArea
# -
# id PK int
# user FK >- User.id User
# light_level FK >- LightLevel.id LightLevel
# soil_type FK >- SoilType.id
# soil_moisture FK >- SoilMoisture.id

# SavedSearch
# -
# id PK int
# user FK >- User.id User
# light_needs FK >- LightLevel.id LightLevel NULL
# soil_type_needs FK >- SoilType.id NULL
# soil_moisture_needs FK >- SoilMoisture.id NULL
# min_height int NULL
# max_height int NULL
# spread int NULL

# Plant
# -
# id PK int

# PlantList
# -
# id PK int
# growing_area FK >- GrowingArea.id
# user FK >- User.id User
# name string

# PlantJoinPlantList
# -
# plant_list_id PK FK >- PlantList.id PlantList.id
# plant_id PK FK >- Plant.id Plant.id


####################################################

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)

