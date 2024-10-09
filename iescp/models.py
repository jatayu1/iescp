from iescp import db, login_manager
from iescp import bcrypt
from flask_login import UserMixin
from sqlalchemy import DateTime, CheckConstraint, Date

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(length=30), nullable=False)
    username = db.Column(db.String(length=30), unique=True, nullable=False)
    email = db.Column(db.String(length=50), nullable=False)
    profilePicture = db.Column(db.String(length=50), nullable=True, default='default-profile-pic.jpg')
    password_hash = db.Column(db.String(length=60), nullable=False)
    user_type = db.Column(db.Integer, nullable=False)
    registration_date = db.Column(db.Date, nullable=False)
    flagged = db.Column(db.Integer, default=0)
    

    __table_args__ = (
        CheckConstraint('user_type IN (0, 1, 2)', name='check_user_type'),
        CheckConstraint('flagged IN (0, 1)', name='check_flagged_user')
    )

    influencer = db.relationship('Influencer', backref='user', uselist=False, cascade='all, delete-orphan')
    sponsor = db.relationship('Sponsors', backref='user', uselist=False, cascade='all, delete-orphan')

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, normal_password):
        self.password_hash = bcrypt.generate_password_hash(normal_password).decode('utf-8')

    def passwordCheck(self, givenPassword):
        return bcrypt.check_password_hash(self.password_hash, givenPassword)

    def get_influencer_details(self):
        return Influencer.query.filter_by(user_id=self.id).first()

    def get_sponsors_details(self):
        return Sponsors.query.filter_by(user_id=self.id).first()

    def get_campaign(self):
        try:
            campaigns = Campaign.query.join(Sponsors, Campaign.created_by == Sponsors.user_id).filter(Sponsors.user_id == self.id).all()
            return campaigns
        except Exception as e:
            print(f"Error fetching campaigns: {e}")
            return []
    
    def get_active_campaign_for_sponsors(self):
        try:
            campaigns = Campaign.query.join(Sponsors, Campaign.created_by == Sponsors.user_id).filter(Sponsors.user_id == self.id).filter(Campaign.status == 1).all()
            return campaigns
        except Exception as e:
            print(f"Error fetching campaigns: {e}")
            return []
        
    def get_active_campaign_for_influencer(self):
        try:
            campaigns = Campaign.query.join(Influencer, Campaign.assigned_to == Influencer.user_id).filter(Influencer.user_id == self.id).filter(Campaign.status == 1).all()
            return campaigns
        except Exception as e:
            print(f"Error fetching campaigns: {e}")
            return []

    def get_recived_ad_request(self):
        return Ad_Request.query.filter_by(sent_to=self.id).all()

    def get_sent_ad_request(self):
        return Ad_Request.query.filter_by(sent_by=self.id).all()

class Influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(length=30), nullable=True)
    niche = db.Column(db.String(length=30), nullable=True)
    reach = db.Column(db.String(length=30), nullable=True)

    instagram_link = db.Column(db.String(length=100), nullable=True)
    instagram_followers = db.Column(db.Integer, nullable=True)

    facebook_link = db.Column(db.String(length=100), nullable=True)
    facebook_followers = db.Column(db.Integer, nullable=True)

    youtube_link = db.Column(db.String(length=100), nullable=True)
    youtube_followers = db.Column(db.Integer, nullable=True)

    X_link = db.Column(db.String(length=100), nullable=True)
    X_followers = db.Column(db.Integer, nullable=True)

    linkedin_link = db.Column(db.String(length=100), nullable=True)
    linkedin_followers = db.Column(db.Integer, nullable=True)

class Sponsors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    industry = db.Column(db.String(length=30), nullable=True)

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=30), nullable=False)
    description = db.Column(db.String(length=300), nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Integer, nullable=True)
    visibility = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    flagged = db.Column(db.Integer, default=0)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    creater = db.relationship('User', foreign_keys=[created_by], backref=db.backref('campaigns', lazy=True, cascade='all, delete-orphan'))
    assignee = db.relationship('User', foreign_keys=[assigned_to], backref=db.backref('assigned_campaigns', lazy=True))

    __table_args__ = (
        CheckConstraint('status IN (0, 1, 2)', name='check_status'),
        CheckConstraint('visibility IN (0, 1)', name='check_visibility'),
        CheckConstraint('flagged IN (0, 1)', name='check_flagged_campaign')
    )

class Ad_Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    sent_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sent_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    payment_amount = db.Column(db.Integer, nullable=True)
    flagged = db.Column(db.Integer, default=0)

    campaign = db.relationship('Campaign', backref=db.backref('ad_requests', lazy=True, cascade='all, delete-orphan'))
    sent_to_user = db.relationship('User', foreign_keys=[sent_to], backref=db.backref('received_ad_requests', lazy=True, cascade='all, delete-orphan'))
    sent_by_user = db.relationship('User', foreign_keys=[sent_by], backref=db.backref('sent_ad_requests', lazy=True, cascade='all, delete-orphan'))

    __table_args__ = (
        CheckConstraint('flagged IN (0, 1)', name='check_flagged_ad_request'),
    )
