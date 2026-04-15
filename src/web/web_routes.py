from flask import render_template, jsonify, request
from web.web_service import WebService
from data.runtime_state import state
from datetime import datetime, timedelta
import config

web_service = WebService()

def register_web_routes(app):
    #结算界面
    @app.route('/')
    def index():
        data = web_service.get_index_data()
        return render_template('index.html', **data)

    # 支付按钮
    @app.route('/pay', methods=['POST'])
    def pay():
        action = request.json.get('action')
        web_service.pay(action)
        return ''

    # 付款界面
    @app.route('/pay_page')
    def pay_page():
        with state.lock:
            state.timeout_time = datetime.now() + timedelta(seconds=config.TIMEOUT_SECONDS) # 重置为新的时间
            total_price = state.current_data.get('total_price', 0.0)
            remaining_time = config.TIMEOUT_SECONDS # 计算剩余时间

        return render_template(
            'pay.html',
            total_price=total_price,
            remaining_time=remaining_time
        )

    # 传输全局信息（class、重量、单品价格、总价等）
    @app.route('/data')
    def data():
        return jsonify(web_service.get_current_data())

    # 全局传输session
    @app.route('/session_items')
    def session_items():
        return jsonify(web_service.get_session_items())

    # 结算界面用户删除商品
    @app.route('/delete_item', methods=['POST'])
    def delete_item():
        item_id = request.json.get('id')
        web_service.delete_item(item_id)
        return ''


