import asyncio

import aiohttp
from flask import flash, redirect, render_template, request, url_for

from settings import Config
from yacut import app, db
from yacut.forms import FilesForm, URLForm
from yacut.models import URLMap
from yacut.utils import get_unique_short_id


@app.route("/", methods=["GET", "POST"])
def index():
    """Главная страница с формой для создания короткой ссылки."""
    form = URLForm()
    if form.validate_on_submit():
        original = form.original_link.data.strip()
        custom = form.custom_id.data.strip() if form.custom_id.data else None

        if custom and (
            custom.lower() == "files"
            or URLMap.query.filter_by(short=custom).first()
        ):
            flash("Предложенный вариант короткой ссылки уже существует.")
            return render_template("index.html", form=form)

        short = custom or get_unique_short_id()
        db.session.add(URLMap(original=original, short=short))
        db.session.commit()
        short_url = url_for("redirect_short", short=short, _external=True)
        return render_template("index.html", form=form, short_url=short_url)

    return render_template("index.html", form=form)


@app.route("/<string:short>")
def redirect_short(short):
    """Перенаправление по короткой ссылке на оригинальный адрес."""
    mapping = URLMap.query.filter_by(short=short).first_or_404()
    return redirect(mapping.original)


async def upload_file_to_yadisk(session, token, file_obj):
    """Асинхронная загрузка одного файла на Яндекс.Диск."""
    headers = {"Authorization": f"OAuth {token}"}
    api_base = "https://cloud-api.yandex.net/v1/disk/resources"
    remote_path = f"app:/{get_unique_short_id()}_{file_obj.filename}"

    async with session.get(
        f"{api_base}/upload",
        headers=headers,
        params={"path": remote_path, "overwrite": "true"},
    ) as resp:
        data = await resp.json()
        if resp.status != 200 or "href" not in data:
            raise Exception(
                f"Ошибка получения ссылки для загрузки: {resp.status} {data}"
            )
        upload_href = data["href"]

    file_obj.stream.seek(0)
    content = file_obj.read()
    async with session.put(upload_href, data=content) as resp:
        if resp.status not in (200, 201):
            raise Exception(
                f"Ошибка загрузки {file_obj.filename}: {resp.status} "
                f"{await resp.text()}"
            )

    public_url = None
    try:
        async with session.put(
            f"{api_base}/publish",
            headers=headers,
            params={"path": remote_path},
        ) as pub_resp:
            if pub_resp.status in (200, 201):
                async with session.get(
                    api_base, headers=headers, params={"path": remote_path}
                ) as info_resp:
                    if info_resp.status == 200:
                        info = await info_resp.json()
                        public_url = info.get("public_url")
    except Exception:
        public_url = None

    if not public_url:
        async with session.get(
            f"{api_base}/download",
            headers=headers,
            params={"path": remote_path},
        ) as resp:
            if resp.status == 200:
                public_url = (await resp.json()).get("href")

    if not public_url:
        raise Exception("Не удалось получить ссылку для скачивания")

    return public_url


async def upload_files(token, files):
    """Асинхронная параллельная загрузка нескольких файлов на Яндекс.Диск."""
    async with aiohttp.ClientSession() as session:
        tasks = [upload_file_to_yadisk(session, token, f) for f in files]
        return await asyncio.gather(*tasks, return_exceptions=True)


@app.route("/files", methods=["GET", "POST"])
def files():
    """Страница загрузки файлов с генерацией коротких ссылок."""
    form = FilesForm()
    uploaded_files = []

    if form.validate_on_submit():
        files_list = request.files.getlist("files")
        if not files_list or all(not f.filename for f in files_list):
            flash("Выберите хотя бы один файл.")
            return render_template(
                "files.html", form=form, uploaded_files=uploaded_files
            )

        token = getattr(Config, "DISK_TOKEN", None)
        if not token:
            flash("Токен Яндекс.Диска не настроен.")
            return render_template(
                "files.html", form=form, uploaded_files=uploaded_files
            )

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(upload_files(token, files_list))
            loop.close()

            for file_obj, result in zip(files_list, results):
                if isinstance(result, Exception):
                    raise result

                short_id = get_unique_short_id()
                while URLMap.query.filter_by(short=short_id).first():
                    short_id = get_unique_short_id()

                db.session.add(URLMap(original=result, short=short_id))
                uploaded_files.append(
                    {
                        "filename": file_obj.filename,
                        "short_url": url_for(
                            "redirect_short", short=short_id, _external=True
                        ),
                    }
                )

            db.session.commit()
            flash("Файлы успешно загружены!")
        except Exception as exc:
            flash(f"Ошибка при загрузке файлов: {exc}")

    return render_template(
        "files.html", form=form, uploaded_files=uploaded_files
    )
