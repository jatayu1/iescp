from iescp import app, db
from flask import render_template, redirect, url_for, flash, Response, request
from flask_login import login_user, logout_user, login_required, current_user
from iescp.models import User, Influencer, Sponsors, Campaign, Ad_Request
from iescp.forms import LoginForm, RegisterForm, CampaignForm, AdRequest, UpdateInfluencerProfile, UpdateSponsorsProfile, Negotiate, searchForm, SearchCampaignForm, SearchAdRequestForm
from werkzeug.utils import secure_filename
import uuid as uuid
import os
from sqlalchemy import or_
from datetime import datetime
from calendar import monthrange
from collections import defaultdict

@app.route("/")
@login_required
def home_page():
    if (current_user.user_type == 0) :
        # numarical data
        user_count  = User.query.count()
        influencer_count  = Influencer.query.count()
        sponsors_count  = Sponsors.query.count()
        admin_count  = User.query.filter_by(user_type = 0).count()
        campaign_count  = Campaign.query.count()
        ad_request_count  = Ad_Request.query.count()
        total_transaction = sum(campaign.budget or 0 for campaign in db.session.query(Campaign).all())

        flagged_influencers = Influencer.query.join(User).filter(User.flagged == 1).all()
        flagged_sponsors = Sponsors.query.join(User).filter(User.flagged == 1).all()
        flagged_campaigns = Campaign.query.filter_by(flagged = 1).all()
        flagged_ad_requests = Ad_Request.query.filter_by(flagged = 1).all()
        # I/S Split
        # data = [influencer_count, sponsors_count]

        today = datetime.today()
        all_users = User.query.all()
        registered_this_month = defaultdict(int)

        for users in all_users:
            if users.registration_date.month == today.month and users.registration_date.year == today.year:
                registered_this_month[users.registration_date.day] += 1

        # Prepare data for the month
        days_in_month = monthrange(today.year, today.month)[1]
        month_labels = list(range(1, days_in_month + 1))
        month_data = [registered_this_month[day] for day in month_labels]

        return render_template(
            'dashboard.html', 
            user_count=user_count, 
            influencer_count=influencer_count ,
            sponsors_count=sponsors_count,
            admin_count=admin_count,
            campaign_count=campaign_count,
            ad_request_count=ad_request_count,
            total_transaction=total_transaction,
            flagged_influencers=flagged_influencers,
            flagged_sponsors=flagged_sponsors,
            flagged_campaigns=flagged_campaigns,
            flagged_ad_requests=flagged_ad_requests,
            month_labels=month_labels,
            month_data=month_data
        )
    elif (current_user.user_type == 1) :
        influencer = current_user.influencer
        reach = (influencer.instagram_followers or 0) + (influencer.facebook_followers or 0) + (influencer.youtube_followers or 0) + (influencer.X_followers or 0) + (influencer.linkedin_followers or 0)
        return render_template('dashboard.html', reach=reach)
    elif (current_user.user_type == 2) :
        return render_template('dashboard.html')

@app.route("/profile")
@login_required
def profile():
    user_id = request.args.get('user')
    user = User.query.filter_by(id = user_id).first()
    if (user.user_type == 1) :
        influencer = user.influencer
        reach = (influencer.instagram_followers or 0) + (influencer.facebook_followers or 0) + (influencer.youtube_followers or 0) + (influencer.X_followers or 0) + (influencer.linkedin_followers or 0)
        return render_template('profile.html', user=user, reach=reach)
    else:
        return render_template('profile.html', user=user)

@app.route("/flag_profile")
@login_required
def flag_profile():
    user_id = request.args.get('user')
    user = User.query.filter_by(id = user_id).first()
    user.flagged = int(1)
    db.session.add(user)
    db.session.commit()
    flash("User Flagged Inappropriate", category="success")
    return redirect(request.referrer)

@app.route("/unflag_profile")
@login_required
def unflag_profile():
    user_id = request.args.get('user')
    user = User.query.filter_by(id = user_id).first()
    user.flagged = int(0)
    db.session.add(user)
    db.session.commit()
    flash("Inappropriate Flag Removed", category="success")
    return redirect(request.referrer)

@app.route("/flag_campaign")
@login_required
def flag_campaign():
    campaign_id = request.args.get('campaign')
    campaign = Campaign.query.filter_by(id = campaign_id).first()
    campaign.flagged = int(1)
    db.session.add(campaign)
    db.session.commit()
    flash("Campaign Flagged Inappropriate", category="success")
    return redirect(request.referrer)

@app.route("/unflag_campaign")
@login_required
def unflag_campaign():
    campaign_id = request.args.get('campaign')
    campaign = Campaign.query.filter_by(id = campaign_id).first()
    campaign.flagged = int(0)
    db.session.add(campaign)
    db.session.commit()
    flash("Inappropriate Campaign Flag Removed", category="success")
    return redirect(request.referrer)

@app.route("/flag_requests")
@login_required
def flag_requests():
    req_id = request.args.get('request')  # Rename variable to avoid conflict
    ad_request = Ad_Request.query.filter_by(id=req_id).first()
    if ad_request:
        ad_request.flagged = 1
        db.session.add(ad_request)
        db.session.commit()
        flash("Ad Request Flagged Inappropriate", category="success")
    else:
        flash("Ad Request not found", category="error")
    return redirect(request.referrer)

@app.route("/unflag_requests")
@login_required
def unflag_requests():
    req_id = request.args.get('request')
    ad_request = Ad_Request.query.filter_by(id=req_id).first()
    if ad_request:
        ad_request.flagged = int(0)
        db.session.add(ad_request)
        db.session.commit()
        flash("Inappropriate Ad Request Flag Removed", category="success")
    else:
        flash("Ad Request not found", category="error")
    return redirect(request.referrer)

@app.route('/update_influencer_user', methods=['GET','POST'])
@login_required
def update_influencer_user():
    form = UpdateInfluencerProfile()
    if form.validate_on_submit():
        user = User.query.filter_by(username = current_user.username).first()
        profile_pic = form.profile_picture.data
        if profile_pic:
            pic_filename = secure_filename(profile_pic.filename)
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            user.profilePicture = pic_name
        user.fullname = form.fullname.data
        user.email = form.email.data
        user.influencer.category = form.category.data
        user.influencer.niche = form.niche.data

        user.influencer.instagram_link = form.ig_link.data
        user.influencer.instagram_followers = form.ig_follower.data
        user.influencer.facebook_link = form.fb_link.data
        user.influencer.facebook_followers = form.fb_follower.data
        user.influencer.youtube_link = form.yt_link.data
        user.influencer.youtube_followers = form.yt_follower.data
        user.influencer.X_link = form.x_link.data
        user.influencer.X_followers = form.x_follower.data
        user.influencer.linkedin_link = form.lin_link.data
        user.influencer.linkedin_followers = form.lin_follower.data

        db.session.add(user)
        db.session.commit()
        flash("Account Updated.", category="success")
        return redirect(url_for('home_page'))
    else:
        print("Form did not validate. Errors:")
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                print(f"Error in {fieldName}: {err}")
    return render_template('update_influencer_user.html', form = form)

@app.route('/update_sponsors_user', methods=['GET','POST'])
@login_required
def update_sponsors_user():
    form = UpdateSponsorsProfile()
    if form.validate_on_submit():
        user = User.query.filter_by(username = current_user.username).first()
        profile_pic = form.profile_picture.data
        if profile_pic:
            pic_filename = secure_filename(profile_pic.filename)
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            user.profilePicture = pic_name
        user.fullname = form.fullname.data
        user.email = form.email.data
        user.sponsor.industry = form.industry.data

        db.session.add(user)
        db.session.commit()
        flash("Account Updated.", category="success")
        return redirect(url_for('home_page'))
    else:
        print("Form did not validate. Errors:")
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                print(f"Error in {fieldName}: {err}")
    return render_template('update_sponsors_user.html', form = form)

@app.route('/delete_profile', methods=['GET','POST'])
@login_required
def delete_profile():
    user = User.query.filter_by(username = current_user.username).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        logout_user()
        flash("User Deleted.", category="danger")
    else:
        flash("User not found.", category="danger")
    return redirect(request.referrer)

@app.route('/admin_delete_profile', methods=['GET','POST'])
@login_required
def admin_delete_profile():
    user_id = request.args.get('user')
    user = User.query.filter_by(id = user_id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted.", category="success")
    else:
        flash("User not found.", category="danger")
    return redirect(request.referrer)

@app.route("/campaign", methods=['GET','POST'])
@login_required
def campaign_page():
    form = CampaignForm()
    if form.validate_on_submit():
        try:
            # Get the sponsor details of the current user
            sponsor_details = current_user.get_sponsors_details()
            if not sponsor_details:
                flash("You are not a sponsor.", category="danger")
                return redirect(url_for('home_page'))
            
            new_campaign = Campaign(
                name=form.name.data,
                description=form.description.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                visibility=int(form.visibility.data),
                status=0,
                created_by=current_user.id
            )
            db.session.add(new_campaign)
            db.session.commit()

            flash("New Campaign Added", category="success")
            return redirect(url_for('campaign_page'))
        except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {e}", category="danger")
    else:
        if form.errors != {}:
            for err_msg in form.errors.values():
                flash(f'There was an error with creating a user: {err_msg}', category='danger')
    return render_template('campaign.html', form=form)

@app.route("/view_campaign")
@login_required
def view_campaign():
    campaign_id = request.args.get('campaign')
    campaign = Campaign.query.filter_by(id = campaign_id).first()
    return render_template('view_campaign.html', campaign=campaign)

@app.route("/edit_campaign", methods=['GET','POST'])
@login_required
def edit_campaign_page():
    campaign_id = request.args.get('campaign')
    campaign = Campaign.query.filter_by(id = campaign_id).first()
    form = CampaignForm(visibility=campaign.visibility)
    if form.validate_on_submit():
        try:
            campaign = Campaign.query.filter_by(id = campaign_id).first()

            campaign.name = form.name.data
            campaign.description=form.description.data
            campaign.start_date = form.start_date.data
            campaign.end_date = form.end_date.data
            campaign.visibility = int(form.visibility.data)

            db.session.add(campaign)
            db.session.commit()

            flash("Campaign Updated", category="success")
            return redirect(url_for('home_page'))
        except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {e}", category="danger")
    else:
        if form.errors != {}:
            for err_msg in form.errors.values():
                flash(f'There was an error with creating a user: {err_msg}', category='danger')
    
    return render_template('edit_campaign.html', form=form, campaign=campaign)

@app.route('/delete_campaign', methods=['GET','POST'])
@login_required
def delete_campaign():
    campaign_id = request.args.get('campaign')
    campaign = Campaign.query.filter_by(id = campaign_id).first()
    if campaign:
        if (campaign.created_by == current_user.id or current_user.user_type == 0 ) :
            db.session.delete(campaign)
            db.session.commit()
            flash("campaign deleted.", category="success")
        else:
            flash("You can't delete this campaign deleted.", category="danger")
    else:
        flash("Campaign not found.", category="danger")
    return redirect(request.referrer)

@app.route('/mark_complete_campaign', methods=['GET','POST'])
@login_required
def mark_complete_campaign():
    campaign_id = request.args.get('campaign')
    campaign = Campaign.query.filter_by(id = campaign_id).first()
    if campaign:
        if (campaign.created_by == current_user.id ) :
            campaign.status = int(2)
            db.session.add(campaign)
            db.session.commit()
            flash("campaign Completed.", category="success")
        else:
            flash("You can't mark this campaign complete.", category="danger")
    else:
        flash("Campaign not found.", category="danger")
    return redirect(url_for('home_page'))

@app.route('/accept_req', methods=['GET','POST'])
@login_required
def accept_req():
    adreq_id = request.args.get('adreq')
    adreq = Ad_Request.query.filter_by(id = adreq_id).first()
    campaign = Campaign.query.filter_by(id = adreq.campaign_id).first()
    campaign.status = int(1)
    if (adreq.sent_to_user.user_type == 1) :
        campaign.assigned_to = int(adreq.sent_to)
    else:
        campaign.assigned_to = int(adreq.sent_by)
    campaign.budget = adreq.payment_amount
    db.session.add(campaign)
    db.session.delete(adreq)
    db.session.commit()

    return redirect(url_for('home_page'))

@app.route('/del_req', methods=['GET','POST'])
@login_required
def del_req():
    req_id = request.args.get('req')
    req = Ad_Request.query.filter_by(id = req_id).first()
    if req:
        if (req.sent_to == current_user.id or req.sent_by == current_user.id or current_user.user_type == 0) :
            db.session.delete(req)
            db.session.commit()
            flash("Ad Request Deleted.", category="success")
        else:
            flash("You can't delete this campaign deleted.", category="danger")
    else:
        flash("Ad Request not found.", category="danger")
    return redirect(request.referrer)

@app.route("/send-add-request/", methods=['GET','POST'])
@login_required
def send_ad_request_page():
    form = AdRequest()
    campaign_id = request.args.get('campaign')
    campaign_status = Campaign.query.filter_by(id = campaign_id).first().status
    if (campaign_status == 0) :
        # Fetch all influencers from the database
        influencers = Influencer.query.all()
        
        # Create a list of tuples (id, 'profilepicture fullname - username')
        influencer_choices = [
            (
                influencer.user.id, 
                f"{influencer.user.fullname} ({influencer.user.username})",
            ) 
            for influencer in influencers
        ]
        # Set the choices for the SelectField
        form.send_to.choices = influencer_choices

        if form.validate_on_submit():
            try:
                if (Ad_Request.query.filter_by(campaign_id = form.campaign_id.data).filter_by(sent_to = form.send_to.data).first()):
                    flash("Can't send multiple Request to Same User for Same campaign", category="danger")
                    return redirect(url_for('home_page'))
                else:
                    new_ad_request = Ad_Request(
                        campaign_id=form.campaign_id.data,
                        sent_to=form.send_to.data,
                        sent_by=form.sent_by.data,
                        payment_amount=form.payment.data,
                    )
                    db.session.add(new_ad_request)
                    db.session.commit()

                    flash("Ad Request Sent", category="success")
                    return redirect(url_for('home_page'))
                
            except Exception as e:
                    db.session.rollback()
                    flash(f"An error occurred: {e}", category="danger")
        
        return render_template('send-ad-request.html', campaign_id=campaign_id, form=form)
    else:
        flash("This campaign is either in-progress or closer ", category="danger")
        return redirect(url_for('home_page'))

@app.route("/negotiate", methods=['GET','POST'])
@login_required
def negotiate():
    adreq_id = request.args.get('adreq')
    adreq = Ad_Request.query.filter_by(id = adreq_id).first()
    form = Negotiate()

    if form.validate_on_submit():
        try:
            db.session.delete(adreq)
            new_ad_request = Ad_Request(
                campaign_id=form.campaign_id.data,
                sent_to=form.send_to.data,
                sent_by=form.sent_by.data,
                payment_amount=form.payment.data,
            )
            db.session.add(new_ad_request)
            db.session.commit()

            flash("Ad Request Sent", category="success")
            return redirect(url_for('home_page'))
        except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {e}", category="danger")

    return render_template('negotiate.html', form=form, adreq=adreq)

@app.route("/influencer_send_request", methods=['GET','POST'])
@login_required
def influencer_send_request():
    form = Negotiate()
    campaign_id = request.args.get('camp')
    campaign = Campaign.query.filter_by(id = campaign_id).filter_by(visibility = 0).first()

    camp_req = Ad_Request.query.filter(
        Ad_Request.campaign_id == campaign_id,
        or_(
            Ad_Request.sent_to == current_user.id,
            Ad_Request.sent_by == current_user.id
        )
    ).all()

    if (camp_req):
        flash("You have already recived or sent ad request for campaign", category="danger")
        return redirect(request.referrer)
    else:
        if form.validate_on_submit():
            if (current_user.user_type == 1 and campaign):
                try:
                    if (Ad_Request.query.filter_by(campaign_id = campaign_id).filter_by(sent_by = current_user.id).first()):
                            flash("Can't send multiple Request to Same User for Same campaign", category="danger")
                            return redirect(url_for('home_page'))
                    new_ad_request = Ad_Request(
                        campaign_id=campaign_id,
                        sent_to=campaign.created_by,
                        sent_by=current_user.id,
                        payment_amount=form.payment.data,
                    )
                    db.session.add(new_ad_request)
                    db.session.commit()

                    flash("Ad Request Sent", category="success")
                    return redirect(url_for('home_page'))
                except Exception as e:
                        db.session.rollback()
                        flash(f"An error occurred: {e}", category="danger")
            else:
                flash("You can't send ad request to this campaign", category="danger")

        return render_template('influencer_send_request.html', form=form, campaign=campaign)

@app.route("/find_sponsors", methods=['GET','POST'])
@login_required
def find_sponsors():
    form = searchForm()
    search_by = [
            (
                1, 
                "All",
            ),
            (
                2, 
                "Name",
            ),
            (
                3, 
                "Username",
            ),
            (
                4, 
                "Email",
            ),
            (
                5, 
                "Industry",
            )
        ]
    # Set the choices for the SelectField
    form.search_by.choices = search_by
    
    if form.validate_on_submit():
        search_term = f"%{form.search.data}%"
        if (form.search_by.data == 1):
            filtered_sponsors = (Sponsors.query
                    .join(Sponsors.user)
                    .filter(or_(User.username.like(search_term), User.fullname.like(search_term), User.email.like(search_term), Sponsors.industry.like(search_term)))
                    .order_by(User.username)
                    .all())
        elif (form.search_by.data == 2):
            filtered_sponsors = (Sponsors.query
                    .join(Sponsors.user)
                    .filter(User.fullname.like(search_term))
                    .order_by(User.fullname)
                    .all())
        elif (form.search_by.data == 3):
            filtered_sponsors = (Sponsors.query
                    .join(Sponsors.user)
                    .filter(User.username.like(search_term))
                    .order_by(User.username)
                    .all())
        elif (form.search_by.data == 4):
            filtered_sponsors = (Sponsors.query
                    .join(Sponsors.user)
                    .filter(User.email.like(search_term))
                    .order_by(User.email)
                    .all())
        elif (form.search_by.data == 5):
            filtered_sponsors = (Sponsors.query
                    .join(Sponsors.user)
                    .filter(Sponsors.industry.like(search_term))
                    .order_by(Sponsors.industry)
                    .all())

        return render_template('find_sponsors.html', form=form, filtered_sponsors = filtered_sponsors)
    all_sponsors = Sponsors.query.all()
    return render_template('find_sponsors.html', form=form, all_sponsors=all_sponsors)

@app.route("/find_influencer", methods=['GET','POST'])
@login_required
def find_influencer():
    form = searchForm()
    search_by = [
            (
                1, 
                "All",
            ),
            (
                2, 
                "Name",
            ),
            (
                3, 
                "Username",
            ),
            (
                4, 
                "Email",
            ),
            (
                5, 
                "category",
            ),
            (
                6, 
                "niche",
            )
        ]
    # Set the choices for the SelectField
    form.search_by.choices = search_by
    
    if form.validate_on_submit():
        search_term = f"%{form.search.data}%"
        if (form.search_by.data == 1):
            filtered_influencers = (Influencer.query
                    .join(Influencer.user)
                    .filter(or_(User.username.like(search_term), User.fullname.like(search_term), User.email.like(search_term), Influencer.category.like(search_term), Influencer.niche.like(search_term)))
                    .order_by(User.username)
                    .all())
        elif (form.search_by.data == 2):
            filtered_influencers = (Influencer.query
                    .join(Influencer.user)
                    .filter(User.fullname.like(search_term))
                    .order_by(User.fullname)
                    .all())
        elif (form.search_by.data == 3):
            filtered_influencers = (Influencer.query
                    .join(Influencer.user)
                    .filter(User.username.like(search_term))
                    .order_by(User.username)
                    .all())
        elif (form.search_by.data == 4):
            filtered_influencers = (Influencer.query
                    .join(Influencer.user)
                    .filter(User.email.like(search_term))
                    .order_by(User.email)
                    .all())
        elif (form.search_by.data == 5):
            filtered_influencers = (Influencer.query
                    .join(Influencer.user)
                    .filter(Influencer.category.like(search_term))
                    .order_by(Influencer.category)
                    .all())
        elif (form.search_by.data == 6):
            filtered_influencers = (Influencer.query
                    .join(Influencer.user)
                    .filter(Influencer.niche.like(search_term))
                    .order_by(Influencer.niche)
                    .all())

        return render_template('find_influencer.html', form=form, filtered_influencers = filtered_influencers)
    all_influencers = Influencer.query.all()
    return render_template('find_influencer.html', form=form, all_influencers=all_influencers)

@app.route("/find_campaign", methods=['GET','POST'])
@login_required
def find_campaign():
    form = SearchCampaignForm()
    if (current_user.user_type == 0) :
        all_Campaign = Campaign.query.all()
    else:
        all_Campaign = Campaign.query.filter_by(visibility = 0).all()
    sponsors = Sponsors.query.all()
        
    # Create a list of tuples (id, 'profilepicture fullname - username')
    sponsors_choices = [
        (0, "All"),
        *[
            (
                sponsor.user.id, 
                f"{sponsor.user.fullname} ({sponsor.user.username})"
            )
            for sponsor in sponsors
        ]
    ]
    # Set the choices for the SelectField
    form.creator.choices = sponsors_choices
        
    if form.validate_on_submit():
        search_term = f"%{form.search.data}%"

        # Start with the base query
        filtered_campaigns = Campaign.query.filter(Campaign.name.like(search_term)).filter(Campaign.visibility == 0)

        # Filter by creator
        if form.creator.data and form.creator.data != 0:
            filtered_campaigns = filtered_campaigns.filter(Campaign.created_by == form.creator.data)
        
        # Filter by status
        if form.status.data:
            filtered_campaigns = filtered_campaigns.filter(Campaign.status.in_(form.status.data))
        
        # Filter by start date if provided
        if form.start_date.data:
            filtered_campaigns = filtered_campaigns.filter(Campaign.start_date == form.start_date.data)
        
        # Filter by end date if provided
        if form.end_date.data:
            filtered_campaigns = filtered_campaigns.filter(Campaign.end_date == form.end_date.data)
        
        # Execute the query
        filtered_campaigns = filtered_campaigns.all()

        return render_template('find_campaign.html', form=form, filtered_campaigns=filtered_campaigns)
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error : {err_msg}',category='danger')

    return render_template('find_campaign.html', form=form, all_campaigns=all_Campaign)

@app.route("/find_ad_request", methods=['GET','POST'])
@login_required
def find_ad_request():
    form = SearchAdRequestForm()
    users = User.query.filter(or_(User.user_type == 1, User.user_type == 2)).all()
    # Create a list of tuples (id, 'profilepicture fullname - username')
    users_choices = [
        (0, "All"),
        *[
            (
                user.id, 
                f"{user.fullname} ({user.username})"
            )
            for user in users
        ]
    ]
    # Set the choices for the SelectField
    form.sender.choices = users_choices
    form.reciver.choices = users_choices

    campaigns = Campaign.query.all()

    requests = Ad_Request.query.all()

    campaign_choices = [
        (0, "All"),
        *[
            (
                campaign.id, 
                campaign.name
            )
            for campaign in campaigns
        ]
    ]

    form.campaign.choices = campaign_choices

    if form.validate_on_submit():
        # Start with the base query
        requests = Ad_Request.query

        # Filter by sender
        if form.sender.data:
            requests = requests.filter(Ad_Request.sent_to == form.sender.data)
        
        # Filter by reciver
        if form.reciver.data:
            requests = requests.filter(Ad_Request.sent_by == form.reciver.data)
        
        # Filter by campaign
        if form.campaign.data:
            requests = requests.filter(Ad_Request.campaign_id == form.campaign.data)
                
        # Execute the query
        requests = requests.all()

        return render_template('find_ad_request.html', form=form, requests=requests)
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error : {err_msg}',category='danger')

    return render_template('find_ad_request.html', form=form, requests=requests)

@app.route("/stats", methods=['GET','POST'])
@login_required
def stats():
    if (current_user.user_type == 0):
        pass
    elif (current_user.user_type == 1):
        # total earning
        total_earning = sum(campaign.budget if campaign.budget is not None else 0 for campaign in current_user.assigned_campaigns)

        # Define Plot Data 
        sorted_campaigns = sorted(current_user.assigned_campaigns, key=lambda campaign: campaign.budget or 0, reverse=True)

        # Get only the top 10 highest budget campaigns
        top_campaigns = sorted_campaigns[:10]

        # earn. vs camp.
        labels = [campaign.name for campaign in top_campaigns]
        data = [campaign.budget if campaign.budget is not None else 0 for campaign in top_campaigns]

        ernvscamp = "Earning V/S Campaigns"
        # campain completed this week
        today = datetime.today()
        completed_this_month = defaultdict(int)
        completed_this_year = defaultdict(int)

        for campaign in current_user.assigned_campaigns:
            if campaign.status == 2:  # Assuming status == 2 means the campaign is closed
                if campaign.end_date.month == today.month and campaign.end_date.year == today.year:
                    completed_this_month[campaign.end_date.day] += 1
                if campaign.end_date.year == today.year:
                    completed_this_year[campaign.end_date.strftime('%B')] += 1

        # Prepare data for the month
        days_in_month = monthrange(today.year, today.month)[1]
        month_labels = list(range(1, days_in_month + 1))
        month_data = [completed_this_month[day] for day in month_labels]

        # Prepare data for the year
        year_labels = [datetime(2023, i, 1).strftime('%B') for i in range(1, 13)]
        year_data = [completed_this_year[month] for month in year_labels]

        return render_template(
            'stats.html', 
            total_earning=total_earning, 
            labels=labels, 
            data=data,
            ernvscamp=ernvscamp,
            month_labels=month_labels, 
            month_data=month_data,
            year_labels=year_labels, 
            year_data=year_data
        )
    elif (current_user.user_type == 2):
        # total expenditure
        total_expenditure = sum(campaign.budget if campaign.budget is not None else 0 for campaign in current_user.campaigns)

        # Define Plot Data 
        sorted_campaigns = sorted(current_user.campaigns, key=lambda campaign: campaign.budget or 0, reverse=True)

        # Get only the top 10 highest budget campaigns
        top_campaigns = sorted_campaigns[:10]

        # earn. vs camp.
        labels = [campaign.name for campaign in top_campaigns]
        data = [campaign.budget if campaign.budget is not None else 0 for campaign in top_campaigns]

        ernvscamp = "Expenditure V/S Campaigns"

        # campain completed this week
        today = datetime.today()
        completed_this_month = defaultdict(int)
        completed_this_year = defaultdict(int)

        for campaign in current_user.campaigns:
            if campaign.status == 2:  # Assuming status == 2 means the campaign is closed
                if campaign.end_date.month == today.month and campaign.end_date.year == today.year:
                    completed_this_month[campaign.end_date.day] += 1
                if campaign.end_date.year == today.year:
                    completed_this_year[campaign.end_date.strftime('%B')] += 1

        # Prepare data for the month
        days_in_month = monthrange(today.year, today.month)[1]
        month_labels = list(range(1, days_in_month + 1))
        month_data = [completed_this_month[day] for day in month_labels]

        # Prepare data for the year
        year_labels = [datetime(2023, i, 1).strftime('%B') for i in range(1, 13)]
        year_data = [completed_this_year[month] for month in year_labels]

        return render_template(
            'stats.html', 
            total_expenditure=total_expenditure, 
            labels=labels, 
            data=data, 
            ernvscamp=ernvscamp,
            month_labels=month_labels, 
            month_data=month_data,
            year_labels=year_labels, 
            year_data=year_data
        )

@app.route("/login", methods=['GET', 'POST'])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))

    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.passwordCheck(givenPassword = form.password.data):
            login_user(attempted_user)
            return redirect(url_for('home_page'))
        else:
            flash("Username or Password is wrong", category="danger")
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error : {err_msg}',category='danger')
    return render_template('login.html', form = form)

@app.route("/registration", methods=['GET', 'POST'])
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))

    form = RegisterForm()
    
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = db.session.query(User).filter(
            (User.username == form.username.data) | (User.email == form.email.data)
        ).first()
        
        if existing_user:
            if existing_user.username == form.username.data:
                flash("Username already exists", category="danger")
            if existing_user.email == form.email.data:
                flash("Email already exists", category="danger")
        else:
            try:
                profile_pic = form.profile_picture.data
                pic_name = ""
                if profile_pic:
                    pic_filename = secure_filename(profile_pic.filename)
                    pic_name = str(uuid.uuid1()) + "_" + pic_filename
                    profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                
                new_user = User(
                    username=form.username.data,
                    fullname=form.fullname.data,
                    email=form.email.data,
                    password=form.password1.data,
                    user_type=form.user_type.data,
                    profilePicture=pic_name,
                    registration_date=datetime.now().date()
                )
                db.session.add(new_user)
                db.session.flush()

                # Convert user_type to integer for comparison
                user_type = int(form.user_type.data)

                if user_type == 1:
                    new_influencer = Influencer(user_id=new_user.id)
                    db.session.add(new_influencer)
                    print(f"Created new influencer with user_id: {new_user.id}")
                elif user_type == 2:
                    new_sponsor = Sponsors(user_id=new_user.id)
                    db.session.add(new_sponsor)
                    print(f"Created new sponsor with user_id: {new_user.id}")
                else:
                    print(f"Unexpected user_type: {user_type} for user_id: {new_user.id}")
                
                db.session.commit()
                
                flash("Your account has been created, you may login now", category="success")
                return redirect(url_for('login_page'))
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {e}", category="danger")
    else:
        if form.errors != {}:
            for err_msg in form.errors.values():
                flash(f'There was an error with creating a user: {err_msg}', category='danger')
                
    return render_template('registration.html', form=form)

@app.route("/logout")
def logout_page():
    logout_user()
    flash("You have been Logged out", category='info')
    return redirect(url_for('login_page'))

