VERSION = '030320241522'
def get_version():
    filename = "https://github.com/shatohindmitry/school_bell/blob/master/version.py"
    with open(filename, 'r') as f:
        first_line = f.readline().strip('\n')
        if not first_line[0, -11] == VERSION:
            version = first_line[0, -11]
            return f'Текущая версия {VERSION} отличается от новой {version}.'
    return VERSION