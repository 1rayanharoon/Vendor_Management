from apps import db
from apps.home import blueprint
from flask import render_template, request, redirect, url_for
from flask_login import login_required
from jinja2 import TemplateNotFound
from apps.authentication.forms import VendorForm
from apps.authentication.models import Vendor

@blueprint.route('/index')
@login_required
def index():
    vendor_form = VendorForm()  # Create a new, empty form instance
    return render_template('home/index.html', segment='index', form=vendor_form)

@blueprint.route('/add_vendor', methods=['POST'])
def add_vendor():
    vendor_form = VendorForm(request.form)
    if vendor_form.validate_on_submit():
        name = vendor_form.name.data
        contact = vendor_form.contact.data
        location = vendor_form.location.data

        # Create a new vendor object
        vendor = Vendor(name=name, contact=contact, location=location)

        # Save vendor to the database
        db.session.add(vendor)
        db.session.commit()

        # Redirect to index with a new, empty form
        return redirect(url_for('home_blueprint.index'))
    
    # If form validation fails, render the template with the current form
    return render_template('home/index.html', form=vendor_form, msg="Failed to add vendor. Please try again.")

# ... (rest of the code remains the same)

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
