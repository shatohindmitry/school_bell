VERSION = '1.0'
import requests
def get_version():
    try:
        filepath = "https://raw.githubusercontent.com/shatohindmitry/school_bell/master/version.py"
        data = requests.get(filepath).text
        first_line = data.split('\n')[0]
        if not VERSION in first_line:
            version = first_line[10:]
            return f'Текущая версия {VERSION} отличается от новой {version}.'
    except:
        pass
    return f'v.{VERSION}'
