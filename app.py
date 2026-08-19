import os
from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super-secret-key-12345")

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

@app.route('/')
def index():
    user = session.get('user')
    
    if not user:
        return render_template('index.html', user=None, notes=[])
    
    try:
        response = supabase.table('notes').select('*').eq('user_id', user['id']).order('id', desc=True).execute()
        notes = response.data
    except Exception:
        notes = []
        
    return render_template('index.html', user=user, notes=notes)

@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        if res.user:
            session['user'] = {"id": res.user.id, "email": res.user.email}
    except Exception as e:
        return render_template('index.html', user=None, notes=[], auth_error=str(e))
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if res.user:
            session['user'] = {"id": res.user.id, "email": res.user.email}
    except Exception as e:
        return render_template('index.html', user=None, notes=[], auth_error=str(e))
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/add', methods=['POST'])
def add_note():
    user = session.get('user')
    if not user:
        return redirect(url_for('index'))
        
    title = request.form.get('title')
    content = request.form.get('content')
    if title and content:
        supabase.table('notes').insert({
            'title': title, 
            'content': content, 
            'user_id': user['id']
        }).execute()
    return redirect(url_for('index'))

@app.route('/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    user = session.get('user')
    if user:
        supabase.table('notes').delete().eq('id', note_id).eq('user_id', user['id']).execute()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)