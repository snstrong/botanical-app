from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class User(db.Model):
    """User in the system."""

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

    # region = db.Column(
    #     db.Text
    # )

    password = db.Column(
        db.Text,
        nullable=False
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, email, password, first_name, last_name):
        """Sign up user. Hashes password and adds user to system."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            first_name=first_name,
            last_name=last_name
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.
        If can't find matching user or password is wrong, returns False.
        If user is found and password is correct,
        returns user instance.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

####################################################

class GrowingArea(db.Model):

    __tablename__ = 'growing_areas'

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    name = db.Column(
        db.String(50),
        default="(no name)"
    )
    description = db.Column(
        db.String(200),
        default="(no description)"
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade")
    )
    user = db.relationship('User', backref="growing_areas")

    light_level = db.Column(
        db.String
    )
    soil_texture = db.Column(
        db.String
    )
    soil_moisture = db.Column(
        db.String
    )
    soil_ph = db.Column(
        db.Float
    )
    notes = db.Column(
        db.String(400)
    )

    def __repr__(self):
        return f"<Growing Area #{self.id}: {self.name}, User #{self.user}>"

####################################################

class Plant(db.Model):
    __tablename__ = "plants"

    # TODO: ADD COMMON NAME(S)

    id = db.Column(
        db.Integer,
        primary_key = True
    )
    slug = db.Column(
        db.String,
        nullable=False,
        unique=True
    )
    scientific_name = db.Column(
        db.String,
        nullable=False
    )
    image_url = db.Column(
        db.String
    )

class PlantList(db.Model):
    __tablename__ = "plant_lists"

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    name = db.Column(
        db.String(30),
        nullable=False,
        default="(no name)"
    )
    description = db.Column(
        db.String(300),
        nullable=True
    )
    growing_area = db.Column(
        db.Integer,
        db.ForeignKey('growing_areas.id', ondelete="cascade"),
        nullable=True
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        nullable=False
    )
    plants = db.relationship('Plant', secondary="plant_list_plants", backref="plant_lists")
    user = db.relationship('User', backref="plant_lists")

class PlantList_Plants(db.Model):
    __tablename__="plant_list_plants"
    
    plant_list_id = db.Column(
        db.Integer,
        db.ForeignKey('plant_lists.id', ondelete="cascade"),
        primary_key = True
    )
    plant_id = db.Column(
        db.Integer,
        db.ForeignKey('plants.id', ondelete="cascade"),
        primary_key = True
    )


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


####################################################

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)

