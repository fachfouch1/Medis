from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum
import bcrypt 
from config import *
from reportlab.platypus import Flowable
from reportlab.lib.colors import blue

app = Flask(__name__)
app.secret_key = "fachfouch"
userpass = 'mysql+pymysql://root:@'
basedir = "127.0.0.1"
dbname = "/medis"

app.config["SQLALCHEMY_DATABASE_URI"] = userpass+basedir+dbname
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)






# Molecule Module which will contain pubchem results



class Molecule(db.Model):
    __tablename__ = 'molecule'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    keyword = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date_of_creation = db.Column(db.DateTime, nullable=False)

class Pubchem(db.Model):
    __tablename__ = 'pubchem'
    id_pubchem = db.Column(db.Integer, primary_key=True)
    compoundname = db.Column(db.String(100), nullable=False)
    pubchem_cid = db.Column(db.String(100), nullable=False)
    molecular_form = db.Column(db.String(100), nullable=False)
    molecular_weight = db.Column(db.String(100), nullable=False)
    cas_reg = db.Column(db.String(100), nullable=False)
    atc_code = db.Column(db.String(1000), nullable=False)
    iupac_name = db.Column(db.String(100), nullable=False)
    solubility = db.Column(db.String(100), nullable=False)
    physical_desc = db.Column(db.String(10000), nullable=False)
    melting_point = db.Column(db.String(100), nullable=False)
    decomposition = db.Column(db.String(10000), nullable=False)
    half_life = db.Column(db.String(10000), nullable=False)
    reactivity = db.Column(db.String(10000), nullable=False)
    molecule_id = db.Column(db.Integer, db.ForeignKey('molecule.id'))
    image_url = db.Column(db.String(1000))



    def __init__(self,compoundname, pubchem_cid, molecular_form, molecular_weight, cas_reg, atc_code, iupac_name, solubility, physical_desc, melting_point, decomposition, half_life, reactivity,molecule_id,image_url):
        self.compoundname = compoundname
        self.pubchem_cid = pubchem_cid
        self.molecular_form = molecular_form
        self.molecular_weight = molecular_weight
        self.cas_reg = cas_reg
        self.atc_code = atc_code
        self.iupac_name = iupac_name
        self.solubility = solubility
        self.physical_desc = physical_desc
        self.melting_point = melting_point
        self.decomposition = decomposition
        self.half_life = half_life
        self.reactivity = reactivity
        self.molecule_id = molecule_id
        self.image_url = image_url

        

class Pubmed(db.Model):
    __tablename__ = 'pubmed'
    id_pubmed = db.Column(db.Integer, primary_key=True)
    Pharmacodynamics = db.Column(db.String(1000000), nullable=False)
    Pharmacodynamics_Drug_Interaction_page = db.Column(db.String(10000), nullable=False)
    Overview_of_Efficacy = db.Column(db.String(10000), nullable=False)
    Clinical_Studies = db.Column(db.String(10000), nullable=False)
    Overview_of_Safety = db.Column(db.String(10000), nullable=False)
    Marketing_Experience = db.Column(db.String(10000), nullable=False)
    Benefits_Risks = db.Column(db.String(10000), nullable=False)
    molecule_id = db.Column(db.Integer, db.ForeignKey('molecule.id'))

    def __init__(self,Pharmacodynamics, Pharmacodynamics_Drug_Interaction_page, Overview_of_Efficacy, Clinical_Studies, Overview_of_Safety, Marketing_Experience, Benefits_Risks,molecule_id):
        self.Pharmacodynamics = Pharmacodynamics
        self.Pharmacodynamics_Drug_Interaction_page = Pharmacodynamics_Drug_Interaction_page
        self.Overview_of_Efficacy = Overview_of_Efficacy
        self.Clinical_Studies = Clinical_Studies
        self.Overview_of_Safety = Overview_of_Safety
        self.Marketing_Experience = Marketing_Experience
        self.Benefits_Risks = Benefits_Risks
        self.molecule_id = molecule_id




# Define an enumeration for user roles
class Role(Enum):
    ADMIN = "ADMIN"
    MEDICAL_DEPARTMENT = "MEDICAL_DEPARTMENT"

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(SQLAlchemyEnum(Role), nullable=False)
    status = db.Column(db.Boolean, nullable=False, default=False) 
    phone_number = db.Column(db.String(8)) 
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200)) 


    def __init__(self, username, password,email, role, status = False ,phone_number=None, first_name=None, last_name=None, address=None):
        self.username = username
        self.email = email
        self.password = self._hash_password(password)  # Hash the password
        self.role = role
        self.status = status
        self.phone_number = phone_number
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        
        print("User Role:", self.role)



    def _hash_password(self, password):
        # Generate a salt
        salt = bcrypt.gensalt()
        # Hash the password with the salt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')  # Ensure the hashed password is a string
    

class Hyperlink(Flowable):
    """A custom flowable to include clickable hyperlinks in a ReportLab PDF."""
    def __init__(self, url, text, fontsize=12, textcolor=blue):
        Flowable.__init__(self)
        self.url = url
        self.text = text
        self.fontsize = fontsize
        self.textcolor = textcolor

    def draw(self):
        """Draw the flowable onto the canvas."""
        self.canv.setFont("Helvetica", self.fontsize)
        self.canv.setFillColor(self.textcolor)
        self.canv.drawString(0, 0, self.text)
        self.canv.linkURL(self.url, (0, -4, self.canv.stringWidth(self.text, "Helvetica", self.fontsize), self.fontsize + 3), relative=1)