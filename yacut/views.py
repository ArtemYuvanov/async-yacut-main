from flask import flash, redirect, render_template

from yacut import app
from yacut.async_upload import upload_files_sync
from yacut.forms import FilesForm, URLForm
from yacut.models import URLMap


@app.route("/", methods=["GET", "POST"])
def index():
    """Главная страница с формой для создания короткой ссылки."""
    form = URLForm()

    if not form.validate_on_submit():
        return render_template("index.html", form=form)

    try:
        return render_template(
            "index.html",
            form=form,
            short_url=URLMap.create(
                original=form.original_link.data,
                short=form.custom_id.data,
                validate=True,
            ).short_url()
        )
    except (ValueError, Exception) as exc:
        flash(str(exc), "danger")
        return render_template("index.html", form=form)


@app.route("/<string:short>")
def redirect_short(short):
    """Перенаправление по короткой ссылке на оригинальный адрес."""
    return redirect(URLMap.get_or_404(short).original)


@app.route("/files", methods=["GET", "POST"])
def files():
    """Загрузка и отображение списка файлов."""
    form = FilesForm()

    if not form.validate_on_submit():
        return render_template("files.html", form=form)

    try:
        uploaded_file_urls = upload_files_sync(form.files.data)
    except Exception as exc:
        flash(str(exc), "danger")
        return render_template("files.html", form=form)

    try:
        return render_template(
            "files.html",
            form=form,
            uploaded_files=[
                {
                    "filename": uploaded_file.filename,
                    "url": uploaded_url,
                    "short_url": URLMap.create(
                        original=uploaded_url,
                        validate=False
                    ).short_url(),
                }
                for uploaded_file, uploaded_url in zip(
                    form.files.data, uploaded_file_urls
                )
            ],
        )
    except ValueError as exc:
        flash(str(exc), "danger")
        return render_template("files.html", form=form)
