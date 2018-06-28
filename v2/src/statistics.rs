//! Plugin Statistics
use actix_web::{HttpRequest, Json, Path};
use regex::Regex;

use AppData;

static PLUGIN_SET: &str = "statistics:plugins";

lazy_static! {
    static ref MINECRAFT_VERSION_RE: Regex =
        Regex::new("\\(MC: ([0-9]\\.]+)\\)").expect("compile-time valid regex");
}

/// Type set(plugin_version)
fn plugin_version_list(name: &str) -> String {
    format!("statistics:live:{}:versions", name)
}

/// Type zset(server_guid => expiration_time)
fn version_server_hash(plugin_name: &str, server_guid: &str) -> String {
    format!(
        "statistics:live:{}:version:{}:servers",
        plugin_name, server_guid
    )
}

/// Type hash("players" => player_count, "server" => server_version)
fn server_data_set(plugin_name: &str, record_time: u64) -> String {
    format!(
        "statistics:live:{}:server:{}:data",
        plugin_name, record_time
    )
}

/// Type list(record_time)
fn record_list(plugin_name: &str) -> String {
    format!("statistics:{}:record-list", plugin_name)
}

/// Type hash(plugin_version => plugin_count)
fn record_plugin_version_plugin_counts(plugin_name: &str, record_time: &str) -> String {
    format!(
        "statistics:{}:record:{}:version-counts",
        plugin_name, record_time
    )
}

/// Type int
fn record_total_players(plugin_name: &str, record_time: &str) -> String {
    format!(
        "statistics:{}:record:{}:total-player-count",
        plugin_name, record_time
    )
}

/// Type set(plugin_version)
fn record_plugin_versions(plugin_name: &str, record_time: &str) -> String {
    format!("statistics:{}:record:{}:versions", plugin_name, record_time)
}

/// Type hash(server_version => plugin_count)
fn record_server_version_plugin_counts(
    plugin_name: &str,
    record_time: &str,
    plugin_version: &str,
) -> String {
    format!(
        "statistics:{}:record:{}:version:{}:server-version-counts",
        plugin_name, record_time, plugin_version
    )
}

fn trim_server_vesion(version: &str) -> &str {
    MINECRAFT_VERSION_RE
        .captures(version)
        .and_then(|c| c.get(1))
        .map(|m| m.as_str())
        .unwrap_or(version)
}

#[derive(Debug, Deserialize)]
pub struct StatisticsPostRequest {
    instance_uuid: String,
    plugin_version: String,
    server_version: String,
    online_players: u32,
}

pub(crate) fn post_statistics(
    (path, info, req): (
        Path<(String,)>,
        Json<StatisticsPostRequest>,
        HttpRequest<AppData>,
    ),
) -> String {
    let (plugin,) = path.into_inner();
    let StatisticsPostRequest {
        instance_uuid,
        plugin_version,
        server_version,
        online_players,
    } = info.into_inner();

    let server_version = trim_server_vesion(&server_version);
    let plugin = plugin.trim().to_lowercase();

    "".to_owned()
}
