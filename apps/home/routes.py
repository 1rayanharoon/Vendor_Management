from apps import db
from apps.home import blueprint
from flask import render_template, request, redirect, url_for, flash,session
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
    vendor_form = VendorForm()  # Create a new, empty form instance
    article_form = ArticleForm()
    client_form = ClientForm()
    inspector_form = InspectorForm()
    vendors = Vendor.query.all()  # Fetch all vendors from the database
    articles = Article.query.all()
    clients= Client.query.all()
    inspectors = Inspector.query.all()
    
    # db.session.query(Article).delete()
    # db.session.commit()
    return render_template('home/index.html', segment='index', vendor_form=vendor_form, article_form=article_form,client_form=client_form, inspector_form=inspector_form, vendors=vendors,articles=articles, clients=clients,inspectors=inspectors, image_files=image_files, session=session)

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


def get_clients_from_csv():
    client_dir = os.path.join(current_app.root_path, 'client')
    csv_file = os.path.join(client_dir, 'clients.csv')

    clients_from_csv = []
    if os.path.exists(csv_file):
        with open(csv_file, mode='r') as file:
            reader = csv.DictReader(file)  # Using DictReader to access the header
            for row in reader:
                clients_from_csv.append({
                    'name': row['name'],
                    'address': row['address'],
                    'city': row['city'],
                    'contact_person_name': row['contact_person_name'],
                    'designation': row['designation'],
                    'contact_number': row['contact_number'],
                    'phone_number': row['phone_number'],
                    'head_name': row['head_name'],
                    'head_designation': row['head_designation'],
                    'head_email': row['head_email'],
                    'head_phone_number': row['head_phone_number']
                })
    return clients_from_csv

@blueprint.route('/add_article', methods=['POST'])
def add_article():
    article_form = ArticleForm(request.form)
    db_clients = Client.query.all()

    # Load clients from the CSV file
    csv_clients = []
    client_dir = os.path.join(current_app.root_path, 'client')
    csv_file = os.path.join(client_dir, 'clients.csv')

    if os.path.exists(csv_file):
        with open(csv_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                csv_clients.append({
                    'name': row['name'],
                    'address': row['address'],
                    'city': row['city'],
                    'contact_person_name': row['contact_person_name'],
                })

    # Combine database and CSV clients
    all_clients = [{'name': client.name, 'address': client.address, 'city': client.city, 'contact_person_name': client.contact_person_name, } for client in db_clients] + csv_clients

    
    if article_form.validate_on_submit():
        # Retrieve data from the form
        Category = article_form.Category.data
        Product_Name = article_form.Product_Name.data
        Article_Number = article_form.Article_Number.data
        Gender = article_form.Gender.data
        Color = article_form.Color.data
        Size = article_form.Size.data
        Description = article_form.Description.data
        client_id=article_form.client.data 

        # Check if the article number already exists in the database
        existing_article = Article.query.filter_by(Article_No=Article_Number).first()
        if existing_article:
            msg = f"Article number {Article_Number} already exists. Please choose a different number."
            return render_template('home/index.html', vendor_form=VendorForm(), article_form=article_form, client_form=ClientForm(), msg=msg)

        # Create a new article object
        article = Article(
            Category=Category,
            Product_Name=Product_Name,
            Article_No=Article_Number,
            Gender=Gender,
            Color=Color,
            Size=Size,
            Description=Description,
            Client_id=client_id
        )

        try:
            # Save article to the database
            db.session.add(article)
            db.session.commit()

            # Retrieve uploaded images
            images = request.files.getlist(article_form.Article_images.name)

            if images:
                # Create the article-specific directory
                article_dir = os.path.join(current_app.root_path, 'static', 'images', secure_filename(Product_Name))
                os.makedirs(article_dir, exist_ok=True)

                for image in images:
                    if image and allowed_file(image.filename):
                        filename = secure_filename(image.filename)
                        image_path = os.path.join(article_dir, filename)
                        image.save(image_path)
                        
                        # Create a new ArticleImage object and save to the database
                        relative_path = os.path.join('images', secure_filename(Product_Name), filename)
                        article_image = ArticleImage(filename=relative_path, article_id=article.Article_No)
                        db.session.add(article_image)

                # Commit the changes to the database
                db.session.commit()

        except IntegrityError as e:
            db.session.rollback()
            msg = "An error occurred while adding the article. Please try again."
            return render_template('home/index.html', vendor_form=VendorForm(), client_form=ClientForm(), article_form=article_form, msg=msg)
        except Exception as e:
            db.session.rollback()
            msg = f"An unexpected error occurred: {str(e)}"
            return render_template('home/index.html', vendor_form=VendorForm(),client_form=ClientForm(), article_form=article_form, msg=msg)

        # Redirect to index with a new, empty form
        return redirect(url_for('home_blueprint.index'))

    # If form validation fails, render the template with the current form
    return render_template('home/index.html', vendor_form=VendorForm(), article_form=article_form, clientform=ClientForm(),inspector_form=InspectorForm(), msg="Failed to add article. Please try again.")

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@blueprint.route('/add_client', methods=['POST'])
def add_client():
    client_form = ClientForm(request.form)
    if client_form.validate_on_submit():
        # Retrieve data from form
        name = client_form.name.data
        address = client_form.address.data
        city = client_form.city.data
        contact_person_name = client_form.contact_person_name.data
        designation = client_form.designation.data
        contact_number = client_form.contact_number.data
        phone_number = client_form.phone_number.data
        head_name = client_form.head_name.data
        head_designation = client_form.head_designation.data
        head_email = client_form.head_email.data
        head_phone_number = client_form.head_phone_number.data
        
        # Add client to the database
        new_client = Client(
            name=name,
            address=address,
            city=city,
            contact_person_name=contact_person_name,
            designation=designation,
            contact_number=contact_number,
            phone_number=phone_number,
            head_name=head_name,
            head_designation=head_designation,
            head_email=head_email,
            head_phone_number=head_phone_number
        )
        db.session.add(new_client)
        db.session.commit()


        client_dir = os.path.join(current_app.root_path, 'client')
        os.makedirs(client_dir, exist_ok=True)  # Create 'client' folder if it doesn't exist

        # Path for the CSV file
        csv_file = os.path.join(client_dir, 'clients.csv')
        
        # Check if CSV file exists to decide whether to write headers
        write_header = not os.path.exists(csv_file)

        # Write the client data to the CSV file
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)

            # Write the header if it's a new file
            if write_header:
                writer.writerow([
                    'name', 'address', 'city', 'contact_person_name', 'designation', 
                    'contact_number', 'phone_number', 'head_name', 
                    'head_designation', 'head_email', 'head_phone_number'
                ])
            
            # Write the client data row
            writer.writerow([name, address, city, contact_person_name, designation, contact_number, 
                             phone_number, head_name, head_designation, head_email, head_phone_number])


        return redirect(url_for('home_blueprint.index'))

    return render_template('home/index.html', client_form=client_form)
            
            
        
    # If form validation fails, render the template with the current form
    return render_template('home/index.html', client_form=client_form, vendor_form=VendorForm(), article_form=ArticleForm(), inspector_form=InspectorForm(),  msg="Failed to add client. Please try again.")


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
