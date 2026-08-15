from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
import os
import hashlib
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo

from config import Config
from models import db, User, Report
from forms import LoginForm, RegisterForm, ReportForm, UpdateReportStatusForm

# ===== CONFIGURACIÓN =====
app = Flask(__name__)
app.config.from_object(Config)

# ===== BASE DE DATOS =====
db.init_app(app)

# ===== LOGIN MANAGER =====
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, inicia sesión para continuar.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ===== RUTAS =====

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/report', methods=['GET', 'POST'])
def report():
    form = ReportForm()
    if form.validate_on_submit():
        nuevo_reporte = Report(
            reporter_name=form.reporter_name.data,
            project=form.project.data,
            description=form.description.data,
            location=form.location.data,
            status='Pendiente'
        )
        db.session.add(nuevo_reporte)
        db.session.commit()
        flash('✅ ¡Reporte enviado correctamente!', 'success')
        return redirect(url_for('report'))
    return render_template('report_form.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        flash('❌ No tienes permisos.', 'danger')
        return redirect(url_for('index'))
    
    reports = Report.query.order_by(Report.created_at.desc()).all()
    
    total = Report.query.count()
    pendientes = Report.query.filter_by(status='Pendiente').count()
    en_revision = Report.query.filter_by(status='En revisión').count()
    resueltos = Report.query.filter_by(status='Resuelto').count()
    
    return render_template('dashboard.html',
                          reports=reports,
                          total=total,
                          pendientes=pendientes,
                          en_revision=en_revision,
                          resueltos=resueltos)

@app.route('/report/<int:report_id>')
@login_required
def report_detail(report_id):
    if not current_user.is_admin:
        flash('❌ No tienes permisos.', 'danger')
        return redirect(url_for('index'))
    
    report = Report.query.get_or_404(report_id)
    form = UpdateReportStatusForm()
    return render_template('report_detail.html', report=report, form=form)

@app.route('/report/<int:report_id>/update', methods=['POST'])
@login_required
def update_report_status(report_id):
    if not current_user.is_admin:
        flash('❌ No tienes permisos.', 'danger')
        return redirect(url_for('index'))
    
    report = Report.query.get_or_404(report_id)
    form = UpdateReportStatusForm()
    
    if form.validate_on_submit():
        nuevo_estado = form.status.data
        report.status = nuevo_estado
        report.updated_at = datetime.utcnow()
        
        if nuevo_estado == 'Resuelto':
            report.resolved_at = datetime.utcnow()
            report.resolved_by = current_user.id
        
        db.session.commit()
        flash(f'✅ Estado actualizado a: {nuevo_estado}', 'success')
    
    return redirect(url_for('report_detail', report_id=report_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('❌ Tu cuenta está desactivada.', 'danger')
                return redirect(url_for('login'))
            
            login_user(user, remember=form.remember_me.data)
            user.last_login = datetime.utcnow()
            db.session.commit()
            flash(f'✅ ¡Bienvenido, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('❌ Usuario o contraseña incorrectos.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        is_first_user = User.query.count() == 0
        user = User(
            username=form.username.data,
            email=form.email.data,
            is_admin=is_first_user,
            is_active=True
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        if is_first_user:
            flash('✅ ¡Eres el primer usuario! Has sido asignado como administrador.', 'success')
        else:
            flash('✅ Registro exitoso. Espera a que un administrador active tu cuenta.', 'success')
        
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('👋 Has cerrado sesión.', 'info')
    return redirect(url_for('login'))

# ===== RUTAS DE DIAGNÓSTICO =====

@app.route('/test')
def test():
    return "✅ Servidor OK"

@app.route('/init')
def init():
    try:
        db.create_all()
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@walr.com', is_admin=True, is_active=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
        return "✅ Base de datos lista"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ===== INICIALIZAR =====
def init_db():
    with app.app_context():
        try:
            db.create_all()
            print('✅ Tablas creadas')
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(username='admin', email='admin@walr.com', is_admin=True, is_active=True)
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print('✅ Admin creado')
            else:
                print('✅ Admin ya existe')
        except Exception as e:
            print(f'❌ Error: {e}')

# ===== EJECUTAR =====
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    init_db()
    print(f'🚀 Servidor ejecutándose en puerto {port}')
    app.run(debug=False, host='0.0.0.0', port=port)