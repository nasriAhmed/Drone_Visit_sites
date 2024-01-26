#models.py#
from flask_sqlalchemy import SQLAlchemy

# création de l'instance SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    # Configuration de la base de données
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:admin@localhost:5432/drone_database"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialisation de l'extension SQLAlchemy
    db.init_app(app)
#création de class Batch
class Batch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    firmware = db.Column(db.String(255), nullable=False)
    compatible_hardware = db.Column(db.ARRAY(db.String), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def initiate_firmware_update(self, new_firmware_version):
        self.firmware = new_firmware_version        

#création de class Firmware
class Firmware(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    compatible_hardware = db.Column(db.ARRAY(db.String), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
#création de class Content
class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    mandatory = db.Column(db.Boolean, default=False)
    min_version = db.Column(db.String(255), nullable=True)
    max_version = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    #firware_relationship_firmware_id
    firmware_id = db.Column(db.Integer, db.ForeignKey('firmware.id'), nullable=True)
    firmware = db.relationship('Firmware', backref=db.backref('contents', lazy=True))
#création de classe Appraisor
class Appraisor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(255), nullable=False)
    mac = db.Column(db.String(17), nullable=False, unique=True)
    last_connection = db.Column(db.DateTime, nullable=True)
    installed_firmware = db.Column(db.String(255), nullable=False)
    hardware = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    #batch_relationship_firmware_id
    batch_id = db.Column(db.Integer, db.ForeignKey('batch.id'), nullable=True)
    batch = db.relationship('Batch', backref=db.backref('appraisors', lazy=True))
    contents = db.relationship('Content', secondary='appraisor_content')

    def install_firmware(self, version):
        self.installed_firmware = version  
    def add_additional_content(self, content):
        if content not in self.contents:
            self.contents.append(content)
    def remove_additional_content(self, content):
        if content in self.contents:
            self.contents.remove(content)
# création la relation many-to-many entre Appraisor et Content
appraisor_content = db.Table('appraisor_content',
    db.Column('appraisor_id', db.Integer, db.ForeignKey('appraisor.id'), primary_key=True),
    db.Column('content_id', db.Integer, db.ForeignKey('content.id'), primary_key=True))