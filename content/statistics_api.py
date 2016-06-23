import logging
import time

from flask import request

from content import app, redis

# (plugin_name, plugin_version): zset(guid: expiration_time)
version_set_key = "statistics:live:{}:version:{}:servers"
# (plugin_name, server_guid): int
player_count_key = "statistics:live:{}:server:{}:players"
# (plugin_name): list(recorded_time)
record_list = "statistics:{}:record-list"
# (plugin_name, recorded_time): hash(version: int)
record_version_counts = "statistics:{}:record:{}:version-counts"
# (plugin_name, recorded_time): int
record_total_players = "statistics:{}:record:{}:total-player-count"


@app.route("/plugin/<plugin>/post/", methods=["POST"])
def statistics_record(plugin):
    if request.content_length > 512:
        return """Error: too large of a message""", 400
    json = request.get_json()
    if json is None:
        logging.debug("Non-json data sent to plugin/skywars/post: {}", request.get_data().decode())
        return

    guid = json["guid"]
    version = json["plugin_version"]
    player_count = json["player_count"]

    if (guid is None or version is None or player_count is None
        or not isinstance(player_count, int)):
        logging.debug("Invalid request to skywars statistics: {}", json)
        return

    set_key = version_set_key.format(plugin, version)
    expiration_time = int(time.time()) + 2 * 60 * 60  # expires in two hours
    redis.zadd(set_key, expiration_time, guid)

    count_key = player_count_key.format(plugin, guid)
    redis.set(count_key, player_count)
