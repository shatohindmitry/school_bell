import configparser, datetime, secrets
import os
import shutil
from flask import Flask, request, render_template, redirect, url_for, flash, session, send_file
from werkzeug.utils import secure_filename
from operator import itemgetter

USERNAMES = {'admin': '321', 'user': '123'}
FILENAME = 'config.ini'
ALLOWED_EXTENSIONS = {'ini'}

app = Flask(__name__)
secret = secrets.token_urlsafe(32)
app.secret_key = secret
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.permanent_session_lifetime = datetime.timedelta(minutes=20)


def save_file(request):
    file = request.files['file']
    file.save(file.filename)

def check_filename(request):
    file = request.files['file']
    if 'file' not in request.files:
        flash('Не могу прочитать файл')
        return redirect(request.url)
    if file.filename == '':
        flash('Нет выбранного файла')
        return redirect(request.url)
    if file and allowed_file(file.filename) == False:
        flash('Тип файла должен быть "ini"')
        return redirect(request.url)
    if file.filename != secure_filename(file.filename):
        flash('Файл содержит запрещенные символы, или русские буквы')
        return redirect(request.url)
    return False

def check_user(username, password):
    if username in USERNAMES and password == USERNAMES[username]:
        session["name"] = username
        session.permanent = False
        session.modified = True
        return True
    else:
        return False

def put_conf_parser(tasks):

    times = tasks['time_data']
    holidays = tasks['holidays']
    output_days = tasks['output_days']
    special_day = []
    weekend = []

    time_all = []
    time_all_diner = []
    time_spec = []
    time_spec_diner = []

    for key in times:
        value_list = times[key]
        if value_list[0] == '00:00':
            continue

        if 'all' in key:
            if value_list[1] == '1':
                time_all.append(value_list[0])
            else:
                time_all_diner.append(value_list[0])
        elif 'spec' in key:
            if value_list[1] == '1':
                time_spec.append(value_list[0])
            else:
                time_spec_diner.append(value_list[0])

    for i in output_days:
        if int(i) >= 20:
            weekend.append(int(i)-19);
        elif int(i) >= 10:
            special_day.append(int(i)-9);

    time_spec = list(set(time_spec))
    time_spec_diner = list(set(time_spec_diner))
    time_all = list(set(time_all))
    time_all_diner = list(set(time_all_diner))

    config = configparser.ConfigParser()

    config['special_dasy'] = {}
    config['special_dasy']['time'] = ','.join(map(str, sorted(time_spec)))
    config['special_dasy']['music_rings'] = 'ring_main.mp3'
    config['special_dasy']['time_diner'] = ','.join(map(str, sorted(time_spec_diner)))
    config['special_dasy']['music_diner'] = 'double_ring.mp3'

    config['all_day'] = {}
    config['all_day']['time'] = ','.join(map(str, sorted(time_all)))
    config['all_day']['music_rings'] = 'ring_main.mp3'
    config['all_day']['time_diner'] = ','.join(map(str, sorted(time_all_diner)))
    config['all_day']['music_diner'] = 'double_ring.mp3'

    config['holidays'] = {}
    config['holidays']['days'] = holidays
    config['holidays']['special_day'] = ','.join(map(str, sorted(special_day)))
    config['holidays']['weekend'] = ','.join(map(str, sorted(weekend)))

    make_backup()

    with open(FILENAME, 'w') as configfile:
        config.write(configfile)

def make_backup():
    current_date = datetime.datetime.now().strftime('%Y_%m-%d_%H_%M')
    new_file_name = 'config_' + current_date + '.ini'
    shutil.copy(FILENAME, new_file_name)

def get_conf_parser():
    config = configparser.ConfigParser()
    config.read(FILENAME)

    bell_time_all = []
    bell_time_spec = []
    bell_days_all = []
    bell_days_spec = []
    bell_days_weekend = []

    spec_time = ','.join(sorted(config['special_dasy']['time'].replace("\n", "").split(',')))
    spec_time_diner = ','.join(sorted(config['special_dasy']['time_diner'].replace("\n", "").split(',')))
    spec_music_rings = config['special_dasy']['music_rings'].replace("\n", "")
    spec_music_diner = config['special_dasy']['music_diner'].replace("\n", "")

    if len(spec_time):
        for s in spec_time.split(','):
            bell_time_spec.append([s, 1])
    if len(spec_time_diner):
        for s in spec_time_diner.split(','):
            bell_time_spec.append([s, 2])

    bell_time_spec = sorted(bell_time_spec, key=itemgetter(0))

    all_time = ','.join(sorted(config['all_day']['time'].replace("\n", "").split(',')))
    all_time_diner = ','.join(sorted(config['all_day']['time_diner'].replace("\n", "").split(',')))
    all_music_rings = config['all_day']['music_rings'].replace("\n", "")
    all_music_diner = config['all_day']['music_diner'].replace("\n", "")

    if len(all_time):
        for s in all_time.split(','):
            bell_time_all.append([s, 1])

    if len(all_time_diner):
        for s in all_time_diner.split(','):
            bell_time_all.append([s, 2])

    bell_time_all = sorted(bell_time_all, key=itemgetter(0))

    holidays = config['holidays']['days'].replace("\n", "")
    spec_days = config['holidays']['special_day'].replace("\n", "")
    weekend = config['holidays']['weekend'].replace("\n", "")

    for i in range(1, 8):
        if str(i) in spec_days:
            bell_days_spec.append([i, 1])
            bell_days_all.append([i, 0])
            bell_days_weekend.append([i, 0])
        elif str(i) in weekend:
            bell_days_weekend.append([i, 1])
            bell_days_all.append([i, 0])
            bell_days_spec.append([i, 0])
        else:
            bell_days_all.append([i, 1])
            bell_days_spec.append([i, 0])
            bell_days_weekend.append([i, 0])

    return_data = {'bell_time_spec': bell_time_spec,
                   'bell_time_all': bell_time_all,
                   'holidays': holidays,
                   'bell_days_all': bell_days_all,
                   'bell_days_spec': bell_days_spec,
                   'bell_days_weekend': bell_days_weekend}

    return return_data

def check_request(tasks):
    message = []

    for i in range(len(tasks)):
        if tasks[i] == '':
            tasks[i] = ' '

    all_time = tasks[4]
    all_time_diner = tasks[5]
    all_music_rings = tasks[6]
    all_music_diner = tasks[7]
    spec_time = tasks[0]
    spec_time_diner = tasks[1]
    spec_music_rings = tasks[2]
    spec_music_diner = tasks[3]
    holidays = tasks[8]
    spec_days = tasks[9]
    weekend = tasks[10]

    for time_str in all_time.split(','):
        try:
            date_time_obj = datetime.datetime.strptime(time_str, '%H:%M')
        except:
            message.append('Указан неверный формат времени в поле "Расписание общее: Час:Минута"')
            break

    for time_str in all_time_diner.split(','):
        try:
            date_time_obj = datetime.datetime.strptime(time_str, '%H:%M')
        except:
            message.append('Указан неверный формат времени в поле "Расписание общее обед: Час:Минута"')
            break

    if spec_time != ' ':
        for time_str in spec_time.split(','):
            try:
                date_time_obj = datetime.datetime.strptime(time_str, '%H:%M')
            except:
                message.append('Указан неверный формат времени в поле "Расписание специальное"')
                break

    if spec_time_diner != ' ':
        for time_str in spec_time_diner.split(','):
            try:
                date_time_obj = datetime.datetime.strptime(time_str, '%H:%M')
            except:
                message.append('Указан неверный формат времени в поле "Расписание специальное обед"')
                break

    return message

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def getBellDays(bell_days_all, bell_days_spec, bell_days_weekend):
    schedules_day_text_start = '<div class="container mx-auto row">'
    schedules_day_text_end = '</div>'
    schedules_day_all = '<div class="panel mt-5 panel-default row col"><b>Общие дни</b>'
    schedules_day_spec = '<div class="panel mt-5 panel-default row col"><b>Специальные дни</b>'
    schedules_day_week = '<div class="panel mt-5 panel-default row col"><b>Выходные</b>'

    weekday_en = ['Monday_', 'Tuesday_', 'Wednesday_', 'Thursday_', 'Friday_', 'Saturday_', 'Sunday_']
    weekday_ru = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    checked = ['', 'checked']

    for i in range(7):
        schedules_day_all = schedules_day_all + f"""
        <div class ="form-check">
        <input class ="form-check-input" type="checkbox" value="{i}" name="checkbox" id="{weekday_en[i]}all" onclick = "validate(this.id)" {checked[bell_days_all[i][1]]}>
        <label class ="form-check-label" for ="{weekday_en[i]}all"> {weekday_ru[i]} </label >
        </div>"""
    schedules_day_all = schedules_day_all + schedules_day_text_end

    for i in range(7):
        schedules_day_spec = schedules_day_spec + f"""
        <div class ="form-check">
        <input class ="form-check-input" type="checkbox" value="{i+10}" name="checkbox" id="{weekday_en[i]}spe" onclick = "validate(this.id)" {checked[bell_days_spec[i][1]]}>
        <label class ="form-check-label" for ="{weekday_en[i]}spe"> {weekday_ru[i]} </label >
        </div>"""
    schedules_day_spec = schedules_day_spec + schedules_day_text_end

    for i in range(7):
        schedules_day_week = schedules_day_week + f"""
        <div class ="form-check">
        <input class ="form-check-input" type="checkbox" value="{i+20}" name="checkbox" id="{weekday_en[i]}wkn" onclick = "validate(this.id)" {checked[bell_days_weekend[i][1]]}>
        <label class ="form-check-label" for ="{weekday_en[i]}wkn"> {weekday_ru[i]} </label >
        </div>"""
    schedules_day_week = schedules_day_week + schedules_day_text_end

    schedules_day_all = schedules_day_text_start + schedules_day_all + schedules_day_spec + schedules_day_week + schedules_day_text_end

    return schedules_day_all

def getBellTimes(all_time, spec_time):
    schedules_time_all_text_start = '<div class="row">'
    schedules_time_all_text_end = '</div>'
    schedules_time_all_text_table = '</table>'
    schedules_time_separator = '<div class ="panel panel-default row col-1"> </div>'

    schedules_time_all = """
        <div class="panel panel-default row col mb-auto"><b>Расписание общее</b>
        <table class="table table-striped mt-2" id="table_all">
            <tr>
                <th class="col-xs-2">Номер</th>
                <th class="col-xs-2">Время</th>
                <th class="col-xs-2">Вид звонка</th>
            </tr>"""

    schedules_time_spec = """
    <div class="panel panel-default row col mb-auto"><b>Расписание специальное</b>
    <table class="table table-striped mt-2" id="table_spec">
            <tr>
                <th class="col-xs-2">Номер</th>
                <th class="col-xs-2">Время</th>
                <th class="col-xs-2">Вид звонка</th>
            </tr>"""

    schedules_time_all_button = """
    <div class="text-right">
            <input type="button" class="btn btn-success float-end" value="Добавить" onclick="add_row('all')"/>
    </div>"""
    schedules_time_spec_button = """
    <div class="text-right">
            <input type="button" class="btn btn-success float-end" onclick="add_row('spec')" value="Добавить"/>
    </div>"""

    for t in all_time:
        ind = all_time.index(t) + 1
        if t[1] == 1:
            selected_one = 'selected'
            selected_two = ''
        elif t[1] == 2:
            selected_one = ''
            selected_two = 'selected'

        schedules_time_all = schedules_time_all + f"""
        <tr id="all_row_{ind}">
                <td>{ind}<button class="btn btn-warning" onclick="delRow('all_row_{ind}')">X</button></td>
                <td><input class="form-control" id="time_all_{ind}" type="time" data-format="hh:mm" value="{t[0]}"/></td>
                <td>
                    <select class="form-select" id="select_all_{ind}">
                        <option value="1" {selected_one}>Одинарный</option>
                        <option class="fw-weight-bold fw-bold" value="2" {selected_two}>Двойной</option>
                    </select>
                </td>
            </tr>"""

    for t in spec_time:
        ind = spec_time.index(t) + 1
        if t[1] == 1:
            selected_one = 'selected'
            selected_two = ''
        elif t[1] == 2:
            selected_one = ''
            selected_two = 'selected'

        schedules_time_spec = schedules_time_spec + f"""
        <tr id="spec_row_{ind}">
                <td>{ind}<button class="btn btn-warning" onclick="delRow('spec_row_{ind}')">X</button></td>
                <td><input class="form-control" id="time_spec_{ind}" type="time" data-format="hh:mm" value="{t[0]}"/></td>
                <td>
                    <select class="form-select" id="select_spec_{ind}">
                        <option value="1" {selected_one}>Одинарный</option>
                        <option value="2" {selected_two}>Двойной</option>
                    </select>
                </td>
            </tr>"""

    schedules_time = schedules_time_all_text_start + schedules_time_all + schedules_time_all_text_table + schedules_time_all_button + schedules_time_all_text_end + schedules_time_separator + schedules_time_spec + schedules_time_all_text_table + schedules_time_spec_button + schedules_time_all_text_end + schedules_time_all_text_end

    return schedules_time

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_user(username, password):
            return redirect(url_for('config_bells'))
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/about', methods=['GET', 'POST'])
def about():
    if not session.get("name"):
        return redirect("/login")
    return render_template('about.html')

@app.route('/')
def config_bells():
    if not session.get("name"):
        return redirect("/login")
    return redirect("/edit_table")

def get_ini_files():
    current_directory = os.getcwd()
    ini_files = []
    for root, dirs, files in os.walk(current_directory):
        for file in files:
            if file.endswith('.ini'):
                ini_files.append(file)
    return ini_files

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if not session.get("name"):
        return redirect("/login")
    if request.method == 'POST':
        result = check_filename(request)
        if result:
            return result
        else:
            save_file(request)
            return redirect(url_for('config_bells'))
    ini_files = get_ini_files()
    return render_template('upload.html', ini_files=ini_files)

@app.route('/download/<file_name>')
def download(file_name):
    if not session.get("name"):
        return redirect("/login")
    if not 'config' in file_name or not'.ini' in file_name:
        flash('Ошибка получения файла')
        return redirect("/edit_table")
    path = os.path.abspath(file_name)
    try:
        return send_file(path, as_attachment=True)
    except FileNotFoundError:
        flash('Ошибка получения файла')
        return redirect("/edit_table")

@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/login")

@app.route('/edit_table', methods=['GET', 'POST'])
def edit_table():
    modal = True
    if not session.get("name"):
        return redirect("/login")
    if session.get('name') == 'admin':
        modal = False
    if request.method == 'POST':
        request_json = request.get_json(force=True)
        put_conf_parser(request_json)
        return render_template('/edit_table.html', modal=modal, username=session.get("name"))
    else:
        tasks = get_conf_parser()

        all_time = tasks['bell_time_all']
        spec_time = tasks['bell_time_spec']
        holidays = tasks['holidays']
        bell_days_all = tasks['bell_days_all']
        bell_days_spec = tasks['bell_days_spec']
        bell_days_weekend = tasks['bell_days_weekend']

        bell_days = getBellDays(bell_days_all, bell_days_spec, bell_days_weekend)
        bell_time = getBellTimes(all_time, spec_time)

        return render_template('/edit_table.html',
                               modal=modal,
                               username=session.get("name"),
                               bell_time=bell_time,
                               bell_days=bell_days,
                               holidays=holidays)

@app.errorhandler(404)
def not_found(e):
    return redirect("/edit_table")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5050')
