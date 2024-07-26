from flask import Flask, render_template, redirect, url_for, request, jsonify, session, send_from_directory
import attendance;
from flask_login import LoginManager, login_user, login_required, logout_user
import claims;
import database
from datetime import datetime;
from werkzeug.utils import secure_filename;
import os
import base64
from PIL import Image
from io import BytesIO


upload_folder = 'Raw_Dataset_Train'
allowed_extensions = set(['png','jpg','jpeg'])
    
app = Flask(__name__)
app.config['upload_folder'] = upload_folder
app.secret_key = 'FRAMS'   # Change this to a secure random key
login_manager = LoginManager()
login_manager.init_app(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/')
def main_page():
    return render_template("index.html")


users = database.get_all_users()
# User loader function required by Flask-Login
@login_manager.user_loader
def load_user(user_id):
    for user in users:
        if user.id == int(user_id):
            return user
    return None  # return None if user is not found

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        userid = request.form['username']
        password = request.form['password']

        for user in users:
            if user.id == int(userid):
                if user and user.password == password and user.status == "Approved":
                    login_user(user)
                    if user.type == 'User':
                        session['user_name'] = user.fname + ' ' + user.lname
                        session['user_id'] = userid
                        session['img_name'] = user.image_name
                        return redirect(url_for('dashboard', user_id=userid, user_name=user.password))
                    elif user.type == 'Admin':
                        session['user_name'] = user.fname + ' ' + user.lname
                        session['user_id'] = userid
                        session['img_name'] = user.image_name
                        return redirect(url_for('admindash', user_id=userid, user_name=user.password))
                else:
                    return render_template('login.html', error="Invalid Credentials")

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)  # Remove username from session
    session.pop('user_name', None)
    # print(session)
    logout_user() 
    return redirect(url_for('login'))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == "POST":
        # print("Form Data:", request.form)  # Add this line to print form data
        user_id = request.form['userid']
        fname = request.form['fname']
        lname = request.form['lname']
        password = request.form['password']
        cpassword = request.form['cpassword']
        wages = 0
        image_name = user_id + '_' + fname + '_' + lname

        if password == cpassword:
            database.generate_new_user(user_id, password, fname, lname, wages, image_name)
            return render_template('addImage.html', image_name=image_name)
        else:
            return render_template('register.html')
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        user_name = session['user_name']
        records = database.get_all_entries_by_user_id(user_id)
        return render_template('dashboard.html', user_id=user_id, user_name=user_name, records = records)
    else:
        return redirect(url_for('login'))

@app.route('/filter_records', methods=['POST'])
@login_required
def filter_records():
    user_id = request.form.get('user_id')
    user_name = request.form.get('user_name')
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')

    # Convert date strings to datetime objects
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    # Get records between the two dates
    filtered_records = database.get_records_between_dates(user_id, start_date, end_date)

    return render_template('filtered_records.html', user_id=user_id, user_name=user_name, records=filtered_records, s = start_date.date(), e = end_date.date())

@app.route('/admindash')
@login_required
def admindash():
    if 'user_id' in session:
        user_id = session['user_id']
        user_name = session['user_name']
        return render_template('admindash.html', user_id=user_id, user_name=user_name)
    else:
        return redirect(url_for('login'))

@app.route("/alldata")
@login_required
def alldata():
    user_id = session['user_id']
    user_name = session['user_name']

    records = database.get_all_attendance_records()

    return render_template('alldata.html', user_id=user_id, user_name=user_name, records = records)

@app.route("/userclaim")
@login_required
def userclaim():

    user_id = session['user_id']
    user_name = session['user_name']

    records = database.get_all_break_records(user_id)
    entries = claims.get_entries_by_userid(user_id)

    return render_template('userclaim.html', user_id=user_id, user_name=user_name, records = records, entries = entries)

@app.route('/approvenewusers')
@login_required
def approvenewusers():
    user_id = session['user_id']
    user_name = session['user_name']

    records = database.get_all_users_with_pending_status()
    
    return render_template('approveNewUsers.html', user_id=user_id, user_name=user_name, records = records)

@app.route('/project_images/<filename>')
def project_images(filename):
    return send_from_directory(os.getcwd(), filename)

@app.route("/calculatesalary", methods=['GET', 'POST'])
@login_required
def calculatesalary():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        user_name = request.form.get('user_name')
        month = request.form.get('month')
        year = request.form.get('year')

        # Check if month and year are not None and are valid integers
        if month is not None and year is not None and month.isdigit() and year.isdigit():
            # records = database.calculate_monthly_salary(month, year)
            records = database.calculate_monthly_salary_breaks(month, year)
            return render_template('calculatesalary.html', user_id=user_id, user_name=user_name, records=records, month=month, year=year)
        else:
            return jsonify({"message": "Error: Both month and year must be provided as valid integers."})
        
@app.route("/dataofprticularemployee", methods = ['GET', 'POST'])
@login_required
def dataofprticularemployee():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        user_name = request.form.get('user_name')

        user_id_emp = request.form.get('id')
        records = database.get_all_entries_by_user_id(user_id_emp)

        return render_template('dataofprticularemployee.html', user_id=user_id, user_name=user_name, records = records, id = user_id_emp)
    
@app.route("/allClaims", methods = ['GET', 'POST'])
@login_required
def allClaims():
    
    user_id = session['user_id']
    user_name = session['user_name']

    records = claims.get_all_claims()

    return render_template('allClaims.html', user_id=user_id, user_name=user_name, records = records)
   
# @app.route("/addImage", methods=['POST'])
# def addImage():
#     if 'file' not in request.files:
#         return jsonify({'Error': 'Media not provided'}), 400
#     file = request.files['file']
#     file_name = request.form['file_name'] if 'file_name' in request.form else None
#     if file_name is None:
#         return jsonify({'Error': 'Image name not provided'}), 400
#     if file.filename == '':
#         return jsonify({'Error': 'No file selected'}), 400
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         file_ext = filename.rsplit('.', 1)[1].lower()
#         new_filename = secure_filename(file_name) + '.' + file_ext
#         file.save(os.path.join(app.config['upload_folder'], new_filename))
#         return jsonify({'success': True, 'msg': 'Image uploaded successfully'})
#     return jsonify({'Error': 'Invalid file format'}), 400

@app.route("/addImage", methods=['POST'])
def addImage():
    if 'file' not in request.files:
        return jsonify({'Error': 'Media not provided'}), 400
    file = request.files['file']
    file_name = request.form['file_name'] if 'file_name' in request.form else None
    if file_name is None:
        return jsonify({'Error': 'Image name not provided'}), 400
    if file.filename == '':
        return jsonify({'Error': 'No file selected'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        new_filename = secure_filename(file_name) + '.' + file_ext
        file.save(os.path.join(app.config['upload_folder'], new_filename))
        
        # Return HTML content with JavaScript for alert and redirection
        return """
        <script>
            alert('Image uploaded successfully, Once your registration is accepted by Admin you can login after some time.');
            window.location.href = '/login'; // Redirect to the login page
        </script>
        """
    return jsonify({'Error': 'Invalid file format'}), 400

@app.route("/addImagebycam", methods=['POST'])
def addImagebycam():
    image_name = request.form.get('image_name')
    image_data = request.form.get('image')

    if not image_data:
        return jsonify({'Error': 'Image data not provided'}), 400
    if not image_name:
        return jsonify({'Error': 'Image name not provided'}), 400

    # Remove the header from the data URL
    encoded_image = image_data.split(',')[1]

    # Decode the Base64 image data
    decoded_image = base64.b64decode(encoded_image)

    # Create a PIL image object from the decoded image data
    img = Image.open(BytesIO(decoded_image))

    # Save the image to the upload folder
    img_path = os.path.join(app.config['upload_folder'], f"{image_name}.png")
    img.save(img_path)

    # return jsonify({'success': True, 'msg': 'Image uploaded successfully'}), 200
    return """
        <script>
            alert('Image uploaded successfully, Once your registration is accepted by Admin you can login after some time.');
            window.location.href = '/login'; // Redirect to the login page
        </script>
    """

@app.route('/check_in', methods=['POST'])
def check_in():
    user_id = request.args.get('user_id')
    name = request.args.get('user_name')
    time, date = attendance.markCheckInAttendances(user_id, name)
    return jsonify({
        "message": 'Check In Attendance marked successfully',
        "time": time,
        "date": date
        })

@app.route('/check_out', methods=['POST'])
def check_out():
    user_id = request.args.get('user_id')
    name = request.args.get('user_name')
    time, date = attendance.markCheckOutAttendances(user_id, name)
    # return jsonify({"message": 'Check Out Attendance marked successfully'})
    return jsonify({
        "message": "Check Out Attendance marked successfully",
        "time": time,
        "date": date
    })

@app.route("/claim_break", methods=['GET', 'POST'])
def claim_break():
    data = request.json
    claims.new_claim(data)
    return jsonify({"message": "Break claimed successfully"})

@app.route("/claim_approve", methods=["POST"])
def claim_approve():
    data = request.json
    claims.claim_approve(data)
    return jsonify({"message": "Claim Approved Successfully"})

@app.route("/claim_reject", methods = ['GET', 'POST'])
def claim_reject():
    data = request.json
    claims.claim_reject(data)
    return jsonify({"message": "Claim Rejected"})

@app.route("/application_approve", methods=["POST"])
def application_approve():
    data = request.json
    # print(data)
    # print("user_id, type, fname, lname, password, image_name, wages_hr, status")
    database.application_approve(data)
    return jsonify({"message": "Application Approved Successfully"})

@app.route("/application_reject", methods = ['GET', 'POST'])
def application_reject():
    data = request.json
    database.application_reject(data)
    return jsonify({"message": "Application Rejected"})
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)