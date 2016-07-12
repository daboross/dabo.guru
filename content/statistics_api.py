import logging
import time

from flask import request

from content import app, redis
from resources_lib.statistics_key_names import *


@app.route("/statistics/v1/<plugin>/post/", methods=["POST"])
def statistics_record(plugin):
    if request.content_length > 512:
        return """Error: too large of a message""", 400
    json = request.get_json()
    if json is None:
        logging.debug("Non-json data sent to plugin/skywars/post: {}", request.get_data().decode())
        return

    guid = json["guid"]
    plugin_version = json["plugin_version"]
    server_version = json["server_version"]
    player_count = json["player_count"]

    if (guid is None or plugin_version is None or player_count is None
        or server_version is None or not isinstance(player_count, int)):
        logging.debug("Invalid request to skywars statistics: {}", json)
        return

    pipe = redis.pipeline(transaction=True)

    pipe.sadd(PLUGIN_VERSION_LIST.format(plugin), plugin_version)

    servers_hash_key = VERSION_SERVER_HASH.format(plugin, plugin_version)
    expiration_time = int(time.time()) + 2 * 60 * 60  # expires in two hours
    pipe.zadd(servers_hash_key, expiration_time, guid)

    data_key = SERVER_DATA_SET.format(plugin, guid)
    pipe.hmset(data_key, {"players": player_count, "server": server_version})
    pipe.expire(data_key, 2 * 61 * 60)  # one minute after key above expires

    pipe.execute()
