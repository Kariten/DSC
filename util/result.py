from flask import jsonify


class ApiResult:
    def __init__(self, data):
        self.data = data

    def success(self, msg):
        return jsonify({'code': '0', 'msg': msg, 'data': self.data})

    def fault(self, msg):
        return jsonify({'code': '1', 'msg': msg, 'data': self.data})
