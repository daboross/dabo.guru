import logging
import time
import traceback

from apscheduler.schedulers.blocking import BlockingScheduler
from collections import Counter
from redis import StrictRedis

from resources_lib import configuration_resources

# (plugin_name): set(plugin_version)
PLUGIN_VERSION_LIST = "statistics:live:{}:versions"
# (plugin_name, plugin_version): zset(server_guid: expiration_time)
VERSION_SERVER_HASH = "statistics:live:{}:version:{}:servers"
# (plugin_name, server_guid): hash("players": player_count, "server": server_version)
SERVER_DATA_SET = "statistics:live:{}:server:{}:data"
# (plugin_name): list(recorded_time)
RECORD_LIST = "statistics:{}:record-list"
# (plugin_name, recorded_time): hash(plugin_version: plugin_count)
RECORD_PLUGIN_VERSION_PLUGIN_COUNTS = "statistics:{}:record:{}:version-counts"
# (plugin_name, recorded_time): int
RECORD_TOTAL_PLAYERS = "statistics:{}:record:{}:total-player-count"
# (plugin_name, recorded_time): set(plugin_version)
RECORD_PLUGIN_VERSIONS = "statistics:{}:record:{}:versions"
# (plugin_name, recorded_time, plugin_version): hash(server_version: plugin_count)
RECORD_SERVER_VERSION_PLUGIN_COUNTS = "statistics:{}:record:{}:version:{}:server-version-counts"

configuration_resources.set_working_directory()
configuration_resources.configure_logger("record_statistics-debug.log")

push = configuration_resources.get_pushbullet()
redis = StrictRedis()


def record_record():
    plugin = "skywars"

    logging.info("Saving record for plugin {}".format(plugin))

    current_time = int(time.time())

    total_player_count = 0
    plugin_versions = set()
    plugin_version_to_count = dict()
    plugin_version_to_server_version_plugin_counts = dict()

    expire_pipeline = redis.pipeline(transaction=False)

    for plugin_version in redis.smembers(PLUGIN_VERSION_LIST.format(plugin)):
        plugin_count = 0
        server_version_to_plugin_count = Counter()
        servers_to_remove = set()

        gte_key = VERSION_SERVER_HASH.format(plugin, plugin_version)

        guid_to_expiration = redis.hgetall(gte_key)
        for (guid, expiration) in guid_to_expiration:
            if expiration > current_time:
                servers_to_remove.add(guid)
                continue

            plugin_count += 1

            sd_key = SERVER_DATA_SET.format(plugin, guid)
            server_data = redis.hgetall(sd_key)
            total_player_count += server_data["players"]
            server_version_to_plugin_count[server_data["server"]] += 1
        if servers_to_remove:
            expire_pipeline.hdel(gte_key, *servers_to_remove)
        if plugin_count > 0:
            plugin_version_to_count[plugin_version] = plugin_count
            plugin_version_to_server_version_plugin_counts[plugin_version] = server_version_to_plugin_count
            plugin_versions.add(plugin_version)

    record_list_key = RECORD_LIST.format(plugin)

    if not plugin_versions:
        expire_pipeline.execute()
        return

    data_pipeline = redis.pipeline(transaction=True)
    data_pipeline.rpush(record_list_key, current_time)

    plugin_version_counts_key = RECORD_PLUGIN_VERSION_PLUGIN_COUNTS.format(plugin, current_time)
    data_pipeline.hmset(plugin_version_counts_key, plugin_version_to_count)

    total_players_key = RECORD_TOTAL_PLAYERS.format(plugin, current_time)
    data_pipeline.set(total_players_key, total_player_count)

    plugin_versions_key = RECORD_PLUGIN_VERSIONS.format(plugin, current_time)
    data_pipeline.rpush(plugin_versions_key, plugin_versions)

    for (plugin_version, server_version_to_plugin_count) in plugin_version_to_server_version_plugin_counts:
        svpc_key = RECORD_SERVER_VERSION_PLUGIN_COUNTS.format(plugin, current_time, plugin_version)
        data_pipeline.hmset(svpc_key, server_version_to_plugin_count)

    expire_pipeline.execute()
    data_pipeline.execute()


def recording_loop():
    sched = BlockingScheduler()
    sched.add_job(record_record, "cron", minute=0)
    sched.start()


def main():
    try:
        recording_loop()
    except Exception:
        logging.exception("Exception!")
        try:
            # since we have pushbullet, we can do exception notices :D
            push.push_note("Python Exception", traceback.format_exc())
        except Exception:
            logging.exception("Exception sending exception note.")


if __name__ == "__main__":
    main()
