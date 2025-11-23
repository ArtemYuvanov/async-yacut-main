import asyncio

from flask import redirect, render_template, flash

from settings import Config
from yacut import app
from yacut.forms import FilesForm, URLForm
from yacut.models import URLMap
from yacut.async_upload import upload_files


@app.route("/", methods=["GET", "POST"])
def index():
    """Главная страница с формой для создания короткой ссылки."""
    form = URLForm()
    if form.validate_on_submit():
        try:
            flash(
                URLMap.create(
                    original=form.original_link.data,
                    short=form.custom_id.data
                ).short_url(),
                "success"
            )
        except ValueError as exc:
            flash(str(exc), "danger")
        return render_template("index.html", form=form)
    return render_template("index.html", form=form)


@app.route("/<string:short>")
def redirect_short(short):
    """Перенаправление по короткой ссылке на оригинальный адрес."""
    mapping = URLMap.get_by_short(short)
    return redirect(mapping.original)


@app.route("/files", methods=["GET", "POST"])
def files():
    form = FilesForm()
    if form.validate_on_submit():
        try:
            try:
                results = asyncio.run(upload_files(
                    Config.DISK_TOKEN, form.files.data
                ))
            except Exception as exc:
                flash(f"Ошибка загрузки файлов: {exc}", "danger")
                return render_template("files.html", form=form)

            uploaded_files = [
                {
                    "filename": f.filename,
                    "short_url": URLMap.create(original=url).short_url()
                } if not isinstance(url, Exception) else {
                    "filename": f.filename,
                    "error": str(url)
                }
                for f, url in zip(form.files.data, results)
            ]
            flash("Файлы успешно загружены!", "success")
            return render_template(
                "files.html",
                form=form,
                uploaded_files=uploaded_files
            )

        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("files.html", form=form)

    return render_template("files.html", form=form)
