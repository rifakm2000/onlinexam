from flask import Flask, render_template, request, redirect, flash, session, url_for, session, make_response
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4
import uuid  # For generating unique session id

exam_link = str(uuid.uuid4())
app = Flask(__name__)  # Initialize Flask App

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '12309857',
    'database': 'proctor'
}



@app.route('/login', methods=['GET', 'POST'])
def stu_login():
    exam_link = request.args.get('exam_link')  # Get exam_link from query params
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        exam_link = request.form.get('exam_link')  # From hidden input

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            
            # Authenticate user
            cursor.execute("SELECT user_id, username, password, session_id FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user[2], password):
                # Check if user already has an active session
                if user[3] is not None:
                    # If there's any active session, prevent login
                    flash("This account is already in use. Please log out from other sessions first.", "danger")
                    return redirect(url_for('stu_login', exam_link=exam_link))
                
                # Create new session
                session_id = str(uuid.uuid4())
                session['user_id'] = user[0]
                session['username'] = user[1]
                
                # Update the session_id in the database
                cursor.execute("UPDATE users SET session_id = %s WHERE user_id = %s", (session_id, user[0]))
                conn.commit()
                
                # Set a cookie with the session_id
                response = make_response(redirect(url_for('studash') if not exam_link else url_for('exam', exam_link=exam_link)))
                response.set_cookie('session_id', session_id, max_age=86400)  # Expires in 24 hours
                
                return response
            else:
                flash("Invalid credentials!", "danger")
                return redirect(url_for('stu_login', exam_link=exam_link))
            
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "danger")
            return redirect(url_for('stu_login', exam_link=exam_link))
        
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    # For GET requests, pass exam_link to the template
    return render_template('student/stu_login.html', exam_link=exam_link)

# for login session
# Add this function to your application
def verify_session(user_id, session_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        cursor.execute("SELECT session_id FROM users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        
        if result and result[0] == session_id:
            return True
        return False
        
    except mysql.connector.Error:
        return False
    
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn and conn.is_connected():
            conn.close()


if __name__ == '__main__':
    app.run(debug=True)
