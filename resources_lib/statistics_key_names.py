
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
