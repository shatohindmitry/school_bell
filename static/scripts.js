function validate(id) {
var name_id = id.slice(0, -3);
var name_id_end = id.slice(-3);

var elm_spe = document.getElementById(name_id + 'spe');
var elm_all = document.getElementById(name_id +'all');
var elm_wkn = document.getElementById(name_id +'wkn');

if (name_id_end == 'wkn'){
if (elm_wkn.checked) {
elm_spe.checked = false;
elm_all.checked = false;
}
}

if (name_id_end == 'all'){
if (elm_all.checked) {
elm_spe.checked = false;
elm_wkn.checked = false;
}
}

if (name_id_end == 'spe'){
if (elm_spe.checked) {
elm_all.checked = false;
elm_wkn.checked = false;
}
}
}

function add_row(id) {
var rowCount = document.getElementById('table_'+id).rows.length;
var idCount = 'select_' + id + '_' + rowCount;
var idTime = 'time_' + id + '_' + rowCount;
var str = `
<tr>
<td>rowCount</td>
<td><input class="form-control" id="time_" type="time" data-format="hh:mm" value="00:00"/></td>
<td>
<select class="form-select" id="select_">
<option value="1" selected>Одинарный</option>
<option value="2">Двойной</option>
</select>
</td> </tr>`;
str = str.replace('rowCount', rowCount);
str = str.replace('select_', idCount);
str = str.replace('time_', idTime);
document.getElementById('table_'+id).innerHTML += str;
}


function sendData() {
    var data = getdata();

const response = fetch('./edit_table', {
  method: 'POST',
  headers: {
   'Content-Type': 'application/json;charset=utf-8'
  },
  body: JSON.stringify(data)
});
window.location.replace(true);
document.getElementById("holidays").focus({ preventScroll: true });
}

function delRow(row_ind){
    const parent = document.getElementById(row_ind)
    while (parent.firstChild) {
        parent.firstChild.remove();
        parent.remove();
        }
    return false;
}

function getdata(){
    result = {}
    table_name = ['all','spec'];
    time_data = {};
    for (const t of table_name){
         rows = document.getElementById('table_'+ t).rows;
         for (r in rows){
            try{
            row_id = rows[Number(r)+1].getAttribute('id');
            if (row_id.slice(0, 3) == 'all'){
                id = row_id.slice(8,);
                }
                else {
                id = row_id.slice(9,);
                }
            time_element = document.getElementById("time_"+ t + '_' +id);
            time_value = time_element.value;
            bell_element = document.getElementById("select_"+ t + '_' +id);
            bell_value = bell_element.value;
            key = ''+t+id;
            value = [time_value, bell_value]
            time_data[key] = value;
            }catch{

            }

         }
    }
    result['time_data'] = time_data;
    let checkboxes = document.querySelectorAll('input[name="checkbox"]:checked');
    let output_days = [];
    checkboxes.forEach((checkbox) => {
        output_days.push(checkbox.value);
    });

    result['output_days'] = output_days;

    let holidays = document.getElementById('holidays');
    result['holidays'] = holidays.value;

    return result;
}
