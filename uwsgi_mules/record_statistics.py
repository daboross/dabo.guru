import logging
import time
import traceback

import sys
from apscheduler.schedulers.blocking import BlockingScheduler
from collections import Counter
from redis import StrictRedis

from resources_lib import configuration_resources

# TODO: Make all of these pure byte format strings once python3.5 (with '%' formatting for bytes) is widely available.
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
        plugin_version = plugin_version.decode('utf-8')
        plugin_count = 0
        server_version_to_plugin_count = Counter()

        gte_key = VERSION_SERVER_HASH.format(plugin, plugin_version)

        # expire things:
        expire_pipeline.zremrangebyscore(gte_key, '-inf', '({}'.format(current_time))

        guid_list = redis.zrangebyscore(gte_key, current_time, '+inf')
        for guid in guid_list:
            guid = guid.decode('utf-8')
            plugin_count += 1
            sd_key = SERVER_DATA_SET.format(plugin, guid)
            server_data = redis.hgetall(sd_key)
            total_player_count += int(server_data[b"players"].decode('ascii'))
            server_version_to_plugin_count[server_data[b"server"].decode('utf-8')] += 1

        if plugin_count > 0:
            plugin_version_to_count[plugin_version] = plugin_count
            plugin_version_to_server_version_plugin_counts[plugin_version] = server_version_to_plugin_count
            plugin_versions.add(plugin_version)

    expire_pipeline.execute()

    if not plugin_versions:
        return

    data_pipeline = redis.pipeline(transaction=True)

    record_list_key = RECORD_LIST.format(plugin)
    data_pipeline.rpush(record_list_key, current_time)

    plugin_version_counts_key = RECORD_PLUGIN_VERSION_PLUGIN_COUNTS.format(plugin, current_time)
    data_pipeline.hmset(plugin_version_counts_key, plugin_version_to_count)

    total_players_key = RECORD_TOTAL_PLAYERS.format(plugin, current_time)
    data_pipeline.set(total_players_key, total_player_count)

    plugin_versions_key = RECORD_PLUGIN_VERSIONS.format(plugin, current_time)
    data_pipeline.rpush(plugin_versions_key, plugin_versions)

    for (plugin_version, server_version_to_plugin_count) in plugin_version_to_server_version_plugin_counts.items():
        svpc_key = RECORD_SERVER_VERSION_PLUGIN_COUNTS.format(plugin, current_time, plugin_version)
        data_pipeline.hmset(svpc_key, server_version_to_plugin_count)

    data_pipeline.execute()


def recording_loop():
    logging.info("Starting recording loop")
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
    if "--record-now" in sys.argv:
        record_record()
    else:
        main()
