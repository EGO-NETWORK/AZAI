import logging
import re
import os
from aiohttp import web
from aiohttp.http_exceptions import BadStatusLine
import asyncio
import config
import aiohttp
import traceback
import math
import mimetypes
import secrets

from config import multi_clients, work_loads
from AloneX.helpers import pyro_utils
from AloneX.helpers.render_template import render_page

logger = logging.getLogger(__name__)
routes = web.RouteTableDef()


@routes.get("/", allow_head=True)
async def root_route_handler(request):
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AZAI - EGO Network</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: Arial, sans-serif;
        }
        body {
            min-height: 100vh;
            background: radial-gradient(circle at top, #14213d 0%, #05060a 55%, #000 100%);
            color: #fff;
            line-height: 1.6;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }
        .card {
            width: 100%;
            max-width: 900px;
            padding: 36px 28px;
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 24px;
            background: rgba(255,255,255,0.06);
            box-shadow: 0 0 60px rgba(0, 136, 255, 0.18);
            text-align: center;
            backdrop-filter: blur(14px);
        }
        .brand {
            color: #9fd3ff;
            letter-spacing: 3px;
            text-transform: uppercase;
            font-size: 13px;
            margin-bottom: 14px;
        }
        h1 {
            font-size: clamp(42px, 8vw, 84px);
            line-height: 1;
            margin-bottom: 18px;
            background: linear-gradient(90deg, #ffffff, #8fd3ff, #f5c542);
            -webkit-background-clip: text;
            color: transparent;
        }
        .subtitle {
            font-size: 18px;
            color: #d7e8ff;
            margin-bottom: 26px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
            gap: 14px;
            margin: 26px 0;
        }
        .chip {
            padding: 14px;
            border-radius: 14px;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.10);
            color: #eef7ff;
        }
        .cta {
            display: inline-block;
            margin-top: 18px;
            padding: 14px 28px;
            border-radius: 999px;
            background: linear-gradient(90deg, #0077ff, #f5c542);
            color: #05060a;
            font-weight: 800;
            text-decoration: none;
        }
        footer {
            margin-top: 28px;
            color: #a9b6c7;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <main class="card">
        <div class="brand">EGO Network · EST. 2026</div>
        <h1>AZAI</h1>
        <p class="subtitle">Official Telegram community automation system by MR EGO.</p>
        <div class="grid">
            <div class="chip">Protection</div>
            <div class="chip">Economy</div>
            <div class="chip">Games</div>
            <div class="chip">Anime Quiz</div>
            <div class="chip">Media Panels</div>
            <div class="chip">AI Chat</div>
        </div>
        <a class="cta" href="https://t.me/EGOxSUPPORT" target="_blank">Support</a>
        <footer>Controlled by MR EGO · Powered by EGO Network</footer>
    </main>
</body>
</html>
    """
    return web.Response(text=html_content, content_type="text/html")


@routes.get("/health", allow_head=True)
@routes.get("/ping", allow_head=True)
@routes.get("/_health", allow_head=True)
async def health_route_handler(request):
    return web.json_response(
        {
            "status": "ok",
            "service": "AZAI",
            "network": "EGO Network",
            "owner": "MR EGO",
        }
    )


####################################################################################################


class InvalidHash(Exception):
    message = "Invalid hash"


class FIleNotFound(Exception):
    message = "File not found"


@routes.get(r"/watch/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)

        if match:
            secure_hash = match.group(1)
            message_id = int(match.group(2))
        else:
            message_id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")

        return web.Response(text=await render_page(message_id, secure_hash), content_type='text/html')
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logger.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=str(e))


@routes.get(r"/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)

        if match:
            secure_hash = match.group(1)
            message_id = int(match.group(2))
        else:
            message_id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")

        return await media_streamer(request, message_id, secure_hash)
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logger.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=str(e))


class_cache = {}


async def media_streamer(request: web.Request, message_id: int, secure_hash: str):
    range_header = request.headers.get("Range", 0)

    index = min(work_loads, key=work_loads.get)
    faster_client = multi_clients[index]

    if config.MULTI_CLIENT:
        logger.debug(f"Client {index} is now serving {request.remote}")

    if faster_client in class_cache:
        tg_connect = class_cache[faster_client]
        logger.debug(f"Using cached ByteStreamer object for client {index}")
    else:
        logger.debug(f"Creating new ByteStreamer object for client {index}")
        tg_connect = pyro_utils.ByteStreamer(faster_client)
        class_cache[faster_client] = tg_connect

    logger.debug("before calling get_file_properties")
    file_id = await tg_connect.get_file_properties(message_id)
    logger.debug("after calling get_file_properties")

    if file_id.unique_id[:6] != secure_hash:
        logger.debug(f"Invalid hash for message with ID {message_id}")
        raise InvalidHash

    file_size = file_id.file_size
    if range_header:
        from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
        from_bytes = int(from_bytes)
        until_bytes = int(until_bytes) if until_bytes else file_size - 1
    else:
        from_bytes = request.http_range.start or 0
        until_bytes = request.http_range.stop or file_size - 1

    req_length = until_bytes - from_bytes
    new_chunk_size = await pyro_utils.chunk_size(req_length)
    offset = await pyro_utils.offset_fix(from_bytes, new_chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = (until_bytes % new_chunk_size) + 1
    part_count = math.ceil(req_length / new_chunk_size)
    body = tg_connect.yield_file(
        file_id, index, offset, first_part_cut, last_part_cut, part_count, new_chunk_size
    )

    mime_type = file_id.mime_type
    file_name = file_id.file_name
    disposition = "attachment"
    if mime_type:
        if not file_name:
            try:
                file_name = f"{secrets.token_hex(2)}.{mime_type.split('/')[1]}"
            except (IndexError, AttributeError):
                file_name = f"{secrets.token_hex(2)}.bin"
    else:
        if file_name:
            mime_type = mimetypes.guess_type(file_id.file_name)
        else:
            mime_type = "application/octet-stream"
            file_name = f"{secrets.token_hex(2)}.bin"
    if "video/" in mime_type or "audio/" in mime_type:
        disposition = "inline"
    return_resp = web.Response(
        status=206 if range_header else 200,
        body=body,
        headers={
            "Content-Type": f"{mime_type}",
            "Range": f"bytes={from_bytes}-{until_bytes}",
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Disposition": f'{disposition}; filename="{file_name}"',
            "Accept-Ranges": "bytes",
        },
    )

    if return_resp.status == 200:
        return_resp.headers.add("Content-Length", str(file_size))

    return return_resp


####################################################################################################


async def keep_alive():
    """
    Pings config.WEB_URL every config.WEB_SLEEP seconds.
    Handles cancellation gracefully so shutdown won't leave a pending task.
    """
    if not config.WEB_URL:
        return

    try:
        while True:
            await asyncio.sleep(config.WEB_SLEEP)
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                    async with session.get(config.WEB_URL) as resp:
                        logger.info("Pinged %s with response: %s", config.WEB_URL, resp.status)
            except asyncio.TimeoutError:
                logger.warning("Couldn't connect to the site URL (timeout).")
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Error while pinging keep-alive URL")
    except asyncio.CancelledError:
        logger.info("keep_alive task cancelled, exiting cleanly.")
        raise


async def _on_startup(app: web.Application):
    """Start background keep_alive task (if configured) and save it on app"""
    if config.WEB_URL:
        logger.debug("Starting keep_alive background task")
        task = asyncio.create_task(keep_alive(), name="keep_alive_task")
        app["keep_alive_task"] = task


async def _on_cleanup(app: web.Application):
    """Cancel background task and await it so it doesn't remain pending"""
    task = app.get("keep_alive_task")
    if not task:
        return
    logger.debug("Cancelling keep_alive background task")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.debug("keep_alive task cancelled successfully during cleanup")
    except Exception:
        logger.exception("Error while waiting for keep_alive task during cleanup")


def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    web_app.on_startup.append(_on_startup)
    web_app.on_cleanup.append(_on_cleanup)
    return web_app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    try:
        web.run_app(web_server(), host="0.0.0.0", port=port)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down web app")
