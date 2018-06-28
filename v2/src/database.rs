use actix::prelude::*;
use failure;
use futures::Future;
use redis_async::resp::{FromResp, RespValue};

use redis::{self, RedisActor};

#[derive(Clone)]
pub struct Database {
    conn: Addr<RedisActor>,
}

impl Database {
    pub fn new() -> impl Future<Item = Database, Error = failure::Error> {
        RedisActor::new()
            .from_err()
            .map(|conn| Database { conn: conn.start() })
    }

    pub fn send<R>(&self, cmd: RespValue) -> impl Future<Item = R, Error = failure::Error>
    where
        R: FromResp + Send + 'static,
    {
        self.conn
            .send(redis::message(cmd))
            .then(|res| res.map_err(Into::into).and_then(|v| v))
    }
    pub fn transaction(
        &self,
        cmd: Vec<RespValue>,
    ) -> impl Future<Item = Vec<RespValue>, Error = failure::Error> {
        self.conn
            .send(redis::transaction(cmd))
            .then(|res| res.map_err(Into::into).and_then(|v| v))
    }
}
