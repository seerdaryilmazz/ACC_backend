from accompany import create_app

app = create_app()


@app.route("/", methods=["GET"])
def home():
    return "<h1>In progress..</h1>"


if __name__ == "__main__":

    app.run()
