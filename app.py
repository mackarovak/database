from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://nuancce:0516@localhost/mydatabase'
db = SQLAlchemy(app)

# Модель таблицы lichsostav
class Lichsostav(db.Model):
    table_id = db.Column(db.Integer, primary_key=True)
    number_cex = db.Column(db.Integer, nullable=False)
    number_uchastka = db.Column(db.Integer, nullable=False)
    code = db.Column(db.Integer, nullable=False)
    razryad = db.Column(db.Integer, nullable=False, server_default='1', info={'check': 'razryad>0 AND razryad<100'})
    sem_poloz = db.Column(db.String(20), nullable=False, default='не состоит в браке')
    familia = db.Column(db.String(50), nullable=False)

# Модель таблицы uchastki
class Uchastki(db.Model):
    number_cex = db.Column(db.Integer, primary_key=True)
    number_uchastka = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    tab_number = db.Column(db.Integer, nullable=False)

# Модель таблицы professions
class Professions(db.Model):
    code_id = db.Column(db.Integer, db.ForeignKey('lichsostav.code', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    name_prof = db.Column(db.String(50), nullable=False)

class CombinedData(db.Model):
    __tablename__ = 'combined_data'
    code = db.Column(db.Integer, primary_key=True)
    number_cex = db.Column(db.Integer, nullable=False)
    number_uchastka = db.Column(db.Integer, nullable=False)
    razryad = db.Column(db.Integer, nullable=False, server_default='1', info={'check': 'razryad>0 AND razryad<100'})
    sem_poloz = db.Column(db.String(20), nullable=False, default='не состоит в браке')
    familia = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    tab_number = db.Column(db.Integer, nullable=False)
    name_prof = db.Column(db.String(50), nullable=False)

    @classmethod
    def create_view(cls):
        # Проверка на существование представления и его удаление, если оно уже существует
        check_view_query = text("""
            DROP VIEW IF EXISTS combined_data
        """)
        db.session.execute(check_view_query)
        db.session.commit()

        # Создание SQL-запроса для создания представления
        create_view_query = text("""
            CREATE VIEW combined_data AS
            SELECT l.code, l.number_cex, l.number_uchastka, l.razryad, l.sem_poloz, l.familia, u.name, u.tab_number, p.name_prof
            FROM lichsostav l
            JOIN uchastki u ON l.number_cex = u.number_cex AND l.number_uchastka = u.number_uchastka
            JOIN professions p ON l.code = p.code_id
        """)
        db.session.execute(create_view_query)
        db.session.commit()

@app.route('/procedure')
def procedure():
    number_cex_param = 7
    number_uchastka_param = 6
    name_param = 'Участок 1'
    tab_number_param = 106

    query = text("CALL insert_uchastok(:number_cex_param, :number_uchastka_param, :name_param, :tab_number_param)")
    db.session.execute(query,
                       {"number_cex_param": number_cex_param,
                        "number_uchastka_param": number_uchastka_param,
                        "name_param": name_param,
                        "tab_number_param": tab_number_param})

    db.session.commit()

    return "Хранимая процедура успешно выполнена" 


@app.route('/alter_from')
def alter_from():
    lichsostav_data = Lichsostav.query.all()
    uchastki = Uchastki.query.all()
    professions = Professions.query.all()  
    return render_template('alter_from.html', lichsostav_data=lichsostav_data, uchastki_data=uchastki, professions_data=professions)
@app.route('/combined_data')
def combined_data():
    # Получение данных из представления
    combined_data = CombinedData.query.all()
    
    return render_template('combined_data.html', combined_data=combined_data)

@app.route('/update_uchastki', methods=['POST'])
def update_uchastki_route():
    number_cex = int(request.form['number_cex'])
    number_uchastka = int(request.form['number_uchastka'])
    name = request.form['name']
    tab_number = int(request.form['tab_number'])
    
    # Find the Uchastki record to update
    uchastki = Uchastki.query.filter_by(number_cex=number_cex, number_uchastka=number_uchastka).first()
    
    if uchastki:
        # Update the record with the new values
        uchastki.name = name
        uchastki.tab_number = tab_number
        db.session.commit()
        return redirect('/')
    else:
        return "Uchastki record not found"

@app.route('/update_professions', methods=['POST'])
def update_prof():
    code_id = int(request.form['code_id'])
    name_prof = request.form['name_prof']
    
    # Find the Uchastki record to update
    professions = Professions.query.filter_by(code_id=code_id).first()
    
    if professions:
        # Update the record with the new values
        professions.name_prof = name_prof
        db.session.commit()
        return redirect('/')
    else:
        return "Professions record not found"
    
@app.route('/update_lichsostav', methods=['POST'])
def update_lichsostav():
    table_id = int(request.form['table_id'])
    number_cex = int(request.form['number_cex'])
    number_uchastka = int(request.form['number_uchastka'])
    code = int(request.form['code'])
    razryad=int(request.form['razryad'])
    sem_poloz = request.form['sem_poloz']
    familia=request.form['familia']
    
    # Find the Uchastki record to update
    lichsostav = Lichsostav.query.filter_by(table_id=table_id).first()
    
    if lichsostav:
        # Update the record with the new values
        lichsostav.number_cex = number_cex
        lichsostav.number_uchastka = number_uchastka
        lichsostav.code=code
        lichsostav.razryad=razryad
        lichsostav.sem_poloz=sem_poloz
        lichsostav.familia=familia
        db.session.commit()
        return redirect('/')
    else:
        return "Lichsostav record not found"

def get_lichistav():
    query = text("""
    SELECT 
    Lichsostav.familia AS ФИО,
    Professions.name_prof AS Наименование_профессии,
    Lichsostav.razryad AS Разряд,
    COUNT(*) OVER (PARTITION BY Lichsostav.number_cex, Lichsostav.number_uchastka, Professions.code_id) AS Количество_рабочих_на_участке,
    AVG(Lichsostav.razryad) OVER (PARTITION BY Professions.code_id) AS Средний_разряд_по_профессии
FROM 
    Lichsostav
JOIN 
    Professions ON Lichsostav.code = Professions.code_id
    """)
    results = db.session.execute(query)
    
    # Преобразование результатов в список словарей
    data = [{'ФИО': result[0], 'Наименование профессии': result[1], 'Разряд': result[2], 'Количество рабочих этой же профессии на этом участке этого цеха': result[3], 'Средний разряд рабочих данной профессии на всём предприятии': result[4]} for result in results]
    
    return data

def get_workers_by_razryad(razryad):
    query = text("SELECT number_cex, familia, name_prof FROM Lichsostav JOIN Professions ON Lichsostav.code = Professions.code_id WHERE razryad = :razryad")
    results = db.session.execute(query, {'razryad': razryad}).fetchall()
    return results

def get_workers_by_razryad_orm(razryad):
    results = db.session.query(Lichsostav.number_cex, Lichsostav.familia, Professions.name_prof) \
        .join(Professions, Lichsostav.code == Professions.code_id) \
        .filter(Lichsostav.razryad == razryad) \
        .all()
    return results

@app.route('/razryad', methods=['GET'])
def pokaz():
    razryad = request.args.get('razryad', default=5)  # Получение значения параметра razryad из GET-запроса, по умолчанию 5
    results_opr_razryad = get_workers_by_razryad(razryad)
    return render_template('results_opr_razryad_sql.html', results_opr_razryad=results_opr_razryad)

@app.route('/razryad_orm', methods=['GET'])
def pokaz_orm():
    razryad = request.args.get('razryad', default=5)  # Получение значения параметра razryad из GET-запроса, по умолчанию 5
    results_opr_razryad = get_workers_by_razryad_orm(razryad)
    return render_template('results_opr_razryad_orm.html', results_opr_razryad=results_opr_razryad)


def get_professions_with_uchastka_7():
    query = text("""
SELECT p.name_prof
FROM professions p
WHERE EXISTS (
  SELECT *
  FROM lichsostav l
  WHERE l.number_cex = 7 AND l.code = p.code_id AND l.razryad > 4
)
AND NOT EXISTS (
  SELECT *
  FROM lichsostav l
  WHERE l.number_cex = 7 AND l.code = p.code_id AND l.razryad <= 4
);
    """)
    cursor = db.session.execute(query)
    results = [row[0] for row in cursor]
    return results

def get_professions_with_uchastka_7_record():
    professions_with_uchastka_7 = db.session.query(Professions).join(Lichsostav).\
        filter(Lichsostav.number_cex == 7).\
        filter(Lichsostav.razryad > 4).all()
    return professions_with_uchastka_7

# Главная страницаhttp://127.0.0.1:5001
@app.route('/')
def index():
    uchastki = Uchastki.query.all()
    lichsostav = Lichsostav.query.all()  # Получение данных из таблицы Lichsostav
    professions = Professions.query.all()  # Получение данных из таблицы Professions
    inspector = inspect(db.engine)
    if 'combined_data' not in inspector.get_table_names():
        CombinedData.create_view()
    
    # Получение данных из представления
    combined_data = CombinedData.query.all()
    results = get_lichistav()
    cvantor_res=get_professions_with_uchastka_7()
    record_res=get_professions_with_uchastka_7_record()
    return render_template('index.html', uchastki=uchastki, lichsostav=lichsostav, professions=professions, combined_data=combined_data, results=results, cvantor_res=cvantor_res, record_res=record_res)

if __name__ == '__main__':
    app.run(port=5001, debug=True)