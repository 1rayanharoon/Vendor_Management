from apps import db
from apps.home import blueprint
from flask import render_template, request, redirect, url_for, flash,session, jsonify
from flask_login import login_required,logout_user
from functools import wraps
from jinja2 import TemplateNotFound
from apps.authentication.forms import VendorForm
from apps.authentication.models import Vendor
from werkzeug.utils import secure_filename
import os, csv
from flask import current_app
from apps.authentication.forms import ArticleForm, InspectorForm
from apps.authentication.models import Article, ArticleImage, Inspector
from sqlalchemy.exc import IntegrityError
from apps.authentication.forms import ClientForm
from apps.authentication.models import Client

def update_clients_csv():
    csv_path = os.path.join(current_app.root_path, 'static', 'clients', 'clients.csv')
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
    # Get all clients from the database
    clients = Client.query.all()
    
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Name'])  # Write header
        for client in clients:
            writer.writerow([client.name])


def check_account_type(*allowed_types):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if 'account_type' is in session and is one of the allowed types
            if 'account_type' in session and session['account_type'] in allowed_types:
                return f(*args, **kwargs)
            else:
                # Here, handle the case where the condition is not met
                # This could be a simple return statement or logging the event
                logout_user()
                return redirect(url_for('home_blueprint.index'))

        return decorated_function
    return decorator

def image_files(article_name):
    image_folder = os.path.join('apps', 'static', 'images', article_name)
    if os.path.exists(image_folder):
        return [f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]
    return []

@blueprint.route('/index')
@login_required
@check_account_type('Admin', 'Vendor', 'Manager', 'Client', 'Inspector')
def index():
    vendor_form = VendorForm()
    article_form = ArticleForm()
    client_form = ClientForm()
    inspector_form = InspectorForm()
    vendors = Vendor.query.all()
    articles = Article.query.all()
    clients = Client.query.all()
    inspectors = Inspector.query.all()
    update_clients_csv()
    
    # Set choices for Client_Name in ArticleForm
    clients_list = get_clients_from_csv()
    article_form.Client_Name.choices = [(client, client) for client in clients_list]
    
    return render_template('home/index.html', 
                           segment='index', 
                           vendor_form=vendor_form, 
                           article_form=article_form,
                           client_form=client_form, 
                           inspector_form=inspector_form, 
                           vendors=vendors,
                           articles=articles, 
                           clients=clients,
                           inspectors=inspectors, 
                           image_files=image_files, 
                           session=session)

@blueprint.route('/add_vendor', methods=['POST'])
def add_vendor():
    vendor_form = VendorForm(request.form)
    if vendor_form.validate_on_submit():
        try:
            vendor = Vendor(
                name=vendor_form.name.data,
                address=vendor_form.address.data,
                city=vendor_form.city.data,
                contact_person_name=vendor_form.contact_person_name.data,
                designation=vendor_form.designation.data,
                contact_number=vendor_form.contact_number.data,
                phone_number=vendor_form.phone_number.data,
                head_name=vendor_form.head_name.data,
                head_designation=vendor_form.head_designation.data,
                head_email=vendor_form.head_email.data,
                head_phone_number=vendor_form.head_phone_number.data,
            )

            db.session.add(vendor)
            db.session.commit()
            flash('Vendor added successfully', 'success')
            current_app.logger.info(f"Vendor {vendor.name} added successfully")
        except Exception as e:
            db.session.rollback()
            flash('Error adding Vendor. Please try again.', 'error')
            current_app.logger.error(f"Error adding Vendor: {str(e)}")
    else:
        for field, errors in vendor_form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'error')
                current_app.logger.warning(f"Form validation error in {field}: {error}")

    return redirect(url_for('home_blueprint.index'))
    
    # If form validation fails, render the template with the current form
    return render_template('home/index.html', vendor_form=vendor_form, article_form=ArticleForm(), client_form=ClientForm(), msg="Failed to add vendor. Please try again.")




def add_client_to_csv(client_name):
    csv_path = os.path.join(current_app.root_path, 'static', 'clients', 'clients.csv')
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
    file_exists = os.path.isfile(csv_path)
    try:
        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(['Name'])  # Write header if file is new
            writer.writerow([client_name])
    except Exception as e:
        current_app.logger.error(f"Error adding client: {str(e)}")
        flash('Error adding client to csv file. Please try again.', 'error')

def get_clients_from_csv():
    csv_path = os.path.join(current_app.root_path, 'static', 'clients', 'clients.csv')
    if not os.path.exists(csv_path):
        return []
    
    with open(csv_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)
        return [row[0] for row in reader]
    



@blueprint.route('/add_article', methods=['POST'])
def add_article():
    current_app.logger.info("Entering add_article route")
    article_form = ArticleForm(request.form)
    clients = get_clients_from_csv()
    article_form.Client_Name.choices = [(client, client) for client in clients]

    current_app.logger.info(f"Form data: {request.form}")
    current_app.logger.info(f"Client choices: {article_form.Client_Name.choices}")

    if article_form.validate_on_submit():
        current_app.logger.info("Form validated successfully")
        try:
            # Retrieve data from the form
            Category = article_form.Category.data
            Product_Name = article_form.Product_Name.data
            Article_Number = article_form.Article_Number.data
            Gender = article_form.Gender.data
            Color = article_form.Color.data
            Size = article_form.Size.data
            Description = article_form.Description.data
            Client_Name = article_form.Client_Name.data

            current_app.logger.info(f"Parsed form data: Category={Category}, Product_Name={Product_Name}, Article_Number={Article_Number}, Gender={Gender}, Color={Color}, Size={Size}, Description={Description}, Client_Name={Client_Name}")

            # Check if the article number already exists in the database
            existing_article = Article.query.filter_by(Article_No=Article_Number).first()
            if existing_article:
                current_app.logger.warning(f"Article number {Article_Number} already exists")
                flash(f"Article number {Article_Number} already exists. Please choose a different number.", 'error')
                return redirect(url_for('home_blueprint.index'))

            # Create a new article object
            article = Article(
                Category=Category,
                Product_Name=Product_Name,
                Article_No=Article_Number,
                Gender=Gender,
                Color=Color,
                Size=Size,
                Description=Description,
                Client_Name=Client_Name
            )

            # Save article to the database
            db.session.add(article)
            db.session.commit()
            current_app.logger.info(f"Article {Article_Number} added successfully")

            # Handle image uploads
            images = request.files.getlist(article_form.Article_images.name)
            if images:
                article_dir = os.path.join(current_app.root_path, 'static', 'images', secure_filename(Product_Name))
                os.makedirs(article_dir, exist_ok=True)

                for image in images:
                    if image and allowed_file(image.filename):
                        filename = secure_filename(image.filename)
                        image_path = os.path.join(article_dir, filename)
                        image.save(image_path)
                        
                        relative_path = os.path.join('images', secure_filename(Product_Name), filename)
                        article_image = ArticleImage(filename=relative_path, article_id=article.Article_No)
                        db.session.add(article_image)

                db.session.commit()
                current_app.logger.info(f"Images for article {Article_Number} saved successfully")

            flash('Article added successfully', 'success')
            return redirect(url_for('home_blueprint.index'))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding article: {str(e)}")
            flash('Error adding article. Please try again.', 'error')
            return redirect(url_for('home_blueprint.index'))
    else:
        current_app.logger.warning("Form validation failed")
        for field, errors in article_form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'error')
                current_app.logger.warning(f"Form validation error in {field}: {error}")
        
    current_app.logger.info("Rendering index template with form errors")
    return render_template('home/index.html', 
                           vendor_form=VendorForm(), 
                           article_form=article_form, 
                           client_form=ClientForm(), 
                           inspector_form=InspectorForm(), 
                           msg="Failed to add article. Please check the form for errors.")

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@blueprint.route('/get_clients')
def get_clients():
    clients = get_clients_from_csv()
    return jsonify(clients=clients)


@blueprint.route('/add_client', methods=['POST'])
def add_client():
    client_form = ClientForm(request.form)
    
    
    if client_form.validate_on_submit():
        try:
            # Create client instance
            client = Client(
                name=client_form.name.data,
                address=client_form.address.data,
                city=client_form.city.data,
                contact_person_name=client_form.contact_person_name.data,
                designation=client_form.designation.data,
                contact_number=client_form.contact_number.data,
                phone_number=client_form.phone_number.data,
                head_name=client_form.head_name.data,
                head_designation=client_form.head_designation.data,
                head_email=client_form.head_email.data,
                head_phone_number=client_form.head_phone_number.data
            )

            
            db.session.add(client)
            db.session.commit()

            
            current_app.logger.info(f"Client {client.name} added successfully")
            flash('Client added successfully', 'success')            
            return redirect(url_for('home_blueprint.index'))

        except Exception as e:
            
            db.session.rollback()
            current_app.logger.error(f"Error adding client: {str(e)}")
            flash('Error adding client. Please try again.', 'error')
    
    # Handle form validation errors
    else:
        for field, errors in client_form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'error')
                current_app.logger.warning(f"Form validation error in {field}: {error}")

    # Re-render the form with validation errors (do not redirect here)
    return render_template(
        'home/index.html',
        client_form=client_form,
        vendor_form=VendorForm(),
        article_form=ArticleForm(),
        inspector_form=InspectorForm()
    )


@blueprint.route('/add_inspector', methods=['POST'])
def add_inspector():
    inspector_form = InspectorForm(request.form)
    if inspector_form.validate_on_submit():
        try:
            inspector = Inspector(
                name=inspector_form.name.data,
                location=inspector_form.location.data,
                contact=inspector_form.contact.data,
                email=inspector_form.email.data
            )

            db.session.add(inspector)
            db.session.commit()
            flash('Inspector added successfully', 'success')
            current_app.logger.info(f"Inspector {inspector.name} added successfully")
        except Exception as e:
            db.session.rollback()
            flash('Error adding inspector. Please try again.', 'error')
            current_app.logger.error(f"Error adding inspector: {str(e)}")
    else:
        for field, errors in inspector_form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'error')
                current_app.logger.warning(f"Form validation error in {field}: {error}")

    return redirect(url_for('home_blueprint.index'))
    
    # If form validation fails, render the template with the current form
    return render_template('home/index.html', inspector_form=inspector_form, vendor_form=VendorForm(), article_form=ArticleForm(),client_form=ClientForm(),  msg="Failed to add inspector. Please try again.")

@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
