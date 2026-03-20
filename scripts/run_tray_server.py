from app import app, get_server_host, get_server_port, init_db


if __name__ == "__main__":
    init_db()
    app.run(host=get_server_host(), port=get_server_port(), debug=False, use_reloader=False)
