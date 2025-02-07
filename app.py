from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Required for flash messages
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://DESKTOP-9TT6CR2\\SQLEXPRESS/Pravi_DB?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes&TrustServerCertificate=yes'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define a model for the database table
class SettingReference(db.Model):
    __tablename__ = 'Setting_Reference'
    key = db.Column('Key1', db.String, primary_key=True)
    ref_val1 = db.Column('ref_val1', db.String)

class RecipeMaster(db.Model):
    __tablename__ = 'Recipe_Master'
    partname = db.Column('Part_name', db.String, primary_key=True)
    subpartname = db.Column('Subpart_name', db.String)
    RecipeID = db.Column('Recipe_id', db.String)

class Defects_Detail(db.Model):
    __tablename__ = 'Defects_Detail'
    PartName = db.Column('PartName', db.String, primary_key=True)
    View = db.Column('View', db.String)
    DefectName = db.Column('DefectName', db.String)

# SELECT TOP (1000) [PartName]
#       ,[View]
#       ,[DefectName]
#   FROM [Pravi_DB].[dbo].[Defects_Detail]


@app.route("/", methods=["GET", "POST"])
def hello_world():
    if request.method == "POST":
        port_name = request.form.get('port-name')
        baud_rate = request.form.get('baud-rate')
        master_local_path = request.form.get('master-local-path')

        try:
            # Update the values in the database
            db.session.query(SettingReference).filter(SettingReference.key == 'Port Name').update({SettingReference.ref_val1: port_name})
            db.session.query(SettingReference).filter(SettingReference.key == 'Baud Rate').update({SettingReference.ref_val1: baud_rate})
            db.session.query(SettingReference).filter(SettingReference.key == 'Master Local Path').update({SettingReference.ref_val1: master_local_path})
            db.session.commit()
            flash("Settings updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error while updating settings: {e}", "error")

        return redirect(url_for('hello_world'))

    # Fetch current values from the database
    part_names = db.session.query(RecipeMaster.partname).distinct()
    defect_details = db.session.query(Defects_Detail).all()
    PartsInfo = db.session.query(RecipeMaster).all()
    port_name = db.session.query(SettingReference).filter(SettingReference.key == 'Port Name').first().ref_val1
    baud_rate = db.session.query(SettingReference).filter(SettingReference.key == 'Baud Rate').first().ref_val1
    master_local_path = db.session.query(SettingReference).filter(SettingReference.key == 'Master Local Path').first().ref_val1

    return render_template('Settings.html', part_names = part_names, defect_details=defect_details, PartsInfo= PartsInfo, port_name=port_name, baud_rate=baud_rate, master_local_path=master_local_path)

@app.route("/settings", methods=["GET", "POST"])
def AddParts():
    if request.method == "POST":
    
        part_name = request.form.get('selected-part-name')
        print(f"Part_Name: {part_name}")
        subpart_name = request.form.get('subpart-name')
        try:
            
            subpartcount = db.session.query(func.count(RecipeMaster.subpartname)).filter(RecipeMaster.subpartname == subpart_name).scalar()
            print(f"Subpart_Count: {subpartcount}")
           
            if subpartcount > 0:
                flash("Subpart already exists!", "error")
                return redirect(url_for('AddParts'))
            recipe_master = RecipeMaster(
                partname=part_name,
                subpartname=subpart_name,
                RecipeID="1234"  # You can modify this value as needed
            )
            db.session.add(recipe_master)
            db.session.commit()
            flash("Part and Subpart added successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error while adding Part and Subpart: {e}", "error")
        return redirect(url_for('AddParts'))
    
    part_names = db.session.query(RecipeMaster.partname).distinct()
    defect_details = db.session.query(Defects_Detail).all()
    PartsInfo = db.session.query(RecipeMaster).all()
    port_name = db.session.query(SettingReference).filter(SettingReference.key == 'Port Name').first().ref_val1
    baud_rate = db.session.query(SettingReference).filter(SettingReference.key == 'Baud Rate').first().ref_val1
    master_local_path = db.session.query(SettingReference).filter(SettingReference.key == 'Master Local Path').first().ref_val1

    return render_template('Settings.html', part_names = part_names, defect_details=defect_details, PartsInfo= PartsInfo, port_name = port_name, baud_rate=baud_rate, master_local_path=master_local_path)

@app.route("/DefectSettings", methods=["GET", "POST"])
def AddDefects():
    if request.method == "POST":

        txtpart_name = request.form.get('cboPartNameDefect')
        print(f"Part_Name_Defect: {txtpart_name}")

        cboView = request.form.get('cboViewDefect')
        print(f"View: {cboView}")

        txtDefectName = request.form.get('defect-name')
        print(f"Defect Name: {txtDefectName}")

        try:
            Defectcount = db.session.query(func.count(Defects_Detail.DefectName)).filter(
                Defects_Detail.DefectName == txtDefectName,
                Defects_Detail.PartName == txtpart_name
            ).scalar()
            print(f"DefectCount: {Defectcount}")

            if Defectcount > 0:
                flash("Defect already exists for this part!", "error")
                return redirect(url_for('AddDefects'))

            DefecDetail = Defects_Detail(
                PartName=txtpart_name,
                View=cboView,
                DefectName=txtDefectName  # You can modify this value as needed
            )
            db.session.add(DefecDetail)
            db.session.commit()
            flash("Defects added successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error while adding Defects: {e}", "error")
        return redirect(url_for('AddDefects'))

    part_names = db.session.query(RecipeMaster.partname).distinct()
    defect_details = db.session.query(Defects_Detail).all()
    PartsInfo = db.session.query(RecipeMaster).all()
    port_name = db.session.query(SettingReference).filter(SettingReference.key == 'Port Name').first().ref_val1
    baud_rate = db.session.query(SettingReference).filter(SettingReference.key == 'Baud Rate').first().ref_val1
    master_local_path = db.session.query(SettingReference).filter(SettingReference.key == 'Master Local Path').first().ref_val1

    return render_template('Settings.html', part_names=part_names, defect_details=defect_details, PartsInfo=PartsInfo, port_name=port_name, baud_rate=baud_rate, master_local_path=master_local_path)


@app.route("/DefectSettings", methods=["GET", "POST"])
def UpdateDefects():
    if request.method == "POST":

        txtpart_name = request.form.get('cboPartNameDefect')
        print(f"Part_Name_Defect: {txtpart_name}")

        cboView = request.form.get('cboViewDefect')
        print(f"View: {cboView}")

        txtDefectName = request.form.get('defect-name')
        print(f"Defect Name: {txtDefectName}")

        try:
            Defectcount = db.session.query(func.count(Defects_Detail.DefectName)).filter(
                Defects_Detail.DefectName == txtDefectName,
                Defects_Detail.PartName == txtpart_name
            ).scalar()
            print(f"DefectCount: {Defectcount}")

            if Defectcount > 0:
                flash("Defect already exists for this part!", "error")
                return redirect(url_for('UpdateDefects'))

            db.session.query(Defects_Detail).filter(Defects_Detail.PartName == txtpart_name, Defects_Detail.View == cboView, Defects_Detail.DefectName == txtDefectName).update({Defects_Detail.PartName: txtpart_name, Defects_Detail.View: cboView, Defects_Detail.DefectName: txtDefectName})
            db.session.commit()
            flash("Defects updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error while updating Defects: {e}", "error")
        return redirect(url_for('UpdateDefects'))

    part_names = db.session.query(RecipeMaster.partname).distinct()
    defect_details = db.session.query(Defects_Detail).all()
    PartsInfo = db.session.query(RecipeMaster).all()
    port_name = db.session.query(SettingReference).filter(SettingReference.key == 'Port Name').first().ref_val1
    baud_rate = db.session.query(SettingReference).filter(SettingReference.key == 'Baud Rate').first().ref_val1
    master_local_path = db.session.query(SettingReference).filter(SettingReference.key == 'Master Local Path').first().ref_val1

    return render_template('Settings.html', part_names=part_names, defect_details=defect_details, PartsInfo=PartsInfo, port_name=port_name, baud_rate=baud_rate, master_local_path=master_local_path)


@app.route("/Settings")
def about():
    return render_template('Settings.html')

if __name__ == "__main__":
    app.run(debug=True, port=9000)








