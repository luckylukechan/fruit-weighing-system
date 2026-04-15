from flask import render_template, request, redirect, session, jsonify
from web.admin_service import AdminService
import config

admin_service = AdminService()

def register_admin_routes(app):

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            ok, msg = admin_service.verify_login(username, password)
            if ok:
                session['admin_login'] = True
                # return redirect('/admin')
                return redirect('/admin/menu')
            else:
                return render_template('login.html', error=msg)

        return render_template('login.html')

    @app.route('/admin/price')
    def admin_home():
        if not session.get('admin_login'):
            return redirect('/login')

        fruits = admin_service.get_all_fruits()
        return render_template('admin_price.html', fruits=fruits)

    @app.route('/logout')
    def logout():
        session.pop('admin_login', None)
        return redirect('/login')

    @app.route('/admin/update_price', methods=['POST'])
    def update_price():
        data = request.json
        class_id = data.get('class')
        new_price = data.get('price')

        admin_service.update_price(class_id, new_price)
        return jsonify({"status": "ok"})

    # 后台管理菜单
    @app.route('/admin/menu')
    def admin_menu():
        if not session.get('admin_login'):
            return redirect('/login')

        return render_template('admin_menu.html')

    # 查找价格界面
    @app.route('/admin/data')
    def data_query():
        if not session.get('admin_login'):
            return redirect('/login')

        page = int(request.args.get('page', 1))
        status = request.args.get('status', 'all')

        data, total = admin_service.get_transaction_list(page, status)

        return render_template(
            'admin_data.html',
            transactions=data,
            page=page,
            status=status,
            total=total,
            PAGE_SIZE=config.PAGE_SIZE
        )

    # 页内展示
    @app.route('/admin/data/detail')
    def data_detail():
        if not session.get('admin_login'):
            return jsonify({"error": "not login"})

        session_id = request.args.get('session')

        details = admin_service.get_session_detail(session_id)

        return jsonify(details)